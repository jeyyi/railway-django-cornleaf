from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import PictureAPI, PostAPI, ListOrBulkDeleteAlbums

router = DefaultRouter()
router.register(r'posts', PostAPI)

urlpatterns = [
    path('api2/', include(router.urls)),
    path('api2/delete-all-posts', ListOrBulkDeleteAlbums.as_view()),
]
