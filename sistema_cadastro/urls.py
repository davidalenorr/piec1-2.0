from django.contrib import admin
from django.urls import path, include
from cadastro import views as cadastro_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cadastro/', include('cadastro.urls')),
    path('', cadastro_views.home, name='home'),
]