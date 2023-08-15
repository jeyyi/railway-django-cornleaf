from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CommentAPI

router = DefaultRouter()
router.register(r'comment', CommentAPI)

urlpatterns = [
    path('api3/', include(router.urls)),
]
