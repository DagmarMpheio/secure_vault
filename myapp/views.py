from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError

# mensagens nos templates
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from .forms import UserForm
from .models import User

# Create your views here.
def register(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        # garantir que a senha coincidem com a confirmacao
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "auth/register.html", {
                "message": "As senhas não coincidem."
            })
        # tentar criar um novo usuario
        try:
            user = User.objects.create_user(
                first_name=first_name, last_name=last_name, username=email, password=password, email=email)
            user.save()
        except IntegrityError:
            return render(request, "auth/register.html", {
                "message": "O Email inserido já se encotrado associado com outra conta!"
            })
        
        #assim que cadastrar é redirecionado no painel
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auth/register.html")


def login_view(request):
    if request.method == "POST":
        # Tentar login
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)

        # verficar se o usuario foi autenticdo com sucesso
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auth/login.html", {
                "message": "Email ou Passowrd inválida."
            })
    return render(request, "auth/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


@login_required(login_url='/login')
def index(request):
    return render(request, "system/index.html")


@login_required(login_url='/login')
def profile(request):

    user = request.user
    form = UserForm(initial={'first_name': user.first_name,
                    'last_name': user.last_name, 'email': user.email})

    return render(request, "user/profile.html", {'form': form})


@login_required(login_url='/login')
def update_profile(request):
    user = request.user
    form = UserForm(initial={'first_name': user.first_name,
                    'last_name': user.last_name, 'email': user.email})

    if request.method == "POST":

        form = UserForm(request.POST, instance=user)

        if form.is_valid():
            try:
                form.save()
                model = form.instance

                messages.success(request, 'Usuário actualizado com sucesso!')
                return redirect('/profile')

            except Exception as e:
                messages.error(request, 'Algo ocorreu mal\nErro: {}'.format(e))
                return redirect('/profile')
    return render(request, "user/edit-profile.html", {'form': form})
