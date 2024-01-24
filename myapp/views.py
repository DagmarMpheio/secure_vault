from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError

# mensagens nos templates
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy

# verificacao de email
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


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

            # Gerar token de verificação
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # Construir o link de verificação
            verification_link = f"{request.build_absolute_uri(reverse('verify_email', kwargs={'uidb64': uid, 'token': token}))}"

            # Enviar e-mail de verificação
            subject = 'Verifique seu e-mail'
            message = render_to_string('auth/verification_email.html', {
                'user': user,
                'verification_link': verification_link,
            })

            # Remover tags HTML para o corpo do e-mail simples
            plain_message = strip_tags(message)
            from_email = 'securevault@gmail.com'
            to_email = user.email
            send_mail(subject, plain_message, from_email,
                      [to_email], html_message=message)

        except IntegrityError:
            return render(request, "auth/register.html", {
                "message": "O Email inserido já se encotrado associado com outra conta!"
            })

        # assim que cadastrar é redirecionado no painel
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
            if user.is_active:
                login(request, user)
                # Resetar o contador de tentativas bem-sucedidas
                user.login_attempts = 0
                user.save()
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "auth/login.html", {
                    "message": "Sua conta está bloqueada. Entre em contato com o suporte."
                })
        else:
            # Incrementar o contador de tentativas malsucedidas
            user = User.objects.get(username=email)
            user.login_attempts += 1
            user.save()

            if user.login_attempts >= 3:
                user.is_active = False
                user.save()

                return render(request, "auth/login.html", {
                    "message": "Sua conta foi bloqueada devido a múltiplas tentativas malsucedidas. Entre em contato com o suporte.."
                })

            return render(request, "auth/login.html", {
                "message": "Credenciais inválidas. Tente novamente."
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


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Marcar o e-mail como verificado
        user.email_is_verified = True
        user.save()

        # Adicionar lógica adicional conforme necessário

        return render(request, "auth/email_verified.html")
    else:
        return render(request, "auth/email_verification_failed.html")
