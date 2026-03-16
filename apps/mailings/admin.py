from django.contrib import admin

from .models import Mailing


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = [
        "external_id",
        "user_id",
        "email",
        "subject",
        "is_sent",
    ]
    search_fields = ["external_id", "user_id", "email", "subject"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "external_id",
                    "user_id",
                ),
            },
        ),
        (
            "Content",
            {
                "fields": ("email", "subject", "message"),
            },
        ),
    )
