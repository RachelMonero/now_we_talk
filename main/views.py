from datetime import date, datetime
import io
import html
from pydub import AudioSegment
import speech_recognition as sr
import uuid, json
from django.utils.html import escape, format_html
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from main.models import Chat, Chatroom, User, Verification
from main.services import EmailService, FriendshipManagerService, GoogleCloudService, get_chatroom_list, language_code_coversion, leave_chatroom_service, search_friends_service, verificate_user
from .control import exist_email, exist_username, exist_verification_code, find_user_id, find_exist_chatroom, is_verified_user
from .control import login_info, valid_date_of_birth, valid_password,  matching_info, valid_verification_code
from main.factories import TextChatFactory, VoiceChatFactory


def login(request):
    if request.method=="POST":
        email = (request.POST.get('login-email')).strip()
        password = (request.POST.get('password')).strip()
        print(email)
        print(password)

        if not email or not password:
              messages.error(request, "Please fill out all fields.")
        elif not exist_email(email):
              messages.error(request, "Invalid email.") 
        elif not login_info(email, password):
              messages.error(request, "Incorrect email or password.")
        else: 
              user_id = find_user_id(email)
              request.session['email'] = email
              request.session['user_id'] = str(user_id)
                  
              if not is_verified_user(email):
                    messages.error(request, "Verification is required.")                   
                    return redirect('verification') 
              else:      
                    return redirect('home')               
    return render(request, 'main/login.html') 


def signup(request):
    if request.method=="POST":
        username = (request.POST.get('username')).strip()
        first_name = (request.POST.get('firstname')).strip()
        last_name = (request.POST.get('lastname')).strip()
        email = (request.POST.get('email')).strip()
        password = (request.POST.get('password')).strip()
        language =  request.POST.get('language')
        date_of_birth =  request.POST.get('birthdate')
        
        if not username or not first_name or not last_name or not email or not password or not language or not date_of_birth:                
            messages.error(request, "Please fill out all fields.")       
        elif exist_username(username):    
              messages.error(request, "Username is in use.")        
        elif exist_email(email):
              messages.error(request, "Email is in use.")
        elif not valid_password(password):
              messages.error(request, "Password must be at least 8 characters.")
        elif not valid_date_of_birth(date_of_birth):
              messages.error(request, "Invalid date of birth.")
        else:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                language=language,
                date_of_birth=date_of_birth             
            )
            user.is_verified = False
            user.save()

            user.user_id = find_user_id(email)
            verification_code = uuid.uuid4()
           
            verification_type = "email verification"
            verification= Verification.objects.create(
              user_id = user,
              verification_code=verification_code,
              verification_type = verification_type,
              creation_date = date.today(), 
              status = "sent"              
            )
            verification.save()

            verificate_user(email, verification_code)

            request.session['email'] = user.email
            request.session['user_id']= str(user.user_id)
            
            messages.success(request, f"Verification Code has been sent to {email}.")                       
            return redirect('verification') 
    return render(request,'main/signup.html')

def verification(request):
    if request.method=="POST":
  
        email = request.session.get('email')
        user_id= request.session.get('user_id')
        user = get_object_or_404(User, email=email)
        
        input_verification_code = request.POST.get('verification_code')
                
        if valid_verification_code(user_id,input_verification_code):
              verification=get_object_or_404(Verification, user_id=user_id)
              print(f"verification info is found: {verification}") #debug
              verification.status="verified"
              verification.save()
              user.is_verified= True
              user.save()

              verification.delete()
              return redirect('login')
    return render(request,'main/verification.html')   



def pw_recovery(request):
    if request.method=="POST":
        username = (request.POST.get('username')).strip()
        email = (request.POST.get('email')).strip()
        
        if  not username or not email:
            messages.error(request, "Please enter username and email.")
        elif not exist_username(username): 
                messages.error(request, f"{username} is not exist.")
        elif not exist_email(email):
                messages.error(request, f"{email} is not exist.")
        elif not matching_info(username,email):
                messages.error(request, "Username and email do not match.")
        else :  
                temp_password = str(uuid.uuid4())[:8]
                user = get_object_or_404(User, email=email)
                user.set_password(temp_password)
                user.save()

                receiver_email = email
                subject = "[Now We Talk] Temporary Password"
                message = f" Your temporary password has been set successfully.\n Temporary Password: {temp_password}"

                EmailService.email_service(receiver_email, subject, message)
                
                messages.success(request, f"Temporary password has been sent to {email} successfully.")
                return redirect('login')   
    return render(request,'main/pw_recovery.html')


    
