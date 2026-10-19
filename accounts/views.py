from datetime import datetime
from decimal import Decimal, InvalidOperation
import os

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.http import FileResponse, Http404
from django.core.paginator import Paginator
from django.utils import timezone

from .models import Profile, Job, ApplyJob, ApplicationDocument, IndustryUpdate, CareerResource,LearningPath,LearningPathItem, LearningProgress
from django.contrib import messages
from django.views.decorators.http import require_POST



# --------------------------------------------------
# FILE VALIDATION HELPERS
# --------------------------------------------------

MAX_PDF_SIZE = 5 * 1024 * 1024  # 5 MB


def validate_pdf(uploaded_file):
    """Validate a PDF file before saving it."""

    if not uploaded_file:
        return None

    if uploaded_file.size > MAX_PDF_SIZE:
        return "PDF files must not exceed 5 MB."

    if os.path.splitext(uploaded_file.name)[1].lower() != ".pdf":
        return "Only PDF files are allowed."

    # Check the file signature rather than relying only on its extension.
    try:
        original_position = uploaded_file.tell()
        uploaded_file.seek(0)
        file_signature = uploaded_file.read(5)
        uploaded_file.seek(original_position)

        if file_signature != b"%PDF-":
            return "The uploaded file is not a valid PDF."

    except (OSError, ValueError):
        return "The uploaded PDF could not be read."

    return None


# --------------------------------------------------
# JOB FORM VALIDATION
# --------------------------------------------------

def validate_job_form(request):
    """Validate job form data without saving it."""

    data = {
        "title": (request.POST.get("title") or "").strip(),
        "company": (request.POST.get("company") or "").strip(),
        "description": (request.POST.get("description") or "").strip(),
        "location": (request.POST.get("location") or "").strip(),
        "job_type": (request.POST.get("job_type") or "").strip(),
        "skills": (request.POST.get("skills") or "").strip(),
        "salary": (request.POST.get("salary") or "").strip(),
        "deadline": (
            request.POST.get("application_deadline") or ""
        ).strip(),
    }

    errors = []

    required_fields = [
        "title",
        "company",
        "description",
        "location",
        "job_type",
        "skills",
        "salary",
        "deadline",
    ]

    if any(not data[field] for field in required_fields):
        errors.append("Please fill in all required fields.")

    salary = None

    if data["salary"]:
        try:
            salary_value = Decimal(data["salary"])

            if not salary_value.is_finite() or salary_value < 0:
                raise InvalidOperation

            if salary_value != salary_value.to_integral_value():
                errors.append("Salary must be a whole number.")
            else:
                salary = int(salary_value)

        except (InvalidOperation, ValueError, OverflowError):
            errors.append(
                "Enter a valid, non-negative whole-number salary."
            )

    deadline = None

    if data["deadline"]:
        try:
            deadline_date = datetime.strptime(
                data["deadline"],
                "%Y-%m-%d",
            ).date()

            deadline = timezone.make_aware(
                datetime.combine(
                    deadline_date,
                    datetime.max.time().replace(microsecond=0),
                ),
                timezone.get_current_timezone(),
            )

        except ValueError:
            errors.append("Enter a valid application deadline.")

    return data, salary, deadline, errors


# --------------------------------------------------
# PROFILE LIST AND PROFILE DETAILS
# --------------------------------------------------


@login_required
def profile_list(request):
    profiles = Profile.objects.select_related("user").all()

    # Preserve the industry filter for professional profiles.
    selected_industry = (
        request.GET.get("industry") or ""
    ).strip()

    valid_industries = [
        choice[0] for choice in Profile.INDUSTRY_CHOICES
    ]

    if selected_industry in valid_industries:
        profiles = profiles.filter(
            industry=selected_industry
        )
    else:
        selected_industry = ""

    # Fetch only updates published by the administrator.
    published_updates = (
        IndustryUpdate.objects
        .filter(published=True)
        .order_by("-featured", "-published_at", "-created_at")
    )

    # Match the field names already used by the HTML template.
    external_updates = [
        {
            "title": update.title,
            "description": update.description,
            "category": update.get_update_type_display(),
            "pubDate": update.published_at,
            "source": update.source_name or "JobHub",
            "link": update.source_url,
            "industry": update.get_industry_display(),
            "featured": update.featured,
        }
        for update in published_updates
    ]

    return render(
        request,
        "accounts/profile_list.html",
        {
            "profiles": profiles,
            "industry_choices": Profile.INDUSTRY_CHOICES,
            "selected_industry": selected_industry,
            "external_updates": external_updates,
        },
    )




