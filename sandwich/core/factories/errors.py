class SandwichError(Exception):
    """Base class for all sandwich-related errors."""


class FactoryError(SandwichError):
    """Raised when a factory-related error occurs."""