def home(request):
    email = request.session.get('email')
    user_id = request.session.get('user_id')

    print(email) # for debugging
    print(user_id)  # for debugging



    friendlist = FriendshipManagerService().get_friend_list(user_id)

    print(friendlist)  # for debugging

    

    context = {
         'friendslist': friendlist,
         'user_id': user_id,
         'email': email,
    }
    return render(request,'main/home.html',context) 


def profile(request):
    email = request.session.get('email')
    user_id = request.session.get('user_id')
    user = get_object_or_404(User, email=email)
    
    username = user.username
    print(f"profile view_username:{username}")
    password = user.password
    first_name = user.first_name
    last_name = user.last_name
    date_of_birth = str(user.date_of_birth)
    language = user.language
    
    user_language= language_code_coversion(language)

    context = {
         'username' : username,
         'email' : email,
         
         'first_name' : first_name,
         'last_name' : last_name,
         'date_of_birth' : date_of_birth,
         'language' : user_language,
         'password' : password,  
     }  
    if request.method=="POST":
            
            verification_type = "update profile"
        
            if not exist_verification_code(user_id):
                            
                verification= Verification.objects.create(
                  user_id = user,
                  verification_code=str(uuid.uuid4()),
                  verification_type = verification_type,
                  creation_date = date.today(), 
                  status = "sent"              
                )
                verification.save()
                print(f"verification_code in exist_verification_code: {verification.verification_code}")  
                verificate_user(email, verification.verification_code)
                messages.error(request, "Your verification code for profile update has been sent to your email.") 
                return redirect('profile_update')
            else:
                 verification= get_object_or_404(Verification, user_id=user_id)
                 verificate_user(email, verification.verification_code)
                 messages.error(request, "Your verification code for profile update has been sent to your email.") 
                 return redirect('profile_update')

    return render(request, 'main/profile.html', context)


def profile_update(request):
    email = request.session.get('email')
    user_id = request.session.get('user_id')
    user = get_object_or_404(User, email=email)

   
    username = user.username
    print(f"profileupdate view_username:{username}")
    password = user.password
    first_name = user.first_name
    last_name = user.last_name
    date_of_birth = str(user.date_of_birth)
    language = user.language
    
    print(f"userid: {user_id}")

    user_language= language_code_coversion(language)

    context = {
         'user_id': user_id,
         'username' : username,
         'email' : email,
        
         'first_name' : first_name,
         'last_name' : last_name,
         'date_of_birth' : date_of_birth,
         'language' : user_language,
         'password' : password,  
     }
    
    if request.method=="POST":
         print(f"user_id in Post :{user_id}")
         
         update_password = (request.POST.get('update_password')).strip()
         update_first_name = (request.POST.get ('update_first_name')).strip()
         update_last_name = (request.POST.get ('update_last_name')).strip()
         update_language = request.POST.get ('language')
         verification_code = str(request.POST.get('profile_update_verification_code')).strip()


         if  not update_password and not update_first_name and not update_last_name and not update_language:
              messages.error(request, "No update has been made.") 
         else:

             if not verification_code:
                    messages.error(request, "Please enter a valid verification code.") 
             else:    
                    print(f"user_id in first if :{user_id}")
                    if valid_verification_code(user_id, verification_code):
                        verification = get_object_or_404(Verification, user_id=user_id)
        
                        if update_first_name:
                          user.first_name = update_first_name
                          user.save()
                        if update_last_name:
                          user.last_name = update_last_name 
                          user.save()
                        if update_language:
                          user.language = update_language
                          user.save()
                        if update_password:
                          user.set_password(update_password)
                          user.save()
             
                        verification.status = "verified"
                        verification.save()
                        messages.success(request, "Update has been made successfully.")
                        print("Update has been made.")
                        verification.delete()
                        return redirect('profile')

                    else:
                         messages.error(request, "Please enter valid verification code.") 
            

    return render(request, 'main/profile_update.html', context)

