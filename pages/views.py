from django.shortcuts import render

# Create your views here.


def homepage(request):
    return render(request, "pages/homepage.html")


def about(request):
    pass


def contact(request):
    pass
