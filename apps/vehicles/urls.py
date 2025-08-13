from rest_framework_nested import routers

from .views import VehicleViewSet
from apps.comments.views import CommentViewSet
from apps.reports.views import ReportViewSet

router = routers.DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')

vehicle_nested_router = routers.NestedDefaultRouter(router, r'vehicles', lookup='vehicle')
vehicle_nested_router.register(r'comments', CommentViewSet, basename='vehicle-comments')
vehicle_nested_router.register(r'reports', ReportViewSet, basename='vehicle-reports')

urlpatterns = [
    *router.urls,
    *vehicle_nested_router.urls,
]