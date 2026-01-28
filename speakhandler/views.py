from .models import *
from django.shortcuts import render, redirect

# Authentication Imports
import re
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate

# Join Meeting Helper Imports
import random, string, secrets

# Email Sending Imports
from django.conf import settings
from django.core.mail import send_mail

# Join Meeting Helper Imports
import time
from decouple import config
from django.http import JsonResponse
from agora_token_builder import RtcTokenBuilder

# Agora Helpers Imports
import json
from django.views.decorators.csrf import csrf_exempt

# Live Transcription Imports
import os
import speechmatics
from httpx import HTTPStatusError

# import httpcore
import httpcore
setattr(httpcore, 'SyncHTTPTransport', 'AsyncHTTPProxy')

from speechmatics.models import ConnectionSettings
from speechmatics.batch_client import BatchClient
from httpx import HTTPStatusError

import subprocess
from pathlib import Path
import tempfile

from deep_translator import GoogleTranslator

SPEECHMATICS_API_KEY=config('SPEECHMATICS_API_KEY')
# CONNECTION_URL = f"wss://eu2.rt.speechmatics.com/v2"
CONNECTION_URL = f"https://asr.api.speechmatics.com/v2"

speechmatics_settings = ConnectionSettings(
    url="https://asr.api.speechmatics.com/v2",
    auth_token=SPEECHMATICS_API_KEY,
)

conf = {
    "type": "transcription",
    "transcription_config": {
        "operating_point": "enhanced",
        "language": "auto",
        "diarization": "speaker",
    }
}



#region ===============   Generic   =================

def home(request):
    return render(request, 'generic/home.html')

def about(request):
    return render(request, 'generic/about.html')

def contact(request):
    if request.method == 'POST':
        send_mail_from_backend(
            'New Contact Request from SpeakEasy Website',
            get_contact_message(request),
            [settings.EMAIL_HOST_USER]
        )
        return redirect('home')
    return render(request, 'generic/contact.html')

#endregion ============   Generic   =================



#region ===============   Authentication   =================

def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method=="POST":
        verification = validate_login_details(request)
        if verification == "Verified":
            try:
                auth_user = authenticate(username=request.POST['email'], password=request.POST['password'])
                login(request, auth_user)
                return redirect('create_room')
            except Exception as e:
                return render_login_form(request.POST, "Incorrect Username or Password. Try Again!", request)
        else:
            return render_login_form(request.POST, verification, request)
    return render(request, 'authentication/login.html')


def signup(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']

        verification = validate_signup_details(request)

        if verification == "Verified":
            try:
                user = User.objects.create_user(
                    first_name=first_name, 
                    last_name=last_name, 
                    email=email, 
                    username=email, 
                    password=password
                )
                user.save()

                auth_user = authenticate(username=email, password=password)
                login(request, auth_user)

                return redirect('create_room')
            except Exception as e:
                return render_signup_form(request.POST, "Email is already taken", request)
        else:
            return render_signup_form(request.POST, verification, request)
    return render(request, 'authentication/signup.html')


@login_required
def logout_user(request):
    logout(request)
    return redirect('login')


# Helper Function
def render_signup_form(form_values, error, request):
    context = {
        'form_values': form_values,
        'error': error
    }
    return render(request, 'authentication/signup.html', context)


def validate_signup_details(request):
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST['email']
    password = request.POST['password']

    # Validate first name
    if not first_name:
        return "First name cannot be empty."
    if not all(part.isalpha() for part in first_name.split()):
        return "First name should only contain alphabets and spaces."
    
    # Validate last name
    if not last_name:
        return "Last name cannot be empty."
    if not all(part.isalpha() for part in last_name.split()):
        return "Last name should only contain alphabets and spaces."

    # Validate email format
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        return "Email should be in a proper format."
    
    # Validate password length
    if len(password) < 8:
        return "Password length should be at least 8 characters."
    
    # Validate password complexity
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)

    if not (has_upper and has_lower and has_digit):
        return "Password should contain at least one uppercase letter, one lowercase letter, and one digit."
    
    return "Verified"


def validate_login_details(request):
    email = request.POST['email']
    password = request.POST['password']

    if not email:

        return "Email cannot be empty."
    if not password:
        return "Password cannot be empty."
    
    return "Verified"


