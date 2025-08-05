from rest_framework_nested import routers

from .views import VehicleViewSet
from apps.comments.views import CommentViewSet

router = routers.DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')

comments_router = routers.NestedDefaultRouter(router, r'vehicles', lookup='vehicle')
comments_router.register(r'comments', CommentViewSet, basename='vehicle-comments')

urlpatterns = [
    *router.urls,
    *comments_router.urls,
]