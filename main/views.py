from datetime import date, datetime
import uuid, json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.contrib import messages
from main.models import Chatroom, User, Verification
from main.services import email_service, language_code_coversion
from .control import exist_email, exist_username, exist_verification_code, find_friend_list, find_user_id, is_verified_user
from .control import login_info, valid_date_of_birth, valid_password,  matching_info, valid_verification_code, verificate_user


def login(request):
    if request.method=="POST":
        email = (request.POST.get('login-email')).strip()
        password = (request.POST.get('password')).strip()

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
                messages.error(request, "Invalid username.")
        elif not exist_email(email):
                messages.error(request, "Invalid email.")
        elif not matching_info(username,email):
                messages.error(request, "Username and email do not match.")
        else :  
                messages.success(request, f"Temporary password has been sent to '{email}' successfully.")
                return redirect('login')   
    return render(request,'main/pw_recovery.html')


    
def home(request):
    email = request.session.get('email')
    user_id = request.session.get('user_id')

    print(email) # for debugging
    print(user_id)  # for debugging

    friendlist = find_friend_list(user_id)

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
    password = user.password
    first_name = user.first_name
    last_name = user.last_name
    date_of_birth = str(user.date_of_birth)
    language = user.language
    
    user_language= language_code_coversion(language)

    context = {

         'email' : email,
         'username' : username,
         'first_name' : first_name,
         'last_name' : last_name,
         'date_of_birth' : date_of_birth,
         'language' : user_language,
         'password' : password,  
     }  
    if request.method=="POST":
            
            verification_type = "update profile"
        
            if exist_verification_code(user_id)==False:
                            
                verification= Verification.objects.create(
                  user_id = user_id,
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
    password = user.password
    first_name = user.first_name
    last_name = user.last_name
    date_of_birth = str(user.date_of_birth)
    language = user.language
    
    print(f"userid: {user_id}")

    user_language= language_code_coversion(language)

    context = {
         'user_id': user_id,
         'email' : email,
         'username' : username,
         'first_name' : first_name,
         'last_name' : last_name,
         'date_of_birth' : date_of_birth,
         'language' : user_language,
         'password' : password,  
     }
    
    if request.method=="POST":
         print(f"user_id in Post :{user_id}")
         update_username = (request.POST.get('update_username')).strip()
         update_password = (request.POST.get('update_password')).strip()
         update_first_name = (request.POST.get ('update_first_name')).strip()
         update_last_name = (request.POST.get ('update_last_name')).strip()
         update_language = request.POST.get ('language')
         verification_code = str(request.POST.get('profile_update_verification_code')).strip()


         if not update_username and not update_password and not update_first_name and not update_last_name and not update_language and not verification_code:
              messages.error(request, "No update has been made.") 
         else:
             print(f"user_id in first if :{user_id}")
             if valid_verification_code(user_id, verification_code):
                 verification = get_object_or_404(Verification, user_id=user_id)
        
                 if update_username:
              
                    if exist_username(update_username):    
                       messages.error(request, "Username is in use.")             
                    else: 
                       user.username = update_username
                       user.save()
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
                       user.password =update_password
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
                 email_service(receiver_email, subject, message)
                 messages.success(request,"Your message has been sent. We will get back to you soon.")
                 return redirect('home')
              except Exception as e:
                   print(f"Failed to send email: {e}") 
                   messages.error(request,"Error, please try again.")

    return render(request,'main/contact.html',context) 