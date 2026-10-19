
from django.contrib import admin
from .models import Profile, Job, ApplyJob, IndustryUpdate, CareerResource,LearningPath,LearningPathItem



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



@admin.register(CareerResource)
class CareerResourceAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "resource_type",
        "category",
        "submitted_by",
        "is_approved",
        "created_at",
    )
    list_filter = ("resource_type", "category", "is_approved")
    search_fields = (
        "title",
        "description",
        "content",
        "submitted_by__username",
    )
    list_editable = ("is_approved",)
    readonly_fields = ("created_at", "updated_at")
    actions = ("approve_resources", "unapprove_resources")

    @admin.action(description="Approve selected resources")
    def approve_resources(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="Unapprove selected resources")
    def unapprove_resources(self, request, queryset):
        queryset.update(is_approved=False)


class LearningPathItemInline(admin.TabularInline):
    model = LearningPathItem
    extra = 1
    autocomplete_fields = ("resource",)


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "level",
        "estimated_duration",
        "is_published",
    )
    list_filter = ("category", "level", "is_published")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = (LearningPathItemInline,)
    readonly_fields = ("created_at", "updated_at")


@admin.register(LearningPathItem)
class LearningPathItemAdmin(admin.ModelAdmin):
    list_display = ("learning_path", "order", "resource")
    list_filter = ("learning_path",)
    autocomplete_fields = ("learning_path", "resource")
