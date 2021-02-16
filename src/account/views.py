from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate

from .models import Account
from .forms import (
    RegistrationForm,
    AccountAuthenticationForm,
    AccountUpdateForm,

)
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage

# Create your views here.


def registration_view(request):
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            # form.save()

            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            current_site = get_current_site(request)
            mail_subject = 'Activate your blog account.'
            message = render_to_string('account/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            messages.success(request, ('Please Confirm your email to complete registration.'))
            # account = authenticate(email=email, password=raw_password)
            # login(request, account)
            return redirect('login')
        else:  # executes when form validation fails

            context['registration_form'] = form
    else:  # GET REQUEST
        form = RegistrationForm()
        context['registration_form'] = form
    return render(request, 'account/register.html', context)


def logout_view(request):
    logout(request)
    return redirect('home')


def login_view(request):
    context = {}
    if request.user.is_authenticated:
        return redirect('home')
    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return redirect('home')
    else:
        form = AccountAuthenticationForm()
    # this line is executed when the form is invalid or get requestsame method can be applied to registration view also
    context['login_form'] = form
    return render(request, 'account/login.html', context)

# updating the account username nad password


def account_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    context = {}
    if request.POST:
        form = AccountUpdateForm(request.POST, instance=request.user)
        if form.is_valid():

            form.initial = {
                "email": form.cleaned_data['email'],
                "username": form.cleaned_data['username'],
            }
            form.save()
            context['success_message'] = "Updated"
            # return redirect('home')
    else:
        form = AccountUpdateForm(
            initial={
                "email": request.user.email,
                "username": request.user.username,
            }
        )
    context['account_form'] = form
    return render(request, 'account/account.html', context)


def must_authenticate_view(request):
    return render(request, 'account/must_authenticate.html', {})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = Account.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, ('Your account have been confirmed.'))
        return redirect('login')
        # return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        # return HttpResponse('Activation link is invalid!')
        messages.warning(request, ('The confirmation link was invalid, possibly because it has already been used.'))
        return redirect('home')