def profile_detail(request, id):
    profile = get_object_or_404(
        Profile.objects.select_related("user"),
        id=id,
    )

    return render(
        request,
        "accounts/profile_detail.html",
        {"profile": profile},
    )


# --------------------------------------------------
# USER REGISTRATION
# --------------------------------------------------


def register(request):
    if request.method != "POST":
        return render(
            request,
            "accounts/register.html",
            {
                "role": "job_seeker",
                "industry": "technology",
            },
        )

    username = (request.POST.get("username") or "").strip()
    first_name = (request.POST.get("first_name") or "").strip()
    last_name = (request.POST.get("last_name") or "").strip()
    email = (request.POST.get("email") or "").strip()
    password = request.POST.get("password") or ""
    confirm_password = request.POST.get("confirm_password") or ""
    role = (request.POST.get("role") or "job_seeker").strip()
    industry = (request.POST.get("industry") or "technology").strip()

    form_data = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "role": role,
        "industry": industry,
    }

    errors = []

    if not username or not password or not confirm_password:
        errors.append(
            "Username and both password fields are required."
        )

    if role not in ["job_seeker", "employer"]:
        errors.append("Please select a valid account type.")

    valid_industries = [
        choice[0] for choice in Profile.INDUSTRY_CHOICES
    ]

    if industry not in valid_industries:
        errors.append("Please select a valid industry.")

    if username and User.objects.filter(username=username).exists():
        errors.append("This username is already taken.")

    if password != confirm_password:
        errors.append("Passwords do not match.")

    candidate_user = User(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
    )

    if password:
        try:
            validate_password(password, user=candidate_user)
        except ValidationError as error:
            errors.extend(error.messages)

    if errors:
        return render(
            request,
            "accounts/register.html",
            {
                "errors": errors,
                **form_data,
            },
        )

    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
            )

            Profile.objects.create(
                user=user,
                role=role,
                industry=industry,
                bio="",
                location="",
                skills="",
                phone_number="",
                linkedin="",
                github="",
            )

    except IntegrityError:
        return render(
            request,
            "accounts/register.html",
            {
                "errors": [
                    "This username may already be in use. "
                    "Please choose another username."
                ],
                **form_data,
            },
        )

    return redirect("login")



# --------------------------------------------------
# LOGIN AND LOGOUT
# --------------------------------------------------

def login(request):
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            auth_login(request, user)
            return redirect("profile-list")

        return render(
            request,
            "accounts/login.html",
            {"error": "Invalid username or password."},
        )

    return render(request, "accounts/login.html")


def logout(request):
    if request.method == "POST":
        auth_logout(request)

    return redirect("login")


# --------------------------------------------------
# MY PROFILE
# --------------------------------------------------

@login_required
def my_profile(request):
    profile = get_object_or_404(Profile, user=request.user)

    return render(
        request,
        "accounts/my_profile.html",
        {"profile": profile},
    )


# --------------------------------------------------
# EDIT PROFILE
# --------------------------------------------------


