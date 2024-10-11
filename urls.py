from django.urls import path
from .views import (
    home,
    index,  # Ensure this matches the function name in views.py
    register,
    user_login,
    user_logout,
    community_list_view,
    community_details_view,
    community_create_view,
    event_list_view,
    event_details_view,  # Make sure this is correct
    event_create_view,
    interfaith_networking,
    CustomLoginView,
    about_us,
    contact,
    OfferHelpView,
    RequestHelpView,
    OfferHelpCategoryView,
    RequestHelpCategory1View, RequestHelpCategory2View, RequestHelpCategory3View, RequestHelpCategory4View,     community_networking,
    search_users,
    create_poll,
    respond_to_poll,
    send_connection_request,
    discussion_forums, create_thread, add_comment, request_resource,
    profile_edit,
    update_password,
    notification_center, mark_as_read, delete_notification , settings_view,  delete_request_view, edit_request_view, create_community_profile,
    view_thread, add_comment,

)

urlpatterns = [
    path('', home, name='home'),
    path('index/', index, name='index'),  # Ensure the function name matches
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', user_logout, name='logout'),
    path('communities/', community_list_view, name='community_list'),
    path('communities/<int:community_id>/', community_details_view, name='community_details'),  # Ensure consistent naming
    path('communities/create/', community_create_view, name='community_create'),
    path('create-community/', create_community_profile, name='community_form'),
    path('events/', event_list_view, name='event_list'),
    path('events/<int:event_id>/', event_details_view, name='event_details'),  # Use 'event_details' for consistency
    path('events/create/', event_create_view, name='event_create'),
    path('interfaith_networking/', interfaith_networking, name='interfaith_networking'),
    path('about/', about_us, name='about_us'),  # Example pattern
    path('contact/', contact, name='contact'),  # Example pattern
    path('offer_help/', OfferHelpView.as_view(), name='offer_help'),
    path('request_help/', RequestHelpView.as_view(), name='request_help'),  # Add this line
    path('offer_help_category_1/', OfferHelpCategoryView.as_view(), {'category': 'Mental Health Support'}, name='offer_help_category_1'),
    path('offer-help/category-2/', OfferHelpCategoryView.as_view(), {'category': 'Food Assistance'}, name='offer_help_category_2'),
    path('offer-help/category-3/', OfferHelpCategoryView.as_view(), {'category': 'Shelter Services'}, name='offer_help_category_3'),
    path('offer-help/category-4/', OfferHelpCategoryView.as_view(), {'category': 'Educational Support'}, name='offer_help_category_4'),
    path('offer_help/submit/', OfferHelpView.as_view(), name='offer_help_submit'),  # add this line
    path('request_help_category_1/', RequestHelpCategory1View.as_view(), name='request_help_category_1'),
    path('request-help/category-2/', RequestHelpCategory2View.as_view(), name='request_help_category_2'),
    path('request-help/category-3/', RequestHelpCategory3View.as_view(), name='request_help_category_3'),
    path('request-help/category-4/', RequestHelpCategory4View.as_view(), name='request_help_category_4'),
    path('request_help/submit/', RequestHelpView.as_view(), name='request_help_submit'),  # Add this line
    path('community/', community_networking, name='community_networking'),
    path('search/', search_users, name='search_users'),
    path('poll/create/', create_poll, name='create_poll'),
    path('poll/respond/<int:poll_id>/', respond_to_poll, name='respond_to_poll'),
    path('connect/<int:user_id>/', send_connection_request, name='send_connection_request'),
    path('forums/', discussion_forums, name='discussion_forums'),
    path('forums/create_thread/', create_thread, name='create_thread'),
    path('forums/add_comment/', add_comment, name='add_comment'),
    path('forums/request_resource/', request_resource, name='request_resource'),
    path('profile/edit/', profile_edit, name='profile_edit'),
    path('profile/update-password/', update_password, name='update_password'),
    path('notifications/', notification_center, name='notification_center'),

    # URLs for marking as read and deleting notifications via AJAX
    path('notifications/mark_as_read/<int:notification_id>/', mark_as_read, name='mark_as_read'),
    path('notifications/delete/<int:notification_id>/', delete_notification, name='delete_notification'),
    path('settings/', settings_view, name='settings'),
    path('delete_request/<int:request_id>/', delete_request_view, name='delete_request'),
    path('edit_request/<int:request_id>/', edit_request_view, name='edit_request'),  # Ensure this exists too
    path('thread/<int:thread_id>/', view_thread, name='view_thread'),  # Thread detail page
    path('create-thread/', create_thread, name='create_thread'),  # Create new thread
    path('events/thread/<int:thread_id>/', view_thread, name='view_thread'),
    path('events/thread/<int:thread_id>/add_comment/', add_comment, name='add_comment'),
    path('thread/<int:thread_id>/', view_thread, name='view_thread'),


]
