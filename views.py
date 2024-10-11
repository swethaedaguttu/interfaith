# events/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.management.base import BaseCommand
from .models import (
    Community,
    Event,
    UnifiedNight,
    Activity,
    Partnership,
    SupportRequest,
    Resource,
    Notification,
    Feedback,
    UserProfile,
    Poll,
    ConnectionRequest,
    DiscussionThread,
    Comment,
    ResourceRequest,
    VolunteerHistory,
    HelpRequest, 
    Thread, # Import your UserProfile model correctly
)

from .forms import CommunityForm, EventForm, UserRegistrationForm, PartnershipForm, SupportForm, FeedbackForm, PollForm, ConnectionRequestForm, ProfileUpdateForm, ProfileEditForm, NotificationPreferencesForm, ProfilePictureForm, CommunityProfileForm, ThreadForm
 # Import your forms
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required  # Import login_required
from features.models import Feature  # Import your Feature model
from django.contrib.auth.views import LoginView
from django.utils import timezone
from django.core.paginator import Paginator
from django_otp.decorators import otp_required
from django.conf import settings
from django.db import IntegrityError
from django.contrib.auth.models import User  # Import the User model
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.views import View
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
import logging

logger = logging.getLogger(__name__)


import openai  # Assuming OpenAI API is used for AI-powered features
import random

def send_otp(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code is: {otp}'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


def verify_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        username = request.session.get('username')

        if user_otp and stored_otp and int(user_otp) == int(stored_otp):
            # If OTP is valid, log the user in
            user = authenticate(request, username=username)
            if user:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                del request.session['otp']  # Remove OTP from session
                del request.session['username']  # Remove username from session
                return redirect('home')  # Redirect to home
            else:
                messages.error(request, 'Authentication failed.')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'events/verify_otp.html')


def home(request):
    communities = Community.objects.all()
    unified_nights = UnifiedNight.objects.all()
    events = Event.objects.all()
    features = Feature.objects.all()
    activities = Activity.objects.all()

    search_query = request.GET.get('search', '')
    if search_query:
        # Ensure you're filtering events using the correct field
        communities = communities.filter(name__icontains=search_query)
        events = events.filter(title__icontains=search_query)

    context = {
        'communities': communities,
        'unified_nights': unified_nights,
        'events': events,
        'features': features,
        'activities': activities,
        'search_query': search_query,  # Include the search query in the context
    }
    return render(request, 'events/home.html', context)

def index(request):
    query = request.GET.get('search', '')  # Default to empty string if not provided
    communities = Community.objects.all()
    events = Event.objects.all()

    if query:
        communities = communities.filter(name__icontains=query)  # Adjust the field name accordingly
        events = events.filter(title__icontains=query)  # Use the correct field for filtering

    context = {
        'communities': communities,
        'events': events,
        'search_query': query,  # Include the search query in the context
    }
    return render(request, 'events/index.html', context)  # Fixed the backslash to forward slash

# Authentication Views

# Custom login view
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'  # Your login template

    def get(self, request, *args, **kwargs):
        # Check if there is a message in the session to display
        message = request.GET.get('message')
        if message:
            messages.error(request, message)
        return super().get(request, *args, **kwargs)

# Registration view
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user
            UserProfile.objects.create(user=user)  # Create a user profile
            messages.success(request, 'Registration successful! You can log in now.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'events/register.html', {'form': form})
# Login view
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if both fields are filled
        if username and password:
            # Authenticate the user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:  # Check if user is active
                    login(request, user)

                    # Check if UserProfile exists
                    try:
                        user_profile = UserProfile.objects.get(user=user)
                    except UserProfile.DoesNotExist:
                        messages.error(request, 'Your profile does not exist. Please contact support.')
                        return redirect('home')

                    return redirect('home')  # Redirect to the home page after login
                else:
                    messages.error(request, 'Your account is inactive. Please contact support.')
            else:
                messages.error(request, 'Invalid username or password.')  # Handle invalid credentials
        else:
            messages.error(request, 'Please fill out both fields.')

    return render(request, 'events/login.html')  # No need to pass messages here

# Logout view
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

# Command to create UserProfiles for existing users
class Command(BaseCommand):
    help = 'Create UserProfiles for existing users'

    def handle(self, *args, **options):
        for user in User.objects.all():
            if not hasattr(user, 'userprofile'):
                UserProfile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f'Created UserProfile for {user.username}'))

