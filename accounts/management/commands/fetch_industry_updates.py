
from django.core.management.base import BaseCommand

from accounts.industry_feed_service import fetch_industry_updates


class Command(BaseCommand):
    help = "Fetch live industry updates from configured RSS feeds"

    def handle(self, *args, **options):
        results = fetch_industry_updates()

        self.stdout.write(
            self.style.SUCCESS(
                f"New updates: {results['created']}"
            )
        )
        self.stdout.write(
            f"Skipped existing or unsuitable entries: "
            f"{results['skipped']}"
        )
        self.stdout.write(
            f"Feed errors: {results['errors']}"
        )
