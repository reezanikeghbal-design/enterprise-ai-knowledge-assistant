class AppError(Exception):
    """Base application exception."""


class InvalidDocumentError(AppError):
    pass


class DuplicateDocumentError(AppError):
    pass


class RetrievalError(AppError):
    pass


class LLMError(AppError):
    pass
