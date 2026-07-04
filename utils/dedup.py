"""
utils/dedup.py
==============

Remove duplicate jobs from the scraped results.
"""

from typing import Any


class JobDeduplicator:
    """
    Removes duplicate jobs from a list.
    """

    @classmethod
    def remove_duplicates(
        cls,
        jobs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Remove duplicate jobs using jobId.

        Fallback:
            jobUrl

        Returns:
            List of unique jobs.
        """

        unique_jobs: list[dict[str, Any]] = []
        seen: set[str] = set()

        for job in jobs:

            unique_key = (
                job.get("jobId")
                or job.get("jobUrl")
            )

            if not unique_key:
                continue

            if unique_key in seen:
                continue

            seen.add(unique_key)
            unique_jobs.append(job)

        return unique_jobs