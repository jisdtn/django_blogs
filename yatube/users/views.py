from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("posts:posts")
    template_name = "users/signup.html"


class PasswordResetComplete(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("/auth/reset/done/")
    template_name = "users/password_reset_complete.html"
