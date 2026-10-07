
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Profile, Job, ApplyJob
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
#from django.core.exceptions import PermissionDenied


@login_required
def profile_list(request):
    profiles = Profile.objects.all()

    return render(
        request,
        'accounts/profile_list.html',
        {'profiles': profiles}
    )


def profile_detail(request, id):
    profile = get_object_or_404(Profile, id=id)

    return render(
        request,
        'accounts/profile_detail.html',
        {'profile': profile}
    )


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html' , {
                'errors':['User Already Exist.'],
                'username':username,
                'first_name':first_name,
                'last_name':last_name,
                'email':email,
            })
        if password != confirm_password:
            return render(request, 'accounts/register.html', {
                'errors': ['Password Did Not Match'],
                'username':username,
                'first_name':first_name,
                'last_name':last_name,
                'email':email,
                
                
                
                })
        
        try:
            validate_password(password)
        except ValidationError as error:
            return render(request, 'accounts/register.html' ,{
                'errors' : error.messages,
                'username':username,
                'first_name':first_name,
                'last_name':last_name,
                'email':email,


                
                
                })
       
            


        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            
        )

        Profile.objects.create(user=user)

        return redirect("login")

    return render(request, "accounts/register.html")


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            auth_login(request, user)
            return redirect("profile-list")

        return render(
            request,
            "accounts/login.html",
            {"error": "Invalid Username or Password"}
        )

    return render(request, "accounts/login.html")


def logout(request):
    if request.method == "POST":
        auth_logout(request)

    return redirect("login")


@login_required
def my_profile(request):
    profile = request.user.profile

    return render(
        request,
        "accounts/my_profile.html",
        {"profile": profile}
    )


@login_required
def profile_edit(request):
    profile = request.user.profile
    user = request.user
    if request.method == "POST":
        
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        profile.bio = request.POST.get("bio")
        profile.location = request.POST.get("location")
        profile.skills = request.POST.get("skills")
        profile.phone_number = request.POST.get("phone_number")
        profile.linkedin = request.POST.get("linkedin")
        profile.github = request.POST.get("github")
        
        profile.profile_image = request.FILES.get("profile_image")
        profile.save()
        return redirect("my-profile")
    return render(request, 'accounts/profile_edit.html' , {'profile':profile})



# Jobs Class
# All Jobs
def all_jobs(request):
    jobs = Job.objects.all()
    # search
    search = request.GET.get("search", "")
    job_type = request.GET.get("job_type", "")
    location = request.GET.get("location", "")

    #dyanamic Location
    locations = Job.objects.values_list('location', flat=True).distinct()
    if search:
        jobs = jobs.filter(
            Q(title__icontains=search)|
            Q(company__icontains=search)|
            Q(skills__icontains=search)
        )
    if job_type:
        jobs = jobs.filter(
            job_type__icontains=job_type
        )
    
    if location:
        jobs = jobs.filter(
            location__icontains=location
        )
    
    pagenator = Paginator(jobs, 6)
    page_number = request.GET.get("page")
    jobs = pagenator.get_page(page_number)

    


    return render(request, 'accounts/all_jobs.html', {
        'jobs':jobs,
        'search':search,
        'job_type': job_type,
        'location': location,
        'locations':locations
    })


# Job Detail
# def job_detail(request , id):
#     job = get_object_or_404(Job, id = id)
#     return render(request, 'accounts/job_detail.html', {'job': job})
def job_detail(request, id):
    job = get_object_or_404(Job, id=id)

    return render(
        request,
        'accounts/job_detail.html',
        {
            'job': job,
            'today': timezone.now()
        }
    )
        
 
    
# create Job
# Create Job
@login_required
def create_job(request):

    if request.method == "POST":
        title = request.POST.get("title")
        company = request.POST.get("company")
        description = request.POST.get("description")
        location = request.POST.get("location")
        job_type = request.POST.get("job_type")
        skills = request.POST.get("skills")
        salary = request.POST.get("salary")
        application_deadline = request.POST.get("application_deadline")
        posted_by = request.user

        if not title or not company or not description or not location or not job_type or not skills:
            return render(
            request,
            'accounts/create_job.html',
            {
            'error': 'Please fill in all required fields.'
            }
        )

        job = Job.objects.create(
            title=title,
            company=company,
            description=description,
            location=location,
            job_type=job_type,
            skills=skills,
            salary=salary,
            deadline=application_deadline,
            posted_by=posted_by
        )

        return redirect("all-jobs")

    return render(request, "accounts/create_job.html")


