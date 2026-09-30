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
        dishes = {}
        dishes_raw = [('Chicken Biryani', 'Aromatic basmati rice cooked with tender chicken pieces, blended with traditional Indian spices.', 25000, ['basmati rice', 'chicken', 'onion', 'tomato', 'ghee', 'yogurt', 'garlic', 'ginger', 'mint', 'coriander'], ['Dairy', 'Ghee'], ['high_protein', 'gluten_free'], 3, 0, 650, 35, 60, 20, 'Indian', 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800&q=80', 'Royal Punjab Dhaba', 'Noodles & Rice'), ('Paneer Butter Masala', 'Cottage cheese cubes cooked in a rich, creamy tomato and cashew butter gravy.', 28000, ['paneer', 'butter', 'tomato', 'cashew', 'cream', 'onion', 'garam masala', 'kasuri methi'], ['Dairy', 'Nuts'], ['vegetarian', 'gluten_free'], 2, 1, 450, 15, 25, 35, 'North Indian', 'https://images.unsplash.com/photo-1631452180519-c014fe946bc0?w=800&q=80', 'Royal Punjab Dhaba', 'North Indian Mains'), ('Masala Dosa', 'Crispy fermented rice crepe stuffed with spiced potato mash, served with coconut chutney.', 12000, ['rice batter', 'urad dal', 'potato', 'onion', 'mustard seeds', 'curry leaves', 'turmeric', 'coconut'], [], ['vegetarian', 'vegan', 'dairy_free'], 2, 0, 300, 8, 45, 10, 'South Indian', 'https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=800&q=80', 'South Taste Express', 'South Indian Tiffin'), ('Rajma Rice', 'Comforting North Indian dish of kidney beans in a thick onion-tomato gravy served over steamed rice.', 18000, ['kidney beans', 'rice', 'onion', 'tomato', 'garlic', 'ginger', 'coriander powder', 'cumin'], [], ['vegetarian', 'vegan', 'high_protein'], 2, 0, 400, 14, 65, 8, 'North Indian', 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800&q=80', 'Royal Punjab Dhaba', 'Noodles & Rice'), ('Veg Hakka Noodles', 'Wok-tossed noodles with fresh crunchy vegetables and a hint of soy sauce.', 20000, ['noodles', 'cabbage', 'carrot', 'capsicum', 'soy sauce', 'garlic', 'spring onion', 'vinegar'], ['Soy', 'Gluten'], ['vegetarian', 'vegan'], 1, 0, 380, 10, 60, 12, 'Indo-Chinese', 'https://images.unsplash.com/photo-1585032226651-759b368d7246?w=800&q=80', 'Spice House', 'Noodles & Rice'), ('Caesar Salad', 'Crisp romaine lettuce with parmesan cheese, croutons, and creamy Caesar dressing.', 22000, ['romaine lettuce', 'parmesan cheese', 'croutons', 'olive oil', 'lemon juice', 'egg', 'garlic', 'anchovies'], ['Dairy', 'Gluten', 'Egg', 'Seafood'], ['low_calorie'], 0, 0, 320, 10, 15, 25, 'Continental', 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&q=80', 'Spice House', 'Starters & Snacks'), ('Grilled Chicken Bowl', 'Healthy bowl with grilled chicken breast, quinoa, roasted vegetables, and a light vinaigrette.', 35000, ['chicken breast', 'quinoa', 'broccoli', 'bell peppers', 'olive oil', 'lemon', 'mixed herbs'], [], ['high_protein', 'low_calorie', 'gluten_free', 'dairy_free'], 1, 0, 420, 45, 35, 12, 'Continental', 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&q=80', 'Spice House', 'North Indian Mains'), ('Chocolate Brownie', 'Fudgy, rich, and decadent dark chocolate brownie with walnuts.', 15000, ['dark chocolate', 'butter', 'sugar', 'eggs', 'flour', 'walnuts', 'vanilla extract', 'cocoa powder'], ['Dairy', 'Egg', 'Gluten', 'Nuts'], ['vegetarian'], 0, 4, 480, 6, 55, 28, 'Dessert', 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=800&q=80', 'Spice House', 'Starters & Snacks'), ('Palak Paneer', 'Fresh spinach purée cooked with Indian spices and soft paneer cubes.', 26000, ['spinach', 'paneer', 'onion', 'tomato', 'garlic', 'cream', 'garam masala', 'ghee'], ['Dairy', 'Ghee'], ['vegetarian', 'gluten_free'], 2, 0, 380, 16, 12, 28, 'North Indian', 'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=800&q=80', 'Royal Punjab Dhaba', 'North Indian Mains'), ('Chicken Tikka Masala', 'Roasted marinated chicken chunks in a spiced curry sauce.', 32000, ['chicken', 'yogurt', 'tomato', 'cream', 'butter', 'ginger', 'garlic', 'spices'], ['Dairy'], ['high_protein', 'gluten_free'], 3, 1, 520, 32, 18, 36, 'North Indian', 'https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=800&q=80', 'Royal Punjab Dhaba', 'North Indian Mains'), ('Mutton Rogan Josh', 'Aromatic lamb dish of Persian origin, slow-cooked in a fiery red gravy.', 45000, ['mutton', 'onion', 'yogurt', 'kashmiri red chili', 'fennel powder', 'ginger powder', 'ghee', 'garam masala'], ['Dairy', 'Ghee'], ['high_protein', 'gluten_free'], 4, 0, 600, 38, 10, 45, 'Kashmiri', 'https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=800&q=80', 'Royal Punjab Dhaba', 'North Indian Mains'), ('Butter Naan', 'Soft and fluffy Indian flatbread brushed with generous amounts of butter.', 6000, ['refined flour', 'yogurt', 'milk', 'baking powder', 'butter', 'sugar', 'salt'], ['Gluten', 'Dairy'], ['vegetarian'], 0, 1, 250, 5, 40, 8, 'North Indian', 'https://images.unsplash.com/photo-1601050690117-94f5f6af8b70?w=800&q=80', 'Royal Punjab Dhaba', 'North Indian Mains'), ('Idli Sambar', 'Steamed rice cakes served with lentil soup and coconut chutney.', 10000, ['rice batter', 'urad dal', 'toor dal', 'tamarind', 'mixed vegetables', 'sambar powder', 'mustard seeds', 'coconut'], [], ['vegetarian', 'vegan', 'dairy_free', 'low_calorie'], 2, 0, 250, 8, 48, 4, 'South Indian', 'https://images.unsplash.com/photo-1589301760014-d929f39ce9b1?w=800&q=80', 'South Taste Express', 'South Indian Tiffin'), ('Medu Vada', 'Crispy fried lentil donuts served with chutney and sambar.', 11000, ['urad dal', 'onion', 'green chilies', 'ginger', 'curry leaves', 'peppercorns', 'oil'], [], ['vegetarian', 'vegan', 'dairy_free'], 1, 0, 350, 10, 30, 22, 'South Indian', 'https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=800&q=80', 'South Taste Express', 'South Indian Tiffin'), ('Chicken 65', 'Spicy, deep-fried chicken bites flavored with curry leaves and red chilies.', 24000, ['chicken', 'yogurt', 'rice flour', 'corn flour', 'red chili powder', 'curry leaves', 'ginger', 'garlic', 'lemon', 'oil'], ['Dairy'], ['high_protein', 'gluten_free'], 4, 0, 480, 28, 15, 35, 'South Indian', 'https://images.unsplash.com/photo-1610057099431-d73a1c9d2f2f?w=800&q=80', 'Spice House', 'Starters & Snacks'), ('Chole Bhature', 'Spicy chickpea curry served with fried puffed bread.', 18000, ['chickpeas', 'refined flour', 'onion', 'tomato', 'chole masala', 'yogurt', 'oil', 'green chilies'], ['Gluten', 'Dairy'], ['vegetarian'], 3, 0, 650, 15, 75, 30, 'North Indian', 'https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=800&q=80', 'Royal Punjab Dhaba', 'North Indian Mains'), ('Dal Makhani', 'Creamy, slow-cooked black lentils and kidney beans, finished with butter and cream.', 22000, ['black lentils', 'kidney beans', 'butter', 'cream', 'tomato', 'garlic', 'ginger', 'garam masala'], ['Dairy'], ['vegetarian', 'gluten_free'], 1, 0, 420, 14, 38, 25, 'North Indian', 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800&q=80', 'Royal Punjab Dhaba', 'North Indian Mains'), ('Tandoori Chicken', 'Whole chicken marinated in yogurt and spices, roasted in a clay oven.', 35000, ['chicken', 'yogurt', 'kashmiri chili powder', 'lemon juice', 'ginger', 'garlic', 'garam masala', 'mustard oil'], ['Dairy'], ['high_protein', 'low_calorie', 'gluten_free'], 3, 0, 400, 45, 8, 20, 'North Indian', 'https://images.unsplash.com/photo-1610057099443-67e04f5be9da?w=800&q=80', 'Royal Punjab Dhaba', 'Starters & Snacks'), ('Garlic Bread', 'Toasted baguette slices topped with garlic butter and herbs.', 12000, ['baguette', 'butter', 'garlic', 'parsley', 'salt'], ['Gluten', 'Dairy'], ['vegetarian'], 0, 0, 280, 5, 30, 15, 'Continental', 'https://images.unsplash.com/photo-1573140247632-f8fd74997d5c?w=800&q=80', 'Spice House', 'Starters & Snacks'), ('Margherita Pizza', 'Classic wood-fired pizza with tomato sauce, fresh mozzarella, and basil.', 30000, ['pizza dough', 'tomato sauce', 'mozzarella cheese', 'fresh basil', 'olive oil'], ['Gluten', 'Dairy'], ['vegetarian'], 0, 0, 600, 22, 65, 25, 'Italian', 'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=800&q=80', 'Spice House', 'North Indian Mains'), ('Penne Arrabbiata', 'Penne pasta tossed in a spicy and garlicky tomato sauce.', 28000, ['penne pasta', 'tomato', 'garlic', 'red chili flakes', 'olive oil', 'parsley', 'parmesan cheese'], ['Gluten', 'Dairy'], ['vegetarian'], 3, 0, 450, 12, 60, 18, 'Italian', 'https://images.unsplash.com/photo-1608897013039-887f214b983c?w=800&q=80', 'Spice House', 'North Indian Mains'), ('Fish and Chips', 'Crispy battered fish fillets served with thick-cut potato fries and tartar sauce.', 35000, ['white fish', 'flour', 'beer', 'potato', 'oil', 'mayonnaise', 'capers', 'lemon'], ['Seafood', 'Gluten', 'Egg'], [], 0, 0, 800, 25, 65, 45, 'British', 'https://images.unsplash.com/photo-1599084924616-e91011e3b62b?w=800&q=80', 'Spice House', 'Starters & Snacks'), ('Sushi Platter', 'Assorted fresh sushi rolls including salmon, tuna, and avocado.', 55000, ['sushi rice', 'nori', 'salmon', 'tuna', 'avocado', 'soy sauce', 'wasabi', 'pickled ginger'], ['Seafood', 'Soy'], ['dairy_free', 'high_protein'], 1, 0, 450, 30, 55, 10, 'Japanese', 'https://images.unsplash.com/photo-1553621042-f6e147245754?w=800&q=80', 'Spice House', 'Starters & Snacks'), ('Pad Thai', 'Stir-fried rice noodles with tofu, shrimp, peanuts, and tamarind sauce.', 32000, ['rice noodles', 'shrimp', 'tofu', 'peanuts', 'bean sprouts', 'egg', 'tamarind paste', 'fish sauce', 'lime'], ['Seafood', 'Peanut', 'Egg', 'Soy'], ['dairy_free'], 2, 2, 550, 22, 70, 20, 'Thai', 'https://images.unsplash.com/photo-1559314809-0d155014e29e?w=800&q=80', 'Spice House', 'Noodles & Rice'), ('Beef Burger', 'Juicy beef patty with lettuce, tomato, cheese, and special sauce in a brioche bun.', 30000, ['beef patty', 'brioche bun', 'cheddar cheese', 'lettuce', 'tomato', 'mayonnaise', 'ketchup', 'pickles'], ['Gluten', 'Dairy', 'Egg'], ['high_protein'], 1, 1, 750, 40, 45, 45, 'American', 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&q=80', 'Spice House', 'Starters & Snacks'), ('Greek Salad', 'Refreshing salad with cucumber, tomatoes, red onion, kalamata olives, and feta cheese.', 22000, ['cucumber', 'tomato', 'red onion', 'kalamata olives', 'feta cheese', 'olive oil', 'oregano'], ['Dairy'], ['vegetarian', 'gluten_free', 'low_calorie'], 0, 0, 300, 8, 15, 25, 'Mediterranean', 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=800&q=80', 'Spice House', 'Starters & Snacks'), ('Mushroom Risotto', 'Creamy arborio rice slow-cooked with earthy mushrooms and parmesan.', 32000, ['arborio rice', 'mushrooms', 'vegetable broth', 'onion', 'white wine', 'butter', 'parmesan cheese'], ['Dairy'], ['vegetarian', 'gluten_free'], 0, 0, 520, 12, 65, 22, 'Italian', 'https://images.unsplash.com/photo-1476124369491-e7addf5db371?w=800&q=80', 'Spice House', 'Noodles & Rice'), ('Prawn Curry', 'Succulent prawns simmered in a spicy and tangy coconut milk gravy.', 38000, ['prawns', 'coconut milk', 'onion', 'tomato', 'tamarind', 'curry leaves', 'mustard seeds', 'red chili powder'], ['Seafood'], ['dairy_free', 'high_protein', 'gluten_free'], 3, 0, 480, 28, 15, 32, 'South Indian', 'https://images.unsplash.com/photo-1559742811-822873691fc8?w=800&q=80', 'South Taste Express', 'North Indian Mains'), ('Aloo Gobi', 'Classic Indian dry curry made with potatoes, cauliflower, and spices.', 18000, ['potato', 'cauliflower', 'onion', 'tomato', 'cumin', 'turmeric', 'coriander powder', 'oil'], [], ['vegetarian', 'vegan', 'gluten_free', 'dairy_free'], 2, 0, 250, 6, 35, 10, 'North Indian', 'https://images.unsplash.com/photo-1589301773727-2c99a4fc126b?w=800&q=80', 'Royal Punjab Dhaba', 'North Indian Mains'), ('Veg Spring Rolls', 'Crispy fried rolls stuffed with shredded vegetables, served with sweet chili sauce.', 15000, ['spring roll wrappers', 'cabbage', 'carrot', 'capsicum', 'soy sauce', 'oil'], ['Gluten', 'Soy'], ['vegetarian', 'vegan'], 1, 1, 350, 5, 45, 18, 'Indo-Chinese', 'https://images.unsplash.com/photo-1548507200-cf44e03a7c96?w=800&q=80', 'Spice House', 'Starters & Snacks'), ('Gulab Jamun', 'Soft milk-solid dumplings deep-fried and soaked in a fragrant sugar syrup.', 12000, ['milk powder', 'refined flour', 'ghee', 'sugar', 'water', 'cardamom', 'rose water'], ['Dairy', 'Gluten', 'Ghee'], ['vegetarian'], 0, 5, 400, 8, 65, 15, 'Dessert', 'https://images.unsplash.com/photo-1666190711742-d75e322dd818?w=800&q=80', 'Royal Punjab Dhaba', 'Starters & Snacks'), ('Lemon Tart', 'Zesty and sweet lemon custard baked in a buttery pastry crust.', 18000, ['flour', 'butter', 'sugar', 'egg', 'lemon juice', 'lemon zest'], ['Gluten', 'Dairy', 'Egg'], ['vegetarian'], 0, 4, 380, 6, 45, 20, 'Dessert', 'https://images.unsplash.com/photo-1519915028121-7d3463d20eb4?w=800&q=80', 'Spice House', 'Starters & Snacks'), ('Chicken Shawarma', 'Middle Eastern wrap filled with spiced grilled chicken, garlic sauce, and pickles.', 22000, ['pita bread', 'chicken', 'garlic', 'yogurt', 'lemon', 'tahini', 'pickles', 'spices'], ['Gluten', 'Dairy', 'Sesame'], ['high_protein'], 2, 0, 550, 35, 45, 25, 'Middle Eastern', 'https://images.unsplash.com/photo-1529006557810-274b9b2fc783?w=800&q=80', 'Spice House', 'Starters & Snacks'), ('Tiramisu', 'Classic Italian dessert made with espresso-soaked ladyfingers and mascarpone cheese.', 25000, ['ladyfingers', 'espresso', 'mascarpone cheese', 'egg', 'sugar', 'cocoa powder', 'liqueur'], ['Gluten', 'Dairy', 'Egg'], ['vegetarian'], 0, 3, 450, 8, 40, 28, 'Dessert', 'https://images.unsplash.com/photo-1571115177098-24ec42ed204d?w=800&q=80', 'Spice House', 'Starters & Snacks'), ('Fish Curry', 'Spicy and tangy fish curry cooked with mustard seeds, coconut, and curry leaves.', 35000, ['fish', 'coconut', 'tamarind', 'onion', 'tomato', 'mustard seeds', 'curry leaves', 'red chili powder'], ['Seafood'], ['dairy_free', 'high_protein', 'gluten_free'], 3, 0, 420, 30, 12, 28, 'South Indian', 'https://images.unsplash.com/photo-1626508035297-4cfb2e89f487?w=800&q=80', 'South Taste Express', 'North Indian Mains'), ('Vegetable Biryani', 'Aromatic basmati rice cooked with mixed vegetables and whole spices.', 22000, ['basmati rice', 'carrot', 'peas', 'beans', 'potato', 'onion', 'tomato', 'ghee', 'yogurt', 'spices'], ['Dairy', 'Ghee'], ['vegetarian', 'gluten_free'], 2, 0, 450, 10, 75, 12, 'Indian', 'https://images.unsplash.com/photo-1633945274405-b6c8069047b0?w=800&q=80', 'Royal Punjab Dhaba', 'Noodles & Rice')]
        for d in dishes_raw:
            dish, created = Dish.objects.get_or_create(
                restaurant=restaurants[d[14]],
                name=d[0],
                defaults={
                    "description": d[1],
                    "price": d[2],
                    "ingredients": d[3],
                    "ingredients_to_avoid": d[4],
                    "dietary_tags": d[5],
                    "spice_level": d[6],
                    "sweet_level": d[7],
                    "calories": d[8],
                    "protein": d[9],
                    "carbs": d[10],
                    "fat": d[11],
                    "cuisine": d[12],
                    "image_url": d[13],
                    "category": categories[d[15]],
                    "can_be_customised": True,
                    "is_active": True
                }
            )
            if created:
                self.stdout.write(f"Created dish: {dish.name}")
            dishes[dish.name] = dish

        # 5. Reviews
        # Add a review for every dish to meet the requirement "Every dish must have reviews"
        import random
        for d_name, d_obj in dishes.items():
            user = random.choice(list(users.values()))
            Review.objects.get_or_create(
                dish=d_obj,
                user=user,
                defaults={
                    "rating": random.randint(3, 5),
                    "comment": "Absolutely delicious, would definitely recommend!",
                    "spice_feedback": "perfect",
                    "taste_feedback": "tasty",
                    "portion_feedback": "good"
                }
            )

        # 6. Favourites
        favs_data = [
            {"user": users["asha.rao@example.com"], "dish": dishes["Chicken Biryani"]},
            {"user": users["rajesh.kumar@example.com"], "dish": dishes["Paneer Butter Masala"]}
        ]
        for fdata in favs_data:
            Favourite.objects.get_or_create(
                user=fdata["user"],
                dish=fdata["dish"]
            )

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully with 35+ realistic dishes!"))
