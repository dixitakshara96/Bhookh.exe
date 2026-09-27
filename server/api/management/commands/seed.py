from datetime import datetime, timezone, timedelta
from django.core.management.base import BaseCommand
from api.models import User, Restaurant, Category, Dish, Review, Favourite

IST = timezone(timedelta(hours=5, minutes=30))

class Command(BaseCommand):
    help = 'Seeds initial Indian restaurant data, users, dishes, reviews, and favourites idempotently with IST timestamps.'

    def handle(self, *args, **options):
        self.stdout.write("Starting idempotent DB seed with IST timestamps...")

        # 1. Users
        users_data = [
            {"email": "asha.rao@example.com", "name": "Asha Rao", "role": "user", "password": "strongpassword123"},
            {"email": "rajesh.kumar@example.com", "name": "Rajesh Kumar", "role": "user", "password": "password123"},
            {"email": "priya.sharma@example.com", "name": "Priya Sharma", "role": "admin", "password": "adminpassword123"},
            {"email": "vikram.patel@example.com", "name": "Vikram Patel", "role": "user", "password": "userpassword123"},
        ]
        users = {}
        for udata in users_data:
            user, created = User.objects.get_or_create(
                email=udata["email"],
                defaults={
                    "name": udata["name"],
                    "role": udata["role"]
                }
            )
            if created:
                user.set_password(udata["password"])
                user.save()
                self.stdout.write(f"Created user: {user.name} ({user.email})")
            else:
                self.stdout.write(f"User already exists: {user.name}")
            users[udata["email"]] = user

        # 2. Restaurants
        restaurants_data = [
            {"name": "Spice House", "area": "Koramangala", "address": "123, 80 Feet Road, 4th Block, Koramangala", "phone": "+919876543210", "is_verified": True},
            {"name": "Royal Punjab Dhaba", "area": "Indiranagar", "address": "456, 100 Feet Road, Indiranagar", "phone": "+919876543211", "is_verified": True},
            {"name": "South Taste Express", "area": "Jayanagar", "address": "789, 4th Main Road, Jayanagar", "phone": "+919876543212", "is_verified": True},
        ]
        restaurants = {}
        for rdata in restaurants_data:
            r, created = Restaurant.objects.get_or_create(
                name=rdata["name"],
                defaults=rdata
            )
            if created:
                self.stdout.write(f"Created restaurant: {r.name}")
            restaurants[rdata["name"]] = r

        # 3. Categories
        categories_data = ["Noodles & Rice", "North Indian Mains", "South Indian Tiffin", "Starters & Snacks"]
        categories = {}
        for cname in categories_data:
            c, created = Category.objects.get_or_create(name=cname)
            categories[cname] = c

        # 4. Dishes
        dishes_data = [
            {
                "restaurant": restaurants["Spice House"],
                "category": categories["Noodles & Rice"],
                "name": "Mushroom Hakka Noodles",
                "description": "Wok-tossed noodles with fresh vegetables and button mushrooms.",
                "price": 22000,
                "ingredients": ["noodles", "mushroom", "cabbage", "carrot", "soy sauce"],
                "ingredients_to_avoid": ["soy"],
                "dietary_tags": ["vegetarian", "dairy_free"],
                "spice_level": 1,
                "can_be_customised": True,
                "is_active": True
            },
            {
                "restaurant": restaurants["Royal Punjab Dhaba"],
                "category": categories["North Indian Mains"],
                "name": "Paneer Butter Masala",
                "description": "Cottage cheese cubes cooked in rich tomato and cashew butter gravy.",
                "price": 28000,
                "ingredients": ["paneer", "butter", "tomato", "cashew", "cream"],
                "ingredients_to_avoid": ["dairy", "nuts"],
                "dietary_tags": ["vegetarian"],
                "spice_level": 2,
                "can_be_customised": True,
                "is_active": True
            },
            {
                "restaurant": restaurants["South Taste Express"],
                "category": categories["South Indian Tiffin"],
                "name": "Masala Dosa",
                "description": "Crispy fermented rice crepe stuffed with spiced potato mash.",
                "price": 12000,
                "ingredients": ["rice batter", "potato", "onion", "mustard seeds", "curry leaves"],
                "ingredients_to_avoid": [],
                "dietary_tags": ["vegetarian", "vegan"],
                "spice_level": 1,
                "can_be_customised": False,
                "is_active": True
            }
        ]
        dishes = {}
        for ddata in dishes_data:
            d, created = Dish.objects.get_or_create(
                restaurant=ddata["restaurant"],
                name=ddata["name"],
                defaults=ddata
            )
            dishes[ddata["name"]] = d

        # 5. Reviews
        reviews_data = [
            {
                "dish": dishes["Mushroom Hakka Noodles"],
                "user": users["asha.rao@example.com"],
                "rating": 5,
                "comment": "Perfectly balanced taste and not too spicy.",
                "spice_feedback": "mild",
                "taste_feedback": "tasty",
                "portion_feedback": "good"
            },
            {
                "dish": dishes["Paneer Butter Masala"],
                "user": users["rajesh.kumar@example.com"],
                "rating": 4,
                "comment": "Rich and creamy gravy, goes well with Naan.",
                "spice_feedback": "medium",
                "taste_feedback": "delicious",
                "portion_feedback": "generous"
            }
        ]
        for revdata in reviews_data:
            Review.objects.get_or_create(
                dish=revdata["dish"],
                user=revdata["user"],
                defaults=revdata
            )

        # 6. Favourites
        favs_data = [
            {"user": users["asha.rao@example.com"], "dish": dishes["Mushroom Hakka Noodles"]},
            {"user": users["rajesh.kumar@example.com"], "dish": dishes["Paneer Butter Masala"]}
        ]
        for fdata in favs_data:
            Favourite.objects.get_or_create(
                user=fdata["user"],
                dish=fdata["dish"]
            )

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully without duplicates!"))
