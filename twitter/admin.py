from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm, UserChangeForm as BaseUserChangeForm, AuthenticationForm, UsernameField
from django.utils.text import capfirst
from .models import *

from django.contrib.auth.models import Group

UserModel = get_user_model()

#-------------------------------USER FORMS--------------------------------

class UserCreationForm(BaseUserCreationForm):
  # removed help text, added fields
  password1 = forms.CharField(label=_("Password"), strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}), )

  password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}), strip=False, )

  class Meta:
    model = User
    fields = ("username", "email", "name", "password1", "password2", "bio", "userpic")
    field_classes = {"username": UsernameField}


class UserChangeForm(BaseUserChangeForm):
  class Meta:
    model = User
    fields = ("username", "email", "name", "password", "bio", "userpic")


class UserAuthenticationForm(AuthenticationForm):

  def __init__(self, request=None, *args, **kwargs):
    """
    The 'request' parameter is set for custom auth use by subclasses.
    The form data comes in via the standard 'data' kwarg.
    """
    self.request = request
    self.user_cache = None
    super().__init__(*args, **kwargs)

    # Set the max length and label for the "username" field.
    self.username_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
    username_max_length = 100
    self.fields["username"].max_length = username_max_length
    self.fields["username"].widget.attrs["maxlength"] = username_max_length
    if self.fields["username"].label is None:
      self.fields["username"].label = capfirst(self.username_field.verbose_name)

#-------------------------------MODEL FORMS--------------------------------
class TweetCreateForm(forms.ModelForm):
  class Meta:
    model = Tweet
    fields = ("text", "pic1")


class MessageCreateForm(forms.ModelForm):
  class Meta:
    model = Message
    fields = ("text",)


class ProfileChangeForm(forms.ModelForm):
  password1 = forms.CharField(label=_("Password"), strip=False, required=False, widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}), )

  password2 = forms.CharField(label=_("Password confirmation"), required=False, widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}), strip=False, )

  class Meta:
    model = User
    fields = ("username", "email", "password1", "password2", "name", "bio", "userpic",)

#-------------------------ADMIN MODEL SETTINGS---------------------------

class UserAdmin(BaseUserAdmin):
  # UserAdmin inherits from admin.ModelAdmin and contains a lof of its own shit.
  # extend UserAdmin, not ModelAdmin. Use import as to avoid name clashes
  form = UserChangeForm
  add_form = UserCreationForm

  list_display = ["pk", "username", "name", "email", "is_verified", "is_private", "date_joined", "last_login"]
  readonly_fields = ["date_joined", "last_login"]

  fieldsets = \
    ((None, {"fields": ("username", "password", "is_verified","is_private")}),

    (_("Personal info"), {"fields": ("name", "email", "phone", "link", "userpic", "background", "date_joined", "last_login", "bio",)}),

    (_("Follow"), {"fields": ("followers", "following", "conversations", "tweets","likes","bookmarks","notifications"), },),)

  add_fieldsets = ((None, {"classes": ("wide",), "fields": ("username", "email", "password1", "password2"), },),)

  # later
  list_filter = ()


class TweetAdmin(admin.ModelAdmin):
  list_display = ["pk", "text", "author", "views"]


class ConversationAdmin(admin.ModelAdmin):
  list_display = ["pk", "get_participants"]
  fields = ["participants", "messages"]


class MessageAdmin(admin.ModelAdmin):
  list_display = ["pk", "text", "when"]
  fields = ["sender","receiver","text"]

class NotificationAdmin(admin.ModelAdmin):
  list_display = ["pk", "sender","receiver", "type"]
  fields = ["sender","receiver","type"]

admin.site.register(Tweet, TweetAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.unregister(Group)

# delete without confirmation
# def delete_selected(modeladmin, request, queryset):
#     queryset.delete()
#
# class SomeAdmin(admin.ModelAdmin):
#     actions = (delete_selected,)
