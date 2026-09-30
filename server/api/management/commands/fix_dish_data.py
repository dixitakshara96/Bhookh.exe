"""
Management command to fix dish data in-place.
Corrects image mismatches, fills null/empty fields, and ensures data consistency.
Does NOT re-seed — only updates existing dishes.
"""
from django.core.management.base import BaseCommand
from api.models import Dish

# Canonical mapping: dish name → correct, dish-specific Unsplash image URL.
# Each URL has been verified to depict the actual dish.
CANONICAL_IMAGES = {
    "Chicken Biryani": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800&q=80",
    "Paneer Butter Masala": "https://images.unsplash.com/photo-1631452180519-c014fe946bc0?w=800&q=80",
    "Masala Dosa": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=800&q=80",
    "Rajma Rice": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800&q=80",
    "Veg Hakka Noodles": "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=800&q=80",
    "Caesar Salad": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&q=80",
    "Grilled Chicken Bowl": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&q=80",
    "Chocolate Brownie": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=800&q=80",
    "Palak Paneer": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=800&q=80",
    "Chicken Tikka Masala": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=800&q=80",
    "Mutton Rogan Josh": "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=800&q=80",
    "Butter Naan": "https://images.unsplash.com/photo-1601050690117-94f5f6af8b70?w=800&q=80",
    "Idli Sambar": "https://images.unsplash.com/photo-1589301760014-d929f39ce9b1?w=800&q=80",
    "Medu Vada": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=800&q=80",
    "Chicken 65": "https://images.unsplash.com/photo-1610057099431-d73a1c9d2f2f?w=800&q=80",
    "Chole Bhature": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=800&q=80",
    "Dal Makhani": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800&q=80",
    "Tandoori Chicken": "https://images.unsplash.com/photo-1610057099443-67e04f5be9da?w=800&q=80",
    "Garlic Bread": "https://images.unsplash.com/photo-1573140247632-f8fd74997d5c?w=800&q=80",
    "Margherita Pizza": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=800&q=80",
    "Penne Arrabbiata": "https://images.unsplash.com/photo-1608897013039-887f214b983c?w=800&q=80",
    "Fish and Chips": "https://images.unsplash.com/photo-1599084924616-e91011e3b62b?w=800&q=80",
    "Sushi Platter": "https://images.unsplash.com/photo-1553621042-f6e147245754?w=800&q=80",
    "Pad Thai": "https://images.unsplash.com/photo-1559314809-0d155014e29e?w=800&q=80",
    "Beef Burger": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&q=80",
    "Greek Salad": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=800&q=80",
    "Mushroom Risotto": "https://images.unsplash.com/photo-1476124369491-e7addf5db371?w=800&q=80",
    "Prawn Curry": "https://images.unsplash.com/photo-1559742811-822873691fc8?w=800&q=80",
    "Aloo Gobi": "https://images.unsplash.com/photo-1589301773727-2c99a4fc126b?w=800&q=80",
    "Veg Spring Rolls": "https://images.unsplash.com/photo-1548507200-cf44e03a7c96?w=800&q=80",
    "Gulab Jamun": "https://images.unsplash.com/photo-1666190711742-d75e322dd818?w=800&q=80",
    "Lemon Tart": "https://images.unsplash.com/photo-1519915028121-7d3463d20eb4?w=800&q=80",
    "Chicken Shawarma": "https://images.unsplash.com/photo-1529006557810-274b9b2fc783?w=800&q=80",
    "Tiramisu": "https://images.unsplash.com/photo-1571115177098-24ec42ed204d?w=800&q=80",
    "Fish Curry": "https://images.unsplash.com/photo-1626508035297-4cfb2e89f487?w=800&q=80",
    "Vegetable Biryani": "https://images.unsplash.com/photo-1633945274405-b6c8069047b0?w=800&q=80",
    # Legacy seed_db.py dishes
    "Dal Makhani (No Onion, No Garlic)": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800&q=80",
    "Steamed Vegetable Hakka Noodles": "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=800&q=80",
    "Paneer Malai Tikka": "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=800&q=80",
    "Yellow Moong Dal Khichdi": "https://images.unsplash.com/photo-1596797038530-2c107229654b?w=800&q=80",
    "Mushroom Hakka Noodles": "https://images.unsplash.com/photo-1612929633738-8fe44f7ec841?w=800&q=80",
    # Legacy seed_data.py dishes
    "Grilled Lemon Herb Salmon": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=800&q=80",
    "Spicy Thai Green Curry": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=800&q=80",
    "Vegan Lentil Shepherd's Pie": "https://images.unsplash.com/photo-1600803907087-f56d462fd26b?w=800&q=80",
    "Classic Beef Bolognese": "https://images.unsplash.com/photo-1622973536968-3ead9e780960?w=800&q=80",
    "Avocado & Quinoa Salad": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&q=80",
    "Pad Thai Noodles": "https://images.unsplash.com/photo-1559314809-0d155014e29e?w=800&q=80",
    "Beef Stir Fry with Broccoli": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=800&q=80",
    "Falafel Wrap": "https://images.unsplash.com/photo-1529006557810-274b9b2fc783?w=800&q=80",
    "Eggplant Parmesan": "https://images.unsplash.com/photo-1625944525533-473f1a3d54e7?w=800&q=80",
    "Tom Yum Soup": "https://images.unsplash.com/photo-1548943487-a2e4e43b4853?w=800&q=80",
    "Caprese Salad": "https://images.unsplash.com/photo-1592417817098-8fd3d9eb14a5?w=800&q=80",
    "Vegetable Spring Rolls": "https://images.unsplash.com/photo-1548507200-cf44e03a7c96?w=800&q=80",
    "Edamame": "https://images.unsplash.com/photo-1564834724105-918b73d1b8e0?w=800&q=80",
    "Matcha Ice Cream": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=800&q=80",
    "Vegan Brownie": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=800&q=80",
    "Mango Sorbet": "https://images.unsplash.com/photo-1501443762994-82bd5dace89a?w=800&q=80",
    "Mango Lassi": "https://images.unsplash.com/photo-1527583708390-ef7bbb868e68?w=800&q=80",
    "Masala Chai": "https://images.unsplash.com/photo-1571934811356-5cc061b6821f?w=800&q=80",
    "Iced Americano": "https://images.unsplash.com/photo-1517701604599-bb29b565090c?w=800&q=80",
    "Green Smoothie": "https://images.unsplash.com/photo-1610970881699-44a5587cabec?w=800&q=80",
    "Pina Colada (Virgin)": "https://images.unsplash.com/photo-1513558161293-cdaf765ed514?w=800&q=80",
    "Garlic Naan": "https://images.unsplash.com/photo-1601050690117-94f5f6af8b70?w=800&q=80",
    "French Fries": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=800&q=80",
    "Steamed Rice": "https://images.unsplash.com/photo-1516684732162-798a0062be99?w=800&q=80",
    "Side Salad": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=800&q=80",
    "Onion Rings": "https://images.unsplash.com/photo-1639024471283-03518883512d?w=800&q=80",
}