@login_required
def profile_edit(request):
    profile = get_object_or_404(Profile, user=request.user)
    user = request.user

    if request.method == "POST":
        user.first_name = (
            request.POST.get("first_name") or ""
        ).strip()

        user.last_name = (
            request.POST.get("last_name") or ""
        ).strip()

        user.email = (
            request.POST.get("email") or ""
        ).strip()

        profile.bio = (
            request.POST.get("bio") or ""
        ).strip()

        profile.location = (
            request.POST.get("location") or ""
        ).strip()

        profile.skills = (
            request.POST.get("skills") or ""
        ).strip()

        profile.phone_number = (
            request.POST.get("phone_number") or ""
        ).strip()

        profile.linkedin = (
            request.POST.get("linkedin") or ""
        ).strip()

        profile.github = (
            request.POST.get("github") or ""
        ).strip()

        # Update the user's industry.
        industry = (
            request.POST.get("industry") or ""
        ).strip()

        valid_industries = [
            choice[0]
            for choice in Profile.INDUSTRY_CHOICES
        ]

        if industry not in valid_industries:
            return render(
                request,
                "accounts/profile_edit.html",
                {
                    "profile": profile,
                    "error": "Please select a valid industry.",
                    "industry_choices": Profile.INDUSTRY_CHOICES,
                },
            )

        profile.industry = industry

        # Update profile image if a new one is uploaded.
        uploaded_image = request.FILES.get("profile_image")

        if uploaded_image:
            profile.profile_image = uploaded_image

        # Update CV if a new one is uploaded.
        uploaded_cv = request.FILES.get("cv")

        if uploaded_cv:
            cv_error = validate_pdf(uploaded_cv)

            if cv_error:
                return render(
                    request,
                    "accounts/profile_edit.html",
                    {
                        "profile": profile,
                        "error": cv_error,
                        "industry_choices": Profile.INDUSTRY_CHOICES,
                    },
                )

            profile.cv = uploaded_cv

        # Remove the existing CV if requested.
        if request.POST.get("remove_cv") == "on":
            if profile.cv:
                profile.cv.delete(save=False)

            profile.cv = None

        user.save()
        profile.save()

        return redirect("my-profile")

    return render(
        request,
        "accounts/profile_edit.html",
        {"profile": profile,
        "industry_choices": Profile.INDUSTRY_CHOICES,
        }
    )

# --------------------------------------------------
# ALL JOBS, SEARCH AND PAGINATION
# --------------------------------------------------

def all_jobs(request):
    jobs = Job.objects.select_related("posted_by").all()

    search = (request.GET.get("search") or "").strip()
    job_type = (request.GET.get("job_type") or "").strip()
    location = (request.GET.get("location") or "").strip()

    locations = (
        Job.objects.order_by("location")
        .values_list("location", flat=True)
        .distinct()
    )

    if search:
        jobs = jobs.filter(
            Q(title__icontains=search)
            | Q(company__icontains=search)
            | Q(skills__icontains=search)
            | Q(description__icontains=search)
        )

    if job_type:
        jobs = jobs.filter(job_type__icontains=job_type)

    if location:
        jobs = jobs.filter(location__icontains=location)

    paginator = Paginator(jobs.order_by("-created_at"), 6)
    page_number = request.GET.get("page")
    jobs = paginator.get_page(page_number)

    return render(
        request,
        "accounts/all_jobs.html",
        {
            "jobs": jobs,
            "search": search,
            "job_type": job_type,
            "location": location,
            "locations": locations,
        },
    )


# --------------------------------------------------
# JOB DETAILS
# --------------------------------------------------

def job_detail(request, id):
    job = get_object_or_404(Job, id=id)

    return render(
        request,
        "accounts/job_detail.html",
        {
            "job": job,
            "today": timezone.now(),
        },
    )


# --------------------------------------------------
# CREATE JOB
# --------------------------------------------------

@login_required
def create_job(request):
    if (
        not hasattr(request.user, "profile")
        or request.user.profile.role != "employer"
    ):
        return redirect("all-jobs")

    if request.method == "POST":
        data, salary, deadline, errors = validate_job_form(request)

        if errors:
            return render(
                request,
                "accounts/create_job.html",
                {
                    "errors": errors,
                    "error": errors[0],
                    **data,
                },
            )

        Job.objects.create(
            title=data["title"],
            company=data["company"],
            description=data["description"],
            location=data["location"],
            job_type=data["job_type"],
            skills=data["skills"],
            salary=salary,
            deadline=deadline,
            posted_by=request.user,
        )

        return redirect("all-jobs")

    return render(request, "accounts/create_job.html")


