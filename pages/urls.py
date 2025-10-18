from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("about", views.about, name="about"),
    path("contact", views.contact, name="contact"),
]
