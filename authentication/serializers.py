from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class TokenObtainPairSerializer_(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["first_name"] = user.first_name

        return token

    def validate(self, attrs):
        attrs["username"] = attrs.get("email")
        data = super().validate(attrs)

        data["user"] = {  # type: ignore
            "id": self.user.id,  # type: ignore
            "email": self.user.email,  # type: ignore
            "first_name": self.user.first_name,  # type: ignore
            "last_name": self.user.last_name,  # type: ignore
        }

        return data