# --------------------------------------------------
# EDIT JOB
# --------------------------------------------------

@login_required
def edit_job(request, id):
    if (
        not hasattr(request.user, "profile")
        or request.user.profile.role != "employer"
    ):
        return redirect("all-jobs")

    job = get_object_or_404(Job, id=id)

    if job.posted_by_id != request.user.id:
        return redirect("all-jobs")

    if request.method == "POST":
        data, salary, deadline, errors = validate_job_form(request)

        if errors:
            return render(
                request,
                "accounts/edit_job.html",
                {
                    "job": job,
                    "errors": errors,
                    "error": errors[0],
                    **data,
                },
            )

        job.title = data["title"]
        job.company = data["company"]
        job.description = data["description"]
        job.location = data["location"]
        job.job_type = data["job_type"]
        job.skills = data["skills"]
        job.salary = salary
        job.deadline = deadline
        job.save()

        return redirect("job-detail", id=job.id)

    return render(
        request,
        "accounts/edit_job.html",
        {"job": job},
    )


# --------------------------------------------------
# DELETE JOB
# --------------------------------------------------

@login_required
def delete_job(request, id):
    if (
        not hasattr(request.user, "profile")
        or request.user.profile.role != "employer"
    ):
        return redirect("all-jobs")

    job = get_object_or_404(Job, id=id)

    if job.posted_by_id != request.user.id:
        return redirect("all-jobs")

    if request.method == "POST":
        job.delete()
        return redirect("all-jobs")

    return render(
        request,
        "accounts/delete_job.html",
        {"job": job},
    )


# --------------------------------------------------
# APPLY FOR A JOB
# --------------------------------------------------

@login_required
def apply_job(request, id):
    # Only job seekers can apply.
    if (
        not hasattr(request.user, "profile")
        or request.user.profile.role != "job_seeker"
    ):
        return redirect("job-detail", id=id)

    job = get_object_or_404(Job, id=id)
    profile = request.user.profile

    # Prevent employers from applying to their own jobs.
    if job.posted_by_id == request.user.id:
        return redirect("job-detail", id=job.id)

    # Prevent applications after the deadline.
    if job.deadline and timezone.now() > job.deadline:
        return render(
            request,
            "accounts/apply_job.html",
            {
                "job": job,
                "profile": profile,
                "error": "The application deadline has passed.",
            },
        )

    if request.method == "POST":
        cover_letter = (
            request.POST.get("cover_letter") or ""
        ).strip()

        cover_letter_file = request.FILES.get("cover_letter_file")
        uploaded_cv = request.FILES.get("cv")
        portfolio_url = (
            request.POST.get("portfolio_url") or ""
        ).strip()

        # Prevent duplicate applications.
        if ApplyJob.objects.filter(
            user=request.user,
            job=job,
        ).exists():
            return render(
                request,
                "accounts/apply_job.html",
                {
                    "job": job,
                    "profile": profile,
                    "error": "You have already applied for this job.",
                },
            )

        # Use the newly uploaded CV or the CV saved on the profile.
        cv_file = uploaded_cv or profile.cv

        if not cv_file:
            return render(
                request,
                "accounts/apply_job.html",
                {
                    "job": job,
                    "profile": profile,
                    "error": (
                        "Please upload a CV for this application "
                        "or save one to your profile."
                    ),
                },
            )

        if not cover_letter and not cover_letter_file:
            return render(
                request,
                "accounts/apply_job.html",
                {
                    "job": job,
                    "profile": profile,
                    "error": (
                        "Please write a cover letter or upload "
                        "a cover letter PDF."
                    ),
                },
            )

        # Validate uploaded files.
        file_errors = []

        if uploaded_cv:
            error = validate_pdf(uploaded_cv)
            if error:
                file_errors.append(f"CV: {error}")

        if cover_letter_file:
            error = validate_pdf(cover_letter_file)
            if error:
                file_errors.append(f"Cover letter: {error}")

        # Validate the portfolio URL when supplied.
        if portfolio_url:
            try:
                URLValidator()(portfolio_url)
            except ValidationError:
                file_errors.append("Enter a valid portfolio URL.")

        # Read the supporting documents using the existing form fields.
        uploaded_documents = request.FILES.getlist("documents")
        document_types = request.POST.getlist("document_type")
        document_titles = request.POST.getlist("document_title")

        valid_document_types = {
            choice[0]
            for choice in ApplicationDocument.DOCUMENT_TYPE_CHOICES
        }

        for uploaded_file in uploaded_documents:
            error = validate_pdf(uploaded_file)
            if error:
                file_errors.append(
                    f"{uploaded_file.name}: {error}"
                )

        for document_type in document_types:
            if document_type not in valid_document_types:
                file_errors.append(
                    "Select a valid type for each supporting document."
                )
                break

        if file_errors:
            return render(
                request,
                "accounts/apply_job.html",
                {
                    "job": job,
                    "profile": profile,
                    "errors": file_errors,
                    "error": file_errors[0],
                },
            )

        try:
            with transaction.atomic():
                application = ApplyJob.objects.create(
                    user=request.user,
                    job=job,
                    cover_letter=cover_letter,
                    cover_letter_file=cover_letter_file,
                    cv=cv_file,
                    portfolio_url=portfolio_url,
                )

                for uploaded_file, document_type, title in zip(
                    uploaded_documents,
                    document_types,
                    document_titles,
                ):
                    if uploaded_file:
                        ApplicationDocument.objects.create(
                            application=application,
                            document_type=document_type,
                            title=(
                                title.strip()
                                or uploaded_file.name
                            ),
                            file=uploaded_file,
                        )

        except IntegrityError:
            return render(
                request,
                "accounts/apply_job.html",
                {
                    "job": job,
                    "profile": profile,
                    "error": (
                        "You have already applied for this job."
                    ),
                },
            )

        return redirect("my-applications")

    return render(
        request,
        "accounts/apply_job.html",
        {
            "job": job,
            "profile": profile,
        },
    )