def render_login_form(form_values, error, request):
    context = {
        'form_values': form_values,
        'error': error
    }
    return render(request, 'authentication/login.html', context)


#endregion ============   Authentication   =================



#region ===============   Meeting Views   =================

@login_required
def lobby(request):
    context = {
        'languages_dict': get_languages_dict(),
        'room_name': generate_unique_link(),
        'join_name': f'{request.user.first_name} {request.user.last_name}'
    }
    return render(request, 'rooms/create_room.html', context)


def room(request):
    return render(request, 'rooms/room.html')


def join_room_with_link(request, meeting_id):
    context = {
        'languages_dict': get_languages_dict(),
        'room_name': meeting_id,
    }
    return render(request, 'rooms/join_room.html', context)


@login_required
def join_room(request):
    context = {
        'languages_dict': get_languages_dict()
    }
    return render(request, 'rooms/join_room.html', context)

#endregion ============   Meeting Views   =================



#region ===============   Language Helper Functions   =================

def get_languages_dict():
    LANGUAGES_DICT = {
        'Arabic': 'ar',
        'Bashkir': 'ba',
        'Basque': 'eu',
        'Belarusian': 'be',
        'Bulgarian': 'bg',
        'Cantonese': 'yue',
        'Catalan': 'ca',
        'Croatian': 'hr',
        'Czech': 'cs',
        'Danish': 'da',
        'Dutch': 'nl',
        'English': 'en',
        'Esperanto': 'eo',
        'Estonian': 'et',
        'Finnish': 'fi',
        'French': 'fr',
        'Galician': 'gl',
        'German': 'de',
        'Greek': 'el',
        'Hindi': 'hi',
        'Hungarian': 'hu',
        'Interlingua': 'ia',
        'Italian': 'it',
        'Indonesian': 'id',
        'Japanese': 'ja',
        'Korean': 'ko',
        'Latvian': 'lv',
        'Lithuanian': 'lt',
        'Malay': 'ms',
        'Mandarin': 'cmn',
        'Marathi': 'mr',
        'Mongolian': 'mn',
        'Norwegian': 'no',
        'Persian': 'fa',
        'Polish': 'pl',
        'Portuguese': 'pt',
        'Romanian': 'ro',
        'Russian': 'ru',
        'Slovakian': 'sk',
        'Slovenian': 'sl',
        'Spanish': 'es',
        'Spanish & English bilingual': 'es (with domain=\'bilingual-en\')',
        'Swedish': 'sv',
        'Tamil': 'ta',
        'Thai': 'th',
        'Turkish': 'tr',
        'Uyghur': 'ug',
        'Urdu': 'ur',
        'Ukrainian': 'uk',
        'Vietnamese': 'vi',
        'Welsh': 'cy'
    }
    return LANGUAGES_DICT

#endregion ============   Language Helper Functions   =================



#region ===============   Join Meeting Helper Functions   =================

def generate_unique_link(length=10):
    characters = string.ascii_letters + string.digits
    unique_link = ''.join(secrets.choice(characters) for _ in range(length))
    return unique_link


def get_token(request):
    app_id = config('AGORA_APP_ID')
    app_certificate = config('AGORA_APP_Certificate')
    channel_name = request.GET.get('channel')
    uid = random.randint(1, 230)

    expiration_time_in_seconds = 3600 * 24  # Token valid for 24 hours
    current_timestamp = int(time.time())
    privilege_expired_ts = current_timestamp + expiration_time_in_seconds

    role = 1  # Role for the Agora SDK (1 = Publisher)

    token = RtcTokenBuilder.buildTokenWithUid(
        app_id, app_certificate, channel_name, uid, role, privilege_expired_ts
    )

    return JsonResponse({'token': token, 'uid': uid}, safe=False)

#endregion ============   Join Meeting Helper Functions   =================



#region ===============   Pricing   =================

def pricing(request):
    return render(request, 'pricing/pricing.html')

#endregion ============   Pricing   =================



#region ===============   Email Sending   =================

def send_mail_from_backend(title, message, receivers):
    try:
        send_mail(
            title,
            message,
            'settings.EMAIL_HOST_USER',
            receivers,
            fail_silently=False
        )
        return True
    except Exception as e:
        return False


