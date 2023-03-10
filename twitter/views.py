from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.views.generic import ListView,DetailView,CreateView
from django.urls import reverse
from .admin import UserCreationForm, UserAuthenticationForm
from django.contrib.auth.views import *
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect

from .models import *

class TweetListView(ListView):
  # feed for currently logged in user. no replies
  context_object_name = "tweets"
  model = Tweet

  # #tweets by only currently logged in user
  # def get_queryset(self):
  #     return Tweet.objects.filter(author=self.request.user)

  def get_queryset(self):
    # get current user
    current_user = User.objects.get(username=self.request.user)
    return Tweet.objects.filter(replied_to__isnull=True).filter(author__in=current_user.following.all())

class UserTweetListView(ListView):
  # need pagination here
  # profile page, user data and feed, follow/unfollow

  model = Tweet
  context_object_name = "tweets"
  template_name = "twitter/user_tweet_list.html"

  # works

  def get_queryset(self):
    user = get_object_or_404(User, username=self.kwargs['author'])
    return Tweet.objects.filter(author=user)

class TweetDetailView(DetailView):
  # single tweet, replies and Reply form
  model = Tweet
  context_object_name = "tweet"

class TweetCreateView(LoginRequiredMixin, CreateView):
  model = Tweet
  context_object_name = "tweet"
  fields = ["text", "pic1"]

  def get_success_url(self):
    return reverse('feed')

  def form_valid(self, form):
    form.instance.author = self.request.user
    return super().form_valid(form)

class MessageCreateView(LoginRequiredMixin, CreateView):
  model = Message
  context_object_name = "message"
  fields = ["sender", "receiver","text"]

  def get_success_url(self):
    return reverse('feed')

  def form_valid(self, form):
    form.instance.author = self.request.user
    return super().form_valid(form)

class ConversationListView(ListView):
  context_object_name = "conversations"
  model = Conversation

  # #tweets by only currently logged in user
  # def get_queryset(self):
  #     return Tweet.objects.filter(author=self.request.user)

  def get_queryset(self):
    # get current user
    return User.objects.get(username=self.request.user).conversations.all()


#user
class UserLoginView(LoginView):
  form_class = UserAuthenticationForm
  template_name = "twitter/login.html"

class UserLogoutView(LogoutView):
  form_class = UserAuthenticationForm
  template_name = "twitter/logout.html"

class UserCreateView(CreateView):
  model = User
  form_class = UserCreationForm

  def get_success_url(self):
    return reverse('feed')


# toggles
def follow(request, pk):
  user = User.objects.get(pk=request.POST.get('user_pk'))
  request.user.following.add(user)
  user.followers.add(request.user)
  return HttpResponseRedirect(request.META['HTTP_REFERER'])

def unfollow(request, pk):
  user = User.objects.get(pk=request.POST.get('user_pk'))
  request.user.following.remove(user)
  user.followers.remove(request.user)
  return HttpResponseRedirect(request.META['HTTP_REFERER'])

def like(request, pk):
  # even tho pk arg is not used, it IS used - we pass it from template
  tweet = Tweet.objects.get(pk=request.POST.get('tweet_pk'))
  tweet.likes.add(request.user)
  return HttpResponseRedirect(request.META['HTTP_REFERER'])

def dislike(request, pk):
  # even tho pk arg is not used, it IS used - we pass it from template
  tweet = Tweet.objects.get(pk=request.POST.get('tweet_pk'))
  tweet.likes.remove(request.user)
  return HttpResponseRedirect(request.META['HTTP_REFERER'])

# def retweet(request,pk):
#     tweet=Tweet.objects.get(pk=request.POST.get('tweet_pk'))
#     tweet.retweets.add(request.user)
#     tweet.pk=None
#     tweet.author=request.user
#     tweet.save()
#     return HttpResponseRedirect(request.META['HTTP_REFERER'])

def retweet(request, pk):
  tweet = Tweet.objects.get(pk=request.POST.get('tweet_pk'))
  tweet.retweets.add(request.user)
  new_tweet = Tweet.objects.create(author=request.user, replied_to=None, text=tweet.text, views=tweet.views, retweeted_from=tweet)
  new_tweet.replies.add(*tweet.replies.all())
  new_tweet.likes.add(*tweet.likes.all())
  new_tweet.retweets.add(*tweet.retweets.all())
  new_tweet.retweets.add(*tweet.bookmarks.all())
  return HttpResponseRedirect(request.META['HTTP_REFERER'])

def unretweet(request, pk):
  tweet = Tweet.objects.get(pk=request.POST.get('tweet_pk'))
  tweet.retweets.remove(request.user)
  #unclear how to grab that tweet and delete it
  return HttpResponseRedirect(request.META['HTTP_REFERER'])