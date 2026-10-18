
from django.contrib import admin
from .models import Profile, Job, ApplyJob, IndustryUpdate


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "industry", "location")
    list_filter = ("role", "industry")
    search_fields = ("user__username", "user__first_name", "location")


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "job_type", "deadline")
    list_filter = ("job_type", "location")
    search_fields = ("title", "company", "description")


@admin.register(ApplyJob)
class ApplyJobAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "status", "applied_at")
    list_filter = ("status", "applied_at")
    search_fields = ("user__username", "job__title")
    readonly_fields = ("applied_at", "updated_at")


@admin.register(IndustryUpdate)
class IndustryUpdateAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "update_type",
        "industry",
        "published",
        "featured",
        "published_at",
    )
    list_filter = (
        "update_type",
        "industry",
        "published",
        "featured",
    )
    search_fields = ("title", "description", "source_name")
    list_editable = ("published", "featured")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        ("Update Information", {
            "fields": (
                "title",
                "description",
                "update_type",
                "industry",
                "image",
            )
        }),
        ("Source", {
            "fields": ("source_name", "source_url")
        }),
        ("Publishing", {
            "fields": (
                "published",
                "featured",
                "published_at",
            )
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
