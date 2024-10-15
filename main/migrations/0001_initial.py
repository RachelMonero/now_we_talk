# Generated by Django 5.1.2 on 2024-10-14 05:20

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('user_id', models.UUIDField(db_column='user_id', default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('first_name', models.CharField(db_column='first_name', max_length=35)),
                ('last_name', models.CharField(db_column='last_name', max_length=35)),
                ('username', models.CharField(db_column='username', max_length=30)),
                ('email', models.EmailField(db_column='email', max_length=254, unique=True)),
                ('password', models.CharField(db_column='password', max_length=128)),
                ('language', models.CharField(db_column='language', max_length=45)),
                ('date_of_birth', models.DateField(db_column='date_of_birth')),
                ('sign_up_date', models.DateField(auto_now_add=True, db_column='sign_up_date')),
                ('is_verified', models.BooleanField(db_column='is_verified', default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('friendship_id', models.IntegerField(db_column='friendship_id', primary_key=True, serialize=False)),
                ('friend', models.ForeignKey(db_column='friend', on_delete=django.db.models.deletion.CASCADE, related_name='friend_friendships', to='main.user')),
                ('user', models.ForeignKey(db_column='user', on_delete=django.db.models.deletion.CASCADE, related_name='user_friendships', to='main.user')),
            ],
        ),
        migrations.CreateModel(
            name='Chatroom',
            fields=[
                ('chatroom_id', models.UUIDField(db_column='chatroom_id', default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at')),
                ('status', models.CharField(db_column='status', max_length=10)),
                ('admin_id', models.ForeignKey(db_column='admin_id', on_delete=django.db.models.deletion.CASCADE, related_name='admin_chatrooms', to='main.user')),
                ('participant_id', models.ForeignKey(db_column='participant_id', on_delete=django.db.models.deletion.CASCADE, related_name='participant_chatrooms', to='main.user')),
            ],
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('chat_id', models.UUIDField(db_column='chat_id', default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('chat_type', models.CharField(db_column='chat_type', max_length=5)),
                ('created_at_timestamp', models.DateTimeField(auto_now_add=True, db_column='created_at_timestamp')),
                ('original_voice_msg', models.BinaryField(db_column='original_voice_msg', null=True)),
                ('original_text_msg', models.TextField(db_column='original_text_msg')),
                ('translated_text_msg', models.TextField(db_column='translated_text_msg')),
                ('translated_voice_msg', models.BinaryField(db_column='translated_voice_msg', null=True)),
                ('chatroom_id', models.ForeignKey(db_column='chatroom_id', on_delete=django.db.models.deletion.CASCADE, related_name='chatroom_chats', to='main.chatroom')),
                ('creator_id', models.ForeignKey(db_column='creator_id', on_delete=django.db.models.deletion.CASCADE, related_name='user_chats', to='main.user')),
            ],
        ),
        migrations.CreateModel(
            name='Verification',
            fields=[
                ('verification_id', models.UUIDField(db_column='verification_id', default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('verification_code', models.UUIDField(db_column='verification_code')),
                ('verification_type', models.CharField(db_column='verification_type', max_length=20)),
                ('creation_date', models.DateField(auto_now_add=True, db_column='creation_date')),
                ('status', models.CharField(db_column='status', max_length=10)),
                ('user_id', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, related_name='user_verifications', to='main.user')),
            ],
        ),
    ]
