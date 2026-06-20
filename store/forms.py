from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Review, Itinerary, ItineraryItem, Booking, ContactMessage, Place


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {f: forms.TextInput(attrs={'class': 'form-control'}) for f in ['first_name', 'last_name']}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['class'] = 'form-control'


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'phone', 'bio', 'interests', 'budget', 'preferred_language']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'interests': forms.Select(attrs={'class': 'form-select'}),
            'budget': forms.Select(attrs={'class': 'form-select'}),
            'preferred_language': forms.Select(attrs={'class': 'form-select'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Share your experience...'}),
        }


class ItineraryForm(forms.ModelForm):
    class Meta:
        model = Itinerary
        fields = ['title', 'description', 'num_days', 'budget']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'My Egypt Adventure'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'num_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 30}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['date', 'time', 'num_guests', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'num_guests': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class PlaceAdminForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_ar': forms.TextInput(attrs={'class': 'form-control'}),
            'place_type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'description_ar': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'historical_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'historical_info_ar': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'governorate': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'activity_type': forms.Select(attrs={'class': 'form-select'}),
            'price_level': forms.Select(attrs={'class': 'form-select'}, choices=[(1,'Budget'),(2,'Mid-Range'),(3,'Luxury')]),
            'entry_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'opening_hours': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': 0, 'max': 5}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_trending': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
