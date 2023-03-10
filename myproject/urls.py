from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from twitter.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('feed/', TweetListView.as_view(), name='feed'),
    path('<author>/tweets', UserTweetListView.as_view(), name='userfeed'),
    path('<author>/<int:pk>/', TweetDetailView.as_view(),name='detail'),
    path('register/', UserCreateView.as_view(),name='register'),
    path('<int:pk>/reply/', TweetCreateView.as_view(),name='create'),
    path('<int:pk>/like/',like, name='like'),
    path('<int:pk>/follow/',follow, name='follow'),
    path('<int:pk>/retweet/', retweet, name='retweet'),
    # path('profile/', UserDetailView.as_view(),name='profile'),
    path('login/', UserLoginView.as_view(),name='login'),
    path('new_message/', MessageCreateView.as_view(),name='new_message'),
    # path('messages/', MessageCreateView.as_view(),name='messages'),
    path('conversations/', ConversationListView.as_view(),name='conversations'),
    path('logout/', UserLogoutView.as_view(),name='logout'),
    path("password_change/", PasswordChangeView.as_view(), name="password_change"),
    path("password_change/done/",PasswordChangeDoneView.as_view(),name="password_change_done"),
    path("password_reset/", PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", PasswordResetDoneView.as_view(),name="password_reset_done"),
    path("reset/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/",PasswordResetCompleteView.as_view(template_name='twitter/password_reset_done.html'),name="password_reset_complete"),
]

if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)