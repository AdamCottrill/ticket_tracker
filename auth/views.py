from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect

#from django import forms
from django.contrib import auth
from django.contrib.auth import authenticate
#from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
#from django.contrib.auth.views import logout
#from django.core.context_processors import csrf
from django.core.urlresolvers import reverse

#from django.template import RequestContext
from .forms import UserForm, ChangePasswordForm


#def login(request):
#    logout(request)
#    username = ""
#    password = ""
#    if request.method =="POST":
#        username = form.cleaned_data['username']
#        password = form.cleaned_data['password']
#        user = authenticate(username, password)
#        if user is not None:
#            if user.is_active:
#                auth.login(request, user)
#                return HttpResponseRedirect(reverse("ticket_list"))
#    return render_to_response('auth/login.html',
#                            context_instance = RequestContext(request))

@login_required
def logout_view(request):
    """
    """
    auth.logout(request)
    return render_to_response(request, 'auth/logged_out.html')

@login_required
def change_password(request):
    """
    """
    if request.method=="POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            user = request.user
            user.set_password(new_password)
            user.save()
            return render(request, 'auth/password_changed.html')            
    else:
        form = UserForm()
    return render(request, 'auth/change_password.html', {'form':form})    

def register(request):
    """
    """
    if request.method=="POST":
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            new_user = User(username=username)
            new_user.set_password(password)
            new_user.save()
            new_user = authenticate(username=username, password=password)
            auth.login(request, new_user)
            return HttpResponseRedirect(reverse('ticket_list'))
    else:
        form = UserForm()
    return render(request, 'auth/register.html', {'form':form})    
