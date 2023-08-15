from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import PictureAPI, PostAPI

router = DefaultRouter()
router.register(r'posts', PostAPI)
# router.register(r'picture', PictureAPI)

urlpatterns = [
    path('api2/', include(router.urls)),
]
