
from django.urls import path
from . import views


urlpatterns = [
    path('', views.profile_list, name='profile-list'),
    path('profile/<int:id>/', views.profile_detail, name='profile-detail'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('myprofile/', views.my_profile, name='my-profile'),
    path('profile/edit/' , views.profile_edit, name='profile-edit'),


    #Jobs Class
    path('jobs/', views.all_jobs , name='all-jobs'),
    path('jobs/<int:id>/', views.job_detail , name='job-detail'),
    path('create/' , views.create_job, name='create-job'),
    path('jobs/<int:id>/edit/', views.edit_job, name='edit-job'),
    path('jobs/<int:id>/delete', views.delete_job , name="delete-job"),
    path('jobs/<int:id>/apply/', views.apply_job, name='apply-job'),

    #My Applications
    path('myapplications/', views.my_application, name='my-applications'),
    path('myapplications/<int:id>/jobapplications/', views.job_applications, name='job-applications'),
    path('myapplications/<int:id>/statusupdate/', views.update_application_status, name='update-status')
]
