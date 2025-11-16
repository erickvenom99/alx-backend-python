# messaging_app/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include router URLs under /api/
    path('api/', include('chats.urls')),
]