def get_contact_message(request):
    message =  f'''
Dear SpeakEasy Admin,

You have received a new contact request through the ProctorVision website. Please find the details below:

Name: {request.POST['name']}

Email Address: {request.POST['email']}

Message:
{request.POST['message']}

Please review and respond to this inquiry at your earliest convenience.

Kind regards,
SpeakEasy Team
'''
    return message

#endregion ============   Email Sending   =================



#region ===============   Agora Helper Functions   =================

def get_member(request):
    uid = request.GET.get('UID')
    room_name = request.GET.get('room_name')

    member = RoomMember.objects.get(
        uid = uid,
        room_name = room_name,
    )

    name = member.name

    return JsonResponse({'name': member.name}, safe=False)


@csrf_exempt
def create_member(request):
    data = json.loads(request.body)

    member, created = RoomMember.objects.get_or_create(
        name = data['name'],
        uid = data['UID'],
        room_name = data['room_name'],
        lang = data['lang']
    )

    return JsonResponse({'name': data['name']}, safe=False)


@csrf_exempt
def delete_member(request):
    data = json.loads(request.body)

    try:
        member = RoomMember.objects.get(
            name = data['name'],
            uid = data['UID'],
            room_name = data['room_name'],
        )
        member.delete()
    except: pass

    return JsonResponse('Member Deleted Successfully', safe=False)

#endregion ============   Agora Helper Functions   =================



#region ===============   Live Transcription   =================

def save_and_convert_audio(audio_file, output_path):
    """
    Save uploaded audio and convert it to proper WAV format using ffmpeg.
    Returns the path to the converted file.
    """
    # First save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        for chunk in audio_file.chunks():
            temp_file.write(chunk)
        temp_input_path = temp_file.name
    
    try:
        # Convert to proper WAV format using ffmpeg
        cmd = [
            'ffmpeg',
            '-i', temp_input_path,  # Input file
            '-vn',  # Disable video if present
            '-acodec', 'pcm_s16le',  # Convert to PCM WAV
            '-ar', '16000',  # Set sample rate to 16kHz
            '-ac', '1',  # Convert to mono
            '-y',  # Overwrite output file if exists
            output_path
        ]
        
        # Run the conversion
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg conversion failed: {process.stderr.decode()}")
            
        return output_path
        
    except Exception as e:
        raise Exception(f"Audio conversion failed: {str(e)}")
        
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_input_path)
        except:
            pass


def upload_audio(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']

        save_directory = Path(settings.BASE_DIR) / 'static' / 'audio_files'
        save_directory.mkdir(parents=True, exist_ok=True)

        # Generate output path
        output_filename = f"{request.POST.get('room')}.wav"
        output_path = str(save_directory / output_filename)

        # Save and convert the audio file
        save_and_convert_audio(request.FILES['audio'], output_path)

        try:
            transcription_result = get_transcription(output_path)

            translated_text = translate_message(transcription_result, request.POST.get('language'))
            return JsonResponse({'message': translated_text})
        except Exception as e:
            return JsonResponse({
                'error': f'Transcription failed: {str(e)}'
            }, status=500)
    else:
        return JsonResponse({'error': 'No audio data found'}, status=400)

#endregion ============   Live Transcription   =================



#region ===============   Transcription Helper Functions   =================

def get_transcription(PATH_TO_FILE):
    try:
        with BatchClient(speechmatics_settings) as client:
            try:
                job_id = client.submit_job(
                    audio=PATH_TO_FILE,
                    transcription_config=conf,
                )

                transcript = client.wait_for_completion(job_id, transcription_format='txt')
                return transcript
            except HTTPStatusError as e:
                if e.response.status_code == 401:
                    print(e)
                    print('Invalid API key - Check your API_KEY at the top of the code!')
                elif e.response.status_code == 400:
                    print("This is the error I got.")
                    print(e.response.json()['error'])
                else:
                    raise e
    except Exception as e:
        print(f"Error during transcription: {str(e)}")


def translate_message(text, lang):
    try:
        translator = GoogleTranslator(source="auto", target=lang)
        translated_text = translator.translate(text)
        return translated_text
    except Exception:
        return text

#endregion ============   Transcription Helper Functions   =================



#region ===============   Generic   =================
#endregion ============   Generic   =================
