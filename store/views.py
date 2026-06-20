from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

from .models import (
    Place, Category, UserProfile, Review, Itinerary,
    ItineraryItem, Booking, PlaceImage, ContactMessage
)
from .forms import (
    UserRegisterForm, UserUpdateForm, ProfileUpdateForm,
    ReviewForm, ItineraryForm, BookingForm, ContactForm, PlaceAdminForm
)


# ─── Homepage ────────────────────────────────────────────────────
def home(request):
    featured = Place.objects.filter(is_featured=True)[:6]
    trending = Place.objects.filter(is_trending=True)[:6]
    heritage = Place.objects.filter(place_type='heritage')[:4]
    medical = Place.objects.filter(place_type='medical')[:4]
    categories = Category.objects.all()

    # AI Recommendations (rule-based)
    recommended = Place.objects.none()
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            if profile.interests == 'heritage':
                recommended = Place.objects.filter(place_type='heritage')
            elif profile.interests == 'medical':
                recommended = Place.objects.filter(place_type='medical')
            else:
                recommended = Place.objects.all()

            if profile.budget == 'budget':
                recommended = recommended.filter(price_level=1)
            elif profile.budget == 'luxury':
                recommended = recommended.filter(price_level=3)

            recommended = recommended.order_by('-rating')[:4]
        except UserProfile.DoesNotExist:
            recommended = Place.objects.order_by('-rating')[:4]

    stats = {
        'total_places': Place.objects.count(),
        'heritage_count': Place.objects.filter(place_type='heritage').count(),
        'medical_count': Place.objects.filter(place_type='medical').count(),
        'total_users': UserProfile.objects.count(),
    }

    return render(request, 'home.html', {
        'featured': featured,
        'trending': trending,
        'heritage': heritage,
        'medical': medical,
        'categories': categories,
        'recommended': recommended,
        'stats': stats,
    })


# ─── Places ──────────────────────────────────────────────────────
def place_list(request):
    places = Place.objects.all()
    categories = Category.objects.all()

    # Search
    q = request.GET.get('q', '')
    if q:
        places = places.filter(
            Q(name__icontains=q) | Q(name_ar__icontains=q) |
            Q(description__icontains=q) | Q(city__icontains=q) |
            Q(governorate__icontains=q)
        )

    # Filters
    place_type = request.GET.get('type', '')
    if place_type:
        places = places.filter(place_type=place_type)

    category = request.GET.get('category', '')
    if category:
        places = places.filter(category__slug=category)

    activity = request.GET.get('activity', '')
    if activity:
        places = places.filter(activity_type=activity)

    price = request.GET.get('price', '')
    if price:
        places = places.filter(price_level=int(price))

    gov = request.GET.get('governorate', '')
    if gov:
        places = places.filter(governorate__icontains=gov)

    # Sort
    sort = request.GET.get('sort', '-rating')
    if sort in ['rating', '-rating', 'entry_fee', '-entry_fee', 'name', '-name', '-views_count']:
        places = places.order_by(sort)

    paginator = Paginator(places, 12)
    page = request.GET.get('page')
    places = paginator.get_page(page)

    governorates = Place.objects.values_list('governorate', flat=True).distinct().order_by('governorate')

    return render(request, 'place_list.html', {
        'places': places,
        'categories': categories,
        'governorates': governorates,
        'q': q,
        'current_type': place_type,
        'current_category': category,
        'current_activity': activity,
        'current_price': price,
        'current_gov': gov,
        'current_sort': sort,
    })


