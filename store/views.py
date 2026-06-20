from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import (
    Place, Category, UserProfile, Review, Itinerary,
    ItineraryItem, Booking, PlaceImage, ContactMessage,
    Doctor, DoctorCase, DoctorReview, DoctorBooking
)
from .forms import (
    UserRegisterForm, UserUpdateForm, ProfileUpdateForm,
    ReviewForm, ItineraryForm, BookingForm, ContactForm, PlaceAdminForm,
    DoctorReviewForm, DoctorBookingForm
)


# ─── Homepage ────────────────────────────────────────────────────
def home(request):
    featured = Place.objects.filter(is_featured=True)[:6]
    trending = Place.objects.filter(is_trending=True)[:6]
    heritage = Place.objects.filter(place_type='heritage')[:4]
    medical = Place.objects.filter(place_type='medical')[:4]
    categories = Category.objects.all()

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
        'featured': featured, 'trending': trending,
        'heritage': heritage, 'medical': medical,
        'categories': categories, 'recommended': recommended, 'stats': stats,
    })


# ─── Places ──────────────────────────────────────────────────────
def place_list(request):
    places = Place.objects.all()
    categories = Category.objects.all()
    q = request.GET.get('q', '')
    if q:
        places = places.filter(
            Q(name__icontains=q) | Q(name_ar__icontains=q) |
            Q(description__icontains=q) | Q(city__icontains=q) |
            Q(governorate__icontains=q)
        )
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
    sort = request.GET.get('sort', '-rating')
    if sort in ['rating', '-rating', 'entry_fee', '-entry_fee', 'name', '-name', '-views_count']:
        places = places.order_by(sort)
    paginator = Paginator(places, 12)
    page = request.GET.get('page')
    places = paginator.get_page(page)
    governorates = Place.objects.values_list('governorate', flat=True).distinct().order_by('governorate')
    return render(request, 'place_list.html', {
        'places': places, 'categories': categories, 'governorates': governorates,
        'q': q, 'current_type': place_type, 'current_category': category,
        'current_activity': activity, 'current_price': price,
        'current_gov': gov, 'current_sort': sort,
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
    # Doctors for medical places
    doctors = place.doctors.filter(is_active=True) if place.place_type == 'medical' else Doctor.objects.none()

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
                    avg = place.reviews.aggregate(Avg('rating'))['rating__avg']
                    place.rating = round(avg, 1) if avg else 4.0
                    place.total_reviews = place.reviews.count()
                    place.save(update_fields=['rating', 'total_reviews'])
                    messages.success(request, 'Review added successfully!')
                    return redirect('place_detail', slug=slug)
    user_itineraries = []
    if request.user.is_authenticated:
        user_itineraries = Itinerary.objects.filter(user=request.user)
    return render(request, 'place_detail.html', {
        'place': place, 'reviews': reviews, 'gallery': gallery,
        'related': related, 'review_form': review_form,
        'booking_form': booking_form, 'user_review': user_review,
        'user_itineraries': user_itineraries, 'doctors': doctors,
    })


# ─── VR 360° Viewer ─────────────────────────────────────────────
def vr_viewer(request, slug):
    place = get_object_or_404(Place, slug=slug)
    return render(request, 'vr_viewer.html', {'place': place})


# ─── AR Scanner ──────────────────────────────────────────────────
def ar_scanner(request):
    places = Place.objects.all().values('id', 'name', 'name_ar', 'latitude', 'longitude',
                                         'city', 'governorate', 'slug', 'place_type', 'rating')
    return render(request, 'ar_scanner.html', {'places_json': list(places)})


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
    messages.success(request, 'Logged out successfully.')
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
            messages.success(request, 'Profile updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)
    bookings = Booking.objects.filter(user=request.user)[:5]
    itineraries = Itinerary.objects.filter(user=request.user)[:5]
    doctor_bookings = DoctorBooking.objects.filter(user=request.user)[:5]
    return render(request, 'profile.html', {
        'u_form': u_form, 'p_form': p_form,
        'bookings': bookings, 'itineraries': itineraries,
        'doctor_bookings': doctor_bookings,
    })


# ─── Itinerary ──────────────────────────────────────────────────
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
    return render(request, 'itinerary_detail.html', {'itinerary': itinerary, 'days': days})


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
    return render(request, 'itinerary_form.html', {'form': form, 'title': f'Edit: {itinerary.title}'})


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
    it_id = request.POST.get('itinerary_id')
    place_id = request.POST.get('place_id')
    day = request.POST.get('day_number', 1)
    itinerary = get_object_or_404(Itinerary, pk=it_id, user=request.user)
    place = get_object_or_404(Place, pk=place_id)
    ItineraryItem.objects.create(itinerary=itinerary, place=place, day_number=int(day))
    messages.success(request, f'{place.name} added to {itinerary.title}!')
    return redirect('place_detail', slug=place.slug)


@login_required
@require_POST
def remove_from_itinerary(request, item_id):
    item = get_object_or_404(ItineraryItem, pk=item_id, itinerary__user=request.user)
    it_pk = item.itinerary.pk
    item.delete()
    messages.success(request, 'Removed from itinerary.')
    return redirect('itinerary_detail', pk=it_pk)


# ─── Booking ────────────────────────────────────────────────────
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
            messages.success(request, 'Booking submitted successfully!')
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


# ─── Doctors ─────────────────────────────────────────────────────
def doctor_list(request):
    doctors = Doctor.objects.filter(is_active=True)
    q = request.GET.get('q', '')
    if q:
        doctors = doctors.filter(Q(name__icontains=q) | Q(name_ar__icontains=q) | Q(specialization__icontains=q))
    spec = request.GET.get('specialization', '')
    if spec:
        doctors = doctors.filter(specialization=spec)
    place_slug = request.GET.get('place', '')
    if place_slug:
        doctors = doctors.filter(places__slug=place_slug)
    doctors = doctors.order_by('-rating')
    specializations = Doctor.SPECIALIZATION_CHOICES
    medical_places = Place.objects.filter(place_type='medical')
    return render(request, 'doctor_list.html', {
        'doctors': doctors, 'q': q, 'current_spec': spec,
        'current_place': place_slug, 'specializations': specializations,
        'medical_places': medical_places,
    })


def doctor_detail(request, slug):
    doctor = get_object_or_404(Doctor, slug=slug)
    cases = doctor.cases.all()[:10]
    reviews = doctor.reviews.all()
    places = doctor.places.all()
    review_form = DoctorReviewForm()
    user_review = None

    if request.user.is_authenticated:
        user_review = DoctorReview.objects.filter(doctor=doctor, user=request.user).first()

    if request.method == 'POST' and request.user.is_authenticated:
        if 'submit_review' in request.POST:
            if user_review:
                messages.warning(request, 'You already reviewed this doctor.')
            else:
                review_form = DoctorReviewForm(request.POST)
                if review_form.is_valid():
                    r = review_form.save(commit=False)
                    r.doctor = doctor
                    r.user = request.user
                    r.save()
                    avg = doctor.reviews.aggregate(Avg('rating'))['rating__avg']
                    doctor.rating = round(avg, 1) if avg else 4.0
                    doctor.total_reviews = doctor.reviews.count()
                    doctor.save(update_fields=['rating', 'total_reviews'])
                    messages.success(request, 'Review submitted!')
                    return redirect('doctor_detail', slug=slug)

    return render(request, 'doctor_detail.html', {
        'doctor': doctor, 'cases': cases, 'reviews': reviews,
        'places': places, 'review_form': review_form, 'user_review': user_review,
    })


@login_required
def doctor_booking(request, slug):
    doctor = get_object_or_404(Doctor, slug=slug)
    if request.method == 'POST':
        form = DoctorBookingForm(request.POST, doctor=doctor)
        if form.is_valid():
            b = form.save(commit=False)
            b.user = request.user
            b.doctor = doctor
            b.save()
            messages.success(request, f'Appointment booked with Dr. {doctor.name}!')
            return redirect('doctor_detail', slug=slug)
    else:
        form = DoctorBookingForm(doctor=doctor)
    return render(request, 'doctor_booking_form.html', {'form': form, 'doctor': doctor})


@login_required
def my_doctor_bookings(request):
    bookings = DoctorBooking.objects.filter(user=request.user).select_related('doctor', 'place')
    return render(request, 'doctor_booking_list.html', {'bookings': bookings})


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
            messages.success(request, 'Your message has been sent!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


# ─── Smart Chatbot API ──────────────────────────────────────────
@csrf_exempt
def chatbot_response(request):
    if request.method == 'POST':
        import json, re
        data = json.loads(request.body)
        user_msg = data.get('message', '').strip()
        msg_lower = user_msg.lower()

        # --- Knowledge base from database ---
        all_places = Place.objects.all()
        heritage_places = all_places.filter(place_type='heritage')
        medical_places = all_places.filter(place_type='medical')
        all_doctors = Doctor.objects.filter(is_active=True)

        # Check if asking about a specific place by name
        matched_place = None
        for p in all_places:
            if p.name.lower() in msg_lower or (p.name_ar and p.name_ar in user_msg):
                matched_place = p
                break

        # Check if asking about a specific doctor
        matched_doctor = None
        for d in all_doctors:
            if d.name.lower() in msg_lower or (d.name_ar and d.name_ar in user_msg):
                matched_doctor = d
                break

        reply = None

        # --- Specific place info ---
        if matched_place:
            p = matched_place
            reply = f"📍 <strong>{p.name}</strong>"
            if p.name_ar:
                reply += f" ({p.name_ar})"
            reply += f"<br>📌 {p.city}, {p.governorate}"
            reply += f"<br>⭐ Rating: {p.rating}/5"
            if p.entry_fee:
                reply += f"<br>💰 Entry: {p.entry_fee} EGP"
            if p.opening_hours:
                reply += f"<br>🕐 Hours: {p.opening_hours}"
            reply += f"<br>📝 {p.description[:200]}..."
            reply += f'<br><a href="/places/{p.slug}/" style="color:var(--gold);">View Details →</a>'

        # --- Specific doctor info ---
        elif matched_doctor:
            d = matched_doctor
            reply = f"👨‍⚕️ <strong>Dr. {d.name}</strong>"
            reply += f"<br>🏥 {d.get_specialization_display()}"
            reply += f"<br>⭐ Rating: {d.rating}/5 ({d.total_reviews} reviews)"
            reply += f"<br>📅 {d.years_experience} years experience"
            reply += f"<br>💰 Consultation: {d.consultation_fee} EGP"
            if d.available_days:
                reply += f"<br>📆 Available: {d.available_days}"
            reply += f'<br><a href="/doctors/{d.slug}/" style="color:var(--gold);">View Profile →</a>'

        # --- Greetings ---
        elif any(w in msg_lower for w in ['hello', 'hi', 'hey', 'مرحبا', 'اهلا', 'السلام', 'صباح', 'مساء']):
            reply = "مرحباً! 👋 Welcome to Egypt Heritage & Wellness Tourism! I can help you with:<br>"
            reply += "🏛️ Heritage sites & archaeological wonders<br>"
            reply += "🧖 Wellness & medical tourism<br>"
            reply += "👨‍⚕️ Finding doctors at wellness centers<br>"
            reply += "📋 Trip planning & itineraries<br>"
            reply += "📅 Booking visits & appointments<br>"
            reply += "Just ask me anything!"

        # --- Heritage questions ---
        elif any(w in msg_lower for w in ['heritage', 'تراث', 'أثر', 'اثري', 'pyramid', 'temple', 'هرم', 'معبد', 'فرعون', 'pharaoh', 'ancient', 'قديم', 'تاريخ', 'history']):
            names = ', '.join([f'<strong>{p.name}</strong>' for p in heritage_places[:5]])
            reply = f"🏛️ Our top heritage sites include: {names}.<br><br>"
            reply += "These sites span thousands of years of ancient Egyptian civilization. "
            reply += 'You can <a href="/places/?type=heritage" style="color:var(--gold);">browse all heritage sites</a> or ask me about any specific one!'

        # --- Medical/Wellness questions ---
        elif any(w in msg_lower for w in ['medical', 'wellness', 'علاج', 'طب', 'spa', 'therapy', 'spring', 'عين', 'حمام', 'صحة', 'health', 'cure', 'treatment']):
            names = ', '.join([f'<strong>{p.name}</strong>' for p in medical_places[:5]])
            reply = f"🧖 Our wellness destinations include: {names}.<br><br>"
            reply += "Egypt offers world-class natural therapy including hot springs, sand therapy, and mineral baths. "
            reply += 'You can <a href="/places/?type=medical" style="color:var(--gold);">browse all wellness centers</a>!'

        # --- Doctor questions ---
        elif any(w in msg_lower for w in ['doctor', 'دكتور', 'طبيب', 'appointment', 'موعد', 'كشف', 'specialist', 'أخصائي', 'consultation']):
            doc_count = all_doctors.count()
            specs = ', '.join(set([d.get_specialization_display() for d in all_doctors[:6]]))
            reply = f"👨‍⚕️ We have <strong>{doc_count} doctors</strong> available across our wellness centers.<br>"
            reply += f"Specializations include: {specs}.<br><br>"
            reply += 'You can <a href="/doctors/" style="color:var(--gold);">browse all doctors</a>, view their profiles, cases, and book appointments!'

        # --- Booking questions ---
        elif any(w in msg_lower for w in ['book', 'حجز', 'reserve', 'appointment', 'موعد']):
            reply = "📅 Booking is easy! You can:<br>"
            reply += "1️⃣ Book a visit to any destination from its detail page<br>"
            reply += "2️⃣ Book a doctor appointment from the doctor's profile<br>"
            reply += "3️⃣ View all your bookings from your profile<br>"
            reply += '<a href="/places/" style="color:var(--gold);">Browse destinations</a> | <a href="/doctors/" style="color:var(--gold);">Find a doctor</a>'

        # --- Trip/Itinerary questions ---
        elif any(w in msg_lower for w in ['itinerary', 'trip', 'plan', 'رحلة', 'برنامج', 'خطة', 'travel', 'سفر', 'tour']):
            reply = "🗺️ I can help you plan your trip! Use our <strong>Itinerary Planner</strong> to:<br>"
            reply += "• Create multi-day travel plans<br>"
            reply += "• Add destinations to each day<br>"
            reply += "• Track your budget<br>"
            reply += '<a href="/itineraries/create/" style="color:var(--gold);">Create Itinerary →</a>'

        # --- Price/Budget questions ---
        elif any(w in msg_lower for w in ['price', 'cost', 'سعر', 'budget', 'ميزانية', 'كام', 'how much', 'fee', 'رسوم', 'cheap', 'expensive', 'رخيص', 'غالي']):
            budget_places = all_places.filter(price_level=1)[:3]
            mid_places = all_places.filter(price_level=2)[:3]
            luxury_places = all_places.filter(price_level=3)[:3]
            reply = "💰 <strong>Price Guide:</strong><br>"
            if budget_places:
                reply += f"🟢 Budget: {', '.join([p.name for p in budget_places])} (from {min([p.entry_fee for p in budget_places])} EGP)<br>"
            if mid_places:
                reply += f"🟡 Mid-Range: {', '.join([p.name for p in mid_places])}<br>"
            if luxury_places:
                reply += f"🔴 Luxury: {', '.join([p.name for p in luxury_places])}<br>"
            reply += '<br>You can <a href="/places/?sort=entry_fee" style="color:var(--gold);">sort by price</a> on the explore page!'

        # --- Location/City questions ---
        elif any(w in msg_lower for w in ['cairo', 'القاهرة', 'luxor', 'الأقصر', 'aswan', 'أسوان', 'giza', 'الجيزة', 'sinai', 'سيناء', 'siwa', 'سيوة', 'sharm', 'شرم']):
            city_match = None
            for keyword, city in [('cairo', 'Cairo'), ('القاهرة', 'Cairo'), ('luxor', 'Luxor'), ('الأقصر', 'Luxor'),
                                  ('aswan', 'Aswan'), ('أسوان', 'Aswan'), ('giza', 'Giza'), ('الجيزة', 'Giza'),
                                  ('sinai', 'Sinai'), ('سيناء', 'Sinai'), ('siwa', 'Siwa'), ('سيوة', 'Siwa'),
                                  ('sharm', 'Sharm El-Sheikh'), ('شرم', 'Sharm El-Sheikh')]:
                if keyword in msg_lower:
                    city_match = city
                    break
            if city_match:
                city_places = all_places.filter(Q(city__icontains=city_match) | Q(governorate__icontains=city_match))
                if city_places:
                    names = ', '.join([f'<strong>{p.name}</strong>' for p in city_places[:5]])
                    reply = f"📍 Destinations in/near {city_match}: {names}.<br>"
                    reply += f'<a href="/places/?q={city_match}" style="color:var(--gold);">See all in {city_match} →</a>'
                else:
                    reply = f"I don't have specific places listed in {city_match} yet, but Egypt has amazing sites everywhere!"

        # --- VR/AR questions ---
        elif any(w in msg_lower for w in ['vr', 'virtual', 'ar', 'augmented', 'واقع', '360', 'scan', 'camera']):
            reply = "🔮 We offer immersive experiences!<br>"
            reply += "📸 <strong>360° VR Viewer:</strong> Explore panoramic views of destinations from the place detail page.<br>"
            reply += "📱 <strong>AR Scanner:</strong> Point your camera at a landmark and we'll identify it for you!<br>"
            reply += '<a href="/ar-scanner/" style="color:var(--gold);">Try AR Scanner →</a>'

        # --- Rating/Best questions ---
        elif any(w in msg_lower for w in ['best', 'top', 'أفضل', 'أحسن', 'recommend', 'suggest', 'popular', 'famous']):
            top = all_places.order_by('-rating')[:5]
            reply = "🌟 <strong>Top Rated Destinations:</strong><br>"
            for i, p in enumerate(top, 1):
                reply += f"{i}. <strong>{p.name}</strong> ⭐ {p.rating}/5 - {p.city}<br>"
            reply += '<br><a href="/recommendations/" style="color:var(--gold);">Get AI Recommendations →</a>'

        # --- Thanks ---
        elif any(w in msg_lower for w in ['thank', 'شكر', 'thanks', 'شكرا']):
            reply = "You're welcome! 😊 Happy to help. Feel free to ask anything else about Egypt tourism!"

        # --- About ---
        elif any(w in msg_lower for w in ['about', 'what is', 'who', 'عن', 'ايه ده', 'ما هو']):
            reply = "🇪🇬 <strong>Egypt Heritage & Wellness Tourism</strong> is your comprehensive guide to exploring Egypt!<br>"
            reply += f"📊 We feature <strong>{all_places.count()}</strong> destinations, "
            reply += f"<strong>{all_doctors.count()}</strong> doctors, and personalized AI recommendations.<br>"
            reply += "Our platform covers heritage sites, wellness centers, trip planning, and medical tourism."

        # --- Help ---
        elif any(w in msg_lower for w in ['help', 'مساعدة', 'what can you', 'ممكن', 'تقدر']):
            reply = "🤖 I can help you with:<br>"
            reply += "🏛️ Ask about any heritage site (Pyramids, Karnak, etc.)<br>"
            reply += "🧖 Find wellness & medical destinations<br>"
            reply += "👨‍⚕️ Find doctors and book appointments<br>"
            reply += "💰 Compare prices and budgets<br>"
            reply += "📍 Find places by city or governorate<br>"
            reply += "📋 Plan your trip itinerary<br>"
            reply += "🌟 Get personalized recommendations<br>"
            reply += "📸 Use VR/AR features<br>"
            reply += "Just type your question in English or Arabic!"

        # --- Default smart response ---
        else:
            # Try to find any matching place or keyword
            words = re.findall(r'\w+', msg_lower)
            found = None
            for word in words:
                if len(word) > 3:
                    match = all_places.filter(
                        Q(name__icontains=word) | Q(city__icontains=word) |
                        Q(description__icontains=word) | Q(governorate__icontains=word)
                    ).first()
                    if match:
                        found = match
                        break
            if found:
                reply = f"I found something related! 📍 <strong>{found.name}</strong> in {found.city} ({found.get_place_type_display()}).<br>"
                reply += f"⭐ {found.rating}/5 | 💰 {found.price_label()}<br>"
                reply += f'<a href="/places/{found.slug}/" style="color:var(--gold);">View Details →</a>'
            else:
                reply = "🤔 I'm not sure about that, but I can help with:<br>"
                reply += "• Heritage sites & archaeological places<br>"
                reply += "• Wellness & medical tourism destinations<br>"
                reply += "• Doctor appointments & consultations<br>"
                reply += "• Trip planning & booking<br>"
                reply += "• Prices & recommendations<br>"
                reply += "Try asking about a specific place, city, or topic!"

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
        'total_doctors': Doctor.objects.filter(is_active=True).count(),
        'total_doctor_bookings': DoctorBooking.objects.count(),
    }
    recent_bookings = Booking.objects.select_related('user', 'place')[:10]
    recent_reviews = Review.objects.select_related('user', 'place')[:10]
    top_places = Place.objects.order_by('-views_count')[:5]
    return render(request, 'admin_dashboard.html', {
        'stats': stats, 'recent_bookings': recent_bookings,
        'recent_reviews': recent_reviews, 'top_places': top_places,
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
            messages.success(request, 'Place added!')
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