# Community Views

def about_us(request):
    return render(request, 'events/about_us.html')  # Adjust the template name as necessary

def contact(request):
    return render(request, 'events/contact.html')  # Adjust the template name as necessary

def profile(request):
    return render(request, 'profile.html')  # Make sure this template exists

 # Ensure only logged-in users can create communities
def community_list_view(request):
    communities = Community.objects.all()
    return render(request, 'events/community_list.html', {'communities': communities})

 # Ensure only logged-in users can view community details
def community_details_view(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    events = Event.objects.filter(community=community)
    return render(request, 'events/community_details.html', {'community': community, 'events': events})

 # Ensure only logged-in users can create communities
def community_create_view(request):
    if request.method == 'POST':
        form = CommunityForm(request.POST)
        if form.is_valid():
            community = form.save(commit=False)
            community.created_by = request.user  # Assign the logged-in user
            community.save()
            messages.success(request, f'Community "{community.name}" created successfully!')
            return redirect('community_detail', community_id=community.id)
    else:
        form = CommunityForm()
    return render(request, 'events/community_form.html', {'form': form})

def create_community_profile(request):
    if request.method == 'POST':
        form = CommunityProfileForm(request.POST, request.FILES)
        if form.is_valid():
            community = form.save(commit=False)
            community.save()
            messages.success(request, f'Community profile for {community.name} has been created successfully.')
            return redirect('community_list')  # Redirect to the community list after saving
        else:
            messages.error(request, 'There was an error creating the community profile. Please try again.')
    else:
        form = CommunityProfileForm()

    # Fetch all communities for the dropdown list in the template
    communities = Community.objects.all()

    return render(request, 'events/community_form.html', {
        'form': form,
        'communities': communities,
    })

# Event Views

  # Ensure only logged-in users can view events
def event_list_view(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {'events': events})

  # Ensure only logged-in users can view event details
def event_details_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/event_details.html', {'event': event})

  # Ensure only logged-in users can create events
def event_create_view(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user  # Assign the logged-in user
            event.save()
            messages.success(request, f'Event "{event.title}" created successfully!')
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form})

def interfaith_networking(request):
    # Fetch communities involved in interfaith activities
    communities = Community.objects.filter(is_interfaith=True)  # Filter communities based on some criteria
    # Fetch upcoming events related to interfaith networking
    events = Event.objects.filter(type='interfaith').order_by('date')  # Assuming you have a 'type' field

    context = {
        'title': 'Interfaith Networking',
        'description': 'Connect with people from different religious backgrounds to share experiences and insights.',
        'communities': communities,
        'events': events,
    }
    
    return render(request, 'events/interfaith_networking.html', context)


def create_event_view(request):
    communities = Community.objects.all()  # Fetch all communities

    if request.method == 'POST':
        # Handle form submission with some validation checks
        try:
            title = request.POST['title']
            community_id = request.POST['community']
            location = request.POST['location']
            date = request.POST['date']
            description = request.POST['description']
            organizer = request.user.username  # Organizer is the logged-in user

            # Fetch selected community, raise 404 if not found
            community = Community.objects.get(id=community_id)

            # Convert the date string to datetime if necessary
            try:
                date = timezone.make_aware(timezone.datetime.strptime(date, '%Y-%m-%dT%H:%M'))
            except ValueError:
                messages.error(request, 'Invalid date format. Please try again.')
                return render(request, 'events/event_form.html', {'communities': communities})

            # Create the new event and save it
            event = Event(title=title, location=location, date=date, description=description, organizer=organizer, community=community)
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', event_id=event.id)

        except Community.DoesNotExist:
            messages.error(request, 'Community does not exist.')
            return render(request, 'events/event_form.html', {'communities': communities})

    return render(request, 'events/create_event.html', {'communities': communities})

def partnership_create_view(request):
    if request.method == 'POST':
        form = PartnershipForm(request.POST)
        if form.is_valid():
            partnership = form.save(commit=False)
            partnership.created_by = request.user  # Assign the logged-in user
            partnership.save()
            messages.success(request, 'Partnership created successfully!')
            return redirect('partnership_detail', partnership_id=partnership.id)
    else:
        form = PartnershipForm()
    return render(request, 'events/partnership_form.html', {'form': form})


