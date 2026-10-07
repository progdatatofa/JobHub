from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    
    bio = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=100)
    skills = models.TextField()

    updated_at = models.DateTimeField(auto_now=True)
    phone_number = models.CharField(max_length=15)
    linkedin = models.URLField()
    
    profile_image = models.ImageField(upload_to='profile/', blank=True, null=True)
    github = models.URLField()
    
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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
    status_choices =  [
        ("Pending", "pending"),
        ("Reviewed", "reviewed"),
        ("Accepted", "accepted"),
        ("Rejected", "rejected")
    ]
    cover_letter = models.TextField()
    status = models.CharField(max_length=20, choices=status_choices , default="pending")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["job" , "user"],
                name="unique_job_application"
            )
        ]

    def __str__(self):
        return self.user.username