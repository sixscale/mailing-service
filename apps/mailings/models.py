from django.core.validators import EmailValidator
from django.db import models


class Mailing(models.Model):

    external_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Уникальный идентификатор записи во внешней системе",
        verbose_name="External ID",
    )
    user_id = models.CharField(
        max_length=255,
        help_text="Идентификатор пользователя",
        verbose_name="User ID",
    )
    email = models.EmailField(
        validators=[EmailValidator()],
        verbose_name="Email",
    )
    subject = models.CharField(
        max_length=500,
        verbose_name="Subject",
    )
    message = models.TextField(
        verbose_name="Message",
    )
    is_sent = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        indexes = [
            models.Index(
                fields=[
                    "external_id",
                ]
            ),
        ]

    def __str__(self) -> str:
        return f"Запись {self.external_id} для {self.email}"
