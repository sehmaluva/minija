"""Custom throttling classes for auth endpoints."""

from rest_framework.throttling import AnonRateThrottle


class RegisterThrottle(AnonRateThrottle):
    """Throttle for user registration: 5 requests per hour."""

    rate = "5/hour"


class LoginThrottle(AnonRateThrottle):
    """Throttle for user login: 10 requests per minute."""

    rate = "10/minute"


class LogoutThrottle(AnonRateThrottle):
    """Throttle for user logout: 100 requests per hour."""

    rate = "100/hour"


class EmailVerificationThrottle(AnonRateThrottle):
    """Throttle for email verification: 3 requests per minute."""

    rate = "3/minute"


class ResendVerificationThrottle(AnonRateThrottle):
    """Throttle for resend verification: 1 request per minute."""

    rate = "1/minute"


class ForgotPasswordThrottle(AnonRateThrottle):
    """Throttle for forgot password: 3 requests per hour."""

    rate = "3/hour"


class ResetPasswordThrottle(AnonRateThrottle):
    """Throttle for reset password: 5 requests per minute."""

    rate = "3/minute"