def support_request_view(request):
    if request.method == 'POST':
        form = SupportForm(request.POST)
        if form.is_valid():
            support_request = form.save(commit=False)
            support_request.created_by = request.user  # Assign the logged-in user
            support_request.save()
            messages.success(request, 'Support request submitted successfully!')
            return redirect('support_request_detail', support_request_id=support_request.id)
    else:
        form = SupportForm()
    return render(request, 'events/support_request_form.html', {'form': form})


def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user  # Assign the logged-in user
            feedback.save()
            messages.success(request, 'Feedback submitted successfully!')
            return redirect('home')
    else:
        form = FeedbackForm()
    return render(request, 'events/feedback_form.html', {'form': form})


def community_delete_view(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    if request.method == 'POST':
        community.delete()
        messages.success(request, 'Community deleted successfully!')
        return redirect('community_list')  # Adjust the redirect as needed
    return render(request, 'events/community_confirm_delete.html', {'community': community})


def event_delete_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('event_list')  # Adjust the redirect as needed
    return render(request, 'events/event_confirm_delete.html', {'event': event})

def ai_response(prompt):
    try:
        openai.api_key = 'your_openai_api_key'  # Use environment variables for sensitive data
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except openai.error.OpenAIError as e:
        return "AI is currently unavailable. Please try again later."


def ai_chat_view(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        ai_reply = ai_response(user_input)
        return render(request, 'events/ai_chat.html', {'ai_reply': ai_reply, 'user_input': user_input})

    return render(request, 'events/ai_chat.html')

def feedback_list_view(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'events/feedback_list.html', {'feedbacks': feedbacks})

def notification_list_view(request):
    notifications = Notification.objects.filter(user=request.user)  # Adjust as per your notification model
    return render(request, 'events/notification_list.html', {'notifications': notifications})


def resources_view(request):
    resources = Resource.objects.all()
    return render(request, 'events/resources.html', {'resources': resources})

class OfferHelpView(View):
    def get(self, request):
        # Retrieve all previous help offers from the database

        return render(request, 'events/offer_help.html', {
        })

    def post(self, request):
        # Get form data
        user_name = request.POST.get('user_name', '').strip()
        category = request.POST.get('category', '').strip()
        description = request.POST.get('description', '').strip()

        # Validate form data
        if not user_name or not category or not description:
            messages.error(request, 'All fields are required.')
            return redirect('offer_help')  # Redirect back to the same page with an error

        # Save the new offer to the database
        OfferHelp.objects.create(user_name=user_name, category=category, description=description)

        # Show success message
        messages.success(request, 'Your help offer has been submitted successfully!')

        # Redirect to the same page after form submission
        return redirect('offer_help')
        
class RequestHelpView(View):
    def get(self, request):
        help_requests = HelpRequest.objects.all()  # Get all help requests
        help_requests_count = {
            'mental_health': HelpRequest.objects.filter(category='mental_health').count(),
            'food_assistance': HelpRequest.objects.filter(category='food_assistance').count(),
            'shelter_services': HelpRequest.objects.filter(category='shelter_services').count(),
            'educational_support': HelpRequest.objects.filter(category='educational_support').count(),
        }

        return render(request, 'events/request_help.html', {
            'help_requests': help_requests,
            'help_requests_count': help_requests_count,
        })

    def post(self, request):
        # Get form data
        category = request.POST.get('category', '').strip()
        description = request.POST.get('description', '').strip()
        user_name = request.POST.get('user_name', '').strip()

        # Validate the form data
        if not category or not description or not user_name:
            messages.error(request, 'All fields are required.')
            return redirect('request_help')  # Redirect to the same page to display the error

        # Process the form data and save to the database
        HelpRequest.objects.create(category=category, description=description, user_name=user_name)

        # Display success message
        messages.success(request, 'Your help request has been submitted successfully!')

        # Redirect to the same page after successful submission
        return redirect('request_help')

def update_status(request, request_id):
    help_request = get_object_or_404(HelpRequest, id=request_id)
    if request.method == "POST":
        help_request.status = not help_request.status  # Toggle the status
        help_request.save()
        messages.success(request, "Help request status updated.")
        return redirect('request_help')

    return render(request, 'update_status.html', {'help_request': help_request})

def view_request_details(request, request_id):
    help_request = get_object_or_404(HelpRequest, id=request_id)
    return render(request, 'request_details.html', {'help_request': help_request})

def request_help_view(request):
    # Get all help requests from the database
    help_requests = HelpRequest.objects.all()  # Adjust the queryset as necessary

    # Process any form submissions if necessary
    if request.method == 'POST':
        # Handle the POST request to create a new help request
        pass

    # Render the template with the help requests
    return render(request, 'request_help.html', {
        'help_requests': help_requests,
        'help_requests_count': help_requests.count(),  # Pass the total count
        'messages': get_messages(request),  # If you are using messages framework
    })

def delete_request_view(request, request_id):
    request_to_delete = get_object_or_404(HelpRequest, id=request_id)
    request_to_delete.delete()
    return redirect('request_help')  # Redirect to the request help page or another page after deletion

def edit_request_view(request, request_id):
    request_to_edit = get_object_or_404(HelpRequest, id=request_id)
    
    if request.method == 'POST':
        # Handle form submission and update logic here
        form = YourForm(request.POST, instance=request_to_edit)  # Replace YourForm with your actual form class
        if form.is_valid():
            form.save()
            return redirect('request_help')
    else:
        form = YourForm(instance=request_to_edit)

    return render(request, 'edit_request.html', {'form': form})  # Adjust template name accordingly

            
class OfferHelpCategoryView(View):
    template_name = 'events/offer_help_category.html'  # Use a common template for all categories

    def get(self, request, category):
        context = {
            'category': category,
        }
        return render(request, self.template_name, context)


class RequestHelpCategory1View(View):
    def get(self, request):
        return render(request, 'events/request_help_category_1.html')

class RequestHelpCategory2View(View):
    def get(self, request):
        return render(request, 'events/request_help_category_2.html')

class RequestHelpCategory3View(View):
    def get(self, request):
        return render(request, 'events/request_help_category_3.html')

class RequestHelpCategory4View(View):
    def get(self, request):
        return render(request, 'events/request_help_category_4.html')


def community_networking(request):
    # Retrieve all users in the community excluding the current user
    try:
        users = UserProfile.objects.exclude(user=request.user)
    except UserProfile.DoesNotExist:
        users = []  # Handle case if no UserProfiles are found

    # Retrieve all discussion threads
    threads = Thread.objects.all()  # Assuming you have a Thread model defined

    if request.method == "POST":
        # Handle connection request
        connection_request_form = ConnectionRequestForm(request.POST, user=request.user)  # Pass the user here
        if connection_request_form.is_valid():
            connection_request_form.save()
            return redirect('community_networking')

    # Instantiate form if request is not POST, also pass the user
    connection_request_form = ConnectionRequestForm(user=request.user)  # Pass the user here

    # Pass necessary context to the template
    context = {
        'users': users,
        'threads': threads,  # Add threads to the context
        'connection_request_form': connection_request_form,
    }

    return render(request, 'events/community_networking.html', context)

def search_users(request):
    if 'q' in request.GET:
        query = request.GET['q']
        users = UserProfile.objects.filter(user__username__icontains=query)
        return render(request, 'search_results.html', {'users': users})
    return JsonResponse([], safe=False)


def create_poll(request):
    if request.method == "POST":
        form = PollForm(request.POST)
        if form.is_valid():
            poll = form.save(commit=False)
            poll.creator = request.user
            poll.save()
            return redirect('community_networking')

    form = PollForm()
    return render(request, 'create_poll.html', {'form': form})


def respond_to_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    if request.method == "POST":
        # Handle poll response (e.g., saving the user's vote)
        response = request.POST.get('response')
        poll.votes.create(user=request.user, response=response)
        return redirect('community_networking')

    return render(request, 'respond_to_poll.html', {'poll': poll})


def send_connection_request(request, user_id):
    if request.method == "POST":
        user_to_connect = get_object_or_404(UserProfile, id=user_id)
        connection_request = ConnectionRequest(sender=request.user, receiver=user_to_connect.user)
        connection_request.save()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False}, status=400)

