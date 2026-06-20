from django.contrib import admin
from .models import (
    UserProfile, Category, Place, PlaceImage,
    Review, Itinerary, ItineraryItem, Booking, ContactMessage,
    Doctor, DoctorCase, DoctorReview, DoctorBooking
)


class PlaceImageInline(admin.TabularInline):
    model = PlaceImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'place_type', 'category', 'city', 'rating', 'is_featured', 'is_trending']
    list_filter = ['place_type', 'category', 'is_featured', 'is_trending', 'price_level']
    search_fields = ['name', 'city', 'governorate']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PlaceImageInline]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'interests', 'budget', 'preferred_language']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'place', 'rating', 'created_at']
    list_filter = ['rating']


@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'num_days', 'budget', 'created_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'place', 'date', 'status', 'total_price']
    list_filter = ['status']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read']


# ─── Doctor Models ───────────────────────────────────────────────
class DoctorCaseInline(admin.TabularInline):
    model = DoctorCase
    extra = 1


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialization', 'rating', 'total_cases', 'is_active']
    list_filter = ['specialization', 'is_active']
    search_fields = ['name', 'name_ar']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['places']
    inlines = [DoctorCaseInline]


@admin.register(DoctorReview)
class DoctorReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'doctor', 'rating', 'created_at']


@admin.register(DoctorBooking)
class DoctorBookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'doctor', 'date', 'status', 'created_at']
    list_filter = ['status']
