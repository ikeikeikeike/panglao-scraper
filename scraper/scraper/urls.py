from django.http import HttpResponse
from django.conf.urls import url, include
#  from django.contrib import admin


urlpatterns = [
    #  url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls')),
    url(r'^ping', lambda request: HttpResponse("ok")),
]