# View for the discussion forums page
def discussion_forums(request):
    threads = DiscussionThread.objects.all()
    return render(request, 'events/discussion_forums.html', {'threads': threads})

# View for creating a new discussion thread
def create_thread(request):
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.author = request.user  # Set the author to the current user
            thread.save()
            return redirect('view_thread', thread_id=thread.id)  # Redirect to the thread's detail page
    else:
        form = ThreadForm()
    return render(request, 'create_thread.html', {'form': form})

  # Ensure the user is logged in
def view_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    comments = thread.comments.all()  # Get all comments related to the thread

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.thread = thread  # Associate comment with the thread
            comment.author = request.user  # Set the author to the current user
            comment.save()
            return redirect('view_thread', thread_id=thread.id)  # Redirect to the thread's detail page
    else:
        comment_form = CommentForm()

    return render(request, 'view_thread.html', {
        'thread': thread,
        'comments': comments,
        'comment_form': comment_form,
    })

  # Ensure the user is logged in
def add_comment(request):
    if request.method == 'POST':
        thread_id = request.POST.get('thread_id')
        thread = get_object_or_404(Thread, id=thread_id)  # Handle thread not found
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.thread = thread
            comment.author = request.user  # Set the author to the current user
            comment.save()
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})

  # Ensure the user is logged in
