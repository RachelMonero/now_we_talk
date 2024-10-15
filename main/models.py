import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, first_name, last_name, password, **extra_fields)
    
# Create User model.
class User(AbstractBaseUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='user_id')
    first_name = models.CharField(max_length=35, db_column='first_name')
    last_name = models.CharField(max_length=35, db_column='last_name')
    username = models.CharField(max_length=30, db_column='username')
    email = models.EmailField(unique=True, db_column='email')
    password = models.CharField(max_length=128, db_column='password')
    language = models.CharField(max_length=45, db_column='language')
    date_of_birth = models.DateField(db_column='date_of_birth')
    sign_up_date = models.DateField(auto_now_add=True, db_column='sign_up_date')
    is_verified = models.BooleanField(default=False, db_column='is_verified')
    

    USERNAME_FIELD='email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'date_of_birth', 'language']

    objects =CustomUserManager()

    def __str__(self):
        return self.email

# Create Verification model
class Verification(models.Model):
    verification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='verification_id')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'user_verifications', db_column='user_id')
    verification_code = models.UUIDField(db_column='verification_code')
    verification_type = models.CharField(max_length=20, db_column='verification_type')
    creation_date = models.DateField(auto_now_add=True, db_column='creation_date')
    status = models.CharField(max_length=10, db_column='status')

# Create Friendship model
class Friendship(models.Model):
    friendship_id = models.IntegerField(primary_key=True, db_column='friendship_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_friendships', db_column='user')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_friendships', db_column='friend')

# Create Chatroom model
class Chatroom(models.Model):
    chatroom_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='chatroom_id')   
    admin_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_chatrooms', db_column='admin_id')
    participant_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participant_chatrooms', db_column='participant_id')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    status = models.CharField(max_length=10, db_column='status')

# Create Chat model
class Chat(models.Model):
    chat_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='chat_id')
    chat_type = models.CharField(max_length=5, db_column='chat_type')
    creator_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_chats', db_column='creator_id')
    chatroom_id = models.ForeignKey(Chatroom, on_delete=models.CASCADE, related_name='chatroom_chats', db_column='chatroom_id')
    created_at_timestamp = models.DateTimeField(auto_now_add=True, db_column='created_at_timestamp')
    original_voice_msg = models.BinaryField(null=True, db_column='original_voice_msg')
    original_text_msg = models.TextField(db_column='original_text_msg')
    translated_text_msg = models.TextField(db_column='translated_text_msg')
    translated_voice_msg = models.BinaryField(null=True, db_column='translated_voice_msg')



