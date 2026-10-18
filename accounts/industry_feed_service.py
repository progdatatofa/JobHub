
import logging
import re
from datetime import datetime, timezone as datetime_timezone
from html import unescape
from urllib.parse import urlparse

import feedparser
from django.utils import timezone
from django.utils.html import strip_tags
from langdetect import detect, LangDetectException

from .models import IndustryUpdate


logger = logging.getLogger(__name__)


# Official RSS sources.
# Add more verified feeds here as the project grows.
FEEDS = [
    {
        "name": "WHO Africa",
        "url": "https://www.afro.who.int/rss/featured-news.xml",
        "industry": "healthcare",
        "type": "news",
        "keywords": [],
    },
]


def clean_text(value):
    """Convert HTML descriptions into readable plain text."""
    if not value:
        return ""

    return re.sub(
        r"\s+",
        " ",
        unescape(strip_tags(value)),
    ).strip()


def is_english(title, description):
    """Reject content that language detection identifies as non-English."""
    sample = f"{title} {description}".strip()

    if len(sample) < 30:
        return False

    try:
        return detect(sample) == "en"
    except LangDetectException:
        return False


def classify_afdb_entry(title, description):
    """Keep only entries relevant to technology and digital careers."""
    text = f"{title} {description}".lower()

    return any(
        keyword in text
        for keyword in FEEDS[0]["keywords"]
    )


def parse_publication_date(entry):
    """Convert an RSS publication date into a timezone-aware datetime."""
    parsed = entry.get("published_parsed") or entry.get(
        "updated_parsed"
    )

    if not parsed:
        return None

    try:
        published = datetime(
            *parsed[:6],
            tzinfo=datetime_timezone.utc,
        )
        return published
    except (TypeError, ValueError, OverflowError):
        return None


def fetch_industry_updates():
    """
    Fetch live RSS entries and save new articles.

    Returns counts for reporting in the management command.
    """
    created_count = 0
    skipped_count = 0
    error_count = 0

    for feed in FEEDS:
        try:
            response = feedparser.parse(
                feed["url"],
                request_headers={
                    "User-Agent": "JobHub Industry Updates/1.0"
                },
            )

            if response.bozo and not response.entries:
                logger.warning(
                    "Could not read feed: %s. Error: %s",
                    feed["name"],
                    response.get("bozo_exception"),
                )
                error_count += 1
                continue
            for entry in response.entries:
                title = clean_text(entry.get("title", ""))
                description = clean_text(
                    entry.get("summary", "")
                    or entry.get("description", "")
                )
                link = (entry.get("link") or "").strip()

                parsed_url = urlparse(link)

                # Do not save entries with invalid or unsafe URLs.
                if (
                    not title
                    or not link
                    or parsed_url.scheme not in ("http", "https")
                    or not parsed_url.netloc
                ):
                    skipped_count += 1
                    continue

                if not is_english(title, description):
                    skipped_count += 1
                    continue

                # AFDB's vacancy feed contains several kinds of
                # vacancies. Keep only technology-related entries.
                if (
                    feed["name"] == "African Development Bank"
                    and not classify_afdb_entry(title, description)
                ):
                    skipped_count += 1
                    continue

                # Prevent the same source URL from being saved twice.
                if IndustryUpdate.objects.filter(
                    source_url=link
                ).exists():
                    skipped_count += 1
                    continue

                published_at = parse_publication_date(entry)

                # Keep unknown publication dates empty rather than
                # pretending that the article is new.
                IndustryUpdate.objects.create(
                    title=title[:200],
                    description=description or title,
                    update_type=feed["type"],
                    industry=feed["industry"],
                    source_name=feed["name"],
                    source_url=link,
                    published=True,
                    featured=False,
                    published_at=published_at,
                )

                created_count += 1

        except Exception:
            logger.exception(
                "Error fetching feed: %s",
                feed["name"],
            )
            error_count += 1

    return {
        "created": created_count,
        "skipped": skipped_count,
        "errors": error_count,
    }