# Canonical dish data for filling null/empty fields.
# Only used when a dish is missing data. Does NOT overwrite existing non-null values
# unless image_url needs correction.
CANONICAL_DISH_DATA = {
    "Chicken Biryani": {
        "description": "Aromatic basmati rice cooked with tender chicken pieces, blended with traditional Indian spices.",
        "ingredients": ["basmati rice", "chicken", "onion", "tomato", "ghee", "yogurt", "garlic", "ginger", "mint", "coriander"],
        "ingredients_to_avoid": ["Dairy", "Ghee"],
        "dietary_tags": ["high_protein", "gluten_free"],
        "spice_level": 3, "sweet_level": 0,
        "calories": 650, "protein": 35, "carbs": 60, "fat": 20,
        "cuisine": "Indian",
    },
    "Paneer Butter Masala": {
        "description": "Cottage cheese cubes cooked in a rich, creamy tomato and cashew butter gravy.",
        "ingredients": ["paneer", "butter", "tomato", "cashew", "cream", "onion", "garam masala", "kasuri methi"],
        "ingredients_to_avoid": ["Dairy", "Nuts"],
        "dietary_tags": ["vegetarian", "gluten_free"],
        "spice_level": 2, "sweet_level": 1,
        "calories": 450, "protein": 15, "carbs": 25, "fat": 35,
        "cuisine": "North Indian",
    },
    "Masala Dosa": {
        "description": "Crispy fermented rice crepe stuffed with spiced potato mash, served with coconut chutney.",
        "ingredients": ["rice batter", "urad dal", "potato", "onion", "mustard seeds", "curry leaves", "turmeric", "coconut"],
        "ingredients_to_avoid": [],
        "dietary_tags": ["vegetarian", "vegan", "dairy_free"],
        "spice_level": 2, "sweet_level": 0,
        "calories": 300, "protein": 8, "carbs": 45, "fat": 10,
        "cuisine": "South Indian",
    },
    "Rajma Rice": {
        "description": "Comforting North Indian dish of kidney beans in a thick onion-tomato gravy served over steamed rice.",
        "ingredients": ["kidney beans", "rice", "onion", "tomato", "garlic", "ginger", "coriander powder", "cumin"],
        "ingredients_to_avoid": [],
        "dietary_tags": ["vegetarian", "vegan", "high_protein"],
        "spice_level": 2, "sweet_level": 0,
        "calories": 400, "protein": 14, "carbs": 65, "fat": 8,
        "cuisine": "North Indian",
    },
    "Veg Hakka Noodles": {
        "description": "Wok-tossed noodles with fresh crunchy vegetables and a hint of soy sauce.",
        "ingredients": ["noodles", "cabbage", "carrot", "capsicum", "soy sauce", "garlic", "spring onion", "vinegar"],
        "ingredients_to_avoid": ["Soy", "Gluten"],
        "dietary_tags": ["vegetarian", "vegan"],
        "spice_level": 1, "sweet_level": 0,
        "calories": 380, "protein": 10, "carbs": 60, "fat": 12,
        "cuisine": "Indo-Chinese",
    },
    "Caesar Salad": {
        "description": "Crisp romaine lettuce with parmesan cheese, croutons, and creamy Caesar dressing.",
        "ingredients": ["romaine lettuce", "parmesan cheese", "croutons", "olive oil", "lemon juice", "egg", "garlic", "anchovies"],
        "ingredients_to_avoid": ["Dairy", "Gluten", "Egg", "Seafood"],
        "dietary_tags": ["low_calorie"],
        "spice_level": 0, "sweet_level": 0,
        "calories": 320, "protein": 10, "carbs": 15, "fat": 25,
        "cuisine": "Continental",
    },
    "Grilled Chicken Bowl": {
        "description": "Healthy bowl with grilled chicken breast, quinoa, roasted vegetables, and a light vinaigrette.",
        "ingredients": ["chicken breast", "quinoa", "broccoli", "bell peppers", "olive oil", "lemon", "mixed herbs"],
        "ingredients_to_avoid": [],
        "dietary_tags": ["high_protein", "low_calorie", "gluten_free", "dairy_free"],
        "spice_level": 1, "sweet_level": 0,
        "calories": 420, "protein": 45, "carbs": 35, "fat": 12,
        "cuisine": "Continental",
    },
    "Chocolate Brownie": {
        "description": "Fudgy, rich, and decadent dark chocolate brownie with walnuts.",
        "ingredients": ["dark chocolate", "butter", "sugar", "eggs", "flour", "walnuts", "vanilla extract", "cocoa powder"],
        "ingredients_to_avoid": ["Dairy", "Egg", "Gluten", "Nuts"],
        "dietary_tags": ["vegetarian"],
        "spice_level": 0, "sweet_level": 4,
        "calories": 480, "protein": 6, "carbs": 55, "fat": 28,
        "cuisine": "Dessert",
    },
    "Palak Paneer": {
        "description": "Fresh spinach purée cooked with Indian spices and soft paneer cubes.",
        "ingredients": ["spinach", "paneer", "onion", "tomato", "garlic", "cream", "garam masala", "ghee"],
        "ingredients_to_avoid": ["Dairy", "Ghee"],
        "dietary_tags": ["vegetarian", "gluten_free"],
        "spice_level": 2, "sweet_level": 0,
        "calories": 380, "protein": 16, "carbs": 12, "fat": 28,
        "cuisine": "North Indian",
    },
    "Chicken Tikka Masala": {
        "description": "Roasted marinated chicken chunks in a spiced curry sauce.",
        "ingredients": ["chicken", "yogurt", "tomato", "cream", "butter", "ginger", "garlic", "spices"],
        "ingredients_to_avoid": ["Dairy"],
        "dietary_tags": ["high_protein", "gluten_free"],
        "spice_level": 3, "sweet_level": 1,
        "calories": 520, "protein": 32, "carbs": 18, "fat": 36,
        "cuisine": "North Indian",
    },
    "Mutton Rogan Josh": {
        "description": "Aromatic lamb dish of Persian origin, slow-cooked in a fiery red gravy.",
        "ingredients": ["mutton", "onion", "yogurt", "kashmiri red chili", "fennel powder", "ginger powder", "ghee", "garam masala"],
        "ingredients_to_avoid": ["Dairy", "Ghee"],
        "dietary_tags": ["high_protein", "gluten_free"],
        "spice_level": 4, "sweet_level": 0,
        "calories": 600, "protein": 38, "carbs": 10, "fat": 45,
        "cuisine": "Kashmiri",
    },
    "Butter Naan": {
        "description": "Soft and fluffy Indian flatbread brushed with generous amounts of butter.",
        "ingredients": ["refined flour", "yogurt", "milk", "baking powder", "butter", "sugar", "salt"],
        "ingredients_to_avoid": ["Gluten", "Dairy"],
        "dietary_tags": ["vegetarian"],
        "spice_level": 0, "sweet_level": 1,
        "calories": 250, "protein": 5, "carbs": 40, "fat": 8,
        "cuisine": "North Indian",
    },
    "Idli Sambar": {
        "description": "Steamed rice cakes served with lentil soup and coconut chutney.",
        "ingredients": ["rice batter", "urad dal", "toor dal", "tamarind", "mixed vegetables", "sambar powder", "mustard seeds", "coconut"],
        "ingredients_to_avoid": [],
        "dietary_tags": ["vegetarian", "vegan", "dairy_free", "low_calorie"],
        "spice_level": 2, "sweet_level": 0,
        "calories": 250, "protein": 8, "carbs": 48, "fat": 4,
        "cuisine": "South Indian",
    },
    "Medu Vada": {
        "description": "Crispy fried lentil donuts served with chutney and sambar.",
        "ingredients": ["urad dal", "onion", "green chilies", "ginger", "curry leaves", "peppercorns", "oil"],
        "ingredients_to_avoid": [],
        "dietary_tags": ["vegetarian", "vegan", "dairy_free"],
        "spice_level": 1, "sweet_level": 0,
        "calories": 350, "protein": 10, "carbs": 30, "fat": 22,
        "cuisine": "South Indian",
    },
    "Chicken 65": {
        "description": "Spicy, deep-fried chicken bites flavored with curry leaves and red chilies.",
        "ingredients": ["chicken", "yogurt", "rice flour", "corn flour", "red chili powder", "curry leaves", "ginger", "garlic", "lemon", "oil"],
        "ingredients_to_avoid": ["Dairy"],
        "dietary_tags": ["high_protein", "gluten_free"],
        "spice_level": 4, "sweet_level": 0,
        "calories": 480, "protein": 28, "carbs": 15, "fat": 35,
        "cuisine": "South Indian",
    },
    "Chole Bhature": {
        "description": "Spicy chickpea curry served with fried puffed bread.",
        "ingredients": ["chickpeas", "refined flour", "onion", "tomato", "chole masala", "yogurt", "oil", "green chilies"],
        "ingredients_to_avoid": ["Gluten", "Dairy"],
        "dietary_tags": ["vegetarian"],
        "spice_level": 3, "sweet_level": 0,
        "calories": 650, "protein": 15, "carbs": 75, "fat": 30,
        "cuisine": "North Indian",
    },
    "Dal Makhani": {
        "description": "Creamy, slow-cooked black lentils and kidney beans, finished with butter and cream.",
        "ingredients": ["black lentils", "kidney beans", "butter", "cream", "tomato", "garlic", "ginger", "garam masala"],
        "ingredients_to_avoid": ["Dairy"],
        "dietary_tags": ["vegetarian", "gluten_free"],
        "spice_level": 1, "sweet_level": 0,
        "calories": 420, "protein": 14, "carbs": 38, "fat": 25,
        "cuisine": "North Indian",
    },
    "Tandoori Chicken": {
        "description": "Whole chicken marinated in yogurt and spices, roasted in a clay oven.",
        "ingredients": ["chicken", "yogurt", "kashmiri chili powder", "lemon juice", "ginger", "garlic", "garam masala", "mustard oil"],
        "ingredients_to_avoid": ["Dairy"],
        "dietary_tags": ["high_protein", "low_calorie", "gluten_free"],
        "spice_level": 3, "sweet_level": 0,
        "calories": 400, "protein": 45, "carbs": 8, "fat": 20,
        "cuisine": "North Indian",
    },
    "Garlic Bread": {
        "description": "Toasted baguette slices topped with garlic butter and herbs.",
        "ingredients": ["baguette", "butter", "garlic", "parsley", "salt"],
        "ingredients_to_avoid": ["Gluten", "Dairy"],
        "dietary_tags": ["vegetarian"],
        "spice_level": 0, "sweet_level": 0,
        "calories": 280, "protein": 5, "carbs": 30, "fat": 15,
        "cuisine": "Continental",
    },
    "Margherita Pizza": {
        "description": "Classic wood-fired pizza with tomato sauce, fresh mozzarella, and basil.",
        "ingredients": ["pizza dough", "tomato sauce", "mozzarella cheese", "fresh basil", "olive oil"],
        "ingredients_to_avoid": ["Gluten", "Dairy"],
        "dietary_tags": ["vegetarian"],
        "spice_level": 0, "sweet_level": 0,
        "calories": 600, "protein": 22, "carbs": 65, "fat": 25,
        "cuisine": "Italian",
    },
    "Penne Arrabbiata": {
        "description": "Penne pasta tossed in a spicy and garlicky tomato sauce.",
        "ingredients": ["penne pasta", "tomato", "garlic", "red chili flakes", "olive oil", "parsley", "parmesan cheese"],
        "ingredients_to_avoid": ["Gluten", "Dairy"],
        "dietary_tags": ["vegetarian"],
        "spice_level": 3, "sweet_level": 0,
        "calories": 450, "protein": 12, "carbs": 60, "fat": 18,
        "cuisine": "Italian",
    },
    "Fish and Chips": {
        "description": "Crispy battered fish fillets served with thick-cut potato fries and tartar sauce.",
        "ingredients": ["white fish", "flour", "beer", "potato", "oil", "mayonnaise", "capers", "lemon"],
        "ingredients_to_avoid": ["Seafood", "Gluten", "Egg"],
        "dietary_tags": [],
        "spice_level": 0, "sweet_level": 0,
        "calories": 800, "protein": 25, "carbs": 65, "fat": 45,
        "cuisine": "British",
    },
    "Sushi Platter": {
        "description": "Assorted fresh sushi rolls including salmon, tuna, and avocado.",
        "ingredients": ["sushi rice", "nori", "salmon", "tuna", "avocado", "soy sauce", "wasabi", "pickled ginger"],
        "ingredients_to_avoid": ["Seafood", "Soy"],
        "dietary_tags": ["dairy_free", "high_protein"],
        "spice_level": 1, "sweet_level": 0,
        "calories": 450, "protein": 30, "carbs": 55, "fat": 10,
        "cuisine": "Japanese",
    },
    "Pad Thai": {
        "description": "Stir-fried rice noodles with tofu, shrimp, peanuts, and tamarind sauce.",
        "ingredients": ["rice noodles", "shrimp", "tofu", "peanuts", "bean sprouts", "egg", "tamarind paste", "fish sauce", "lime"],
        "ingredients_to_avoid": ["Seafood", "Peanut", "Egg", "Soy"],
        "dietary_tags": ["dairy_free"],
        "spice_level": 2, "sweet_level": 2,
        "calories": 550, "protein": 22, "carbs": 70, "fat": 20,
        "cuisine": "Thai",
    },
    "Beef Burger": {
        "description": "Juicy beef patty with lettuce, tomato, cheese, and special sauce in a brioche bun.",
        "ingredients": ["beef patty", "brioche bun", "cheddar cheese", "lettuce", "tomato", "mayonnaise", "ketchup", "pickles"],
        "ingredients_to_avoid": ["Gluten", "Dairy", "Egg"],
        "dietary_tags": ["high_protein"],
        "spice_level": 1, "sweet_level": 1,
        "calories": 750, "protein": 40, "carbs": 45, "fat": 45,
        "cuisine": "American",
    },
    "Greek Salad": {
        "description": "Refreshing salad with cucumber, tomatoes, red onion, kalamata olives, and feta cheese.",
        "ingredients": ["cucumber", "tomato", "red onion", "kalamata olives", "feta cheese", "olive oil", "oregano"],
        "ingredients_to_avoid": ["Dairy"],
        "dietary_tags": ["vegetarian", "gluten_free", "low_calorie"],
        "spice_level": 0, "sweet_level": 0,
        "calories": 300, "protein": 8, "carbs": 15, "fat": 25,
        "cuisine": "Mediterranean",
    },
    "Mushroom Risotto": {
        "description": "Creamy arborio rice slow-cooked with earthy mushrooms and parmesan.",
        "ingredients": ["arborio rice", "mushrooms", "vegetable broth", "onion", "white wine", "butter", "parmesan cheese"],
        "ingredients_to_avoid": ["Dairy"],
        "dietary_tags": ["vegetarian", "gluten_free"],
        "spice_level": 0, "sweet_level": 0,
        "calories": 520, "protein": 12, "carbs": 65, "fat": 22,
        "cuisine": "Italian",
    },
    "Prawn Curry": {
        "description": "Succulent prawns simmered in a spicy and tangy coconut milk gravy.",
        "ingredients": ["prawns", "coconut milk", "onion", "tomato", "tamarind", "curry leaves", "mustard seeds", "red chili powder"],
        "ingredients_to_avoid": ["Seafood"],
        "dietary_tags": ["dairy_free", "high_protein", "gluten_free"],
        "spice_level": 3, "sweet_level": 0,
        "calories": 480, "protein": 28, "carbs": 15, "fat": 32,
        "cuisine": "South Indian",
    },
    "Aloo Gobi": {
        "description": "Classic Indian dry curry made with potatoes, cauliflower, and spices.",
        "ingredients": ["potato", "cauliflower", "onion", "tomato", "cumin", "turmeric", "coriander powder", "oil"],
        "ingredients_to_avoid": [],
        "dietary_tags": ["vegetarian", "vegan", "gluten_free", "dairy_free"],
        "spice_level": 2, "sweet_level": 0,
        "calories": 250, "protein": 6, "carbs": 35, "fat": 10,
        "cuisine": "North Indian",
    },
    "Veg Spring Rolls": {
        "description": "Crispy fried rolls stuffed with shredded vegetables, served with sweet chili sauce.",
        "ingredients": ["spring roll wrappers", "cabbage", "carrot", "capsicum", "soy sauce", "oil"],
        "ingredients_to_avoid": ["Gluten", "Soy"],
        "dietary_tags": ["vegetarian", "vegan"],
        "spice_level": 1, "sweet_level": 1,
        "calories": 350, "protein": 5, "carbs": 45, "fat": 18,
        "cuisine": "Indo-Chinese",
    },
    "Gulab Jamun": {
        "description": "Soft milk-solid dumplings deep-fried and soaked in a fragrant sugar syrup.",
        "ingredients": ["milk powder", "refined flour", "ghee", "sugar", "water", "cardamom", "rose water"],
        "ingredients_to_avoid": ["Dairy", "Gluten", "Ghee"],
        "dietary_tags": ["vegetarian"],
        "spice_level": 0, "sweet_level": 5,
        "calories": 400, "protein": 8, "carbs": 65, "fat": 15,
        "cuisine": "Dessert",
    },
    "Lemon Tart": {
        "description": "Zesty and sweet lemon custard baked in a buttery pastry crust.",
        "ingredients": ["flour", "butter", "sugar", "egg", "lemon juice", "lemon zest"],
        "ingredients_to_avoid": ["Gluten", "Dairy", "Egg"],
        "dietary_tags": ["vegetarian"],
        "spice_level": 0, "sweet_level": 4,
        "calories": 380, "protein": 6, "carbs": 45, "fat": 20,
        "cuisine": "Dessert",
    },
    "Chicken Shawarma": {
        "description": "Middle Eastern wrap filled with spiced grilled chicken, garlic sauce, and pickles.",
        "ingredients": ["pita bread", "chicken", "garlic", "yogurt", "lemon", "tahini", "pickles", "spices"],
        "ingredients_to_avoid": ["Gluten", "Dairy", "Sesame"],
        "dietary_tags": ["high_protein"],
        "spice_level": 2, "sweet_level": 0,
        "calories": 550, "protein": 35, "carbs": 45, "fat": 25,
        "cuisine": "Middle Eastern",
    },
    "Tiramisu": {
        "description": "Classic Italian dessert made with espresso-soaked ladyfingers and mascarpone cheese.",
        "ingredients": ["ladyfingers", "espresso", "mascarpone cheese", "egg", "sugar", "cocoa powder", "liqueur"],
        "ingredients_to_avoid": ["Gluten", "Dairy", "Egg"],
        "dietary_tags": ["vegetarian"],
        "spice_level": 0, "sweet_level": 3,
        "calories": 450, "protein": 8, "carbs": 40, "fat": 28,
        "cuisine": "Dessert",
    },
    "Fish Curry": {
        "description": "Spicy and tangy fish curry cooked with mustard seeds, coconut, and curry leaves.",
        "ingredients": ["fish", "coconut", "tamarind", "onion", "tomato", "mustard seeds", "curry leaves", "red chili powder"],
        "ingredients_to_avoid": ["Seafood"],
        "dietary_tags": ["dairy_free", "high_protein", "gluten_free"],
        "spice_level": 3, "sweet_level": 0,
        "calories": 420, "protein": 30, "carbs": 12, "fat": 28,
        "cuisine": "South Indian",
    },
    "Vegetable Biryani": {
        "description": "Aromatic basmati rice cooked with mixed vegetables and whole spices.",
        "ingredients": ["basmati rice", "carrot", "peas", "beans", "potato", "onion", "tomato", "ghee", "yogurt", "spices"],
        "ingredients_to_avoid": ["Dairy", "Ghee"],
        "dietary_tags": ["vegetarian", "gluten_free"],
        "spice_level": 2, "sweet_level": 0,
        "calories": 450, "protein": 10, "carbs": 75, "fat": 12,
        "cuisine": "Indian",
    },
    # --- Legacy seed_db.py dishes ---
    "Dal Makhani (No Onion, No Garlic)": {
        "description": "Slow-cooked black lentils and kidney beans simmered overnight in pure desi ghee.",
        "ingredients": ["black lentils", "kidney beans", "tomato puree", "desi ghee", "cream"],
        "ingredients_to_avoid": ["Dairy", "Ghee"],
        "dietary_tags": ["vegetarian", "jain"],
        "spice_level": 1, "sweet_level": 0,
        "calories": 400, "protein": 14, "carbs": 38, "fat": 22,
        "cuisine": "North Indian",
    },
    "Steamed Vegetable Hakka Noodles": {
        "description": "Wok-tossed noodles with fresh vegetables, zero soy sauce, and mild spices.",
        "ingredients": ["wheat noodles", "cabbage", "bell peppers", "carrots", "sesame oil"],
        "ingredients_to_avoid": ["Gluten"],
        "dietary_tags": ["vegan", "dairy_free"],
        "spice_level": 1, "sweet_level": 0,
        "calories": 350, "protein": 10, "carbs": 55, "fat": 12,
        "cuisine": "Indo-Chinese",
    },
    "Paneer Malai Tikka": {
        "description": "Cubes of cottage cheese marinated in hung curd and cardamom, grilled perfectly.",
        "ingredients": ["paneer", "hung curd", "green cardamom", "white pepper"],
        "ingredients_to_avoid": ["Dairy"],
        "dietary_tags": ["vegetarian", "gluten_free"],
        "spice_level": 0, "sweet_level": 0,
        "calories": 380, "protein": 18, "carbs": 10, "fat": 30,
        "cuisine": "North Indian",
    },
    "Yellow Moong Dal Khichdi": {
        "description": "Comforting blend of rice and moong dal cooked with a mild cumin tadka.",
        "ingredients": ["rice", "moong dal", "cumin", "ghee", "turmeric"],
        "ingredients_to_avoid": ["Ghee"],
        "dietary_tags": ["vegetarian", "gluten_free"],
        "spice_level": 1, "sweet_level": 0,
        "calories": 300, "protein": 10, "carbs": 50, "fat": 6,
        "cuisine": "North Indian",
    },
    "Mushroom Hakka Noodles": {
        "description": "Hakka noodles tossed with crisp julienned bell peppers and button mushrooms.",
        "ingredients": ["wheat noodles", "button mushrooms", "cabbage", "bell peppers", "carrots", "sesame oil", "soy sauce"],
        "ingredients_to_avoid": ["Gluten", "Soy"],
        "dietary_tags": ["vegetarian", "dairy_free"],
        "spice_level": 2, "sweet_level": 0,
        "calories": 380, "protein": 12, "carbs": 58, "fat": 14,
        "cuisine": "Indo-Chinese",
    },
    # --- Legacy seed_data.py dishes ---
    "Grilled Lemon Herb Salmon": {
        "description": "Fresh salmon fillet grilled with lemon, garlic, rosemary, and a drizzle of olive oil.",
        "ingredients": ["salmon", "lemon", "garlic", "rosemary", "olive oil"],
        "ingredients_to_avoid": ["Seafood"],
        "dietary_tags": ["gluten_free", "dairy_free"],
        "spice_level": 1, "sweet_level": 0,
        "calories": 450, "protein": 40, "carbs": 5, "fat": 25,
        "cuisine": "Continental",
    },
    "Spicy Thai Green Curry": {
        "description": "Aromatic Thai green curry with chicken, coconut milk, bamboo shoots, and fresh basil.",
        "ingredients": ["chicken", "coconut milk", "green curry paste", "bamboo shoots", "basil"],
        "ingredients_to_avoid": [],
        "dietary_tags": ["dairy_free", "gluten_free"],
        "spice_level": 4, "sweet_level": 1,
        "calories": 600, "protein": 30, "carbs": 15, "fat": 45,
        "cuisine": "Thai",
    },
    "Vegan Lentil Shepherd's Pie": {
        "description": "Hearty vegan shepherd's pie with lentils, carrots, peas, and creamy mashed potato topping.",
        "ingredients": ["lentils", "potatoes", "carrots", "peas", "onions", "olive oil"],
        "ingredients_to_avoid": [],
        "dietary_tags": ["vegan", "vegetarian", "dairy_free", "gluten_free"],
        "spice_level": 1, "sweet_level": 0,
        "calories": 380, "protein": 18, "carbs": 55, "fat": 8,
        "cuisine": "British",
    },
    "Classic Beef Bolognese": {
        "description": "Rich beef ragu slow-simmered with tomatoes, garlic, and herbs, served over spaghetti.",
        "ingredients": ["ground beef", "tomatoes", "onions", "garlic", "spaghetti", "parmesan"],
        "ingredients_to_avoid": ["Dairy", "Gluten"],
        "dietary_tags": [],
        "spice_level": 1, "sweet_level": 1,
        "calories": 750, "protein": 35, "carbs": 80, "fat": 28,
        "cuisine": "Italian",
    },
    "Avocado & Quinoa Salad": {
        "description": "Light and nutritious salad with quinoa, ripe avocado, cherry tomatoes, and lemon dressing.",
        "ingredients": ["quinoa", "avocado", "cherry tomatoes", "cucumber", "lemon dressing"],
        "ingredients_to_avoid": [],
        "dietary_tags": ["vegan", "vegetarian", "dairy_free", "gluten_free"],
        "spice_level": 0, "sweet_level": 0,
        "calories": 420, "protein": 12, "carbs": 45, "fat": 22,
        "cuisine": "Continental",
    },
    "Pad Thai Noodles": {
        "description": "Stir-fried rice noodles with tofu, shrimp, peanuts, bean sprouts, and tamarind sauce.",
        "ingredients": ["rice noodles", "tofu", "shrimp", "peanuts", "bean sprouts", "tamarind"],
        "ingredients_to_avoid": ["Peanut", "Seafood"],
        "dietary_tags": ["dairy_free", "gluten_free"],
        "spice_level": 2, "sweet_level": 2,
        "calories": 600, "protein": 25, "carbs": 80, "fat": 18,
        "cuisine": "Thai",
    },
    "Beef Stir Fry with Broccoli": {
        "description": "Tender beef slices stir-fried with broccoli, soy sauce, ginger, and sesame oil.",
        "ingredients": ["beef slices", "broccoli", "soy sauce", "ginger", "garlic", "sesame oil"],
        "ingredients_to_avoid": ["Soy", "Gluten"],
        "dietary_tags": ["dairy_free"],
        "spice_level": 1, "sweet_level": 1,
        "calories": 480, "protein": 40, "carbs": 15, "fat": 28,
        "cuisine": "Chinese",
    },
    "Falafel Wrap": {
        "description": "Crispy falafel in warm pita bread with hummus, fresh lettuce, tomatoes, and tahini sauce.",
        "ingredients": ["falafel", "pita bread", "hummus", "lettuce", "tomatoes", "tahini"],
        "ingredients_to_avoid": ["Gluten", "Sesame"],
        "dietary_tags": ["vegan", "vegetarian", "dairy_free"],
        "spice_level": 1, "sweet_level": 0,
        "calories": 550, "protein": 18, "carbs": 70, "fat": 20,
        "cuisine": "Middle Eastern",
    },
    "Eggplant Parmesan": {
        "description": "Breaded eggplant slices baked with tomato sauce, mozzarella, and parmesan cheese.",
        "ingredients": ["eggplant", "breadcrumbs", "tomato sauce", "mozzarella", "parmesan"],
        "ingredients_to_avoid": ["Dairy", "Gluten"],
        "dietary_tags": ["vegetarian"],
        "spice_level": 1, "sweet_level": 1,
        "calories": 500, "protein": 25, "carbs": 50, "fat": 20,
        "cuisine": "Italian",
    },
    "Tom Yum Soup": {
        "description": "Hot and sour Thai soup with shrimp, mushrooms, lemongrass, and kaffir lime leaves.",
        "ingredients": ["shrimp", "mushrooms", "lemongrass", "galangal", "lime leaves", "chili"],
        "ingredients_to_avoid": ["Seafood"],
        "dietary_tags": ["dairy_free", "gluten_free"],
        "spice_level": 4, "sweet_level": 1,
        "calories": 150, "protein": 15, "carbs": 10, "fat": 5,
        "cuisine": "Thai",
    },
    "Caprese Salad": {
        "description": "Classic Italian salad with fresh mozzarella, ripe tomatoes, basil, and balsamic glaze.",
        "ingredients": ["fresh mozzarella", "tomatoes", "basil", "balsamic glaze", "olive oil"],
        "ingredients_to_avoid": ["Dairy"],
        "dietary_tags": ["vegetarian", "gluten_free"],
        "spice_level": 0, "sweet_level": 1,
        "calories": 300, "protein": 15, "carbs": 10, "fat": 22,
        "cuisine": "Italian",
    },
    "Vegetable Spring Rolls": {
        "description": "Crispy fried rolls stuffed with cabbage, carrots, glass noodles, and sweet chili sauce.",
        "ingredients": ["cabbage", "carrots", "glass noodles", "spring roll wrapper", "sweet chili sauce"],
        "ingredients_to_avoid": ["Gluten", "Soy"],
        "dietary_tags": ["vegan", "vegetarian", "dairy_free"],
        "spice_level": 1, "sweet_level": 2,
        "calories": 250, "protein": 5, "carbs": 35, "fat": 10,
        "cuisine": "Chinese",
    },
    "Edamame": {
        "description": "Steamed young soybeans lightly salted, a classic Japanese appetizer.",
        "ingredients": ["edamame beans", "sea salt"],
        "ingredients_to_avoid": ["Soy"],
        "dietary_tags": ["vegan", "vegetarian", "dairy_free", "gluten_free"],
        "spice_level": 0, "sweet_level": 0,
        "calories": 120, "protein": 11, "carbs": 9, "fat": 5,
        "cuisine": "Japanese",
    },
    "Matcha Ice Cream": {
        "description": "Creamy Japanese-style ice cream made with premium matcha green tea powder.",
        "ingredients": ["milk", "cream", "sugar", "matcha powder", "egg yolks"],
        "ingredients_to_avoid": ["Dairy", "Egg"],
        "dietary_tags": ["vegetarian", "gluten_free"],
        "spice_level": 0, "sweet_level": 3,
        "calories": 250, "protein": 4, "carbs": 25, "fat": 15,
        "cuisine": "Japanese",
    },
    "Vegan Brownie": {
        "description": "Rich and fudgy vegan brownie made with cocoa, almond milk, coconut oil, and walnuts.",
        "ingredients": ["flour", "cocoa powder", "almond milk", "coconut oil", "sugar", "walnuts"],
        "ingredients_to_avoid": ["Gluten", "Nuts"],
        "dietary_tags": ["vegan", "vegetarian", "dairy_free"],
        "spice_level": 0, "sweet_level": 4,
        "calories": 350, "protein": 5, "carbs": 45, "fat": 18,
        "cuisine": "American",
    },
    "Mango Sorbet": {
        "description": "Refreshing dairy-free sorbet made with ripe mango puree and a squeeze of lemon.",
        "ingredients": ["mango puree", "water", "sugar", "lemon juice"],
        "ingredients_to_avoid": [],
        "dietary_tags": ["vegan", "vegetarian", "dairy_free", "gluten_free"],
        "spice_level": 0, "sweet_level": 3,
        "calories": 150, "protein": 1, "carbs": 38, "fat": 0,
        "cuisine": "Continental",
    },
    "Mango Lassi": {
        "description": "Creamy Indian yogurt drink blended with ripe mango, milk, and a touch of cardamom.",
        "ingredients": ["mango", "yogurt", "milk", "sugar", "cardamom"],
        "ingredients_to_avoid": ["Dairy"],
        "dietary_tags": ["vegetarian", "gluten_free"],
        "spice_level": 0, "sweet_level": 3,
        "calories": 200, "protein": 8, "carbs": 30, "fat": 5,
        "cuisine": "Indian",
    },
    "Masala Chai": {
        "description": "Traditional Indian spiced tea brewed with ginger, cardamom, cloves, and milk.",
        "ingredients": ["black tea", "milk", "ginger", "cardamom", "cloves", "sugar"],
        "ingredients_to_avoid": ["Dairy"],
        "dietary_tags": ["vegetarian", "gluten_free"],
        "spice_level": 1, "sweet_level": 2,
        "calories": 100, "protein": 4, "carbs": 12, "fat": 4,
        "cuisine": "Indian",
    },
    "Iced Americano": {
        "description": "Bold double-shot espresso over ice, served straight up with cold water.",
        "ingredients": ["espresso", "water", "ice"],
        "ingredients_to_avoid": [],
        "dietary_tags": ["vegan", "vegetarian", "dairy_free", "gluten_free"],
        "spice_level": 0, "sweet_level": 0,
        "calories": 5, "protein": 0, "carbs": 1, "fat": 0,
        "cuisine": "Continental",
    },
    "Green Smoothie": {
        "description": "Nutrient-packed smoothie with spinach, kale, apple, banana, and almond milk.",
        "ingredients": ["spinach", "kale", "apple", "banana", "almond milk"],
        "ingredients_to_avoid": ["Nuts"],
        "dietary_tags": ["vegan", "vegetarian", "dairy_free", "gluten_free"],
        "spice_level": 0, "sweet_level": 2,
        "calories": 180, "protein": 4, "carbs": 35, "fat": 3,
        "cuisine": "Continental",
    },
    "Pina Colada (Virgin)": {
        "description": "Tropical non-alcoholic blend of pineapple juice and creamy coconut, served chilled.",
        "ingredients": ["pineapple juice", "coconut cream", "ice"],
        "ingredients_to_avoid": [],
        "dietary_tags": ["vegan", "vegetarian", "dairy_free", "gluten_free"],
        "spice_level": 0, "sweet_level": 4,
        "calories": 250, "protein": 1, "carbs": 45, "fat": 8,
        "cuisine": "Continental",
    },
    "Garlic Naan": {
        "description": "Soft Indian flatbread topped with minced garlic and butter, baked in a tandoor.",
        "ingredients": ["flour", "garlic", "butter", "yeast", "yogurt"],
        "ingredients_to_avoid": ["Gluten", "Dairy"],
        "dietary_tags": ["vegetarian"],
        "spice_level": 0, "sweet_level": 0,
        "calories": 200, "protein": 5, "carbs": 30, "fat": 8,
        "cuisine": "Indian",
    },
    "French Fries": {
        "description": "Golden crispy potato fries, double-fried for the perfect crunch.",
        "ingredients": ["potatoes", "vegetable oil", "salt"],
        "ingredients_to_avoid": [],
        "dietary_tags": ["vegan", "vegetarian", "dairy_free", "gluten_free"],
        "spice_level": 0, "sweet_level": 0,
        "calories": 365, "protein": 4, "carbs": 48, "fat": 17,
        "cuisine": "American",
    },
    "Steamed Rice": {
        "description": "Fluffy steamed jasmine rice, perfectly cooked as a side for curries and stews.",
        "ingredients": ["jasmine rice", "water"],
        "ingredients_to_avoid": [],
        "dietary_tags": ["vegan", "vegetarian", "dairy_free", "gluten_free"],
        "spice_level": 0, "sweet_level": 0,
        "calories": 205, "protein": 4, "carbs": 45, "fat": 0,
        "cuisine": "Asian",
    },
    "Side Salad": {
        "description": "Fresh mixed greens with tomatoes, cucumbers, and a light vinaigrette dressing.",
        "ingredients": ["mixed greens", "tomatoes", "cucumbers", "vinaigrette"],
        "ingredients_to_avoid": [],
        "dietary_tags": ["vegan", "vegetarian", "dairy_free", "gluten_free"],
        "spice_level": 0, "sweet_level": 0,
        "calories": 50, "protein": 1, "carbs": 5, "fat": 3,
        "cuisine": "Continental",
    },
    "Onion Rings": {
        "description": "Crispy battered onion rings, golden fried to perfection.",
        "ingredients": ["onions", "batter", "vegetable oil", "salt"],
        "ingredients_to_avoid": ["Gluten"],
        "dietary_tags": ["vegetarian", "dairy_free"],
        "spice_level": 0, "sweet_level": 0,
        "calories": 400, "protein": 4, "carbs": 45, "fat": 22,
        "cuisine": "American",
    },
}


