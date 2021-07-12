from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path, re_path

app_name = 'ubfcore'


urlpatterns = [
	path("search/", views.SearchSubscriptionsView.as_view()),
	path("general-notification/",views.Notification.as_view()),
	#path("personal-notification/",views.PersonalNotification.as_view()),
	#path("promo-code/",views.PromocodeAPI.as_view()),
	#path("promo-code-view/",views.PromoCodeViewAPI.as_view()),

]

router = DefaultRouter()

router.register('articles', views.ArticleViewSet, basename='articles')
router.register('categories', views.CategoryViewSet, basename='category')
router.register('sub-categories', views.SubCategoryViewSet, basename='sub-category')
router.register('pdfs', views.PDFSerializer, basename='pdf')
router.register('mcqs', views.MCQSerializer, basename='mcq')
router.register('summaries', views.SummarySerializer, basename='summary')
router.register('sessions', views.SessionSerializer, basename='session')
router.register('user-subscriptions', views.UserSubscriptionsSerializer, basename='user-subscription')

urlpatterns += router.urls