# edit Job
@login_required
def edit_job(request, id):
    job = get_object_or_404(Job, id=id)

    if job.posted_by != request.user:
        return redirect('all-jobs')

    if request.method == "POST":
        job.title = request.POST.get("title")
        job.company = request.POST.get("company")
        job.description = request.POST.get("description")
        job.location = request.POST.get("location")
        job.job_type = request.POST.get("job_type")
        job.skills = request.POST.get("skills")
        job.salary = request.POST.get("salary")
        job.deadline = request.POST.get("application_deadline")

        if not job.title or not job.company or not job.description  or not job.location or not job.job_type or not job.skills:
            return render(request, 'accounts/edit_job.html', {'error':'please fill all required fields.'})

        job.save()

        return redirect('job-detail', id=job.id)

    return render(request, 'accounts/edit_job.html', {'job': job})




# deleate job
def delete_job(request , id):
    job = get_object_or_404(Job, id=id)
    if job.posted_by != request.user:
        return redirect('all-jobs')
    if request.method == "POST":
        job.delete()
       
        return redirect('all-jobs')
    return render(request, 'accounts/delete_job.html', {'job':job})


# def apply_job(request , id):
#     job = get_object_or_404(Job, id=id)
    
#     if request.method == "POST":
#         cover_letter = request.POST.get("cover_letter")
       
#         existed_user = ApplyJob.objects.filter(user=request.user , job=job).exists()
#         if existed_user:
#             return redirect('job-detail' , id=job.id)
#         ApplyJob.objects.create(
#             cover_letter=cover_letter,
#             user = request.user,
#             job=job
#         )
        
#         return redirect('all-jobs')
#     return render(request, 'accounts/apply_job.html', {'job': job})
# @login_required
# def apply_job(request, id):
#     job = get_object_or_404(Job, id=id)

#     # Prevent users from applying for their own job
#     if job.posted_by == request.user:
#         return redirect('job-detail', id=job.id)

#     # Prevent applications after the deadline
#     if job.deadline and timezone.now().date() > job.deadline:
#         return redirect('job-detail', id=job.id)

#     if request.method == "POST":

#         cover_letter = request.POST.get("cover_letter")

#         existed_user = ApplyJob.objects.filter(
#             user=request.user,
#             job=job
#         ).exists()

#         if existed_user:
#             return redirect('job-detail', id=job.id)

#         ApplyJob.objects.create(
#             cover_letter=cover_letter,
#             user=request.user,
#             job=job
#         )

#         return redirect('all-jobs')

#     return render(
#         request,
#         'accounts/apply_job.html',
#         {'job': job}
#     )
@login_required
def apply_job(request, id):
    job = get_object_or_404(Job, id=id)

    # Prevent users from applying for their own job
    if job.posted_by == request.user:
        return redirect('job-detail', id=job.id)

    # Prevent applications after the deadline
    if job.deadline and timezone.now() > job.deadline:
        return redirect('job-detail', id=job.id)

    if request.method == "POST":

        cover_letter = request.POST.get("cover_letter")

        existed_user = ApplyJob.objects.filter(
            user=request.user,
            job=job
        ).exists()

        if existed_user:
            return render(
                request,
                'accounts/apply_job.html',
                {
                    'job': job,
                    'error': 'You have already applied for this job.'
                }
            )

        ApplyJob.objects.create(
            cover_letter=cover_letter,
            user=request.user,
            job=job
        )

        return redirect('all-jobs')

    return render(
        request,
        'accounts/apply_job.html',
        {'job': job}
    )


# USER APPLICATION
@login_required
def my_application(request):
    applications = ApplyJob.objects.filter(user=request.user)
    return  render(request, 'accounts/my_applications.html', {'applications':applications})


#EMPLOYER ACTION ON APPLICANT JOB
@login_required
def job_applications(request, id):
    job = get_object_or_404(Job, id=id)

    if job.posted_by != request.user:
        return redirect('all-jobs')

    applications = ApplyJob.objects.filter(job=job)

    return render(
        request,
        'accounts/job_applications.html',
        {
            'job': job,
            'applications': applications
        }
    )


    #UPDATE STATUS
@login_required
def update_application_status(request, id):

    application = get_object_or_404(ApplyJob, id=id)

    if application.job.posted_by != request.user:
        return redirect('all-jobs')

    if request.method == "POST":
        status = request.POST.get("status")

        if status in ["pending", "reviewed", "accepted", "rejected"]:
            application.status = status
            application.save()

        return redirect(
            'job-applications',
            id=application.job.id
        )

    return redirect(
        'job-applications',
        id=application.job.id
    )


# Eroro Handling

def custom_404(request, exception):
    return render(request, 'accounts/404.html', status=404)



# def test_403(request):
#     raise PermissionDenied


# Test 500
# def test_500(request):
#     raise Exception("test 500 error")