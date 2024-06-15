from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields= ['username','password1', 'password2']
        exclude = ['email']
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'





class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields= ['username', 'password']
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['password'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'



class PromptForm(forms.Form):
    PROMPT_CHOICES = [
        ('prompt1', 'System Prompt 1'),
        ('prompt2', 'System Prompt 2'),
        ('prompt3', 'System Prompt 3'),
        ('custom', 'Custom Prompt'),
    ]
    prompt = forms.ChoiceField(choices=PROMPT_CHOICES, required=True)
    custom_prompt_text = forms.CharField(widget=forms.Textarea, required=False)