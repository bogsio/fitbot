"""fitbot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path
from fitbot.views import webhook
from fitbot.utils import init_messenger_profile
from fitbot.menu import PERSISTENT_MENU, GET_STARTED

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webhook', webhook),
]


print(init_messenger_profile(
    get_started=GET_STARTED,
    persistent_menu=PERSISTENT_MENU
))