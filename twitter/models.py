from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _
from django.core.validators import RegexValidator, URLValidator
from django.utils.deconstruct import deconstructible
from django.contrib.auth.base_user import BaseUserManager
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password

@deconstructible
class UsernameValidator(RegexValidator):
  regex = r'(?=[0-9a-z_]{4,})(?=^[a-z])'
  message = _("Enter a valid username. This value may contain only letters, "
              "numbers, and underscores")
  flags = 0

@deconstructible
class EmailValidator(RegexValidator):
  regex = r'(?=\w{2,}@[a-z]{2,}\.[a-z]{2,})(?=^[a-z])'
  message = _("Enter a valid email")
  flags = 0

@deconstructible
class PhoneValidator(RegexValidator):
  regex = r'^\d+$'
  message = _("Enter a valid phone number with country code without +")
  flags = 0

# user
class User(AbstractUser):
  username_validator = UsernameValidator()
  email_validator = EmailValidator()
  url_validator = URLValidator()
  phone_validator = PhoneValidator()

  username = models.CharField(_("username"),
                              max_length=15, unique=True,
                              help_text=_("Required. 15 characters or fewer. Letters, digits and _ only."),
                              validators=[username_validator],
                              error_messages={"unique": _("A user with that username already exists."), }, )

  email = models.EmailField(_('email'),
                            unique=True,
                            error_messages={"unique": _("A user with that email already exists."), },
                            validators=[email_validator], )

  phone = models.CharField(_("phone"),
                           max_length=20, unique=True, blank=True, null=True,
                           help_text=_("Full phone number with country code"),
                           validators=[username_validator],
                           error_messages={"unique": _("A user with that phone number already exists."), }, )

  name = models.CharField(max_length=50)
  link = models.CharField(max_length=50, blank=True, validators=[url_validator])
  userpic = models.ImageField(default='default.jpg', upload_to='userpics')
  background = models.ImageField(default='default.jpg', upload_to='backgrounds')
  is_verified = models.BooleanField(default=False)
  bio = models.TextField(max_length=160, blank=True)

  blocked = models.ManyToManyField('self', symmetrical=False, related_name='user_blocked')
  muted = models.ManyToManyField('self', symmetrical=False, related_name='user_muted')

  followers = models.ManyToManyField('self', symmetrical=False, related_name='user_followers')
  following = models.ManyToManyField('self', symmetrical=False, related_name='user_following')

  conversations = models.ManyToManyField('Conversation', symmetrical=False, related_name='user_conversations')
  tweets = models.ManyToManyField('Tweet', symmetrical=False, related_name='user_tweets')

  likes = models.ManyToManyField('Tweet', symmetrical=False, related_name='user_likes')
  bookmarks = models.ManyToManyField('Tweet', symmetrical=False, related_name='user_bookmarks')
  notifications = models.ManyToManyField('Notification', symmetrical=False, related_name='user_notifications')

  is_private = models.BooleanField(default=False)
  lists = models.ManyToManyField('TweetList', symmetrical=False, related_name='user_lists')

  def __str__(self):
    return f'{self.username}'

class UserManager(BaseUserManager):
  use_in_migrations = True

  def _create_user(self, username, email, password, **extra_fields):

    if not username:
      raise ValueError("username required")
    if not email:
      raise ValueError("email required")
    email = self.normalize_email(email)
    GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
    username = GlobalUserModel.normalize_username(username)
    user = self.model(username=username, email=email, **extra_fields)
    user.password = make_password(password)
    user.save(using=self._db)
    return user

  def create_user(self, username, email, password, **extra_fields):
    extra_fields.setdefault("is_staff", False)
    extra_fields.setdefault("is_superuser", False)
    return self._create_user(username, email, password, **extra_fields)

  def create_superuser(self, username, email, password, **extra_fields):
    extra_fields.setdefault("is_staff", True)
    extra_fields.setdefault("is_superuser", True)
    return self._create_user(username, email, password, **extra_fields)

