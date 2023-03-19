from django.views.generic import CreateView,UpdateView
from django.urls import reverse
from .admin import *
from django.contrib.auth.views import *
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect
from django.contrib import messages as django_messages
from django.core.paginator import Paginator
import re
from django.utils import timezone

from .models import *

def clean_text(text):
  return re.sub(r'(\r\n){3,}',"\n\n", text)

@login_required
def feed(request):
  current_user=get_object_or_404(User,username=request.user)
  # current_user = User.objects.get(username=request.user)
  tweets=Tweet.objects.filter(replied_to__isnull=True).filter(author__in=current_user.following.all())
  paginator=Paginator(tweets,4)
  page_number=request.GET.get('page')
  page_obj=paginator.get_page(page_number)
  form = TweetCreateForm()
  #we can lump up user.tweets by al users we are following to avoid filtering all()
  return render(request,'twitter/feed.html',{'tweets':page_obj, 'form':form})

def base(request):
  # trends=Tweet.objects.filter(when__gt=timezone.now()-timezone.timedelta(days=1))
  trends=Tweet.objects.all().order_by('-when')[:5]
  return render(request,'twitter/base.html',{'trends':trends})

def userfeed(request,pk):
  form=MessageCreateForm()
  requested_user = User.objects.get(pk=pk)
  tweets=requested_user.tweets.all().filter(replied_to__isnull=True)
  paginator=Paginator(tweets,2)
  page_number=request.GET.get('page')
  page_obj=paginator.get_page(page_number)
  return render(request,'twitter/userfeed.html',{'requested_user':requested_user,'tweets':page_obj,'form':form})

def detail(request,author,pk):
  requested_tweet = Tweet.objects.get(pk=pk)
  requested_tweet.views+=1
  requested_tweet.save()
  form = TweetCreateForm()
  replies=requested_tweet.replies.all()
  paginator=Paginator(replies,1)
  page_number=request.GET.get('page')
  page_obj=paginator.get_page(page_number)
  return render(request,'twitter/detail.html',{'tweet':requested_tweet,'form':form,'tweets':page_obj})

def search(request,str):
  tweets=Tweet.objects.filter(text__icontains=str)
  return render(request, 'twitter/explore.html', {'tweets': tweets})

#----------------------------------REDIRECTS----------------------------
def reply(request,pk):
  replied_to_tweet=Tweet.objects.get(pk=pk)
  if request.method == 'POST':
    cleaned_text = clean_text(request.POST.get('text'))
    Tweet.objects.create(author=request.user,text=cleaned_text,replied_to=replied_to_tweet)
    django_messages.success(request,f'Your reply has been sent')
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
  else:
    form = TweetCreateForm()
    return render(request, 'twitter/detail.html', {'requested_tweet': replied_to_tweet, 'form': form})

def message(request,pk):
  receiver = User.objects.get(pk=pk)
  if request.method == 'POST':
    cleaned_text=clean_text(request.POST.get('text'))
    Message.objects.create(sender=request.user,receiver=receiver,text=cleaned_text)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
  else:
    form = MessageCreateForm()
    tweets = receiver.tweets.all().filter(replied_to__isnull=True)
    return render(request, 'twitter/userfeed.html', {'requested_user': receiver, 'tweets': tweets, 'form': form})

def tweet(request):
  if request.method == 'POST':
    cleaned_text = clean_text(request.POST.get('text'))
    Tweet.objects.create(author=request.user,text=cleaned_text)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
  else:
    current_user = User.objects.get(username=request.user)
    tweets = Tweet.objects.filter(replied_to__isnull=True).filter(author__in=current_user.following.all())
    form = TweetCreateForm()
    return render(request, 'twitter/feed.html', {'tweets': tweets, 'form': form})

def update_profile(request,pk):
  current_user = User.objects.get(pk=pk)
  if request.method == 'POST':
    form=ProfileChangeForm(request.POST,instance=request.user)
    if form.is_valid():
      form.save()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
  else:
    form = MessageCreateForm(instance=request.user)
    return render(request, 'twitter/profile.html', {'current_user': current_user, 'form': form})

#profile and my userfeed are 2 different things. and twitter doesnt do 1 separate page for profile update
@login_required
def profile(request,pk):
  current_user = User.objects.get(pk=pk)
  tweets=current_user.tweets.all().filter(replied_to__isnull=True)
  likes=current_user.likes.all()
  paginator_tweets=Paginator(tweets,2)
  paginator_likes = Paginator(likes, 2)

  page_number=request.GET.get('page')

  page_obj_tweets=paginator_tweets.get_page(page_number)
  page_obj_likes=paginator_likes.get_page(page_number)
  form=ProfileChangeForm(instance=request.user) #pre fill data
  return render(request,'twitter/profile.html',{'current_user':current_user,'form':form,'tweets':page_obj_tweets,'likes':page_obj_likes})

