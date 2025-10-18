from django.shortcuts import render

# Create your views here.


def homepage(request):
    return render(request, "pages/homepage.html")


def about(request):
    return render(request, "pages/about.html")


def contact(request):
    return render(request, "pages/contact.html")