# tweets
class Tweet(models.Model):
  author = models.ForeignKey(User, on_delete=models.CASCADE)
  text = models.TextField(max_length=280)
  when = models.DateTimeField(auto_now_add=True)  # first created. can edit tweets with twitter blue only
  replied_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name='replied')
  retweeted_from = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name='retweeted')

  pic1 = models.ImageField(upload_to='tweetpics', blank=True)
  pic2 = models.ImageField(upload_to='tweetpics', blank=True)
  pic3 = models.ImageField(upload_to='tweetpics', blank=True)
  pic4 = models.ImageField(upload_to='tweetpics', blank=True)

  likes = models.ManyToManyField(User, symmetrical=False, related_name='tweet_likes')
  retweets = models.ManyToManyField(User, symmetrical=False, related_name='tweet_retweets')
  replies = models.ManyToManyField('self', symmetrical=False, related_name='tweet_replies')

  views = models.IntegerField(default=0)
  is_pinned = models.BooleanField(default=False)

  def __str__(self):
    return f"{self.pk} {self.text} by {self.author} at {self.when}"

  def save(self, *args, **kwargs):
    '''DONT call save() on self.replied_to
    add() and create() doesnt require save()'''
    super().save(*args, **kwargs)
    self.author.tweets.add(self)
    #not sure if we need this, it's taken care of by reply()
    if self.replied_to:
      self.replied_to.replies.add(self)

class TweetList(models.Model):
  '''
  basically filtered feed. create list, add users. list might be pinned or not
  clicking on the same list a person is already in actually removes them from the list. bullshit
  you can get a person into a list but not follow them. might ignore this, such a minor detail

  def get_queryset(self):
  current_user=User.objects.get(username=self.request.user)
  users_in_list=List.objects.get(pk=).users.all()
  return Tweet.objects.filter(replied_to__isnull=True).filter(author__in=users_in_list.all())
  '''
  name = models.CharField(max_length=25)
  description = models.TextField(max_length=100, blank=True)
  # tweets = models.ManyToManyField(User, symmetrical=False, related_name='list_users')
  is_pinned = models.BooleanField(default=False)

class Message(models.Model):
  # cant be null. probably better to set to 'deleted account' on delete
  sender = models.ForeignKey(User, on_delete=models.SET, related_name='message_sender')
  receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_receiver')
  #forwarded from deleted message like in telegram.
  #apparently you cannot forward messages in twitter at al, so
  forwarded_from=models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='forwarded')
  attached_tweet=models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True, related_name='msg_attached_tweet')
  text = models.TextField()
  when = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"from {self.sender} to {self.receiver} {self.text}"
  #message fk to convo? not sure if we need, we wont really manage individual messages
  #message.conversation - not really see where it might be useful

  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    try:
      existing_convo = self.sender.conversations.all().get(participants__in=[self.receiver])
      existing_convo.messages.add(self)
    except ObjectDoesNotExist:
      #requires at least 1 convo already there
      next_available_pk = (Conversation.objects.last().pk + 1)
      new_convo=Conversation.objects.create(pk=next_available_pk)
      new_convo.participants.add(self.sender,self.receiver)
      self.sender.conversations.add(new_convo)
      self.receiver.conversations.add(new_convo)
      new_convo.messages.add(self)

class Conversation(models.Model):
  #possibly can be notifications on for user and reflect on convo with him
  is_pinned = models.BooleanField(default=False)
  messages = models.ManyToManyField(Message, symmetrical=False, related_name='convo_messages')
  participants = models.ManyToManyField(User, symmetrical=False, related_name='convo_participants')

  def __str__(self):
    return f"convo between {self.participants.all()}"

  def save(self, *args, **kwargs):
    if self.participants.count()>2:
      raise ValueError
    super().save(*args, **kwargs)

  def get_participants(self):
    '''displays participants in admin as 1 string'''
    return " ".join([str(x) for x in self.participants.all().only("username")])

class Reaction(models.Model):
  emoji = models.CharField(max_length=6)
  message = models.ForeignKey(User, on_delete=models.SET, related_name='reaction_message')

class Notification(models.Model):
  NOTIFICATION_CHOICES=[('like','like'),('reply', 'reply'),('retweet', 'retweet'),('follow', 'follow'),('follow_request', 'follow_request')]

  sender = models.ForeignKey(User, on_delete=models.SET, related_name='notification_sender')
  receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_receiver')
  type = models.CharField(max_length=20, choices=NOTIFICATION_CHOICES)

  def __str__(self):
    return f"{self.type} from {self.sender} to {self.receiver}"

  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    self.sender.notifications.add(self)
    self.receiver.notifications.add(self)