def place_detail(request, slug):
    place = get_object_or_404(Place, slug=slug)
    place.views_count += 1
    place.save(update_fields=['views_count'])

    reviews = place.reviews.all()
    gallery = place.images.all()
    related = Place.objects.filter(
        place_type=place.place_type, category=place.category
    ).exclude(id=place.id)[:4]

    review_form = ReviewForm()
    booking_form = BookingForm()
    user_review = None

    if request.user.is_authenticated:
        user_review = Review.objects.filter(place=place, user=request.user).first()

    if request.method == 'POST' and request.user.is_authenticated:
        if 'submit_review' in request.POST:
            if user_review:
                messages.warning(request, 'You have already reviewed this place.')
            else:
                review_form = ReviewForm(request.POST)
                if review_form.is_valid():
                    review = review_form.save(commit=False)
                    review.place = place
                    review.user = request.user
                    review.save()
                    # Update place rating
                    avg = place.reviews.aggregate(Avg('rating'))['rating__avg']
                    place.rating = round(avg, 1) if avg else 4.0
                    place.total_reviews = place.reviews.count()
                    place.save(update_fields=['rating', 'total_reviews'])
                    messages.success(request, 'Review added successfully!')
                    return redirect('place_detail', slug=slug)

    # User itineraries for "add to itinerary" dropdown
    user_itineraries = []
    if request.user.is_authenticated:
        user_itineraries = Itinerary.objects.filter(user=request.user)

    return render(request, 'place_detail.html', {
        'place': place,
        'reviews': reviews,
        'gallery': gallery,
        'related': related,
        'review_form': review_form,
        'booking_form': booking_form,
        'user_review': user_review,
        'user_itineraries': user_itineraries,
    })


# ─── Auth ────────────────────────────────────────────────────────
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Welcome! Your account has been created.')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    bookings = Booking.objects.filter(user=request.user)[:5]
    itineraries = Itinerary.objects.filter(user=request.user)[:5]
    reviews = Review.objects.filter(user=request.user)[:5]

    return render(request, 'profile.html', {
        'u_form': u_form,
        'p_form': p_form,
        'bookings': bookings,
        'itineraries': itineraries,
        'reviews': reviews,
    })


# ─── Itinerary ───────────────────────────────────────────────────
@login_required
def itinerary_list(request):
    itineraries = Itinerary.objects.filter(user=request.user)
    return render(request, 'itinerary_list.html', {'itineraries': itineraries})


@login_required
def itinerary_create(request):
    if request.method == 'POST':
        form = ItineraryForm(request.POST)
        if form.is_valid():
            it = form.save(commit=False)
            it.user = request.user
            it.save()
            messages.success(request, 'Itinerary created!')
            return redirect('itinerary_detail', pk=it.pk)
    else:
        form = ItineraryForm()
    return render(request, 'itinerary_form.html', {'form': form, 'title': 'Create Itinerary'})


@login_required
def itinerary_detail(request, pk):
    itinerary = get_object_or_404(Itinerary, pk=pk, user=request.user)
    items = itinerary.items.select_related('place').all()
    days = {}
    for item in items:
        days.setdefault(item.day_number, []).append(item)
    return render(request, 'itinerary_detail.html', {
        'itinerary': itinerary,
        'days': dict(sorted(days.items())),
    })