def contact(request):
    email = request.session.get('email')
    user_id = request.session.get('user_id')

    context = {

         'user_id': user_id,
         'email': email,
    }

    if request.method=="POST":
         
         user_info=f"User ID: {user_id} \n User Email: {email}"
         contact_from_name = request.POST.get('contact_from_name')
         contact_from_email = (request.POST.get('contact_from_email')).strip()
         contact_from_subject = (request.POST.get('contact_from_subject')).strip()
         contact_from_message = (request.POST.get('contact_from_message')).strip()

         if not contact_from_name or not contact_from_email or not contact_from_subject or not contact_from_message:
              messages.error(request, "Please fill out the contact form")
         else: 
              receiver_email = "for.dev.practice@gmail.com"   #admin email
              subject = contact_from_subject
              message =f" User Account Information: \n\n {user_info} \n Name: {contact_from_name} \n Email: {contact_from_email} \n\n\n {contact_from_message}" 
              
              try: 
                 EmailService.email_service(receiver_email, subject, message)
                 messages.success(request,"Your message has been sent. We will get back to you soon.")
                 return redirect('home')
              except Exception as e:
                   print(f"Failed to send email: {e}") 
                   messages.error(request,"Error, please try again.")

    return render(request,'main/contact.html',context) 

def friends(request):
        email = request.session.get('email')
        user_id = request.session.get('user_id')

        friendlist = FriendshipManagerService().get_friend_list(user_id)

        context = {
         'friendslist': friendlist,
         'user_id': user_id,
         'email': email,
        }
    
        return render(request,'main/friends.html',context) 

def search(request):
    email = request.session.get('email')
    user_id = request.session.get('user_id')

    if request.method=="POST":
                  
         search_by = request.POST.get('search_by')
         search_friend = request.POST.get('search_friend')

         if not search_by or not search_friend:
              messages.error(request,"Please select a search category and enter a search keyword.")
         else:
              search_results = search_friends_service(search_by, search_friend, user_id)  

              if not search_results:
                   messages.info(request,"No users matched your search.") 
              else: 
                   return render (request, 'main/search.html',{'search_results': search_results})  

    return render(request,'main/search.html') 

def add_to_myfriend(request, user_id):
     email = request.session.get('email')
     current_user_id = request.session.get('user_id')

     if request.method == "POST":
          user = current_user_id
          friend = user_id

          print(f"user:{user}")
          print(f"friend:{friend}")

          friendship_service = FriendshipManagerService()

          try:                
               friendship_service.add_friend(user, friend)

          except Exception as e:
               messages.error(request, f"Error, please try again.") 
               print(e)    
          return redirect('friends')
     
def open_chat(request, user_id):
          
    email = request.session.get('email')
    current_user_id = request.session.get('user_id')

    if request.method =="POST":

        user = current_user_id
        friend = user_id

        print(f"user:{user}")
        print(f"friend:{friend}")

# create interfaces for creating chatroom
        
        exist_chatroom = find_exist_chatroom(user,friend)
        print(f"exist chatroom: {exist_chatroom}")

        if not exist_chatroom:
            user_instance = get_object_or_404(User, user_id=user)
            friend_instance = get_object_or_404(User, user_id=friend)   
            print(f"user_again:{user_instance}")
            print(f"friend_again:{friend_instance}")

            chatroom=Chatroom.objects.create(
                admin_id=user_instance , 
                participant_id=friend_instance,
                created_at = datetime.now(), 
                status = "open"
                )
            chatroom.save()

            
            chatroom_id=chatroom.chatroom_id
            admin_id=chatroom.admin_id.user_id
            participant_id = chatroom.participant_id.user_id
            status = chatroom.status
            chatlist = None
            #chatlist = None

        else:
             
             chatroom = get_object_or_404(Chatroom, chatroom_id=exist_chatroom)
             chatroom_id = chatroom.chatroom_id
             admin_id = chatroom.admin_id.user_id
             participant_id = chatroom.participant_id.user_id
             status = chatroom.status

             print(f"admin_id:{admin_id}")
             print(f"participant_id:{participant_id}")
             print(f"chatroom:{chatroom} /n {chatroom.admin_id} /n {chatroom_id}" )  
             
             
             #Required function to check chat exist in chatroom

             try: 
                 chats= Chat.objects.filter(chatroom_id=chatroom_id).order_by('created_at_timestamp')
                 chatlist = chats if chats.exists() else None   
                 print(chatlist)             
                       
             except Exception as e:
                    messages.error(request, "Error retrieving chat list, please try again.")
                    print(e)
                    chatlist = None

        admin = get_object_or_404(User, user_id=admin_id) 
        participant=get_object_or_404(User, user_id=participant_id) 

        admin_username = admin.username
        admin_language = admin.language

        participant_username = participant.username
        participant_language = participant.language

        friendlist = FriendshipManagerService().get_friend_list(current_user_id)
        print(friendlist)
        if chatlist is not None:
            context = {
                       'chatroom_id': chatroom_id,
                       'admin_id' : admin_id,
                       'admin_username': admin_username,
                       'admin_language': admin_language,
                       'participant_id' : participant_id,
                       'participant_username':participant_username,
                       'participant_language':participant_language,
                       'status' : status,
                       'friendslist': friendlist,           
                       'chatlist': chatlist,
   
                      }
        else:
             
            context = {
                       'chatroom_id': chatroom_id,
                       'admin_id' : admin_id,
                       'admin_username': admin_username,
                       'admin_language': admin_language,
                       'participant_id' : participant_id,
                       'participant_username':participant_username,
                       'participant_language':participant_language,
                       'status' : status,
                       'friendslist': friendlist,           
   
                      }
        print(chatlist)  
        return render(request,'main/home.html',context) #render to home with context
        


    return render(request,'main/home.html', context) 

