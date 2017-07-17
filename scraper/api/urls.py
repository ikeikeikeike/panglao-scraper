from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^info/(?P<encoded>.*=?)", views.info, name="info"),
    url(r"^progress/(?P<encoded>.*=?)", views.progress, name="progress"),
    url(r"^download/(?P<encoded>.*=?)", views.download, name="download"),
    url(r"^nodeinfo", views.nodeinfo, name="nodeinfo"),
    url(r"^findfile/(?P<encoded>.*=?)", views.findfile, name="findfile"),
    url(r"^removefile/(?P<encoded>.*=?)", views.removefile, name="removefile"),
]
