import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from google.cloud import translate_v2 as translate
from google.cloud import speech
from google.cloud import texttospeech
import io
from django.shortcuts import get_object_or_404

from main.control import find_user_id
from main.interfaces import FriendshipManager
from main.models import Friendship, User, Chatroom

class EmailService:
# sending email service
   @staticmethod
   def email_service(receiver_email, subject, message):
    
    admin_email = "for.dev.practice@gmail.com"
    admin_password = "dqsr fqkb wuwp nxph"

    try:
        email_msg =MIMEMultipart()
        email_msg["From"] = admin_email
        email_msg["To"] = receiver_email
        email_msg["Subject"] = subject
        email_msg.attach(MIMEText(message,"plain"))
    
        server = smtplib.SMTP("smtp.gmail.com",587)
        server.starttls()
        server.login(admin_email, admin_password)
        server.sendmail(admin_email, receiver_email, email_msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")    

# service to convert language code to language
def language_code_coversion(language):
    
    match language:
        case "ar":
            return "Arabic"
        case "bg":
            return "Bulgarian"
        case "zh-CN":
            return "Chinese (PRC)"
        case "zh-TW":
            return "Chinese (Taiwan)"
        case "nl":
            return "Dutch"
        case "en":
            return "English"
        case "fil":
            return "Filipino"
        case "fr":
            return "French"
        case "de":
            return "German"
        case "el":
            return "Greek"
        case "iw":
            return "Hebrew"
        case "hi":
            return "Hindi"
        case "hu":
            return "Hungarian"
        case "id":
            return "Indonesian"
        case "it":
            return "Italian"
        case "ja":
            return "Japanese"
        case "ko":
            return "Korean"
        case "ms":
            return "Malay"
        case "no":
            return "Norwegian"
        case "pl":
            return "Polish"
        case "pt-BR":
            return "Portugese (Brazil)"
        case "pt-PT":
            return "Portuguese (Portugal)"
        case "ro":
            return "Romanian"
        case "ru":
            return "Russian"
        case "es":
            return "Spanish"
        case "sv":
            return "Swedish"
        case "th":
            return "Thai"
        case "tr":
            return "Turkish"
        case "uk":
            return "Ukrainian"
        case "vi":
            return "Vietnamese"



def verificate_user(email, verification_code):
    
     subject = "[ Now We Talk ] Verification Code"
     message = (f"Your verification Code is {verification_code}")
     EmailService.email_service(email, subject, message)


def search_friends_service(search_by, search_friend,user):

    match search_by:
        case "username":
            return User.objects.filter(username__icontains=search_friend).exclude(user_id=user)
        case "email":
            return User.objects.filter(email__icontains=search_friend).exclude(user_id=user)
        case "last_name":
            return User.objects.filter(last_name__icontains=search_friend).exclude(user_id=user)
        case "first_name":
            return User.objects.filter(first_name__icontains=search_friend).exclude(user_id=user)
        


class FriendshipManagerService(FriendshipManager):

    def add_friend(self, user, friend):
        user = get_object_or_404(User, user_id=user) 
        friend = get_object_or_404(User, user_id=friend)

        Friendship.objects.create(user=user, friend=friend)
        return super().add_friend(user,friend)
    
    def remove_friend(self, user, friend):
        user = get_object_or_404(User, user_id=user) 
        friend = get_object_or_404(User, user_id=friend)

        Friendship.objects.filter(user=user, friend=friend).delete()

        return super().remove_friend(user,friend)

    def get_friend_list(self,user):
        try:
           friendships= Friendship.objects.filter(user=user)
           friend_ids= []

           for friendship in friendships:
               friend=find_user_id(friendship.friend)
               print(f"Friendship: {friendship.friend}, {friend}")
               friend_ids.append(friend)

           friends = User.objects.filter(user_id__in=friend_ids)
           return list(friends)
                    
                    
        except Exception as e:
               print(f"An error occurred: {e}")  # for debugging
               return []

def get_chatroom_list(user):
        try:
           chatroomslist= Chatroom.objects.filter(admin_id=user) | Chatroom.objects.filter(participant_id=user)
           chatroom_ids= []

           for chatroom in chatroomslist:
               chatroom_ids.append(chatroom.chatroom_id)
               
           chatrooms=Chatroom.objects.filter(chatroom_id__in=chatroom_ids)
           return chatrooms
                    
                    
        except Exception as e:
               print(f"An error occurred: {e}")  # for debugging
               return []

def leave_chatroom_service(user, chatroom_id):
        user = get_object_or_404(User, user_id=user) 
        chatroom = get_object_or_404(Chatroom, chatroom_id=chatroom_id)

        if user == chatroom.admin_id:
            chatroom.delete()

        elif user == chatroom.participant_id:
            chatroom.participant_id = None
            chatroom.save()


        return 

# Google API
class GoogleCloudService:

    def __init__(self):
        # Initialize Google API clients
        self.translate_client = translate.Client()
        self.speech_client = speech.SpeechClient()
        self.tts_client = texttospeech.TextToSpeechClient()

    def detect_language(self, text):
        
        detection = self.translate_client.detect_language(text)
        language_code = detection['language']
        return language_code    

    def translate(self, text, language):
        try:
            result = self.translate_client.translate(text, target_language=language)
            if isinstance(result, list):  # If result is a list, get the first item
                translated_text = result[0]['translatedText']
            else:  # Otherwise, it may already be a dictionary
                translated_text = result['translatedText']
            
            return translated_text
        except Exception as e:
            print("Translation error:", e)
            return None
    def speech_to_text(self, audio,language):

        audio_content = speech.RecognitionAudio(content=audio)
        config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                language_code=language
            )
        try:
          # Send the audio data and configuration to the speech client
          response = self.speech_client.recognize(config=config, audio=audio_content)
        
          # Check if any results were returned
          if response.results:
            # Get the first alternative transcript from the first result
            text = response.results[0].alternatives[0].transcript
            
            # Detect language (if you have a function for this)
            detected_language = self.detect_language(text)
            
            # Print detected language for debugging
            print("Detected language:", detected_language)
            
            return text, detected_language
          else:
            # Handle case where no speech was detected
            print("No speech detected.")
            return None, None
        except Exception as e:
          # Handle any exceptions or errors
          print(f"Error during speech-to-text: {e}")
        return None, None
        
    def text_to_speech(self, text, language):
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(language_code=language, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL) 
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)
            response = self.tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
            return response.audio_content  # Binary audio content
        except Exception as e:
            print("Text-to-speech error:", e)
            return None
