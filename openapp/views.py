from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from dotenv import load_dotenv
import os
from openai import OpenAI
import openai
from .models import ChatGptBot
from django.contrib.auth import authenticate, login
from django.views.generic import CreateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import SignUpForm, UserLoginForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.views.decorators.http import require_POST

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def index(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            user_input = request.POST.get('userInput')
            clean_user_input = str(user_input).strip()
            
            # Retrieve the entire conversation history for the user
            conversation_history = ChatGptBot.objects.filter(user=request.user).order_by('timestamp')
            
            # Format messages for OpenAI API
            messages_to_send = [
                {"role": "system", "content": "You are a helpful assistant."}
            ]
            
            for chat in conversation_history:
                messages_to_send.append({"role": "user", "content": chat.messageInput})
                messages_to_send.append({"role": "assistant", "content": chat.bot_response})
                
            # Include the current user input
            messages_to_send.append({"role": "user", "content": clean_user_input})
            
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages_to_send,
                )
                bot_response = response.choices[0].message.content

                ChatGptBot.objects.create(
                    user=request.user,
                    messageInput=clean_user_input,
                    bot_response=bot_response,
                    system_prompt="You are a helpful assistant.",
                )
            except openai.APIConnectionError:
                messages.warning(request, "Failed to connect to OpenAI API, check your internet connection")
            except openai.RateLimitError:
                messages.warning(request, "You exceeded your current quota, please check your plan and billing details.")
                messages.warning(request, "If you are a developer, change the API Key")

            return redirect(request.META['HTTP_REFERER'])
        else:
            get_history = ChatGptBot.objects.filter(user=request.user).order_by('timestamp')
            context = {'get_history': get_history}
            return render(request, 'index.html', context)
    else:
        return redirect("login")

class SignUp(CreateView):
    form_class = SignUpForm
    template_name = "users/register.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return response

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.warning(self.request, f"{field}: {error}")
        return redirect(self.request.META['HTTP_REFERER'])

    def get_success_url(self):
        return reverse("main")

class LoginView(FormView):
    form_class = UserLoginForm
    template_name = "login.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        login(self.request, user)
        messages.success(self.request, "You are logged in")
        return response

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.warning(self.request, f"{error}")
        return redirect(self.request.META['HTTP_REFERER'])

    def get_success_url(self):
        return reverse("main")

@login_required
def DeleteHistory(request):
    chatGptobjs = ChatGptBot.objects.filter(user=request.user)
    chatGptobjs.delete()
    messages.success(request, "All messages have been deleted")
    return redirect(request.META['HTTP_REFERER'])

def logout_view(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect("main")

@require_POST
def update_prompt(request):
    prompt = request.POST.get('prompt')
    custom_prompt = request.POST.get('custom_prompt_text', '')

    if prompt == 'custom' and custom_prompt:
        selected_prompt = custom_prompt
    else:
        selected_prompt = prompt

    ChatGptBot.objects.create(
        user=request.user,
        messageInput='System prompt updated',
        bot_response=f'System prompt changed to: {selected_prompt}',
        system_prompt=selected_prompt,
    )

    messages.success(request, f'System prompt updated to: {selected_prompt}')
    return redirect('main')
