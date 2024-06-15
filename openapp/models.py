from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatGptBot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    messageInput = models.TextField()
    bot_response = models.TextField()
    system_prompt = models.TextField(default="default")  # New field for tracking system prompts
    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp for tracking message order

    def __str__(self):
        return self.user.username