def request_resource(request):
    if request.method == 'POST':
        resource_name = request.POST.get('resource_name')
        resource_details = request.POST.get('resource_details')
        new_request = ResourceRequest(name=resource_name, details=resource_details)
        new_request.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})

def profile_edit(request):
    user_profile = request.user.userprofile  # Get the user profile
    if request.method == 'POST':
        profile_form = ProfileEditForm(request.POST, instance=user_profile)
        picture_form = ProfilePictureForm(request.POST, request.FILES, instance=user_profile)
        password_form = PasswordUpdateForm(user=request.user, data=request.POST)
        
        if profile_form.is_valid() and picture_form.is_valid():
            profile_form.save()
            picture_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile_edit')

        if password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form.user)  # Prevents user from being logged out after password change
            messages.success(request, 'Your password has been updated successfully.')
            return redirect('profile_edit')

    else:
        profile_form = ProfileEditForm(instance=user_profile)
        picture_form = ProfilePictureForm(instance=user_profile)
        password_form = PasswordUpdateForm(user=request.user)

    return render(request, 'profile_edit.html', {
        'profile_form': profile_form,
        'picture_form': picture_form,
        'password_form': password_form,
    })


# View for updating the password

def update_password(request):
    if request.method == 'POST':
        form = PasswordUpdateForm(user=request.user, data=request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been updated successfully.')
            return redirect('profile_edit')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = PasswordUpdateForm(user=request.user)

    return render(request, 'update_password.html', {'form': form})

def notification_center(request):
    # Query all notifications for the logged-in user, ordered by most recent first
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'events/notifications.html', {
        'notifications': notifications
    })


# View to mark a notification as read (AJAX call)

def mark_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)

# View to delete a notification (AJAX call)

def delete_notification(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.delete()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)

@login_required
def settings_view(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Check if the request is for account deletion
        if 'delete_account' in request.POST:
            user.delete()
            messages.success(request, 'Your account has been deleted.')
            return redirect('home')  # Redirect to the home page after deletion

        # Handle profile update
        profile_form = ProfileEditForm(request.POST, instance=profile)
        profile_picture_form = ProfilePictureForm(request.POST, request.FILES, instance=profile)
        notification_form = NotificationPreferencesForm(request.POST, instance=profile)

        if profile_form.is_valid() and profile_picture_form.is_valid() and notification_form.is_valid():
            profile_form.save()
            profile_picture_form.save()
            notification_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('settings')  # Redirect to the settings page after updating

    else:
        profile_form = ProfileEditForm(instance=profile)
        profile_picture_form = ProfilePictureForm(instance=profile)
        notification_form = NotificationPreferencesForm(instance=profile)

    context = {
        'user': user,
        'profile_form': profile_form,
        'profile_picture_form': profile_picture_form,
        'notification_form': notification_form,
    }
    return render(request, 'events/settings.html', context)
