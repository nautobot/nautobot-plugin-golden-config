"""API for Custom Jobs ."""

from django.urls import path
from rest_framework import routers

from . import views

app_name = "nautobot_golden_config"

router = routers.DefaultRouter()
router.register("line_remove", views.ConfigRemoveViewSet)
router.register("line_replace", views.ConfigReplaceViewSet)
urlpatterns = router.urls
urlpatterns += [
    path(
        "sotagg/<uuid:pk>/",
        views.SOTAggDeviceDetailView.as_view(),
        name="device_detail",
    )
]
