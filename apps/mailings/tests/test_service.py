from unittest.mock import MagicMock, patch

import pytest

from apps.mailings.exceptions import ValidationError
from apps.mailings.models import Mailing
from apps.mailings.services import (
    ImportResult,
    MailingImporter,
)
from apps.mailings.tests.factories import MailingFactory


@pytest.mark.django_db
class TestImportResult:
    def test_str_representation(self):
        result = ImportResult(total_rows=100, created=80, skipped=15, errors=5)
        result_str = str(result)

        assert "Total rows processed: 100" in result_str
        assert "Created: 80" in result_str
        assert "Skipped: 15" in result_str
        assert "Errors: 5" in result_str

    def test_import_skips_duplicates_in_database(self):
        MailingFactory(external_id="existing")

        rows = [
            {
                "external_id": "existing",
                "user_id": "user1",
                "email": "user1@example.com",
                "subject": "Subject",
                "message": "Message",
            },
            {
                "external_id": "new",
                "user_id": "user2",
                "email": "user2@example.com",
                "subject": "Subject 2",
                "message": "Message 2",
            },
        ]

        mock_sender = MagicMock()
        importer = MailingImporter()

        result = importer.import_from_rows(iter(rows))

        assert result.total_rows == 2
        assert result.created == 1
        assert result.skipped == 1
        assert result.errors == 0

    def test_import_skips_duplicates_in_same_file(self):
        rows = [
            {
                "external_id": "dup",
                "user_id": "user1",
                "email": "user1@example.com",
                "subject": "Subject 1",
                "message": "Message 1",
            },
            {
                "external_id": "dup",
                "user_id": "user2",
                "email": "user2@example.com",
                "subject": "Subject 2",
                "message": "Message 2",
            },
        ]

        mock_sender = MagicMock()
        importer = MailingImporter()

        result = importer.import_from_rows(iter(rows))

        assert result.total_rows == 2
        assert result.created == 1
        assert result.skipped == 1
        assert result.errors == 0

    def test_import_handles_validation_errors(self):
        rows = [
            {
                "external_id": "",
                "user_id": "user1",
                "email": "user1@example.com",
                "subject": "Subject",
                "message": "Message",
            },
            {
                "external_id": "valid",
                "user_id": "user2",
                "email": "",
                "subject": "Subject",
                "message": "Message",
            },
            {
                "external_id": "good",
                "user_id": "user3",
                "email": "user3@example.com",
                "subject": "Subject",
                "message": "Message",
            },
        ]

        mock_sender = MagicMock()
        importer = MailingImporter()

        result = importer.import_from_rows(iter(rows))

        assert result.total_rows == 3
        assert result.created == 1
        assert result.skipped == 0
        assert result.errors == 2

    def test_import_from_rows_creates_mailings(self):
        rows = [
            {
                "external_id": "ext1",
                "user_id": "user1",
                "email": "a@b.com",
                "subject": "S1",
                "message": "M1",
            },
            {
                "external_id": "ext2",
                "user_id": "user2",
                "email": "b@c.com",
                "subject": "S2",
                "message": "M2",
            },
        ]

        with patch("apps.mailings.services.send_email_task") as mock_task:
            importer = MailingImporter(batch_size=10)
            result = importer.import_from_rows(iter(rows))

            assert result.total_rows == 2
            assert result.created == 2
            assert Mailing.objects.count() == 2
            mock_task.delay.assert_called()

    def test_process_row_validates_required_fields(self):
        importer = MailingImporter()

        with pytest.raises(ValidationError, match="external_id is required"):
            importer._process_row(
                {"user_id": "1", "email": "a@b.com", "subject": "S", "message": "M"}
            )

        with pytest.raises(ValidationError, match="user_id is required"):
            importer._process_row(
                {"external_id": "1", "email": "a@b.com", "subject": "S", "message": "M"}
            )

        with pytest.raises(ValidationError, match="email is required"):
            importer._process_row(
                {"external_id": "1", "user_id": "1", "subject": "S", "message": "M"}
            )

        with pytest.raises(ValidationError, match="subject is required"):
            importer._process_row(
                {"external_id": "1", "user_id": "1", "email": "a@b.com", "message": "M"}
            )

        with pytest.raises(ValidationError, match="message is required"):
            importer._process_row(
                {"external_id": "1", "user_id": "1", "email": "a@b.com", "subject": "S"}
            )
