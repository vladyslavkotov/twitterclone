from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.views.generic import ListView,DetailView,CreateView
from django.urls import reverse
from .admin import UserCreationForm, UserAuthenticationForm
from django.contrib.auth.views import *
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect
from twitter.admin import TweetCreateForm

from .models import *

#tweet create form, author=current user
def feed(request):
  current_user = User.objects.get(username=request.user)
  tweets=Tweet.objects.filter(replied_to__isnull=True).filter(author__in=current_user.following.all())
  #we can lump up user.tweets by al users we are following to avoid filtering all()
  return render(request,'twitter/feed.html',{'tweets':tweets})

#no form. requires pagination
def userfeed(request,author):
  requested_user = User.objects.get(username=author)
  tweets=requested_user.tweets.all().filter(replied_to__isnull=True)
  #we can lump up user.tweets by al users we are following to avoid filtering all()
  return render(request,'twitter/userfeed.html',{'requested_user':requested_user,'tweets':tweets})

#requires pagination
def detail(request,author,pk):
  requested_tweet = Tweet.objects.get(pk=pk)
  form = TweetCreateForm()
  return render(request,'twitter/detail.html',{'requested_tweet':requested_tweet,'form':form})

#when we actually hit Reply. How we display form etc is outside the scope
def reply(request,pk):
  replied_to_tweet=Tweet.objects.get(pk=pk)
  if request.method == 'POST':
      Tweet.objects.create(author=request.user,text=request.POST.get('text'),replied_to=replied_to_tweet)
      return HttpResponseRedirect(request.META['HTTP_REFERER'])
  else:
    form = TweetCreateForm()
    return render(request, 'twitter/detail.html', {'requested_tweet': replied_to_tweet, 'form': form})

# class TweetCreateView(LoginRequiredMixin, CreateView):
#   model = Tweet
#   context_object_name = "tweet"
#   fields = ["text", "pic1"]
#
#   def get_success_url(self):
#     return reverse('feed')
#
#   def form_valid(self, form):
#     form.instance.author = self.request.user
#     return super().form_valid(form)

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


def follow(request, pk):
  user = User.objects.get(pk=request.POST.get('requested_user_pk'))
  request.user.following.add(user)
  user.followers.add(request.user)
  # return render(request,'twitter/follow.html',{'request':request,'requested_user':user,})
  return HttpResponseRedirect(request.META['HTTP_REFERER'])

def unfollow(request, pk):
  user = User.objects.get(pk=request.POST.get('requested_user_pk'))
  request.user.following.remove(user)
  user.followers.remove(request.user)
  # return render(request,'twitter/follow.html',{'request':request,'requested_user':user,})
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

#probably will redo
def bookmark(request, pk):
  tweet = Tweet.objects.get(pk=request.POST.get('tweet_pk'))
  tweet.bookmarks.add(request.user)
  return HttpResponseRedirect(request.META['HTTP_REFERER'])

def unbookmark(request, pk):
  tweet = Tweet.objects.get(pk=request.POST.get('tweet_pk'))
  tweet.bookmarks.remove(request.user)
  return HttpResponseRedirect(request.META['HTTP_REFERER'])

#possibly unfinished
def retweet(request, pk):
  #we may be able to optimize it by calling get() on request.user.tweets instead of filtering through
  #ALL the tweets. but both filter() and get() are greedy, because get() errors when found >1 args
  #that means it actually checks everything which we are trying to avoid
  #find out if sql uses subscription to get the obj by pk, bc linear search is not possible here
  tweet = Tweet.objects.get(pk=request.POST.get('tweet_pk'))
  tweet.retweets.add(request.user)
  new_tweet = Tweet.objects.create(author=request.user, replied_to=None, text=tweet.text, views=tweet.views, retweeted_from=tweet)

  new_tweet.likes.add(*tweet.likes.all())
  new_tweet.retweets.add(*tweet.retweets.all())
  new_tweet.replies.add(*tweet.replies.all())
  new_tweet.bookmarks.add(*tweet.bookmarks.all())
  #views?
  return HttpResponseRedirect(request.META['HTTP_REFERER'])

def unretweet(request, pk):
  #logic is, we wont even see this unless it is retweeted. it is filtered at render level
  # so either hide urls or build in checking if it alreay exists
  tweet = Tweet.objects.get(pk=request.POST.get('tweet_pk'))
  new_retweet=request.user.tweets.get(retweeted_from=tweet)
  tweet.retweets.remove(request.user)
  new_retweet.delete()
  return HttpResponseRedirect(request.META['HTTP_REFERER'])