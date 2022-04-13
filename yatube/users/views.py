from django.views.generic import CreateView
from django.urls import reverse_lazy
from users.forms import CreationForm


class SignUp(CreateView):
    """Вью-класс создания пользоветля"""
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'
