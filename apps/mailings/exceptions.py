class MailingImportError(Exception):
    pass


class FileFormatError(MailingImportError):
    pass


class RequiredColumnError(MailingImportError):
    pass


class DuplicateExternalIdError(MailingImportError):
    pass


class ValidationError(MailingImportError):
    pass
