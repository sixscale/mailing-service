import logging
import random
import time

from celery import shared_task

from .models import Mailing

logger = logging.getLogger(__name__)


@shared_task
def send_email_task(mailing_id: int):
    time.sleep(random.randint(5, 20))

    mailing = Mailing.objects.get(id=mailing_id)

    logger.info(
        "Send EMAIL...",
        extra={
            "external_id": mailing.external_id,
            "user_id": mailing.user_id,
            "email": mailing.email,
            "subject": mailing.subject,
        },
    )

    mailing.is_sent = True
    mailing.save(update_fields=["is_sent"])