def conversations(request):
  conversations=request.user.conversations.all()
  paginator=Paginator(conversations,2)
  page_number=request.GET.get('page')
  page_obj=paginator.get_page(page_number)
  return render(request,'twitter/conversations.html',{'conversations':page_obj})

def one_conversation(request,pk):
  messages = Conversation.objects.get(pk=pk).messages.all()
  form = TweetCreateForm()
  paginator=Paginator(messages,2)
  page_number=request.GET.get('page')
  page_obj=paginator.get_page(page_number)
  return render(request,'twitter/messages.html',{'messages':page_obj,'form':form})

def bookmarks(request):
  tweets=request.user.bookmarks.all()
  paginator=Paginator(tweets,2)
  page_number=request.GET.get('page')
  page_obj=paginator.get_page(page_number)
  return render(request,'twitter/bookmarks.html',{'tweets':page_obj})

#pending next migration
def lists(request):
  pass
  lists=request.user.lists.all()
  return render(request,'twitter/bookmarks.html',{'lists':lists})

#-------------------------------------USER--------------------------------

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

class UserUpdateView(UpdateView):
  model = User
  form_class = UserChangeForm

  def get_success_url(self):
    return reverse('feed')



#---------------------------------TWEET ACTIONS-----------------------------
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


#confirmation pop up
def delete_tweet(request,pk):
  tweet = Tweet.objects.get(pk=request.POST.get('tweet_pk'))
  tweet.delete()
  return HttpResponseRedirect(request.META['HTTP_REFERER'])

def delete_message(request,pk):
  message = Message.objects.get(pk=request.POST.get('tweet_pk'))
  message.delete()
  return HttpResponseRedirect(request.META['HTTP_REFERER'])

def delete_conversation(request,pk):
  conversation = Conversation.objects.get(pk=request.POST.get('tweet_pk'))
  conversation.delete()
  return HttpResponseRedirect(request.META['HTTP_REFERER'])


def block(request, pk):
  user = User.objects.get(pk=request.POST.get('user_pk'))
  request.user.blocked.add(user)
  return HttpResponseRedirect(request.META['HTTP_REFERER'])

def unblock(request, pk):
  user = User.objects.get(pk=request.POST.get('user_pk'))
  request.user.blocked.remove(user)
  return HttpResponseRedirect(request.META['HTTP_REFERER'])


def mute(request, pk):
  user = User.objects.get(pk=request.POST.get('user_pk'))
  request.user.muted.add(user)
  return HttpResponseRedirect(request.META['HTTP_REFERER'])

def unmute(request, pk):
  user = User.objects.get(pk=request.POST.get('user_pk'))
  request.user.muted.remove(user)
  return HttpResponseRedirect(request.META['HTTP_REFERER'])


def bookmark(request, pk):
  tweet = Tweet.objects.get(pk=request.POST.get('tweet_pk'))
  request.user.bookmarks.add(tweet)
  return HttpResponseRedirect(request.META['HTTP_REFERER'])

def unbookmark(request, pk):
  tweet = Tweet.objects.get(pk=request.POST.get('tweet_pk'))
  request.user.bookmarks.remove(tweet)
  return HttpResponseRedirect(request.META['HTTP_REFERER'])


def retweet(request, pk):
  #we may be able to optimize it by calling get() on request.user.tweets instead of filtering through
  #ALL the tweets. but both filter() and get() are greedy, because get() errors when found >1 args
  #that means it actually checks everything which we are trying to avoid
  #find out if sql uses subscription to get the obj by pk, bc linear search is not possible here
  #views get copied automatically no problem
  tweet = Tweet.objects.get(pk=request.POST.get('tweet_pk'))
  tweet.retweets.add(request.user)
  new_tweet = Tweet.objects.create(author=request.user, replied_to=None, text=tweet.text, views=tweet.views, retweeted_from=tweet)

  new_tweet.likes.add(*tweet.likes.all())
  new_tweet.retweets.add(*tweet.retweets.all())
  new_tweet.replies.add(*tweet.replies.all())
  return HttpResponseRedirect(request.META['HTTP_REFERER'])

def unretweet(request, pk):
  #logic is, we wont even see this unless it is retweeted. it is filtered at render level
  # so either hide urls or build in checking if it alreay exists
  tweet = Tweet.objects.get(pk=request.POST.get('tweet_pk'))
  new_retweet=request.user.tweets.get(retweeted_from=tweet)
  tweet.retweets.remove(request.user)
  new_retweet.delete()
  return HttpResponseRedirect(request.META['HTTP_REFERER'])