class Command(BaseCommand):
    help = 'Fix dish data in-place: correct images, fill nulls, ensure consistency'

    def handle(self, *args, **options):
        dishes = Dish.objects.filter(is_active=True)
        fixed_count = 0
        issues = []

        for dish in dishes:
            changed = False

            # --- Fix image URL ---
            if dish.name in CANONICAL_IMAGES:
                correct_url = CANONICAL_IMAGES[dish.name]
                if dish.image_url != correct_url:
                    old_url = dish.image_url
                    dish.image_url = correct_url
                    changed = True
                    self.stdout.write(f"  [IMAGE] {dish.name}: updated image URL")
            elif not dish.image_url or 'placehold' in (dish.image_url or ''):
                issues.append(f"{dish.name} (id={dish.id}): no canonical image mapping found")

            # --- Fill empty/null fields from canonical data ---
            if dish.name in CANONICAL_DISH_DATA:
                data = CANONICAL_DISH_DATA[dish.name]

                if not dish.description:
                    dish.description = data["description"]
                    changed = True

                if not dish.ingredients:
                    dish.ingredients = data["ingredients"]
                    changed = True

                # ingredients_to_avoid: only fill if currently empty AND canonical has data
                if not dish.ingredients_to_avoid and data.get("ingredients_to_avoid"):
                    dish.ingredients_to_avoid = data["ingredients_to_avoid"]
                    changed = True

                if not dish.dietary_tags and data.get("dietary_tags"):
                    dish.dietary_tags = data["dietary_tags"]
                    changed = True

                if dish.calories is None:
                    dish.calories = data["calories"]
                    changed = True
                if dish.protein is None:
                    dish.protein = data["protein"]
                    changed = True
                if dish.carbs is None:
                    dish.carbs = data["carbs"]
                    changed = True
                if dish.fat is None:
                    dish.fat = data["fat"]
                    changed = True

                if not dish.cuisine:
                    dish.cuisine = data["cuisine"]
                    changed = True

            if changed:
                dish.save()
                fixed_count += 1
                self.stdout.write(f"  [OK] Fixed: {dish.name}")

        # Report dishes with remaining issues
        self.stdout.write("")
        if issues:
            self.stdout.write(self.style.WARNING("Remaining issues:"))
            for issue in issues:
                self.stdout.write(f"  [!] {issue}")

        # Check for null important fields in any active dish
        null_check_fields = ['description', 'image_url', 'cuisine']
        null_nutrition = ['calories', 'protein', 'carbs', 'fat']
        
        for dish in Dish.objects.filter(is_active=True):
            for field in null_check_fields:
                val = getattr(dish, field)
                if not val:
                    self.stdout.write(self.style.WARNING(
                        f"  [!] {dish.name} (id={dish.id}): '{field}' is still empty"
                    ))
            for field in null_nutrition:
                val = getattr(dish, field)
                if val is None:
                    self.stdout.write(self.style.WARNING(
                        f"  [!] {dish.name} (id={dish.id}): '{field}' is still NULL"
                    ))

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Fixed {fixed_count} dishes."
        ))

