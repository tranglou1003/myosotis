"""
Custom exceptions for TTS API
"""


class TTSAPIException(Exception):
    """Base exception for TTS API"""
    pass


class TTSError(TTSAPIException):
    """Exception raised when TTS synthesis fails"""
    pass


class ValidationError(TTSAPIException):
    """Exception raised when request validation fails"""
    pass


class ConfigurationError(TTSAPIException):
    """Exception raised when configuration is invalid"""
    pass


class ResourceNotFoundError(TTSAPIException):
    """Exception raised when required resource is not found"""
    pass
