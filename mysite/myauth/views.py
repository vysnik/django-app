from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView, View, UpdateView, ListView, DetailView

from .models import Profile
from .forms import ProfileForm

class UserListView(ListView):
    template_name = 'myauth/user-list.html'
    context_object_name = "users"
    queryset = User.objects.all()

class UserDetailsView(DetailView):
    template_name = 'myauth/user-details.html'
    model = User
    context_object_name = "user"

class AboutMeView(TemplateView):
    template_name = "myauth/about-me.html"

class ProfileUpdateView(UserPassesTestMixin, UpdateView):
    model = Profile
    fields = ["avatar"]
    template_name = "myauth/profile_update_form.html"

    def test_func(self):
        if self.request.user.is_superuser or self.get_object().user == self.request.user:
            return True
    def get_success_url(self):
        return reverse("myauth:about-me")



class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)

        Profile.objects.create(user=self.object)

        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user=user)

        return response

def logout_view(request: HttpRequest):
    logout(request)
    return redirect(reverse("myauth:login"))

class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse('Cookie set')
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response

def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default_value")
    return HttpResponse(f"Cookie value: {value!r}")

@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse('Session set!')

@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default_value")
    return HttpResponse(f"Session value: {value!r}")

class FooBarView(View):
    def get(self, reuest: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})
