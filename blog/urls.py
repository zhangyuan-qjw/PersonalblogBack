from .views import BlogView, FantasyView
from rest_framework.routers import DefaultRouter

urlpatterns = []

router = DefaultRouter()

router.register('', BlogView, basename='blog')
router.register('', FantasyView, basename='fantasy')

urlpatterns += router.urls
