import uuid
from django.db import models

# Create User model.
class User(models.Model):
    userID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firstName = models.CharField(max_length=35)
    lastName = models.CharField(max_length=35)
    userName = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=25)
    language = models.CharField(max_length=45)
    dateOfBirth = models.DateField()
    signUpDate = models.DateField(auto_now_add=True)
    isVerified = models.BooleanField(default=False)

# Create Verification model
class Verification(models.Model):
    verificationID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    userID = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'user_verifications')
    verificationCode = models.UUIDField()
    verificationType = models.CharField(max_length=20)
    creationDate = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10)

# Create Friendship model
class Friendship(models.Model):
    friendshipID = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_friendships')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_friendships')

# Create Chatroom model
class Chatroom(models.Model):
    chatroomID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)   
    adminID = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_chatrooms')
    participantID = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participant_chatrooms')
    createdAt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10)

# Create Chat model
class Chat(models.Model):
    chatID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chatType = models.CharField(max_length=5)
    creatorID = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_chats')
    chatroomID = models.ForeignKey(Chatroom, on_delete=models.CASCADE, related_name='chatroom_chats')
    createdAT = models.DateTimeField(auto_now_add=True)
    originalVoiceMsg = models.BinaryField(null=True)
    originalTextMsg = models.TextField()
    translatedTextMsg = models.TextField()
    translatedVoiceMsg = models.BinaryField(null=True)


