from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
import json


# ─── User Profile ────────────────────────────────────────────────
class UserProfile(models.Model):
    INTEREST_CHOICES = [
        ('heritage', 'Heritage & Archaeological'),
        ('medical', 'Medical & Wellness'),
        ('both', 'Both'),
    ]
    BUDGET_CHOICES = [
        ('budget', 'Budget'),
        ('mid', 'Mid-Range'),
        ('luxury', 'Luxury'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    interests = models.CharField(max_length=20, choices=INTEREST_CHOICES, default='both')
    budget = models.CharField(max_length=20, choices=BUDGET_CHOICES, default='mid')
    preferred_language = models.CharField(max_length=5, choices=[('en', 'English'), ('ar', 'العربية')], default='en')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


# ─── Category ────────────────────────────────────────────────────
class Category(models.Model):
    TYPE_CHOICES = [
        ('heritage', 'Heritage & Archaeological'),
        ('medical', 'Medical & Wellness'),
    ]
    name = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    category_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    icon = models.CharField(max_length=50, default='fas fa-landmark')
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ─── Place ───────────────────────────────────────────────────────
class Place(models.Model):
    TYPE_CHOICES = [
        ('heritage', 'Heritage & Archaeological'),
        ('medical', 'Medical & Wellness'),
    ]
    ACTIVITY_CHOICES = [
        ('sightseeing', 'Sightseeing'),
        ('therapy', 'Therapy & Wellness'),
        ('adventure', 'Adventure'),
        ('relaxation', 'Relaxation'),
        ('cultural', 'Cultural Experience'),
        ('diving', 'Diving'),
        ('safari', 'Safari'),
    ]

    name = models.CharField(max_length=200)
    name_ar = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    place_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='places')
    description = models.TextField()
    description_ar = models.TextField(blank=True)
    historical_info = models.TextField(blank=True, help_text="Historical or medical information")
    historical_info_ar = models.TextField(blank=True)

    # Location
    city = models.CharField(max_length=100)
    governorate = models.CharField(max_length=100)
    address = models.CharField(max_length=300, blank=True)
    latitude = models.FloatField(default=30.0444)
    longitude = models.FloatField(default=31.2357)

    # Details
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES, default='sightseeing')
    price_level = models.IntegerField(default=2, help_text="1=Budget, 2=Mid, 3=Luxury")
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    opening_hours = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)

    # Media
    main_image = models.ImageField(upload_to='places/', blank=True, null=True)
    video_url = models.URLField(blank=True)
    panorama_image = models.ImageField(upload_to='places/panorama/', blank=True, null=True,
                                        help_text="360° panoramic image for VR viewer")

    # Stats
    rating = models.FloatField(default=4.0)
    total_reviews = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-rating']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('place_detail', kwargs={'slug': self.slug})

    def price_label(self):
        return {1: 'Budget', 2: 'Mid-Range', 3: 'Luxury'}.get(self.price_level, 'Mid-Range')

    def stars_range(self):
        return range(int(self.rating))

    def __str__(self):
        return self.name


class PlaceImage(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='places/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.place.name}"


# ─── Review ──────────────────────────────────────────────────────
class Review(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['place', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.place.name}"


# ─── Doctor ──────────────────────────────────────────────────────
class Doctor(models.Model):
    SPECIALIZATION_CHOICES = [
        ('dermatology', 'Dermatology'),
        ('rheumatology', 'Rheumatology'),
        ('physiotherapy', 'Physiotherapy'),
        ('orthopedics', 'Orthopedics'),
        ('respiratory', 'Respiratory Medicine'),
        ('balneotherapy', 'Balneotherapy'),
        ('hydrotherapy', 'Hydrotherapy'),
        ('naturopathy', 'Naturopathic Medicine'),
        ('general', 'General Medicine'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile', null=True, blank=True)
    name = models.CharField(max_length=200)
    name_ar = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    specialization = models.CharField(max_length=30, choices=SPECIALIZATION_CHOICES)
    title = models.CharField(max_length=100, blank=True, help_text="e.g. Professor, Consultant")
    bio = models.TextField(blank=True)
    bio_ar = models.TextField(blank=True)
    photo = models.ImageField(upload_to='doctors/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    years_experience = models.IntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=300)
    available_days = models.CharField(max_length=200, blank=True, help_text="e.g. Sun,Mon,Tue,Wed")
    available_hours = models.CharField(max_length=100, blank=True, help_text="e.g. 9:00 AM - 5:00 PM")

    # Linked to medical places
    places = models.ManyToManyField(Place, related_name='doctors', blank=True,
                                    limit_choices_to={'place_type': 'medical'})

    rating = models.FloatField(default=4.0)
    total_reviews = models.IntegerField(default=0)
    total_cases = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def stars_range(self):
        return range(int(self.rating))

    def __str__(self):
        return f"Dr. {self.name}"


class DoctorCase(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='cases')
    patient_name = models.CharField(max_length=100, help_text="Anonymized or with consent")
    condition = models.CharField(max_length=200)
    treatment = models.TextField()
    outcome = models.TextField(blank=True)
    duration_weeks = models.IntegerField(default=1)
    is_success = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Case: {self.condition} - Dr. {self.doctor.name}"


class DoctorReview(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['doctor', 'user']

    def __str__(self):
        return f"{self.user.username} reviewed Dr. {self.doctor.name}"


class DoctorBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_bookings')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='bookings')
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    symptoms = models.TextField(blank=True, help_text="Describe your symptoms")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → Dr. {self.doctor.name} ({self.date})"


# ─── Itinerary ───────────────────────────────────────────────────
class Itinerary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='itineraries')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    num_days = models.IntegerField(default=1)
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Itineraries"
        ordering = ['-updated_at']

    def total_cost(self):
        return sum(item.place.entry_fee for item in self.items.all())

    def __str__(self):
        return f"{self.title} by {self.user.username}"


class ItineraryItem(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name='items')
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    day_number = models.IntegerField(default=1)
    order = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    visit_time = models.TimeField(null=True, blank=True)

    class Meta:
        ordering = ['day_number', 'order']

    def __str__(self):
        return f"Day {self.day_number}: {self.place.name}"


# ─── Booking ─────────────────────────────────────────────────────
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    num_guests = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.place.name} ({self.date})"


# ─── Contact Message ─────────────────────────────────────────────
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
