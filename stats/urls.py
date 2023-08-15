from django.urls import include, path
from .views import (
    get_all_stats,
    get_stats_per_day,
    get_farmer_all_stats,
    get_farmer_stats_per_day,
    test_module
)

urlpatterns = [
    path("total-stats/<int:user_id>/", get_all_stats, name="get-all-stats"),
    path(
        "daily-stats/<int:user_id>/<str:date>/",
        get_stats_per_day,
        name="get-stats-per-day",
    ),
    path(
        "farmer-total-stats/<int:user_id>/", get_farmer_all_stats, name="get-all-stats"
    ),
    path(
        "farmer-daily-stats/<int:user_id>/<str:date>/",
        get_farmer_stats_per_day,
        name="get-stats-per-day",
    ),
    path('test/', test_module, name='multi-detect'),
    # path('multi-detect/', multi_leaves_classification, name='multi-detect'),
]