def get_voice(request, chat_id):
    try:
        chat = Chat.objects.get(chat_id=chat_id)
        if chat.original_voice_msg:
            response = HttpResponse(chat.original_voice_msg, content_type='audio/mpeg')
            response['Content-Disposition'] = 'inline; filename="voice_message.mp3"'
            return response
        else:
            return HttpResponse("No audio found", status=404)
    except Chat.DoesNotExist:
        return HttpResponse("Chat not found", status=404)

def get_audio(request, chat_id):
    try:
        chat = Chat.objects.get(chat_id=chat_id)
        if chat.translated_voice_msg:
            response = HttpResponse(chat.translated_voice_msg, content_type='audio/mpeg')
            response['Content-Disposition'] = 'inline; filename="voice_message.mp3"'
            return response
        else:
            return HttpResponse("No audio found", status=404)
    except Chat.DoesNotExist:
        return HttpResponse("Chat not found", status=404)
    


def chatroom(request):
     return render(request,'main/chatroom.html') 


def chatroom_list(request):
     
        email = request.session.get('email')
        current_user_id = request.session.get('user_id')

        print(email) # for debugging
        print(f"current_user_id:{current_user_id}")

        chatroomlist = get_chatroom_list(current_user_id)

        print(f"chatroom_list: {chatroomlist}")  # for debugging

        context = {
         'chatroomlist': chatroomlist,
         'current_user_id': current_user_id,
         'email': email,
        }
        return render(request,'main/chatroom_list.html', context) 



def delete_friend(request):
    email = request.session.get('email')
    current_user_id = request.session.get('user_id')
    print(f"current_user_id:{current_user_id}")


    if request.method == "POST":
        user = current_user_id
        friend = request.POST.get("delete_button")
        print(f"user:{user}")
        print (f"friend: {friend}")
        try:
            friendship_service = FriendshipManagerService()
            friendship_service.remove_friend(user, friend)

        except Exception as e:
               messages.error(request, f"Error, please try again.") 
               print(e)    
     
        return redirect('friends')
    
def leave_chatroom(request):
    email = request.session.get('email')
    current_user_id = request.session.get('user_id')
    print(f"current_user_id:{current_user_id}")


    if request.method == "POST":
        user = current_user_id
        chatroom = request.POST.get("leave_chatroom_id")

        # TO DO: required to find whether user is admin or not and if admin delete the chat, participant send message to admin that user has left the chatroom 
        try:
            
            leave_chatroom_service(user, chatroom)       
            return render(request,'main/chatroom_list.html') 


        except Exception as e:
               messages.error(request, f"Error, please try again.") 
               print(f"Error in leave_chatroom_service: {e}") 
     
        return redirect('chatroom_list')
    
