from .views import BlogView, FantasyView, PhilosophyView
from rest_framework.routers import DefaultRouter

urlpatterns = []

router = DefaultRouter()

router.register('', BlogView, basename='blog')
router.register('', FantasyView, basename='fantasy')
router.register('philosophy', PhilosophyView, basename='philosophy')

urlpatterns += router.urls
