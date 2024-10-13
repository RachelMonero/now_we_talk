from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from main.models import Chatroom, Friendship, Verification, User

def exist_username(username):
    if User.objects.filter(username=username).exists():
        return True
    return False

def exist_email(email):
    if User.objects.filter(email=email).exists():
        return True
    return False

def matching_info(username,email):
    if User.objects.filter(username=username,email=email).exists():
        return True
    return False

def login_info(email, password):
    try: 
        user =  User.objects.get(email=email)
        return check_password(password, user.password)
    except User.DoesNotExist:
        return False
    
def is_verified_user(email):
    try:    
        user =  User.objects.get(email=email)
        return user.is_verified ==1
    except User.DoesNotExist:
        return False

def valid_password(password):
    if len(password)>=8:
        return True
    return False

def valid_date_of_birth(date_of_birth):
    dof = datetime.strptime(date_of_birth, '%Y-%m-%d')
    if dof < datetime.now():
        return True
    return False

def find_user_id(email):
    try:
        user= User.objects.get(email=email)
        return user.user_id
    except User.DoesNotExist:
        return None

def valid_verification_code(email,verification_code):
    if Verification.objects.filter(email=email, verification_code=verification_code).exists():
        return True
    return False

def find_friend_list(user_id):
    try:
        friendships= Friendship.objects.filter(user=user_id)
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
    
def find_exist_chatroom(user_id, friend_user_id):
    try: 
        chatroom = Chatroom.objects.get(admin_id=user_id, participant_id=friend_user_id)
        return chatroom.chatroom_id
    except Chatroom.DoesNotExist:
        return None