@login_required
def itinerary_edit(request, pk):
    itinerary = get_object_or_404(Itinerary, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ItineraryForm(request.POST, instance=itinerary)
        if form.is_valid():
            form.save()
            messages.success(request, 'Itinerary updated!')
            return redirect('itinerary_detail', pk=pk)
    else:
        form = ItineraryForm(instance=itinerary)
    return render(request, 'itinerary_form.html', {'form': form, 'title': 'Edit Itinerary'})


@login_required
def itinerary_delete(request, pk):
    itinerary = get_object_or_404(Itinerary, pk=pk, user=request.user)
    if request.method == 'POST':
        itinerary.delete()
        messages.success(request, 'Itinerary deleted.')
        return redirect('itinerary_list')
    return render(request, 'confirm_delete.html', {'object': itinerary, 'type': 'itinerary'})


@login_required
@require_POST
def add_to_itinerary(request):
    place_id = request.POST.get('place_id')
    itinerary_id = request.POST.get('itinerary_id')
    day = request.POST.get('day_number', 1)

    place = get_object_or_404(Place, pk=place_id)
    itinerary = get_object_or_404(Itinerary, pk=itinerary_id, user=request.user)

    if not ItineraryItem.objects.filter(itinerary=itinerary, place=place).exists():
        order = itinerary.items.filter(day_number=day).count() + 1
        ItineraryItem.objects.create(
            itinerary=itinerary, place=place,
            day_number=int(day), order=order
        )
        messages.success(request, f'{place.name} added to {itinerary.title}!')
    else:
        messages.info(request, f'{place.name} is already in this itinerary.')

    return redirect('place_detail', slug=place.slug)


@login_required
@require_POST
def remove_from_itinerary(request, item_id):
    item = get_object_or_404(ItineraryItem, pk=item_id, itinerary__user=request.user)
    itinerary_pk = item.itinerary.pk
    item.delete()
    messages.success(request, 'Item removed from itinerary.')
    return redirect('itinerary_detail', pk=itinerary_pk)


# ─── Booking ─────────────────────────────────────────────────────
@login_required
def booking_create(request, slug):
    place = get_object_or_404(Place, slug=slug)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.place = place
            booking.total_price = place.entry_fee * booking.num_guests
            booking.save()
            messages.success(request, 'Booking request submitted successfully!')
            return redirect('booking_list')
    else:
        form = BookingForm()
    return render(request, 'booking_form.html', {'form': form, 'place': place})


@login_required
def booking_list(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'booking_list.html', {'bookings': bookings})


@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled.')
    return redirect('booking_list')


# ─── AI Recommendations ─────────────────────────────────────────
def recommendations(request):
    places = Place.objects.all()

    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            if profile.interests in ('heritage', 'medical'):
                places = places.filter(place_type=profile.interests)
            if profile.budget == 'budget':
                places = places.filter(price_level=1)
            elif profile.budget == 'luxury':
                places = places.filter(price_level=3)
        except UserProfile.DoesNotExist:
            pass

    # Also consider user's reviewed places for collaborative filtering
    if request.user.is_authenticated:
        liked_categories = Review.objects.filter(
            user=request.user, rating__gte=4
        ).values_list('place__category', flat=True)
        if liked_categories:
            places = places.filter(
                Q(category__in=liked_categories) | Q(is_featured=True)
            ).distinct()

    places = places.order_by('-rating', '-views_count')[:12]
    return render(request, 'recommendations.html', {'places': places})


# ─── Contact ─────────────────────────────────────────────────────
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent. We will get back to you soon!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


# ─── Chatbot API ─────────────────────────────────────────────────
def chatbot_response(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        user_msg = data.get('message', '').lower()

        # Simple rule-based chatbot
        if any(w in user_msg for w in ['hello', 'hi', 'مرحبا', 'اهلا']):
            reply = "Hello! Welcome to Egypt Heritage & Wellness Tourism. How can I help you? You can ask about heritage sites, wellness destinations, or trip planning."
        elif any(w in user_msg for w in ['heritage', 'تراث', 'أثر', 'pyramid', 'temple']):
            heritage_places = Place.objects.filter(place_type='heritage')[:3]
            names = ', '.join([p.name for p in heritage_places])
            reply = f"We have amazing heritage sites! Some popular ones: {names}. Would you like more details about any of them?"
        elif any(w in user_msg for w in ['medical', 'wellness', 'علاج', 'spa', 'therapy']):
            medical_places = Place.objects.filter(place_type='medical')[:3]
            names = ', '.join([p.name for p in medical_places])
            reply = f"For wellness and medical tourism, check out: {names}. These offer therapeutic and relaxation experiences."
        elif any(w in user_msg for w in ['itinerary', 'trip', 'plan', 'رحلة', 'برنامج']):
            reply = "I can help you plan a trip! Visit our Itinerary Planner to create a custom travel plan. You can add destinations day by day."
        elif any(w in user_msg for w in ['book', 'حجز', 'reserve']):
            reply = "You can book sessions and visits directly from any place's detail page. Just click 'Book Now' and select your preferred date and time."
        elif any(w in user_msg for w in ['price', 'cost', 'سعر', 'budget']):
            reply = "Prices vary by destination. You can filter places by budget level (Budget, Mid-Range, Luxury) on our search page."
        else:
            reply = "I can help you with heritage sites, wellness destinations, trip planning, and bookings. What would you like to know about?"

        return JsonResponse({'reply': reply})
    return JsonResponse({'error': 'POST only'}, status=405)


# ─── Admin Dashboard ─────────────────────────────────────────────
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')

    stats = {
        'total_places': Place.objects.count(),
        'heritage_count': Place.objects.filter(place_type='heritage').count(),
        'medical_count': Place.objects.filter(place_type='medical').count(),
        'total_users': UserProfile.objects.count(),
        'total_bookings': Booking.objects.count(),
        'pending_bookings': Booking.objects.filter(status='pending').count(),
        'total_reviews': Review.objects.count(),
        'total_itineraries': Itinerary.objects.count(),
        'total_messages': ContactMessage.objects.filter(is_read=False).count(),
    }

    recent_bookings = Booking.objects.select_related('user', 'place')[:10]
    recent_reviews = Review.objects.select_related('user', 'place')[:10]
    top_places = Place.objects.order_by('-views_count')[:5]

    return render(request, 'admin_dashboard.html', {
        'stats': stats,
        'recent_bookings': recent_bookings,
        'recent_reviews': recent_reviews,
        'top_places': top_places,
    })


@login_required
def admin_places(request):
    if not request.user.is_staff:
        return redirect('home')
    places = Place.objects.all().order_by('-created_at')
    return render(request, 'admin_places.html', {'places': places})


@login_required
def admin_place_add(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        form = PlaceAdminForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Place added successfully!')
            return redirect('admin_places')
    else:
        form = PlaceAdminForm()
    return render(request, 'admin_place_form.html', {'form': form, 'title': 'Add Place'})


@login_required
def admin_place_edit(request, pk):
    if not request.user.is_staff:
        return redirect('home')
    place = get_object_or_404(Place, pk=pk)
    if request.method == 'POST':
        form = PlaceAdminForm(request.POST, request.FILES, instance=place)
        if form.is_valid():
            form.save()
            messages.success(request, 'Place updated!')
            return redirect('admin_places')
    else:
        form = PlaceAdminForm(instance=place)
    return render(request, 'admin_place_form.html', {'form': form, 'title': f'Edit: {place.name}'})


@login_required
def admin_place_delete(request, pk):
    if not request.user.is_staff:
        return redirect('home')
    place = get_object_or_404(Place, pk=pk)
    if request.method == 'POST':
        place.delete()
        messages.success(request, 'Place deleted.')
        return redirect('admin_places')
    return render(request, 'confirm_delete.html', {'object': place, 'type': 'place'})


@login_required
def admin_users(request):
    if not request.user.is_staff:
        return redirect('home')
    from django.contrib.auth.models import User
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin_users.html', {'users': users})


@login_required
def admin_bookings(request):
    if not request.user.is_staff:
        return redirect('home')
    bookings = Booking.objects.select_related('user', 'place').all()

    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)

    return render(request, 'admin_bookings.html', {'bookings': bookings})


@login_required
@require_POST
def admin_booking_status(request, pk):
    if not request.user.is_staff:
        return redirect('home')
    booking = get_object_or_404(Booking, pk=pk)
    new_status = request.POST.get('status')
    if new_status in ['confirmed', 'cancelled', 'completed']:
        booking.status = new_status
        booking.save()
        messages.success(request, f'Booking status updated to {new_status}.')
    return redirect('admin_bookings')
