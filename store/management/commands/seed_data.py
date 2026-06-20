from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Place, UserProfile, Doctor, DoctorCase


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
            {'name': 'Pyramids of Giza', 'name_ar': 'أهرامات الجيزة', 'place_type': 'heritage', 'category': 'Pyramids',
             'description': 'The Great Pyramids of Giza are among the Seven Wonders of the Ancient World. Built as royal tombs during the Fourth Dynasty.',
             'historical_info': 'The Great Pyramid of Khufu was built around 2560 BC.',
             'city': 'Giza', 'governorate': 'Giza', 'latitude': 29.9792, 'longitude': 31.1342,
             'activity_type': 'sightseeing', 'price_level': 2, 'entry_fee': 200, 'opening_hours': '8:00 AM - 5:00 PM',
             'rating': 4.8, 'is_featured': True, 'is_trending': True},
            {'name': 'Karnak Temple', 'name_ar': 'معبد الكرنك', 'place_type': 'heritage', 'category': 'Temples & Tombs',
             'description': 'The Karnak Temple Complex is a vast mix of temples, chapels, and pylons dedicated to the god Amun.',
             'city': 'Luxor', 'governorate': 'Luxor', 'latitude': 25.7188, 'longitude': 32.6573,
             'activity_type': 'sightseeing', 'price_level': 2, 'entry_fee': 150, 'opening_hours': '6:00 AM - 5:30 PM',
             'rating': 4.7, 'is_featured': True, 'is_trending': True},
            {'name': 'Valley of the Kings', 'name_ar': 'وادي الملوك', 'place_type': 'heritage', 'category': 'Temples & Tombs',
             'description': 'Burial ground for pharaohs with over 60 tombs including Tutankhamun.',
             'city': 'Luxor', 'governorate': 'Luxor', 'latitude': 25.7402, 'longitude': 32.6014,
             'activity_type': 'sightseeing', 'price_level': 2, 'entry_fee': 240, 'rating': 4.6, 'is_featured': True},
            {'name': 'Khan El-Khalili Bazaar', 'name_ar': 'خان الخليلي', 'place_type': 'heritage', 'category': 'Islamic Heritage',
             'description': 'One of the oldest bazaars in the Middle East, full of traditional crafts and spices.',
             'city': 'Cairo', 'governorate': 'Cairo', 'latitude': 30.0477, 'longitude': 31.2625,
             'activity_type': 'cultural', 'price_level': 1, 'entry_fee': 0, 'rating': 4.4, 'is_trending': True},
            {'name': 'Grand Egyptian Museum', 'name_ar': 'المتحف المصري الكبير', 'place_type': 'heritage', 'category': 'Museums',
             'description': 'Largest archaeological museum in the world with over 100,000 artifacts.',
             'city': 'Giza', 'governorate': 'Giza', 'latitude': 29.9946, 'longitude': 31.1171,
             'activity_type': 'cultural', 'price_level': 2, 'entry_fee': 500, 'rating': 4.9, 'is_featured': True, 'is_trending': True},
            {'name': 'Abu Simbel Temples', 'name_ar': 'معابد أبو سمبل', 'place_type': 'heritage', 'category': 'Temples & Tombs',
             'description': 'Two massive rock-cut temples built by Ramesses II. A UNESCO World Heritage site.',
             'city': 'Aswan', 'governorate': 'Aswan', 'latitude': 22.3360, 'longitude': 31.6256,
             'activity_type': 'sightseeing', 'price_level': 3, 'entry_fee': 255, 'rating': 4.8, 'is_featured': True},
            # Medical
            {'name': 'Siwa Oasis Wellness', 'name_ar': 'واحة سيوة العلاجية', 'place_type': 'medical', 'category': 'Oasis Wellness',
             'description': 'Siwa Oasis offers natural hot springs, salt lakes, and sand therapy for various conditions.',
             'city': 'Siwa', 'governorate': 'Matrouh', 'latitude': 29.2032, 'longitude': 25.5195,
             'activity_type': 'therapy', 'price_level': 2, 'entry_fee': 50,
             'rating': 4.5, 'is_featured': True, 'is_trending': True},
            {'name': 'Cleopatra Spring', 'name_ar': 'عين كليوباترا', 'place_type': 'medical', 'category': 'Hot Springs',
             'description': 'Natural hot spring where Cleopatra is said to have bathed. Known for healing properties.',
             'city': 'Siwa', 'governorate': 'Matrouh', 'latitude': 29.2012, 'longitude': 25.5280,
             'activity_type': 'relaxation', 'price_level': 1, 'entry_fee': 30, 'rating': 4.3, 'is_featured': True},
            {'name': 'Helwan Sulfur Springs', 'name_ar': 'عيون حلوان الكبريتية', 'place_type': 'medical', 'category': 'Hot Springs',
             'description': 'Historic sulfur springs treating rheumatic diseases and skin conditions.',
             'city': 'Helwan', 'governorate': 'Cairo', 'latitude': 29.8420, 'longitude': 31.3340,
             'activity_type': 'therapy', 'price_level': 1, 'entry_fee': 40, 'rating': 4.0},
            {'name': 'Ras Mohammed Diving', 'name_ar': 'رأس محمد للغوص', 'place_type': 'medical', 'category': 'Diving & Marine',
             'description': 'World-renowned marine park with crystal-clear waters and vibrant coral reefs.',
             'city': 'Sharm El-Sheikh', 'governorate': 'South Sinai', 'latitude': 27.7325, 'longitude': 34.2547,
             'activity_type': 'diving', 'price_level': 3, 'entry_fee': 100, 'rating': 4.7, 'is_trending': True},
            {'name': 'Dakhla Sand Therapy', 'name_ar': 'العلاج بالرمال - الداخلة', 'place_type': 'medical', 'category': 'Sand Therapy',
             'description': 'Renowned for sand burial therapy treating joint pain and rheumatism.',
             'city': 'Dakhla', 'governorate': 'New Valley', 'latitude': 25.4833, 'longitude': 29.0000,
             'activity_type': 'therapy', 'price_level': 1, 'entry_fee': 80, 'rating': 4.2, 'is_featured': True},
            {'name': 'Moses Hot Springs', 'name_ar': 'حمامات موسى', 'place_type': 'medical', 'category': 'Hot Springs',
             'description': 'Natural hot sulfuric springs at the foot of Mount Sinai with mineral-rich water.',
             'city': 'Ras Sedr', 'governorate': 'South Sinai', 'latitude': 29.2500, 'longitude': 33.2333,
             'activity_type': 'therapy', 'price_level': 1, 'entry_fee': 25, 'rating': 4.1},
        ]

        place_objs = {}
        for pd in places_data:
            cat_name = pd.pop('category')
            pd['category'] = cat_objs.get(cat_name)
            p, _ = Place.objects.get_or_create(name=pd['name'], defaults=pd)
            place_objs[p.name] = p

        # ─── Doctors ───
        doctors_data = [
            {'name': 'Ahmed El-Shazly', 'name_ar': 'أحمد الشاذلي', 'specialization': 'rheumatology',
             'title': 'Professor of Rheumatology', 'years_experience': 22, 'consultation_fee': 500,
             'bio': 'Professor of Rheumatology at Cairo University with over 22 years of experience in treating joint disorders using natural thermal therapy. Published 40+ papers on balneotherapy.',
             'bio_ar': 'أستاذ أمراض الروماتيزم بجامعة القاهرة، خبرة أكثر من 22 عامًا في علاج أمراض المفاصل.',
             'phone': '+20 100 123 4567', 'email': 'dr.shazly@egyptwellness.com',
             'available_days': 'Sun, Mon, Tue, Wed', 'available_hours': '9:00 AM - 3:00 PM',
             'places': ['Siwa Oasis Wellness', 'Helwan Sulfur Springs'], 'rating': 4.8, 'total_cases': 350},
            {'name': 'Fatma Hassan', 'name_ar': 'فاطمة حسن', 'specialization': 'dermatology',
             'title': 'Consultant Dermatologist', 'years_experience': 15, 'consultation_fee': 400,
             'bio': 'Consultant Dermatologist specializing in treating skin conditions with natural mineral water and mud therapy. Expert in psoriasis and eczema treatment.',
             'phone': '+20 101 234 5678', 'email': 'dr.fatma@egyptwellness.com',
             'available_days': 'Sun, Tue, Thu', 'available_hours': '10:00 AM - 4:00 PM',
             'places': ['Cleopatra Spring', 'Moses Hot Springs'], 'rating': 4.6, 'total_cases': 210},
            {'name': 'Mohamed Abdel-Rahman', 'name_ar': 'محمد عبد الرحمن', 'specialization': 'physiotherapy',
             'title': 'Senior Physiotherapist', 'years_experience': 18, 'consultation_fee': 350,
             'bio': 'Senior Physiotherapist with expertise in sand therapy and hydrotherapy techniques. Treats sports injuries, back pain, and post-surgical rehabilitation.',
             'phone': '+20 102 345 6789', 'email': 'dr.mohamad@egyptwellness.com',
             'available_days': 'Sat, Sun, Mon, Wed', 'available_hours': '8:00 AM - 2:00 PM',
             'places': ['Dakhla Sand Therapy', 'Siwa Oasis Wellness'], 'rating': 4.7, 'total_cases': 480},
            {'name': 'Sarah El-Masry', 'name_ar': 'سارة المصري', 'specialization': 'respiratory',
             'title': 'Pulmonologist', 'years_experience': 12, 'consultation_fee': 450,
             'bio': 'Pulmonologist specializing in respiratory rehabilitation using salt cave therapy and mineral inhalation techniques at Siwa Oasis.',
             'phone': '+20 103 456 7890', 'email': 'dr.sarah@egyptwellness.com',
             'available_days': 'Mon, Wed, Thu', 'available_hours': '9:00 AM - 5:00 PM',
             'places': ['Siwa Oasis Wellness'], 'rating': 4.5, 'total_cases': 150},
            {'name': 'Khaled Youssef', 'name_ar': 'خالد يوسف', 'specialization': 'orthopedics',
             'title': 'Orthopedic Surgeon', 'years_experience': 20, 'consultation_fee': 600,
             'bio': 'Orthopedic Surgeon combining modern techniques with traditional sand and hot spring therapies for bone and joint rehabilitation.',
             'phone': '+20 104 567 8901', 'email': 'dr.khaled@egyptwellness.com',
             'available_days': 'Sun, Tue, Thu', 'available_hours': '10:00 AM - 3:00 PM',
             'places': ['Helwan Sulfur Springs', 'Moses Hot Springs', 'Dakhla Sand Therapy'], 'rating': 4.9, 'total_cases': 520},
            {'name': 'Nour El-Din Ibrahim', 'name_ar': 'نور الدين إبراهيم', 'specialization': 'hydrotherapy',
             'title': 'Hydrotherapy Specialist', 'years_experience': 10, 'consultation_fee': 300,
             'bio': 'Hydrotherapy Specialist focusing on aquatic rehabilitation for chronic pain management. Expert in thermal water treatments for stress and anxiety.',
             'phone': '+20 105 678 9012', 'email': 'dr.nour@egyptwellness.com',
             'available_days': 'Sat, Mon, Wed, Thu', 'available_hours': '8:00 AM - 4:00 PM',
             'places': ['Cleopatra Spring', 'Helwan Sulfur Springs'], 'rating': 4.4, 'total_cases': 180},
            {'name': 'Amira Soliman', 'name_ar': 'أميرة سليمان', 'specialization': 'naturopathy',
             'title': 'Naturopathic Doctor', 'years_experience': 8, 'consultation_fee': 280,
             'bio': 'Naturopathic Doctor combining herbal medicine, mineral therapy, and traditional Egyptian healing techniques.',
             'phone': '+20 106 789 0123', 'email': 'dr.amira@egyptwellness.com',
             'available_days': 'Sun, Tue, Wed', 'available_hours': '9:00 AM - 3:00 PM',
             'places': ['Siwa Oasis Wellness', 'Dakhla Sand Therapy'], 'rating': 4.3, 'total_cases': 95},
            {'name': 'Hassan Mostafa', 'name_ar': 'حسن مصطفى', 'specialization': 'balneotherapy',
             'title': 'Balneotherapy Expert', 'years_experience': 25, 'consultation_fee': 550,
             'bio': 'Egypt\'s leading Balneotherapy expert with 25 years of experience. Pioneer in therapeutic mineral bath treatments.',
             'phone': '+20 107 890 1234', 'email': 'dr.hassan@egyptwellness.com',
             'available_days': 'Sat, Sun, Mon, Tue', 'available_hours': '8:00 AM - 2:00 PM',
             'places': ['Moses Hot Springs', 'Cleopatra Spring', 'Helwan Sulfur Springs'], 'rating': 4.8, 'total_cases': 680},
        ]

        # Cases data
        cases_data = [
            {'doctor': 'Ahmed El-Shazly', 'patient_name': 'Patient A.M.', 'condition': 'Rheumatoid Arthritis',
             'treatment': 'Combined hot spring immersion therapy with targeted physiotherapy exercises over 6 weeks.',
             'outcome': 'Significant reduction in joint inflammation and pain. Patient regained 80% mobility.', 'duration_weeks': 6, 'is_success': True},
            {'doctor': 'Ahmed El-Shazly', 'patient_name': 'Patient S.K.', 'condition': 'Chronic Back Pain',
             'treatment': 'Mineral-rich mud therapy combined with sulfur bath sessions 3 times weekly.',
             'outcome': 'Pain levels decreased by 70%. Patient returned to normal daily activities.', 'duration_weeks': 4, 'is_success': True},
            {'doctor': 'Fatma Hassan', 'patient_name': 'Patient L.H.', 'condition': 'Psoriasis',
             'treatment': 'Natural mineral water immersion therapy combined with Dead Sea salt application.',
             'outcome': 'Psoriasis plaques reduced by 85%. Remission maintained for 8 months.', 'duration_weeks': 8, 'is_success': True},
            {'doctor': 'Fatma Hassan', 'patient_name': 'Patient R.A.', 'condition': 'Chronic Eczema',
             'treatment': 'Sulfuric spring water therapy with herbal compress applications.',
             'outcome': 'Skin condition significantly improved with reduced flare-ups.', 'duration_weeks': 5, 'is_success': True},
            {'doctor': 'Mohamed Abdel-Rahman', 'patient_name': 'Patient Y.M.', 'condition': 'Sports Knee Injury',
             'treatment': 'Hot sand therapy combined with progressive resistance training and hydrotherapy.',
             'outcome': 'Full recovery achieved. Returned to competitive sports after 10 weeks.', 'duration_weeks': 10, 'is_success': True},
            {'doctor': 'Mohamed Abdel-Rahman', 'patient_name': 'Patient N.S.', 'condition': 'Post-Surgery Hip Rehab',
             'treatment': 'Sand burial therapy sessions alternated with aquatic exercises in mineral pools.',
             'outcome': 'Excellent recovery. Full range of motion restored.', 'duration_weeks': 12, 'is_success': True},
            {'doctor': 'Khaled Youssef', 'patient_name': 'Patient F.T.', 'condition': 'Osteoarthritis',
             'treatment': 'Combination of hot spring therapy, therapeutic ultrasound, and joint mobilization.',
             'outcome': 'Significant pain relief and improved joint function.', 'duration_weeks': 8, 'is_success': True},
            {'doctor': 'Khaled Youssef', 'patient_name': 'Patient M.A.', 'condition': 'Spinal Disc Herniation',
             'treatment': 'Progressive rehabilitation including sand therapy and mineral water traction.',
             'outcome': 'Avoided surgery. 90% symptom relief achieved.', 'duration_weeks': 16, 'is_success': True},
            {'doctor': 'Sarah El-Masry', 'patient_name': 'Patient H.B.', 'condition': 'Chronic Bronchitis',
             'treatment': 'Salt cave inhalation therapy combined with mineral steam sessions.',
             'outcome': 'Respiratory function improved by 40%. Reduced medication dependency.', 'duration_weeks': 6, 'is_success': True},
            {'doctor': 'Hassan Mostafa', 'patient_name': 'Patient O.K.', 'condition': 'Fibromyalgia',
             'treatment': 'Systematic balneotherapy protocol including mineral baths and thermal mud applications.',
             'outcome': 'Pain levels significantly reduced. Sleep quality improved dramatically.', 'duration_weeks': 8, 'is_success': True},
            {'doctor': 'Hassan Mostafa', 'patient_name': 'Patient D.R.', 'condition': 'Chronic Stress Syndrome',
             'treatment': 'Relaxation-focused mineral bath therapy with aromatic sulfur inhalation.',
             'outcome': 'Cortisol levels normalized. Patient reported 90% improvement in wellbeing.', 'duration_weeks': 3, 'is_success': True},
            {'doctor': 'Nour El-Din Ibrahim', 'patient_name': 'Patient W.S.', 'condition': 'Sciatica',
             'treatment': 'Aquatic therapy in mineral-rich pools combined with targeted stretching.',
             'outcome': 'Pain reduced by 75%. Maintained improvement at 6-month follow-up.', 'duration_weeks': 5, 'is_success': True},
        ]

        doc_objs = {}
        for dd in doctors_data:
            place_names = dd.pop('places')
            doc, created = Doctor.objects.get_or_create(name=dd['name'], defaults=dd)
            if created:
                for pn in place_names:
                    if pn in place_objs:
                        doc.places.add(place_objs[pn])
            doc_objs[doc.name] = doc

        for cd in cases_data:
            doc_name = cd.pop('doctor')
            if doc_name in doc_objs:
                cd['doctor'] = doc_objs[doc_name]
                DoctorCase.objects.get_or_create(
                    doctor=cd['doctor'], condition=cd['condition'],
                    defaults=cd
                )

        # Users
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@egypt.com', 'admin123')
            UserProfile.objects.get_or_create(user=admin, defaults={'interests': 'both', 'budget': 'mid'})
        if not User.objects.filter(username='traveler').exists():
            user = User.objects.create_user('traveler', 'traveler@egypt.com', 'travel123', first_name='Ahmed', last_name='Hassan')
            UserProfile.objects.get_or_create(user=user, defaults={'interests': 'both', 'budget': 'mid'})

        self.stdout.write(self.style.SUCCESS(
            f'✅ Seeded: {Category.objects.count()} categories, {Place.objects.count()} places, '
            f'{Doctor.objects.count()} doctors, {DoctorCase.objects.count()} cases, {User.objects.count()} users'
        ))
