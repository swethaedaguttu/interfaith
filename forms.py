from django import forms
from django.contrib.auth.models import User  # Import User model
from django.contrib.auth.forms import UserCreationForm 

from .models import (
    Community, Event, UnifiedNight, Activity, Partnership, SupportRequest,
    Resource, Notification, Feedback, UserProfile, Poll, ConnectionRequest,
    DiscussionThread, Comment, ResourceRequest, VolunteerHistory, Thread, Comment,

)



class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['name', 'description', 'created_by']

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'community', 'title', 'date', 'location', 'description',
            'organizer', 'max_participants', 'rsvp_deadline'
        ]

class UserRegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords must match.')

        return cleaned_data

class PartnershipForm(forms.ModelForm):
    class Meta:
        model = Partnership
        fields = ['community', 'partner_name', 'partnership_date', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'partnership_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(PartnershipForm, self).__init__(*args, **kwargs)
        self.fields['partner_name'].widget.attrs.update({'placeholder': 'Enter partner name'})
        self.fields['description'].widget.attrs.update({'placeholder': 'Enter description'})

class SupportForm(forms.ModelForm):
    class Meta:
        model = SupportRequest
        fields = ['community', 'user_name', 'request_details']
        widgets = {
            'request_details': forms.Textarea(attrs={'rows': 4}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['community', 'user_name', 'feedback_text']
        widgets = {
            'feedback_text': forms.Textarea(attrs={'rows': 4}),
        }

class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['question', 'options']
        widgets = {
            'options': forms.Textarea(attrs={'placeholder': 'Enter options as JSON, e.g. ["Option 1", "Option 2"]'}),
        }

    def clean_options(self):
        options = self.cleaned_data['options']
        try:
            import json
            options = json.loads(options)
        except json.JSONDecodeError:
            raise forms.ValidationError("Options must be valid JSON.")
        return options

class ConnectionRequestForm(forms.ModelForm):
    class Meta:
        model = ConnectionRequest
        fields = ['receiver']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # Get the current user
        super().__init__(*args, **kwargs)
        self.fields['receiver'].queryset = User.objects.exclude(id=user.id)  # Exclude the current user from the receiver options

    def clean_receiver(self):
        receiver = self.cleaned_data['receiver']
        if receiver == self.instance.sender:
            raise forms.ValidationError("You cannot send a connection request to yourself.")
        return receiver

class ProfileEditForm(forms.ModelForm):  # This should be correct
    class Meta:
        model = UserProfile
        fields = ['location', 'faith_background', 'interests', 'social_links']

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture.size > 5 * 1024 * 1024:  # Limit size to 5 MB
            raise forms.ValidationError("Image file too large ( > 5 MB )")
        return profile_picture

class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

class NotificationPreferencesForm(forms.ModelForm):
    email_notifications = forms.BooleanField(required=False, label="Receive email notifications")
    sms_notifications = forms.BooleanField(required=False, label="Receive SMS notifications")
    push_notifications = forms.BooleanField(required=False, label="Receive push notifications")

    class Meta:
        model = UserProfile  # Specify the correct model
        fields = ['email_notifications', 'sms_notifications', 'push_notifications']

    def save(self, user):
        user.profile.email_notifications = self.cleaned_data['email_notifications']
        user.profile.sms_notifications = self.cleaned_data['sms_notifications']
        user.profile.push_notifications = self.cleaned_data['push_notifications']
        user.profile.save()

class CommunityProfileForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['name', 'description', 'contact_email', 'contact_phone', 'location', 'worship_house_name',
                  'map_location', 'members', 'suggest_members', 'worship_details', 'community_type',
                  'profile_image', 'facebook_link', 'twitter_link', 'instagram_link', 'is_interfaith']

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title', 'content']  # Fields to include in the form
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter thread title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your message here...', 'rows': 5}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']  # Field to include in the comment form
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Add a comment...', 'rows': 3}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'profile_picture']  # Include fields you want to update
