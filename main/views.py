from datetime import datetime
import email
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.contrib import messages
from main.models import Chatroom, User
from .control import exist_email, exist_username, find_exist_chatroom, find_friend_list, find_user_id, is_verified_user, login_info, valid_date_of_birth, valid_password,  matching_info, valid_verification_code


def login(request):
    if request.method=="POST":
        email = request.POST.get('login-email')
        password = request.POST.get('password')

        if not email or not password:
              messages.error(request, "Please fill out all fields.")
        elif not exist_email:
              messages.error(request, "Invalid email.") 
        elif not login_info(email, password):
              messages.error(request, "Incorrect email or password.")
        else:  
              request.session['email'] = email
              
              if not is_verified_user(email):
                    messages.error(request, "Verification is required.")                   
                    return redirect('verification') 
              else:      
                    return redirect('home')               
    return render(request, 'main/login.html') 

def signup(request):
    if request.method=="POST":
        username = request.POST.get('username')
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        email = request.POST.get('email')
        password = request.POST.get('password')
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
              messages.error(request, "Password must be at least 8 characters.")
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

            messages.success(request, f"Verification Code has been sent to {email}.")
            request.session['email'] = email
            return redirect('verification') 
 
    return render(request,'main/signup.html')

def verification(request):
    if request.method=="POST":
        verification_code = request.POST.get('verification_code')
        email = request.session.get('email')
        user_id = find_user_id(email)
        if valid_verification_code(user_id,verification_code):
              return redirect('login')
    return render(request,'main/verification.html')   

def pw_recovery(request):
    if request.method=="POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        
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
    user_id = find_user_id(email)

    print(email) # for debugging
    print(user_id)  # for debugging

    friendlist = find_friend_list(user_id)

    print(friendlist)  # for debugging

    context = {
         'friendslist': friendlist,
    }

    return render(request,'main/home.html',context) 

def create_chatroom(request, friend_user_id ):
     
        print(f"Friend user ID: {friend_user_id}") #debug

        email = request.session.get('email')   
        user_id = find_user_id(email) 

        user = get_object_or_404(User, user_id=user_id)
        friend= get_object_or_404(User, user_id=friend_user_id)

        print(f"user_id:'{user_id}', friend_id:'{friend_user_id}'") #debug

        exist_chatroom = find_exist_chatroom(user_id,friend_user_id)

        if exist_chatroom:
             chatroom_id = exist_chatroom
             print(f"chatroomID: '{chatroom_id}'")
             return redirect('home') # use chatroom_id to redirect to the chatroom. Need to create chatroom.html
        else :   
              
             chatroom = Chatroom.objects.create(
                 admin_id = user,
                 created_at = datetime.now(),
                 status='active',
                 participant_id = friend
             )

             print(f"chatroom: '{chatroom}' ") #debug
             chatroom_id= chatroom.chatroom_id
             print(f"chatroomID: '{chatroom_id}") #debug

             return redirect('home') # use chatroom_id to redirect to the chatroom. Need to create chatroom.html
        
        return render(request,'main/home.html')
  