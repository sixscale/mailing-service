import logging
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.mailings.exceptions import MailingImportError
from apps.mailings.services import ImportResult, MailingImporter
from apps.mailings.utils import read_xlsx_file

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Импорт записей из XLSX файла"

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path",
            type=str,
            help="Путь к XLSX файлу с данными рассылок",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Проверить файл без импорта",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file_path"])
        dry_run = options["dry_run"]

        self.stdout.write(f"Обработка файла: {file_path}")

        if dry_run:
            self.stdout.write(
                self.style.WARNING("РЕЖИМ ПРОВЕРКИ - Изменения не будут сохранены")
            )

        try:
            rows = read_xlsx_file(
                file_path=file_path,
                required_columns=MailingImporter.REQUIRED_COLUMNS,
            )

            if dry_run:
                row_count = sum(1 for _ in rows)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Файл валиден. Найдено {row_count} строк данных."
                    )
                )
                return
            importer = MailingImporter()

            result = importer.import_from_rows(rows)

            self._print_result(result)

        except MailingImportError as e:
            logger.error("Импорт не удался", extra={"error": str(e)})
            raise CommandError(str(e))
        except Exception as e:
            logger.exception("Неожиданная ошибка при импорте")
            raise CommandError(f"Неожиданная ошибка: {e}")

    def _print_result(self, result: ImportResult) -> None:
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("РЕЗУЛЬТАТЫ ИМПОРТА"))
        self.stdout.write("=" * 50)

        self.stdout.write(f"Всего обработано строк: {result.total_rows}")
        self.stdout.write(self.style.SUCCESS(f"Создано: {result.created}"))

        if result.skipped > 0:
            self.stdout.write(self.style.WARNING(f"Пропущено: {result.skipped}"))
        else:
            self.stdout.write(f"Пропущено: {result.skipped}")

        if result.errors > 0:
            self.stdout.write(self.style.ERROR(f"Ошибок: {result.errors}"))
        else:
            self.stdout.write(f"Ошибок: {result.errors}")

        self.stdout.write("=" * 50)

        if result.errors > 0:
            self.stdout.write(
                self.style.WARNING(
                    "Завершено с ошибками. Проверьте логи для подробностей."
                )
            )
