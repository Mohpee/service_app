from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.user.profile_completed:
                if not request.path.startswith('/users/profile/create/'):
                    messages.warning(request, 'Please complete your profile to continue.')
                    return redirect('users:profile-create')
        return self.get_response(request)