
from django.urls import path
from . import views
from .views import recruiter_dashboard


urlpatterns = [
    path('', views.home, name='home'),
    path('professionals/', views.profile_list, name='profile-list'),
    path('profile/<int:id>/', views.profile_detail, name='profile-detail'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('myprofile/', views.my_profile, name='my-profile'),
    path('profile/edit/', views.profile_edit, name='profile-edit'),

    # Jobs
    path('jobs/', views.all_jobs, name='all-jobs'),
    path('jobs/<int:id>/', views.job_detail, name='job-detail'),
    path('create/', views.create_job, name='create-job'),
    path('jobs/<int:id>/edit/', views.edit_job, name='edit-job'),
    path('jobs/<int:id>/delete', views.delete_job, name='delete-job'),
    path('jobs/<int:id>/apply/', views.apply_job, name='apply-job'),

    # My Applications
    path('myapplications/', views.my_application, name='my-applications'),
    path(
        'myapplications/<int:id>/jobapplications/',
        views.job_applications,
        name='job-applications',
    ),
    path(
        'myapplications/<int:id>/statusupdate/',
        views.update_application_status,
        name='update-status',
    ),

    # Career Hub
    path('career-hub/', views.career_hub, name='career-hub'),
    path(
        'career-hub/submit/',
        views.submit_career_resource,
        name='career-resource-submit',
    ),
    path(
        'career-hub/resource/<int:pk>/',
        views.career_resource_detail,
        name='career-resource-detail',
    ),
    path(
        'career-hub/learning-path/<slug:slug>/',
        views.career_learning_path_detail,
        name='career-learning-path-detail',
    ),
    path(
        'career-hub/learning-path/<slug:slug>/item/<int:item_id>/progress/',
        views.toggle_learning_progress,
        name='toggle-learning-progress',
    ),

    # Saved Jobs
    path('jobs/<int:id>/save/', views.save_job, name='save-job'),
    path(
        'jobs/<int:id>/remove-saved/',
        views.remove_saved_job,
        name='remove-saved-job',
    ),
    path('saved-jobs/', views.saved_jobs, name='saved-jobs'),

    # Job Alerts
    path('job-alerts/', views.job_alerts, name='job-alerts'),
    path('job-alerts/create/', views.create_job_alert, name='create-job-alert'),
    path(
        'job-alerts/<int:id>/toggle/',
        views.toggle_job_alert,
        name='toggle-job-alert',
    ),
    path(
        'job-alerts/<int:id>/delete/',
        views.delete_job_alert,
        name='delete-job-alert',
    ),

    # Job Notifications
    path(
        'notifications/',
        views.job_notifications,
        name='job-notifications',
    ),
    path(
        'notifications/<int:id>/read/',
        views.mark_job_notification_read,
        name='mark-job-notification-read',
    ),

    # Secure application document downloads
    path(
        'myapplications/<int:id>/download/<str:document_type>/',
        views.download_application_document,
        name='download-application-document',
    ),

    # Download the logged-in user's profile CV
    path(
        'profile/download-cv/',
        views.download_profile_cv,
        name='download-profile-cv',
    ),

    # Recruiter Dashboard
    path(
        'recruiter-dashboard/',
        recruiter_dashboard,
        name='recruiter-dashboard',
    ),
]
