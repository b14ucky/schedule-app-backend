from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import TokenObtainPairSerializer_


# Create your views here.
class TokenObtainPairView_(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer_