# --------------------------------------------------
# APPLICANT'S APPLICATIONS
# --------------------------------------------------

@login_required
def my_application(request):
    applications = (
        ApplyJob.objects.filter(user=request.user)
        .select_related("job")
        .prefetch_related("documents")
    )

    return render(
        request,
        "accounts/my_applications.html",
        {"applications": applications},
    )


# --------------------------------------------------
# APPLICATIONS FOR AN EMPLOYER'S JOB
# --------------------------------------------------

@login_required
def job_applications(request, id):
    job = get_object_or_404(Job, id=id)

    if job.posted_by_id != request.user.id:
        return redirect("all-jobs")

    applications = (
        ApplyJob.objects.filter(job=job)
        .select_related("user", "job")
        .prefetch_related("documents")
    )

    return render(
        request,
        "accounts/job_applications.html",
        {
            "job": job,
            "applications": applications,
        },
    )


# --------------------------------------------------
# UPDATE APPLICATION STATUS
# --------------------------------------------------

@login_required
def update_application_status(request, id):
    application = get_object_or_404(ApplyJob, id=id)

    if (
        not hasattr(request.user, "profile")
        or request.user.profile.role != "employer"
    ):
        return redirect("all-jobs")

    if application.job.posted_by_id != request.user.id:
        return redirect("all-jobs")

    if request.method != "POST":
        return redirect(
            "job-applications",
            id=application.job.id,
        )

    status = request.POST.get("status")

    valid_statuses = {
        choice[0]
        for choice in ApplyJob.STATUS_CHOICES
    }

    if status in valid_statuses:
        application.status = status

        if status == "reviewed" and not application.reviewed_at:
            application.reviewed_at = timezone.now()

        application.save(
            update_fields=["status", "reviewed_at", "updated_at"]
        )

    return redirect(
        "job-applications",
        id=application.job.id,
    )


# --------------------------------------------------
# DOWNLOAD APPLICATION DOCUMENTS
# --------------------------------------------------

