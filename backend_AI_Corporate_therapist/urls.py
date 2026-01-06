# project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # URL for the admin panel (superuser access)
    path('admin/', admin.site.urls),
    # Forward any other request to the app_1 URLs file defined above
    path('', include('app_1.urls')),
]