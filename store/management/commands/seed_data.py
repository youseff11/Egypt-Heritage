from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Place, UserProfile


class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **kwargs):
        # Categories
        cats = [
            ('Temples & Tombs', 'معابد ومقابر', 'heritage', 'fas fa-gopuram'),
            ('Pyramids', 'أهرامات', 'heritage', 'fas fa-monument'),
            ('Islamic Heritage', 'تراث إسلامي', 'heritage', 'fas fa-mosque'),
            ('Museums', 'متاحف', 'heritage', 'fas fa-university'),
            ('Hot Springs', 'عيون حارة', 'medical', 'fas fa-hot-tub'),
            ('Sand Therapy', 'علاج بالرمال', 'medical', 'fas fa-sun'),
            ('Oasis Wellness', 'واحات علاجية', 'medical', 'fas fa-spa'),
            ('Diving & Marine', 'غوص وبحري', 'medical', 'fas fa-water'),
        ]
        cat_objs = {}
        for name, name_ar, ctype, icon in cats:
            c, _ = Category.objects.get_or_create(name=name, defaults={
                'name_ar': name_ar, 'category_type': ctype, 'icon': icon
            })
            cat_objs[name] = c

        # Places
        places_data = [
            {
                'name': 'Pyramids of Giza', 'name_ar': 'أهرامات الجيزة',
                'place_type': 'heritage', 'category': 'Pyramids',
                'description': 'The Great Pyramids of Giza are among the Seven Wonders of the Ancient World. Built as royal tombs during the Fourth Dynasty, they remain the most iconic symbol of ancient Egyptian civilization.',
                'description_ar': 'أهرامات الجيزة العظيمة من عجائب الدنيا السبع. بنيت كمقابر ملكية خلال الأسرة الرابعة.',
                'historical_info': 'The Great Pyramid of Khufu was built around 2560 BC and stood as the tallest man-made structure for over 3,800 years.',
                'city': 'Giza', 'governorate': 'Giza',
                'latitude': 29.9792, 'longitude': 31.1342,
                'activity_type': 'sightseeing', 'price_level': 2,
                'entry_fee': 200, 'opening_hours': '8:00 AM - 5:00 PM',
                'rating': 4.8, 'is_featured': True, 'is_trending': True,
            },
            {
                'name': 'Karnak Temple', 'name_ar': 'معبد الكرنك',
                'place_type': 'heritage', 'category': 'Temples & Tombs',
                'description': 'The Karnak Temple Complex is a vast mix of temples, chapels, and pylons. It was the most important religious center of ancient Egypt dedicated to the god Amun.',
                'description_ar': 'مجمع معابد الكرنك هو أكبر مجمع ديني في العالم القديم.',
                'historical_info': 'Construction began in the Middle Kingdom and continued through the Ptolemaic period, spanning over 2,000 years of construction.',
                'city': 'Luxor', 'governorate': 'Luxor',
                'latitude': 25.7188, 'longitude': 32.6573,
                'activity_type': 'sightseeing', 'price_level': 2,
                'entry_fee': 150, 'opening_hours': '6:00 AM - 5:30 PM',
                'rating': 4.7, 'is_featured': True, 'is_trending': True,
            },
            {
                'name': 'Valley of the Kings', 'name_ar': 'وادي الملوك',
                'place_type': 'heritage', 'category': 'Temples & Tombs',
                'description': 'The Valley of the Kings is a burial ground for pharaohs and powerful nobles of the New Kingdom. It contains over 60 tombs including that of Tutankhamun.',
                'historical_info': 'The most famous tomb, KV62 of Tutankhamun, was discovered by Howard Carter in 1922.',
                'city': 'Luxor', 'governorate': 'Luxor',
                'latitude': 25.7402, 'longitude': 32.6014,
                'activity_type': 'sightseeing', 'price_level': 2,
                'entry_fee': 240, 'opening_hours': '6:00 AM - 4:00 PM',
                'rating': 4.6, 'is_featured': True,
            },
            {
                'name': 'Khan El-Khalili Bazaar', 'name_ar': 'خان الخليلي',
                'place_type': 'heritage', 'category': 'Islamic Heritage',
                'description': 'Khan El-Khalili is one of the oldest and most famous bazaars in the Middle East. A vibrant marketplace full of traditional crafts, spices, jewelry, and Egyptian souvenirs.',
                'historical_info': 'Founded in 1382 during the Mamluk era, it has served as a major commercial center for over 600 years.',
                'city': 'Cairo', 'governorate': 'Cairo',
                'latitude': 30.0477, 'longitude': 31.2625,
                'activity_type': 'cultural', 'price_level': 1,
                'entry_fee': 0, 'opening_hours': '9:00 AM - 11:00 PM',
                'rating': 4.4, 'is_trending': True,
            },
            {
                'name': 'Grand Egyptian Museum', 'name_ar': 'المتحف المصري الكبير',
                'place_type': 'heritage', 'category': 'Museums',
                'description': 'The Grand Egyptian Museum is the largest archaeological museum in the world, housing over 100,000 artifacts including the complete Tutankhamun collection.',
                'city': 'Giza', 'governorate': 'Giza',
                'latitude': 29.9946, 'longitude': 31.1171,
                'activity_type': 'cultural', 'price_level': 2,
                'entry_fee': 500, 'opening_hours': '9:00 AM - 7:00 PM',
                'rating': 4.9, 'is_featured': True, 'is_trending': True,
            },
            {
                'name': 'Abu Simbel Temples', 'name_ar': 'معابد أبو سمبل',
                'place_type': 'heritage', 'category': 'Temples & Tombs',
                'description': 'Two massive rock-cut temples built by Pharaoh Ramesses II, featuring four colossal statues. A UNESCO World Heritage site famously relocated to save it from Nile flooding.',
                'city': 'Aswan', 'governorate': 'Aswan',
                'latitude': 22.3360, 'longitude': 31.6256,
                'activity_type': 'sightseeing', 'price_level': 3,
                'entry_fee': 255, 'opening_hours': '5:00 AM - 6:00 PM',
                'rating': 4.8, 'is_featured': True,
            },
            # Medical/Wellness
            {
                'name': 'Siwa Oasis Wellness', 'name_ar': 'واحة سيوة العلاجية',
                'place_type': 'medical', 'category': 'Oasis Wellness',
                'description': 'Siwa Oasis is famous for its natural hot springs, salt lakes, and sand therapy. A therapeutic paradise offering traditional healing methods in the heart of the Western Desert.',
                'description_ar': 'واحة سيوة شهيرة بعيونها الحارة وبحيراتها المالحة والعلاج بالرمال.',
                'historical_info': 'Siwa has been used for therapeutic purposes for centuries. The hot springs contain minerals beneficial for arthritis and skin conditions.',
                'city': 'Siwa', 'governorate': 'Matrouh',
                'latitude': 29.2032, 'longitude': 25.5195,
                'activity_type': 'therapy', 'price_level': 2,
                'entry_fee': 50, 'opening_hours': 'Open 24 hours',
                'rating': 4.5, 'is_featured': True, 'is_trending': True,
            },
            {
                'name': 'Cleopatra Spring', 'name_ar': 'عين كليوباترا',
                'place_type': 'medical', 'category': 'Hot Springs',
                'description': 'A natural hot spring in Siwa Oasis where Cleopatra is said to have bathed. The warm sulfuric water is known for its healing properties for skin and joint conditions.',
                'city': 'Siwa', 'governorate': 'Matrouh',
                'latitude': 29.2012, 'longitude': 25.5280,
                'activity_type': 'relaxation', 'price_level': 1,
                'entry_fee': 30, 'rating': 4.3,
                'is_featured': True,
            },
            {
                'name': 'Helwan Sulfur Springs', 'name_ar': 'عيون حلوان الكبريتية',
                'place_type': 'medical', 'category': 'Hot Springs',
                'description': 'Historic sulfur springs near Cairo known for treating rheumatic diseases, skin conditions, and respiratory problems. One of Egypt\'s oldest therapeutic destinations.',
                'city': 'Helwan', 'governorate': 'Cairo',
                'latitude': 29.8420, 'longitude': 31.3340,
                'activity_type': 'therapy', 'price_level': 1,
                'entry_fee': 40, 'rating': 4.0,
            },
            {
                'name': 'Ras Mohammed Diving', 'name_ar': 'رأس محمد للغوص',
                'place_type': 'medical', 'category': 'Diving & Marine',
                'description': 'A world-renowned marine national park at the southern tip of Sinai. Crystal-clear waters with vibrant coral reefs offering therapeutic diving and snorkeling experiences.',
                'city': 'Sharm El-Sheikh', 'governorate': 'South Sinai',
                'latitude': 27.7325, 'longitude': 34.2547,
                'activity_type': 'diving', 'price_level': 3,
                'entry_fee': 100, 'rating': 4.7,
                'is_trending': True,
            },
            {
                'name': 'Dakhla Oasis Sand Therapy', 'name_ar': 'العلاج بالرمال - الداخلة',
                'place_type': 'medical', 'category': 'Sand Therapy',
                'description': 'Dakhla Oasis is renowned for its sand burial therapy. Patients are buried in heated desert sand to treat joint pain, rheumatism, and various musculoskeletal conditions.',
                'historical_info': 'Sand therapy in Dakhla follows ancient Pharaonic healing traditions passed down through generations.',
                'city': 'Dakhla', 'governorate': 'New Valley',
                'latitude': 25.4833, 'longitude': 29.0000,
                'activity_type': 'therapy', 'price_level': 1,
                'entry_fee': 80, 'rating': 4.2,
                'is_featured': True,
            },
            {
                'name': 'Moses Hot Springs', 'name_ar': 'حمامات موسى',
                'place_type': 'medical', 'category': 'Hot Springs',
                'description': 'Natural hot sulfuric springs at the foot of Mount Sinai. The mineral-rich water reaches 72°C and is used to treat skin diseases, rheumatism, and bone ailments.',
                'city': 'Ras Sedr', 'governorate': 'South Sinai',
                'latitude': 29.2500, 'longitude': 33.2333,
                'activity_type': 'therapy', 'price_level': 1,
                'entry_fee': 25, 'rating': 4.1,
            },
        ]

        for pd in places_data:
            cat_name = pd.pop('category')
            pd['category'] = cat_objs.get(cat_name)
            Place.objects.get_or_create(name=pd['name'], defaults=pd)

        # Admin user
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@egypt.com', 'admin123')
            UserProfile.objects.get_or_create(user=admin, defaults={'interests': 'both', 'budget': 'mid'})

        # Demo user
        if not User.objects.filter(username='traveler').exists():
            user = User.objects.create_user('traveler', 'traveler@egypt.com', 'travel123', first_name='Ahmed', last_name='Hassan')
            UserProfile.objects.get_or_create(user=user, defaults={'interests': 'both', 'budget': 'mid'})

        self.stdout.write(self.style.SUCCESS(
            f'✅ Seeded: {Category.objects.count()} categories, {Place.objects.count()} places, {User.objects.count()} users'
        ))