@login_required
def download_application_document(request, id, document_type):
    application = get_object_or_404(ApplyJob, id=id)

    # Only the applicant or the employer who posted the job
    # may access application documents.
    is_applicant = application.user_id == request.user.id
    is_job_owner = application.job.posted_by_id == request.user.id

    if not (is_applicant or is_job_owner):
        raise Http404("Document not found.")

    if document_type == "cv":
        document = application.cv

    elif document_type == "cover_letter":
        document = application.cover_letter_file

    elif document_type == "supporting":
        document_id = request.GET.get("document_id")

        if not document_id or not document_id.isdigit():
            raise Http404("Document not found.")

        supporting_document = get_object_or_404(
            ApplicationDocument,
            id=int(document_id),
            application=application,
        )

        document = supporting_document.file

    else:
        raise Http404("Document not found.")

    if not document:
        raise Http404("Document not found.")

    try:
        document.open("rb")
    except (FileNotFoundError, OSError, ValueError):
        raise Http404("Document not found.")

    return FileResponse(
        document,
        as_attachment=True,
        filename=os.path.basename(document.name),
        content_type="application/octet-stream",
    )


# --------------------------------------------------
# DOWNLOAD THE CURRENT USER'S PROFILE CV
# --------------------------------------------------

@login_required
def download_profile_cv(request):
    profile = get_object_or_404(Profile, user=request.user)

    if not profile.cv:
        raise Http404("CV not found.")

    try:
        profile.cv.open("rb")
    except (FileNotFoundError, OSError, ValueError):
        raise Http404("CV not found.")

    return FileResponse(
        profile.cv,
        as_attachment=True,
        filename=os.path.basename(profile.cv.name),
        content_type="application/octet-stream",
    )


# --------------------------------------------------
# CUSTOM 404 ERROR PAGE
# --------------------------------------------------

def custom_404(request, exception):
    return render(
        request,
        "accounts/404.html",
        status=404,
    )




# --------------------------------------------------
# CAREER DEVELOPMENT HUB
# --------------------------------------------------

