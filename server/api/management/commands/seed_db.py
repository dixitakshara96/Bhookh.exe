import random
from django.core.management.base import BaseCommand
from api.models import User, Restaurant, Category, Dish, Review

class Command(BaseCommand):
    help = 'Seeds the database with highly realistic data for the NIVAALA app'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding realistic data...')

        # Clear existing data
        User.objects.all().delete()
        Restaurant.objects.all().delete()
        Category.objects.all().delete()
        Dish.objects.all().delete()
        Review.objects.all().delete()

        # Create Users
        user1 = User.objects.create_user(email='akshara.dixit@example.com', name='Akshara Dixit', password='password')
        user2 = User.objects.create_user(email='test@example.com', name='Test Diner', password='password')

        # Create Categories
        cat_noodles = Category.objects.create(name='Noodles & Asian')
        cat_north = Category.objects.create(name='North Indian Mains')
        cat_light = Category.objects.create(name='Light Meals')

        # Create Restaurants
        r_swastik = Restaurant.objects.create(name='Swastik Bhojnalaya', area='Alambagh', address='14, Main Market, Alambagh, Lucknow', phone='+919876543201', is_verified=True)
        r_greenwok = Restaurant.objects.create(name='Green Wok', area='Gomti Nagar', address='Plot 12, Riverside Mall Road, Gomti Nagar, Lucknow', phone='+919876543202', is_verified=True)
        r_awadh = Restaurant.objects.create(name='Awadh Delight', area='Hazratganj', address='Shop 4, Regency Plaza, Hazratganj', phone='+919876543203', is_verified=True)
        r_thegreen = Restaurant.objects.create(name='The Green Kitchen', area='Hazratganj', address='Ground Floor, Eco Hub', phone='+919876543204', is_verified=True)

        # Create Dishes
        dish1 = Dish.objects.create(
            restaurant=r_swastik, category=cat_north, 
            name='Dal Makhani (No Onion, No Garlic)',
            description='Slow-cooked black lentils and kidney beans simmered overnight in pure desi ghee.',
            price=21000, 
            ingredients=['black lentils', 'kidney beans', 'tomato puree', 'desi ghee', 'cream'],
            ingredients_to_avoid=['onion', 'garlic', 'cashew', 'nuts'], 
            dietary_tags=['vegetarian', 'jain'], 
            spice_level=1,
            image_url='https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800&q=80'
        )

        dish2 = Dish.objects.create(
            restaurant=r_greenwok, category=cat_noodles, 
            name='Steamed Vegetable Hakka Noodles',
            description='Wok-tossed noodles with fresh vegetables, zero soy sauce, and mild spices.',
            price=19000, 
            ingredients=['wheat noodles', 'cabbage', 'bell peppers', 'carrots', 'sesame oil'],
            ingredients_to_avoid=['cashew', 'dairy'], 
            dietary_tags=['vegan', 'dairy-free'], 
            spice_level=1,
            image_url='https://images.unsplash.com/photo-1612929633738-8fe44f7ec841?w=800&q=80'
        )

        dish3 = Dish.objects.create(
            restaurant=r_awadh, category=cat_north, 
            name='Paneer Malai Tikka',
            description='Cubes of cottage cheese marinated in hung curd and cardamom, grilled perfectly.',
            price=29000, 
            ingredients=['paneer', 'hung curd', 'green cardamom', 'white pepper'],
            ingredients_to_avoid=['cashew', 'gluten'], 
            dietary_tags=['vegetarian', 'gluten-free'], 
            spice_level=0,
            image_url='https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=800&q=80'
        )

        dish4 = Dish.objects.create(
            restaurant=r_thegreen, category=cat_light, 
            name='Yellow Moong Dal Khichdi',
            description='Comforting blend of rice and moong dal cooked with a mild cumin tadka.',
            price=16000, 
            ingredients=['rice', 'moong dal', 'cumin', 'ghee', 'turmeric'],
            ingredients_to_avoid=['msg', 'preservatives', 'nuts'], 
            dietary_tags=['vegetarian', 'gluten-free', 'jain'], 
            spice_level=1,
            image_url='https://images.unsplash.com/photo-1596797038530-2c107229654b?w=800&q=80'
        )
        
        dish5 = Dish.objects.create(
            restaurant=r_greenwok, category=cat_noodles, 
            name='Mushroom Hakka Noodles',
            description='Gluten-free Hakka Noodles tossed with crisp julienned bell peppers and button mushrooms.',
            price=22000, 
            ingredients=['wheat noodles', 'fresh button mushrooms', 'green cabbage', 'bell peppers', 'carrots', 'cold-pressed sesame oil', 'naturally brewed dark soy'],
            ingredients_to_avoid=['cashews', 'peanuts', 'dairy'], 
            dietary_tags=['vegetarian', 'dairy-free'], 
            spice_level=2,
            image_url='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&q=80'
        )

        # Create Reviews
        Review.objects.create(dish=dish5, user=user1, rating=5, comment='Perfect mild spice. Confirmed dairy-free with zero stomach irritation.', taste_feedback='Strict Dairy-Free', portion_feedback='good')
        Review.objects.create(dish=dish5, user=user2, rating=4, comment='Very fresh mushrooms and definitely no cashews or nuts detected.', taste_feedback='Nut Allergy Safe', portion_feedback='large')
        
        Review.objects.create(dish=dish1, user=user1, rating=5, comment='Absolutely authentic and safe for Jain diet.', taste_feedback='Jain Safe', portion_feedback='generous')
        Review.objects.create(dish=dish4, user=user2, rating=5, comment='Very soothing on the stomach.', taste_feedback='Digestible', portion_feedback='perfect')

        self.stdout.write(self.style.SUCCESS('Successfully seeded realistic data!'))