def create_chat(request, chatroom_id):
          
    email = request.session.get('email')
    current_user_id = request.session.get('user_id')    

    if request.method == "POST":
      created_at_timestamp=datetime.now() 
      chat_type= (request.POST.get("chat_type")).strip()
      admin_id = (request.POST.get('admin_id')).strip()
      admin_language = (request.POST.get('admin_language')).strip()
      participant_id = (request.POST.get('participant_id')).strip()
      participant_language = (request.POST.get('participant_language')).strip()

      creator= User.objects.get(user_id=current_user_id)
      chat_with= participant_id if current_user_id == admin_id else participant_id
      chatroom = Chatroom.objects.get(chatroom_id=chatroom_id)

      user_language = participant_language if current_user_id == participant_language else admin_language
      target_language = participant_language if current_user_id == admin_id else admin_language

      factory = TextChatFactory() if chat_type == "text" else VoiceChatFactory()
      google_service = GoogleCloudService()

      recognizer = sr.Recognizer()


      match chat_type:
           
           case "voice":
                audio_file = request.FILES.get("voice_data")
                
                if not audio_file:
                        # Handle missing audio file error
                        return render(request, 'home.html', {'message': 'No audio file provided'})
                
                # Save the original audio (blob)
                audio_data = audio_file.read()  # Reads audio as binary for blob storage
                audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))  # Automatically detects the format
                wav_data = io.BytesIO()
                audio_segment.export(wav_data, format="wav")  # Export to WAV format
                wav_data.seek(0) 

                if wav_data.getbuffer().nbytes > 0:
                  print("WAV audio data successfully created. Size:", wav_data.getbuffer().nbytes, "bytes")
                else:
                  print("Failed to create WAV audio data.")


                original_voice_msg= wav_data.read()
                
                wav_data.seek(0)
                with sr.AudioFile(wav_data) as source:
                    audio_data = recognizer.record(source)                                
        
                # Convert audio to text using Speech-to-Text
                original_text_msg = google_service.speech_to_text(audio_data.get_wav_data(),user_language)
                if not original_text_msg:
                    return render(request, 'home.html', {'message': 'Speech-to-text conversion failed'})

                translated_text_msg = google_service.translate(original_text_msg, target_language)
                print("Translated Text:", translated_text_msg)
        
                translated_voice_msg = google_service.text_to_speech(translated_text_msg,target_language)
                translated_text_msg = html.unescape(translated_text_msg) 

                chat = factory.create_chat(
                    chat_type=chat_type,
                    creator_id=creator,
                    chatroom_id=chatroom,
                    created_at_timestamp=created_at_timestamp,
                    original_voice_msg=original_voice_msg,  
                    original_text_msg=original_text_msg,
                    translated_text_msg=translated_text_msg,
                    translated_voice_msg=translated_voice_msg,
                )
                chat.save()
 
           case "text":
                original_text_msg = (request.POST.get('text_chat')).strip() # required to be translated.
                 #translate it & save
                translated_text_msg = google_service.translate(original_text_msg, target_language)
                translated_text_msg = html.unescape(translated_text_msg) 
                print("Translated Text:", translated_text_msg)
        

                chat = factory.create_chat(
                    chat_type=chat_type,
                    creator_id=creator,
                    chatroom_id=chatroom,
                    created_at_timestamp=created_at_timestamp,
                    original_text_msg=original_text_msg,
                    translated_text_msg=translated_text_msg,
                )
                chat.save()

    # TO Do: redirection or rendering is required.
      try: 
                 chats= Chat.objects.filter(chatroom_id=chatroom_id).order_by('created_at_timestamp')
                 chatlist = chats if chats.exists() else None   
                 print(chatlist)             
                       
      except Exception as e:
                    messages.error(request, "Error retrieving chat list, please try again.")
                    print(e)
                    chatlist = None

      admin = get_object_or_404(User, user_id=admin_id) 
      participant=get_object_or_404(User, user_id=participant_id) 

      admin_username = admin.username
      admin_language = admin.language

      participant_username = participant.username
      participant_language = participant.language

      friendlist = FriendshipManagerService().get_friend_list(current_user_id)
      print(friendlist)
      if chatlist is not None:
            context = {
                       'chatroom_id': chatroom_id,
                       'admin_id' : admin_id,
                       'admin_username': admin_username,
                       'admin_language': admin_language,
                       'participant_id' : participant_id,
                       'participant_username':participant_username,
                       'participant_language':participant_language,
                     
                       'friendslist': friendlist,           
                       'chatlist': chatlist,
   
                      }
      else:
             
            context = {
                       'chatroom_id': chatroom_id,
                       'admin_id' : admin_id,
                       'admin_username': admin_username,
                       'admin_language': admin_language,
                       'participant_id' : participant_id,
                       'participant_username':participant_username,
                       'participant_language':participant_language,
                       
                       'friendslist': friendlist,           
   
                      }
    return render(request,'main/home.html',context) 
      
  
        
  


        
        
 
        





    

      


