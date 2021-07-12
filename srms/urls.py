from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .routers import router
# from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

# from rest_framework.routers import DefaultRouter

# fcm_router = DefaultRouter()

#fcm_router.register('devices', FCMDeviceAuthorizedViewSet)
urlpatterns = [
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls), name='api'),
    # path('fcm/', include("fcm.urls")),
    path('accounts/', include('allauth.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls')),
    path('',include('student.urls'),name='studentcorner'),
    path('',include('owner.urls'),name='studentenquiry'),
    path('',include('library.urls'),name='custom-library-urls'),
    path('',include('owner.baseurls')),
    path('',include('owner.employeeurls')),
    path('api/ubfcore/', include('ubfcore.urls', namespace='ubfcore')),
    path('api/ubfquiz/', include('ubfquiz.urls', namespace='ubfquiz')),
    path('api/ubfcart/', include('ubfcart.urls', namespace='ubfcart')),
    path('api/payments/',include('payment.urls')),
    path('',include('reward.urls')),
]

urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)