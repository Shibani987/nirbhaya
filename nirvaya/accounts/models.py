from django.db import models
from django.contrib.auth.models import User

class EmergencyContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15, default="0000000000")

    def save(self, *args, **kwargs):
        # Ensure phone number starts with +91
        if not self.phone.startswith("+91"):
            self.phone = f"+91{self.phone[-10:]}"  # Enforce +91 and take last 10 digits
        super(EmergencyContact, self).save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.name} - {self.email} - {self.phone}"
   

class VoiceCommand(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    voice_command = models.CharField(max_length=255)

    def __str__(self):
        return f"Voice Command for {self.user.username}: {self.voice_command}"

class SOSAlert(models.Model):
    location = models.CharField(max_length=255)  # Example: "23.4567, 78.1234"
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SOS Alert at {self.location} on {self.timestamp}"





from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username
