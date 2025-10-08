from rest_framework_simplejwt.authentication import JWTAuthentication  # type: ignore
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError  # type: ignore


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that looks for tokens in cookies
    """

    def authenticate(self, request):
        # First try to get token from Authorization header
        header = self.get_header(request)
        if header:
            raw_token = self.get_raw_token(header)
        else:
            # Try to get token from cookies
            raw_token = request.COOKIES.get("access_token")

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        return self.get_user(validated_token), validated_token
