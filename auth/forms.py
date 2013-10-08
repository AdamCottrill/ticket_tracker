from django import forms
from django.contrib.auth.models import User

from passwords.fields import PasswordField

class UserForm(forms.Form):
    username = forms.CharField(max_length=30)
    password1 = PasswordField(label="Password")
    password2 = PasswordField(label="Password")

    def clean_username (self): 
        try:
            User.objects.get(username=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError("Username already in use.")

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return self.cleaned_data


class ChangePasswordForm(forms.Form):
    new_password1 = PasswordField(label="Password")
    new_password2 = PasswordField(label="Password")

    def clean(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')

        if password1 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return self.cleaned_data
