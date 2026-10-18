from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Profile(models.Model):
    ROLE_CHOICES = [
        ("job_seeker", "Job Seeker"),
        ("employer", "Employer"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="job_seeker",
    )

    bio = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=100)
    skills = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    phone_number = models.CharField(max_length=15)
    linkedin = models.URLField()
    profile_image = models.ImageField(
        upload_to="profile/",
        blank=True,
        null=True,
    )
    github = models.URLField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    cv = models.FileField(
        upload_to="private/profile_cvs/",
        blank=True,
        null=True,
    )
    INDUSTRY_CHOICES = [
    ("technology", "Technology"),
    ("healthcare", "Healthcare"),
    ("agriculture", "Agriculture"),
    ("education", "Education"),
    ("engineering", "Engineering"),
    ("finance", "Finance and Banking"),
    ("business", "Business and Entrepreneurship"),
    ("media", "Media and Communications"),
    ("construction", "Construction and Real Estate"),
    ("transportation", "Transportation and Logistics"),
    ("energy", "Energy"),
    ("manufacturing", "Manufacturing"),
    ("hospitality", "Hospitality and Tourism"),
    ("other", "Other"),
    ]

    industry = models.CharField(
        max_length=50,
        choices=INDUSTRY_CHOICES,
        default="technology",
    )


    def __str__(self):
        return self.user.first_name





class Job(models.Model):
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)

    description = models.TextField()
    location = models.CharField(max_length=100)
    job_type = models.TextField()
    skills = models.TextField()
    salary = models.IntegerField()
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE , related_name='jobs')


    def __str__(self):
        return self.title



#apply job

class ApplyJob(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("reviewed", "Reviewed"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    # Keep this existing field so old cover letters are preserved.
    cover_letter = models.TextField(blank=True)

    # Optional uploaded cover letter for applicants who prefer a file.
    cover_letter_file = models.FileField(
        upload_to="private/applications/cover_letters/",
        blank=True,
        null=True,
    )

    # Snapshot of the CV submitted with this particular application.
    cv = models.FileField(
        upload_to="private/applications/cvs/",
        blank=True,
        null=True,
    )

    # Optional link to a portfolio, GitHub profile, or personal website.
    portfolio_url = models.URLField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    # Private notes for the employer reviewing this application.
    employer_notes = models.TextField(blank=True)

    # Set by the view when the employer first reviews the application.
    reviewed_at = models.DateTimeField(blank=True, null=True)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="job_applications",
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications",
    )

    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["job", "user"],
                name="unique_job_application",
            )
        ]
        ordering = ["-applied_at"]

    def __str__(self):
        return f"{self.user.username} - {self.job.title}"


class ApplicationDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ("professional_certificate", "Professional Certificate"),
        ("academic_certificate", "Academic Certificate"),
        ("training_certificate", "Training Certificate"),
        ("supporting_document", "Other Supporting Document"),
    ]

    application = models.ForeignKey(
        ApplyJob,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    document_type = models.CharField(
        max_length=40,
        choices=DOCUMENT_TYPE_CHOICES,
    )

    title = models.CharField(max_length=150)

    file = models.FileField(
        upload_to="private/applications/documents/",
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["uploaded_at"]

    def __str__(self):
        return f"{self.title} - {self.application.user.username}"
    




class IndustryUpdate(models.Model):
    UPDATE_TYPE_CHOICES = [
        ("job", "Job Opportunity"),
        ("scholarship", "Scholarship"),
        ("training", "Training"),
        ("news", "Industry News"),
        ("event", "Event"),
        ("other", "Other Opportunity"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    update_type = models.CharField(
        max_length=20,
        choices=UPDATE_TYPE_CHOICES,
        default="news",
    )

    industry = models.CharField(
        max_length=50,
        choices=Profile.INDUSTRY_CHOICES,
        default="technology",
    )

    source_name = models.CharField(
        max_length=150,
        blank=True,
    )
    source_url = models.URLField(max_length=500)
    image = models.ImageField(
        upload_to="industry_updates/",
        blank=True,
        null=True,
    )

    published = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)

    published_at = models.DateTimeField(
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-featured", "-published_at", "-created_at"]

    def __str__(self):
        return self.title

