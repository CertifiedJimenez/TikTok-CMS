# django
from django.conf import settings

# Allauth
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.google.provider import GoogleProvider
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter, OAuth2CallbackView, OAuth2LoginView,
)

#utils
import jwt


ACCESS_TOKEN_URL = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("google", {})
    .get("ACCESS_TOKEN_URL", "https://oauth2.googleapis.com/token")
)

AUTHORIZE_URL = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("google", {})
    .get("ACCESS_TOKEN_URL", "https://accounts.google.com/o/oauth2/v2/auth")
)

ID_TOKEN_ISSUER = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("google", {})
    .get("ID_TOKEN_ISSUER", "https://accounts.google.com")
)


class CustomGoogleOAuth2Adapter(OAuth2Adapter):
    provider_id = GoogleProvider.id
    access_token_url = ACCESS_TOKEN_URL
    authorize_url = AUTHORIZE_URL
    id_token_issuer = ID_TOKEN_ISSUER

    def complete_login(self, request, app, token, response, **kwargs):
        try:
            identity_data = jwt.decode(
                response,
                # Since the token was received by direct communication
                # protected by TLS between this library and Google, we
                # are allowed to skip checking the token signature
                # according to the OpenID Connect Core 1.0
                # specification.
                # https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation
                options={
                    "verify_signature": False,
                    "verify_iss": True,
                    "verify_aud": True,
                    "verify_exp": True,
                },
                issuer=self.id_token_issuer,
                audience=app.client_id,
                verify = False
            )
        except jwt.PyJWTError as e:
            raise OAuth2Error("Invalid id_token") from e
        login = self.get_provider().sociallogin_from_response(request, identity_data)
        return login