@login_required
def career_hub(request):
    resources = CareerResource.objects.filter(
        is_approved=True
    ).select_related("submitted_by")

    search = (request.GET.get("search") or "").strip()
    category = (request.GET.get("category") or "").strip()
    resource_type = (request.GET.get("type") or "").strip()

    valid_categories = {
        value for value, label in CareerResource.CATEGORIES
    }
    valid_types = {
        value for value, label in CareerResource.RESOURCE_TYPES
    }

    if category not in valid_categories:
        category = ""

    if resource_type not in valid_types:
        resource_type = ""

    if search:
        resources = resources.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(content__icontains=search)
        )

    if category:
        resources = resources.filter(category=category)

    if resource_type:
        resources = resources.filter(resource_type=resource_type)

    paginator = Paginator(resources, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    learning_paths = (
        LearningPath.objects.filter(is_published=True)
        .prefetch_related("items")
    )

    return render(
        request,
        "accounts/career_hub.html",
        {
            "page_obj": page_obj,
            "resources": page_obj.object_list,
            "learning_paths": learning_paths,
            "search": search,
            "selected_category": category,
            "selected_type": resource_type,
            "categories": CareerResource.CATEGORIES,
            "resource_types": CareerResource.RESOURCE_TYPES,
            "resource_count": CareerResource.objects.filter(
                is_approved=True
            ).count(),
            "path_count": learning_paths.count(),
        },
    )


@login_required
def career_resource_detail(request, pk):
    resource = get_object_or_404(
        CareerResource,
        pk=pk,
        is_approved=True,
    )

    return render(
        request,
        "accounts/career_resource_detail.html",
        {"resource": resource},
    )


@login_required
def submit_career_resource(request):
    form_data = {
        "title": "",
        "description": "",
        "category": "",
        "resource_type": "article",
        "content": "",
        "resource_url": "",
    }

    if request.method == "POST":
        form_data = {
            "title": (request.POST.get("title") or "").strip(),
            "description": (
                request.POST.get("description") or ""
            ).strip(),
            "category": (request.POST.get("category") or "").strip(),
            "resource_type": (
                request.POST.get("resource_type") or ""
            ).strip(),
            "content": (request.POST.get("content") or "").strip(),
            "resource_url": (
                request.POST.get("resource_url") or ""
            ).strip(),
        }

        errors = []

        valid_categories = {
            value for value, label in CareerResource.CATEGORIES
        }
        valid_types = {
            value for value, label in CareerResource.RESOURCE_TYPES
        }

        if not form_data["title"]:
            errors.append("Please enter a title.")

        if len(form_data["title"]) > 200:
            errors.append("The title cannot exceed 200 characters.")

        if not form_data["description"]:
            errors.append("Please enter a short description.")

        if len(form_data["description"]) > 350:
            errors.append("The description cannot exceed 350 characters.")

        if form_data["category"] not in valid_categories:
            errors.append("Please select a valid category.")

        if form_data["resource_type"] not in valid_types:
            errors.append("Please select a valid resource type.")

        if (
            form_data["resource_type"] == "article"
            and not form_data["content"]
        ):
            errors.append("Please provide the article content.")

        if (
            form_data["resource_type"] == "external"
            and not form_data["resource_url"]
        ):
            errors.append("Please provide the external resource URL.")

        if form_data["resource_type"] == "external" and form_data["resource_url"]:
            try:
                URLValidator(schemes=["http", "https"])(
                    form_data["resource_url"]
                )
            except ValidationError:
                errors.append("Enter a valid HTTP or HTTPS URL.")

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            resource = CareerResource(
                title=form_data["title"],
                description=form_data["description"],
                category=form_data["category"],
                resource_type=form_data["resource_type"],
                content=form_data["content"],
                resource_url=form_data["resource_url"],
                submitted_by=request.user,
                is_approved=False,
            )

            try:
                resource.full_clean()
                resource.save()
            except ValidationError as error:
                for field_errors in error.message_dict.values():
                    for error_message in field_errors:
                        messages.error(request, error_message)
            else:
                messages.success(
                    request,
                    "Your resource has been submitted for admin review.",
                )
                return redirect("career-hub")

    return render(
        request,
        "accounts/career_resource_form.html",
        {
            "form_data": form_data,
            "categories": CareerResource.CATEGORIES,
            "resource_types": CareerResource.RESOURCE_TYPES,
        },
    )



@login_required
def career_learning_path_detail(request, slug):
    learning_path = get_object_or_404(
        LearningPath,
        slug=slug,
        is_published=True,
    )

    items = list(
        learning_path.items
        .filter(resource__is_approved=True)
        .select_related("resource")
        .order_by("order")
    )

    progress_records = {
        record.path_item_id: record
        for record in LearningProgress.objects.filter(
            user=request.user,
            path_item__learning_path=learning_path,
        )
    }

    completed_count = 0

    for item in items:
        record = progress_records.get(item.pk)
        item.is_completed = bool(record and record.is_completed)

        if item.is_completed:
            completed_count += 1

    total_count = len(items)

    progress_percentage = (
        round(completed_count / total_count * 100)
        if total_count else 0
    )

    return render(
        request,
        "accounts/career_learning_path_detail.html",
        {
            "learning_path": learning_path,
            "items": items,
            "completed_count": completed_count,
            "total_count": total_count,
            "progress_percentage": progress_percentage,
        },
    )




@login_required
@require_POST
def toggle_learning_progress(request, slug, item_id):
    learning_path = get_object_or_404(
        LearningPath,
        slug=slug,
        is_published=True,
    )

    path_item = get_object_or_404(
        LearningPathItem,
        pk=item_id,
        learning_path=learning_path,
        resource__is_approved=True,
    )

    completed = request.POST.get("completed") == "true"

    LearningProgress.objects.update_or_create(
        user=request.user,
        path_item=path_item,
        defaults={
            "is_completed": completed,
            "completed_at": timezone.now() if completed else None,
        },
    )

    return redirect(
        "career-learning-path-detail",
        slug=learning_path.slug,
    )
