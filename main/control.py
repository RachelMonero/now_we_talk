from datetime import datetime,date
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from main.models import Chatroom, Friendship, Verification, User


# check if username exists in db
def exist_username(username):
    if User.objects.filter(username=username).exists():
        return True
    return False

# check if email exists in db
def exist_email(email):
    if User.objects.filter(email=email).exists():
        return True
    return False

# check if username and email match with user information in db
def matching_info(username,email):
    if User.objects.filter(username=username,email=email).exists():
        return True
    return False

# check if login infomation is valid
def login_info(email, password):
    try: 
        user =  User.objects.get(email=email)
        print(f"user.password (hashed): {user.password}")
        if check_password(password, user.password):
          return True
    except User.DoesNotExist:
        print(user.password)
        return False
    
    
# check user verification status by email   
def is_verified_user(email):
    try:    
        user =  User.objects.get(email=email)
        return user.is_verified ==1
    except User.DoesNotExist:
        return False

# check if password length meet the required minimum length
def valid_password(password):
    if len(password)>=8:
        return True
    return False

# check validation of date of birth 
def valid_date_of_birth(date_of_birth):
    dof = datetime.strptime(date_of_birth, '%Y-%m-%d')
    if dof < datetime.now():
        return True
    return False

# get user_id by email
def find_user_id(email):
    try:
        user= User.objects.get(email=email)
        return user.user_id
    except User.DoesNotExist:
        return None

# check existing verification code
def exist_verification_code(user_id):
    print(f"exist_verification_code function:{user_id}")
    if Verification.objects.filter(user_id=user_id).exists():
        return True
    return False

# check validation of verification code
def valid_verification_code(user_id,verification_code):
    if Verification.objects.filter(user_id=user_id, verification_code=verification_code).exists():
        return True
    return False



def find_exist_chatroom(user_id,friend_user_id):
    print(f"find_exist_chatroom function:{user_id}, {friend_user_id}")

    try:
           chatroom = Chatroom.objects.get(admin_id=user_id, participant_id =friend_user_id)
           return chatroom.chatroom_id
        
    except Chatroom.DoesNotExist:

        try: 
            chatroom=Chatroom.objects.get(admin_id=friend_user_id, participant_id= user_id)
            return chatroom.chatroom_id
        
        except Chatroom.DoesNotExist:

               return None