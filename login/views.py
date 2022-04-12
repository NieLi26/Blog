from django.shortcuts import redirect
from django.views.generic import FormView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, get_user_model
from django.urls import reverse_lazy
from blog.models import Author

# User = User = get_user_model()
# Create your models here.

class LoginFormView(LoginView):
    template_name = 'login/login.html'
    redirect_authenticated_user = True

class RegisterFormView(FormView):
    template_name = 'login/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('index')
    
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            author = Author()
            author.user = user
            author.save()
            login(self.request, user)
        return super().form_valid(form)

class PerfilUpdateView(UpdateView):
    model = Author
    fields = 'profile_picture', 
    template_name = 'login/perfil.html'
    success_url = reverse_lazy('index')

    

