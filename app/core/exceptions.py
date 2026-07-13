"""Domain and application exceptions — mapped to HTTP responses via exception handlers."""


class ApplicationError(Exception):
    """Base application exception."""

    def __init__(self, message: str, code: str = "APPLICATION_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(ApplicationError):
    def __init__(self, resource: str, identifier: str | int) -> None:
        super().__init__(f"{resource} no encontrado: {identifier}", code="NOT_FOUND")


class ConflictError(ApplicationError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="CONFLICT")


class AuthenticationError(ApplicationError):
    def __init__(self, message: str = "Credenciales inválidas") -> None:
        super().__init__(message, code="AUTHENTICATION_FAILED")


class AuthorizationError(ApplicationError):
    def __init__(self, message: str = "No autorizado") -> None:
        super().__init__(message, code="AUTHORIZATION_FAILED")
