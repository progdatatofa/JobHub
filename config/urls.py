"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
#from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('' , include('accounts.urls')),
    #path('test-403/', views.test_403, name='test-403'),
    #path('test-500/', views.test_500, name='test-500'),
]



urlpatterns += [
    path(
        'media/<path:path>',
        serve,
        {'document_root': settings.MEDIA_ROOT},
    ),
]

handler404 = 'accounts.views.custom_404'

