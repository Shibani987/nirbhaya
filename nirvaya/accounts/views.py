from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .models import EmergencyContact
import time  # To simulate delayed response
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404

from .models import EmergencyContact, VoiceCommand
from django.contrib.auth.models import User

# Signup View
def signup_view(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully! You can now log in.")
        return redirect('signin')
    
    return render(request, 'accounts/signin_signup.html')

# Signin View
def signin_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirecting to 'home' instead of 'dashboard'
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('signin')
    
    return render(request, 'accounts/signin_signup.html')

# Logout View
def logout_view(request):
    logout(request)
    return redirect('signin')




def request_password_reset(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.filter(email=email).first()
            if user:
                subject = "Password Reset Request"
                message = render_to_string("accounts/password_reset_email.html", {
                    "user": user,
                    "domain": request.get_host(),
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                })
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
                messages.success(request, "Check your email for password reset instructions.")
                return redirect("password_reset_done")
    else:
        form = PasswordResetForm()
    return render(request, "accounts/password_reset_form.html", {"form": form})

def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                user.save()  # <-- Ensure the user is saved
                messages.success(request, "Password has been reset. You can now log in.")
                return redirect("password_reset_complete")
            else:
                print(form.errors)  # <-- Debugging: Print form errors in the console
        else:
            form = SetPasswordForm(user)

        return render(request, "accounts/password_reset_confirm.html", {"form": form})

    else:
        messages.error(request, "Invalid password reset link.")
        return redirect("password_reset")

def reset_password_done(request):
    return render(request, "accounts/password_reset_done.html")

def reset_password_complete(request):
    return render(request, "accounts/password_reset_complete.html")



import json
import logging
from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client

# Configure logging
logger = logging.getLogger(__name__)

# Twilio Credentials (Replace with actual credentials)
TWILIO_ACCOUNT_SID = "ACXXXXXXXXXXXXXXXX"
TWILIO_AUTH_TOKEN = "your_auth_token"  # Replace with your actual Twilio Auth Token
TWILIO_PHONE_NUMBER = "your_twilio_phone_number"  # Twilio trial number

@csrf_exempt
def send_sos_email(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            contacts = data.get("contacts", [])
            phone_numbers = data.get("phone_numbers", [])  # List of phone numbers for voice call
            location = data.get("location", {})
            message = data.get("message", "🚨🚨 EMERGENCY SOS ALERT! 🚨🚨")

            if not contacts and not phone_numbers:
                return JsonResponse({"success": False, "error": "At least one email or phone number is required."})

            # Generate Google Maps link if location is available
            if location.get("latitude") and location.get("longitude"):
                maps_link = f"https://www.google.com/maps?q={location['latitude']},{location['longitude']}"
                location_info = f"📍 Location: {maps_link}"
            else:
                location_info = "📍 Location not available"

            # Construct the SOS email message
            email_body = (
                "❗❗❗ URGENT SOS ALERT ❗❗❗\n\n"
                f"{message}\n\n"
                "⚠️ This is an emergency alert sent from Nirvaya SOS System.\n"
                "🔴 Please check on the sender immediately!\n\n"
                f"{location_info}\n\n"
                "🚑 Stay safe and take action now!"
            )

            # Send email alerts
            for contact in contacts:
                email = contact.get("email")
                if email:
                    send_mail(
                        subject="🚨 URGENT: SOS ALERT 🚨",
                        message=email_body,
                        from_email="your_email@example.com",  # Replace with actual email
                        recipient_list=[email],
                        fail_silently=False,
                    )

            # Twilio client
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

            # 📞 Custom Twilio Call Message
            call_message = (
                "🚨 Emergency Alert! 🚨 "
                f"{message}. "
                "This is an automated SOS call from the Nirvaya SOS System. "
                "The sender is in distress and requires immediate assistance. "
                f"{location_info}. "
                "Please take action now!"
            )

            # Send voice call alerts
            for phone in phone_numbers:
                if phone:
                    call = client.calls.create(
                        twiml=f'<Response><Say>{call_message}</Say></Response>',
                        to=phone,
                        from_=TWILIO_PHONE_NUMBER
                    )
                    logger.info(f"📞 Call initiated: {call.sid} for {phone}")

            return JsonResponse({"success": True, "message": "🚨 SOS alert emails and calls sent successfully."})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON format."})
        except Exception as e:
            logger.error(f"Error in send_sos_alert: {e}")
            return JsonResponse({"success": False, "error": "An unexpected error occurred. Please try again."})

    return JsonResponse({"success": False, "error": "Invalid request method."})


# Save voice command
@csrf_exempt
def save_voice_command(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_id = data.get("user_id")
        voice_command = data.get("voice_command")

        user = get_object_or_404(User, id=user_id)

        # Check if the user already has a saved voice command
        command_obj, created = VoiceCommand.objects.update_or_create(
            user=user, defaults={"voice_command": voice_command}
        )

        return JsonResponse({"message": "Voice command saved successfully!"})


# Get saved voice command
def get_voice_command(request, user_id):
    user = get_object_or_404(User, id=user_id)
    voice_command = VoiceCommand.objects.filter(user=user).first()
    return JsonResponse({"voice_command": voice_command.voice_command if voice_command else ""})

def track_view(request):
    
    return render(request, 'accounts/track.html') 


@login_required(login_url='signin') 

def main_home(request):
    return render(request, 'accounts/main_home.html')

def about(request):
    return render(request, 'accounts/about.html')

def services(request):
    return render(request, 'accounts/services.html')

def contact(request):
    return render(request, 'accounts/contact.html')
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserProfile

@login_required
def user_profile(request):
    # Get or create the user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Update user fields
        request.user.username = request.POST.get('username')
        request.user.email = request.POST.get('email')
        request.user.save()

        # Update profile fields
        profile.address = request.POST.get('address')
        profile.bio = request.POST.get('bio')
        profile.age = request.POST.get('age')
        profile.location = request.POST.get('location')
        profile.save()

        return redirect('user_profile')  # Reload page with updated data

    return render(request, 'accounts/user_profile.html', {'profile': profile})
import json
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import EmergencyContact

@csrf_exempt
def add_contact(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("📥 Received Data:", data)  # Log received data

            user_id = data.get("user_id")
            name = data.get("name", "").strip()
            email = data.get("email", "").strip()
            phone = data.get("phone", "").strip()

            if not all([user_id, name, email, phone]):
                print("⚠️ Missing Fields Error")
                return JsonResponse({"error": "⚠️ Missing fields! Please enter all details."}, status=400)

            # Ensure user_id is a valid integer
            try:
                user_id = int(user_id)
            except ValueError:
                print("⚠️ Invalid user_id:", user_id)
                return JsonResponse({"error": "⚠️ Invalid user ID!"}, status=400)

            # Normalize phone number (Handle cases with or without +91)
            phone = phone.replace(" ", "")  # Remove spaces
            if phone.startswith("+91"):  
                phone = phone[3:]  # Remove "+91" prefix if present
            phone = re.sub(r"\D", "", phone)  # Remove non-numeric characters

            if len(phone) != 10:
                print("⚠️ Invalid phone number:", phone)
                return JsonResponse({"error": "⚠️ Invalid phone number! Enter 10 digits."}, status=400)

            formatted_phone = f"+91{phone}"  # Ensure format: +91XXXXXXXXXX
            print("📞 Formatted Phone:", formatted_phone)

            # Ensure user exists
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                print("⚠️ User not found with ID:", user_id)
                return JsonResponse({"error": "⚠️ User not found!"}, status=404)

            # Create emergency contact
            contact = EmergencyContact.objects.create(
                user=user, name=name, email=email, phone=formatted_phone
            )
            print("✅ Contact Saved:", contact)

            return JsonResponse({"message": "✅ Contact added successfully!"}, status=201)

        except json.JSONDecodeError:
            print("❌ JSON Decode Error")
            return JsonResponse({"error": "⚠️ Invalid JSON format!"}, status=400)
        except Exception as e:
            print("❌ Unexpected Error:", str(e))
            return JsonResponse({"error": f"⚠️ Server error: {str(e)}"}, status=500)

    return JsonResponse({"error": "⚠️ Invalid request method!"}, status=405)

def get_contacts(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        contacts = EmergencyContact.objects.filter(user=user).values("id", "name", "email", "phone")  # Include ID

        return JsonResponse({"contacts": list(contacts)}, status=200)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json
from .models import EmergencyContact

@csrf_exempt
def remove_contact(request):
    if request.method in ["POST", "DELETE"]:  # Accept both DELETE & POST
        try:
            data = json.loads(request.body)
            contact_id = data.get("contact_id")

            contact = get_object_or_404(EmergencyContact, id=contact_id)
            contact.delete()
            return JsonResponse({"message": "Contact removed successfully"}, status=200)

        except EmergencyContact.DoesNotExist:
            return JsonResponse({"error": "Contact not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

from django.shortcuts import render, redirect

def join_us(request):
    return render(request, 'accounts/joinus.html')  # Render the Join Us page
