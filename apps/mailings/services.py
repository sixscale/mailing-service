import logging
import random
import time
from dataclasses import dataclass
from typing import Generator, Optional

from django.db import transaction

from apps.mailings.tasks import send_email_task

from .exceptions import ValidationError
from .models import Mailing

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ImportResult:
    total_rows: int
    created: int
    skipped: int
    errors: int

    def __str__(self) -> str:
        return (
            f"Import completed:\n"
            f"  Total rows processed: {self.total_rows}\n"
            f"  Created: {self.created}\n"
            f"  Skipped: {self.skipped}\n"
            f"  Errors: {self.errors}"
        )


class MailingImporter:

    REQUIRED_COLUMNS = {"external_id", "user_id", "email", "subject", "message"}

    def __init__(
        self,
        batch_size: int = 100,
    ):
        self.batch_size = batch_size
        self._existing_external_ids: set[str] = set()

    def import_from_rows(
        self,
        rows: Generator[dict[str, str], None, None],
    ) -> ImportResult:
        total_rows = 0
        created = 0
        skipped = 0
        errors = 0

        self._existing_external_ids = set(
            Mailing.objects.values_list("external_id", flat=True)
        )

        batch: list[Mailing] = []

        for row in rows:
            total_rows += 1

            try:
                mailing = self._process_row(row)

                if mailing is None:
                    skipped += 1
                    continue

                batch.append(mailing)
                created += 1

                if len(batch) >= self.batch_size:
                    self._process_batch(batch)
                    batch = []

            except ValidationError as e:
                logger.warning(
                    "Row validation failed",
                    extra={
                        "row_number": total_rows,
                        "error": str(e),
                        "external_id": row.get("external_id"),
                    },
                )
                errors += 1
            except Exception as e:
                logger.error(
                    "Unexpected error processing row",
                    extra={
                        "row_number": total_rows,
                        "error": str(e),
                        "external_id": row.get("external_id"),
                    },
                )
                errors += 1

        if batch:
            self._process_batch(batch)

        return ImportResult(
            total_rows=total_rows,
            created=created,
            skipped=skipped,
            errors=errors,
        )

    def _process_row(self, row: dict[str, str]) -> Optional[Mailing]:
        external_id = row.get("external_id", "").strip()
        if not external_id:
            raise ValidationError("external_id is required")

        if external_id in self._existing_external_ids:
            logger.info(
                "Skipping duplicate external_id", extra={"external_id": external_id}
            )
            return None

        user_id = row.get("user_id", "").strip()
        if not user_id:
            raise ValidationError("user_id is required")

        email = row.get("email", "").strip()
        if not email:
            raise ValidationError("email is required")

        subject = row.get("subject", "").strip()
        if not subject:
            raise ValidationError("subject is required")

        message = row.get("message", "").strip()
        if not message:
            raise ValidationError("message is required")

        mailing = Mailing(
            external_id=external_id,
            user_id=user_id,
            email=email,
            subject=subject,
            message=message,
        )

        self._existing_external_ids.add(external_id)

        return mailing

    @transaction.atomic
    def _process_batch(self, batch: list[Mailing]) -> None:
        created = Mailing.objects.bulk_create(batch)

        for mailing in created:
            send_email_task.delay(mailing.id)
