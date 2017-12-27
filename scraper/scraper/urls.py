from django.http import HttpResponse
from django.conf.urls import url, include
#  from django.contrib import admin


urlpatterns = [
    #  url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls', namespace='api')),
    url(r'^lifecycle/', include('lifecycle.urls', namespace='lifecycle')),
    url(r'^ping', lambda request: HttpResponse("ok")),
]
