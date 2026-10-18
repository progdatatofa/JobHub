
from django.db import migrations, models


def assign_existing_employers(apps, schema_editor):
    Profile = apps.get_model("accounts", "Profile")
    Job = apps.get_model("accounts", "Job")

    employer_user_ids = (
        Job.objects
        .values_list("posted_by_id", flat=True)
        .distinct()
    )

    Profile.objects.filter(
        user_id__in=employer_user_ids
    ).update(role="employer")


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0010_applyjob"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="role",
            field=models.CharField(
                choices=[
                    ("job_seeker", "Job Seeker"),
                    ("employer", "Employer"),
                ],
                default="job_seeker",
                max_length=20,
            ),
        ),
        migrations.RunPython(
            assign_existing_employers,
            migrations.RunPython.noop,
        ),
    ]
