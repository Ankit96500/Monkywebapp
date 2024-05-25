from django import forms
from chat.models import CustomUser
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm,UserChangeForm,SetPasswordForm



class UserLoginForm(AuthenticationForm):
    password=forms.CharField(widget=forms.PasswordInput(attrs={'class':"form-control focus-ring focus-ring-light border","placeholder":"Password"}),label='',)
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class':"form-control focus-ring focus-ring-light border","placeholder":"email"}),label="")
    class Meta:
        model = CustomUser
        fields = ['email','password']



#user signup form
class signupform(UserCreationForm):
    password1=forms.CharField(widget=forms.PasswordInput(attrs={'class':"form-control focus-ring focus-ring-light border","placeholder":"Password"}),label='',)
    password2=forms.CharField(widget=forms.PasswordInput(attrs={'class':"form-control focus-ring focus-ring-light border","placeholder":"Password Conformation"}),label='',)
    email= forms.EmailField(required=True,widget=forms.EmailInput(attrs={'class':"form-control focus-ring focus-ring-light border","placeholder":"email"}),label="")
    first_name = forms.CharField(required=True,widget=forms.TextInput(attrs={'class':"form-control focus-ring focus-ring-light border","placeholder":"First Name"}),label="")
    last_name = forms.CharField(required=True,widget=forms.TextInput(attrs={'class':"form-control focus-ring focus-ring-light border","placeholder":"Last Name"}),label="")
    
    class Meta:
        model = CustomUser
        fields=['email','first_name','last_name']
      
class PasswordFormChange(SetPasswordForm):
    error_messages = {
        "password_mismatch": ("The two password fields didn’t match."),
    }
    new_password1 = forms.CharField(
        label=(""),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password","class":"form-control focus-ring focus-ring-light border","placeholder":"New Password"}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=(""),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password","class":"form-control focus-ring focus-ring-light border","placeholder":"New Password Conformation"}),
    )
    class Meta:
        model = CustomUser



"all these a customized forms"


    
