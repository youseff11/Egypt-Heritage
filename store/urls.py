from django.urls import path
from . import views

urlpatterns = [
    # Homepage
    path('', views.home, name='home'),

    # Places
    path('places/', views.place_list, name='place_list'),
    path('places/<slug:slug>/', views.place_detail, name='place_detail'),

    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # Itinerary
    path('itineraries/', views.itinerary_list, name='itinerary_list'),
    path('itineraries/create/', views.itinerary_create, name='itinerary_create'),
    path('itineraries/<int:pk>/', views.itinerary_detail, name='itinerary_detail'),
    path('itineraries/<int:pk>/edit/', views.itinerary_edit, name='itinerary_edit'),
    path('itineraries/<int:pk>/delete/', views.itinerary_delete, name='itinerary_delete'),
    path('itinerary/add/', views.add_to_itinerary, name='add_to_itinerary'),
    path('itinerary/remove/<int:item_id>/', views.remove_from_itinerary, name='remove_from_itinerary'),

    # Booking
    path('book/<slug:slug>/', views.booking_create, name='booking_create'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/<int:pk>/cancel/', views.booking_cancel, name='booking_cancel'),

    # AI Recommendations
    path('recommendations/', views.recommendations, name='recommendations'),

    # Contact
    path('contact/', views.contact, name='contact'),

    # Chatbot
    path('api/chatbot/', views.chatbot_response, name='chatbot_response'),

    # Admin Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/places/', views.admin_places, name='admin_places'),
    path('dashboard/places/add/', views.admin_place_add, name='admin_place_add'),
    path('dashboard/places/<int:pk>/edit/', views.admin_place_edit, name='admin_place_edit'),
    path('dashboard/places/<int:pk>/delete/', views.admin_place_delete, name='admin_place_delete'),
    path('dashboard/users/', views.admin_users, name='admin_users'),
    path('dashboard/bookings/', views.admin_bookings, name='admin_bookings'),
    path('dashboard/bookings/<int:pk>/status/', views.admin_booking_status, name='admin_booking_status'),
]
