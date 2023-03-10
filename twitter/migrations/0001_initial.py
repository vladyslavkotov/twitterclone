# Generated by Django 4.1.6 on 2023-03-08 22:20

from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import twitter.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 15 characters or fewer. Letters, digits and _ only.', max_length=15, unique=True, validators=[twitter.models.UsernameValidator()], verbose_name='username')),
                ('email', models.EmailField(error_messages={'unique': 'A user with that email already exists.'}, max_length=254, unique=True, validators=[twitter.models.EmailValidator()], verbose_name='email')),
                ('phone', models.CharField(blank=True, error_messages={'unique': 'A user with that phone number already exists.'}, help_text='Full phone number with country code', max_length=20, null=True, unique=True, validators=[twitter.models.UsernameValidator()], verbose_name='phone')),
                ('name', models.CharField(max_length=50)),
                ('link', models.CharField(blank=True, max_length=50, validators=[django.core.validators.URLValidator()])),
                ('userpic', models.ImageField(default='default.jpg', upload_to='userpics')),
                ('background', models.ImageField(default='default.jpg', upload_to='backgrounds')),
                ('is_verified', models.BooleanField(default=False)),
                ('bio', models.TextField(blank=True, max_length=160)),
                ('blocked', models.ManyToManyField(related_name='user_blocked', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=280)),
                ('when', models.DateTimeField(auto_now_add=True)),
                ('pic1', models.ImageField(blank=True, upload_to='tweetpics')),
                ('pic2', models.ImageField(blank=True, upload_to='tweetpics')),
                ('pic3', models.ImageField(blank=True, upload_to='tweetpics')),
                ('pic4', models.ImageField(blank=True, upload_to='tweetpics')),
                ('views', models.IntegerField(default=0)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('bookmarks', models.ManyToManyField(related_name='tweet_bookmarks', to=settings.AUTH_USER_MODEL)),
                ('likes', models.ManyToManyField(related_name='tweet_likes', to=settings.AUTH_USER_MODEL)),
                ('replied_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replied', to='twitter.tweet')),
                ('replies', models.ManyToManyField(related_name='tweet_replies', to='twitter.tweet')),
                ('retweeted_from', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='retweeted', to='twitter.tweet')),
                ('retweets', models.ManyToManyField(related_name='tweet_retweets', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TweetList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('is_pinned', models.BooleanField(default=False)),
                ('tweets', models.ManyToManyField(related_name='tweetlist', to='twitter.tweet')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('when', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_receiver', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_sender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_pinned', models.BooleanField(default=False)),
                ('messages', models.ManyToManyField(related_name='convo_messages', to='twitter.message')),
                ('participants', models.ManyToManyField(related_name='convo_participants', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='conversations',
            field=models.ManyToManyField(related_name='user_conversations', to='twitter.conversation'),
        ),
        migrations.AddField(
            model_name='user',
            name='followers',
            field=models.ManyToManyField(related_name='user_followers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='following',
            field=models.ManyToManyField(related_name='user_following', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='muted',
            field=models.ManyToManyField(related_name='user_muted', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
