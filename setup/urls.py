# setup/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings # IMPORTANTE
from django.conf.urls.static import static # IMPORTANTE
from hotel.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('hotel/', include('hotel.urls')),
    path('cadastros/', include('cadastros.urls')),
    path('financeiro/', include('financeiro.urls')),
    path('estoque/', include('estoque.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

# ESTA LINHA ABAIXO É O QUE FAZ A IMAGEM APARECER NO NAVEGADOR
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)