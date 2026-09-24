<<<<<<< HEAD
``# Digital Restaurant Menu — MVP Features
=======
# Bhookh.exe — MVP Features (v1)

> This is the final build scope for the sprint. `MVP_ideation.md` is the brainstorm. If the two files disagree, follow this one.
>>>>>>> b4295911153bb257349ee29c7cb48e7e18d00453

## What the app does

Bhookh.exe helps diners find a restaurant dish that fits their diet, their spice level and the ingredients they want to avoid. They can check the dish details and reviews, save the dish, or call the restaurant.

```text
Search or filter → View dish details → Read reviews → Save to Favourites or call restaurant
```

## Who uses the app

| Role | What they can do | Login needed? |
|---|---|---|
| **Guest** | Search, filter, view dishes and read reviews | No |
| **Diner** | Everything a guest can do, plus save Favourites and write reviews | Yes |
| **Admin** | Add restaurants, add dishes and edit dishes | Yes |

For v1, the admin adds all menu data. Restaurant owner accounts will come later.

## Modules and features

| Module | Feature | What it does | CRUD |
|---|---|---|---|
| **1. Account** | Sign up | Create an account with name, email and password | Create |
| | Log in | Log in with email and password | Read |
| | Log out | Log out of the app | — |
| **2. Find Dishes** | Search | Search by dish name, restaurant name, ingredient or area | Read |
| | Diet filter | Show only Vegetarian, Vegan, Jain, Dairy-free or Gluten-free dishes | Read |
| | Spice filter | Show dishes up to the chosen spice level | Read |
| | Avoid ingredient | Hide dishes that contain an ingredient, such as mushroom or cashew | Read |
| | Dish details | Show price, ingredients, tags, spice level, restaurant phone and address, restaurant-confirmed status, last updated date and the disclaimer | Read |
| **3. Reviews** | Add review | Give a dish 1–5 stars and a short comment (one review per dish) | Create |
| | View reviews | See reviews with dates, plus the average rating and number of reviews | Read |
| **4. Favourites** | Save favourite | Tap ♡ to save a dish | Create |
| | View favourites | See all saved dishes in one list | Read |
| | Remove favourite | Tap ♡ again to remove a dish | Delete |
| **5. Admin** | Add restaurant | Add name, area, address and phone number | Create |
| | Add dish | Add a dish to a restaurant | Create |
| | Edit dish | Fix dish details, mark it restaurant-confirmed, or mark it unavailable | Update |

Each search result shows the dish name, restaurant, price, tags, spice level, average rating and review count.

## Dietary tags

| Tag | The dish has no… |
|---|---|
| Vegetarian | meat, fish or egg |
| Vegan | meat, fish, egg, dairy or honey |
| Jain | meat, fish, egg, onion, garlic, potato or other root vegetables |
| Dairy-free | milk, butter, ghee, cream, paneer, curd or cheese |
| Gluten-free | wheat, maida, barley or rye |

The Avoid ingredient filter checks exact ingredient names. To avoid all dairy, use the Dairy-free tag. To avoid egg without choosing Vegetarian, use the Avoid ingredient filter.

## Spice levels

| 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| No spice | Mild | Medium | Spicy | Very spicy |

If a diner chooses Mild, the app shows No spice and Mild dishes.

## Disclaimer

Shown on every dish page:

> Menu details come from the restaurant and can change. If you have an allergy or a medical condition, please confirm with the restaurant before ordering.

## Main diner journey

1. **Open the website.** No login is needed to search.
2. **Search** for a dish, restaurant, ingredient or area.
3. **Apply filters**, such as Vegetarian, Mild, and avoid cashew.
4. **Open a dish** to see its ingredients, tags, restaurant contact and last updated date.
5. **Read reviews** from other diners.
6. **Save it to Favourites** or **call the restaurant**. Saving and reviewing need a login.

## Simple feature map

```text
GUEST / DINER
  ├── Account (sign up, log in, log out)
  ├── Find dishes
  │     ├── Search by dish, restaurant, ingredient or area
  │     ├── Filter by diet
  │     ├── Filter by spice level
  │     └── Avoid an ingredient
  ├── View dish details and reviews
  ├── Save to Favourites   (login needed)
  └── Write a review       (login needed)

ADMIN
  ├── Add restaurant
  ├── Add dish
  └── Edit dish
```

## Special cases

| Situation | What the app does |
|---|---|
| No dishes match the filters | Show "No dishes match your filters. Try removing one." |
| A dish has no reviews | Show "No reviews yet" instead of ★ 0 |
| A guest taps ♡ or Write review | Ask them to log in first |
| A diner saves the same dish twice | Do not add it again |
| A diner reviews the same dish twice | Show "You have already reviewed this dish" |
| A dish is marked unavailable | Hide it from search and show "Currently unavailable" in Favourites |

## Database tables

| Table | Fields |
|---|---|
| **users** | id, name, email, password (hashed), role (diner or admin) |
| **restaurants** | id, name, area, address, phone |
| **dishes** | id, restaurant_id, name, price, ingredients, diet_tags, spice_level (0–4), is_available, restaurant_confirmed, updated_at |
| **reviews** | id, dish_id, user_id, rating (1–5), comment, created_at |
| **favourites** | id, user_id, dish_id |

## API endpoints

| Method | Endpoint | What it does | Who |
|---|---|---|---|
| POST | `/api/auth/signup` | Create an account | Guest |
| POST | `/api/auth/login` | Log in | Guest |
| GET | `/api/dishes` | Search and filter dishes, e.g. `?q=noodles&diet=vegetarian&maxSpice=1&avoid=cashew` | Everyone |
| GET | `/api/dishes/:id` | Get one dish with its restaurant details | Everyone |
| GET | `/api/dishes/:id/reviews` | Get reviews for a dish | Everyone |
| POST | `/api/dishes/:id/reviews` | Add a review | Diner |
| GET | `/api/favourites` | Get saved dishes | Diner |
| POST | `/api/favourites` | Save a dish | Diner |
| DELETE | `/api/favourites/:dishId` | Remove a saved dish | Diner |
| GET | `/api/admin/dishes` | List all dishes, including unavailable ones | Admin |
| POST | `/api/admin/restaurants` | Add a restaurant | Admin |
| POST | `/api/admin/dishes` | Add a dish | Admin |
| PUT | `/api/admin/dishes/:id` | Edit a dish | Admin |

Log out does not need an endpoint. The frontend deletes the saved login token.

## Not included in v1

| Feature | Why the app still works without it |
|---|---|
| Price filter and sorting | Price is shown on every result, so diners can compare easily. |
| Location or distance search | Searching an area name, such as "Koramangala", is enough for now. |
| Restaurant owner accounts | The admin adds the menu data. |
| Deleting dishes | Marking a dish unavailable hides it without losing its reviews. |
| Dish photos | Ingredients and tags already explain the dish. |
| Customisation options | Diners can ask the restaurant by phone. |
| Editing or deleting reviews | One review per dish keeps things simple. |
| Restaurant replies to reviews | Diners can choose a dish without them. |
| Report incorrect information | The disclaimer and the restaurant phone number cover this for now. |
| Mood filters, personalised suggestions, Hindi toggle, share links | Nice extras; the main journey works without them. |

## Build order

1. Create the database tables and add sample data: 3–4 restaurants and 15–20 dishes covering every tag and spice level.
2. Build search, filters and the dish details page.
3. Add sign up, log in and log out.
4. Add Favourites and reviews.
5. Build the admin pages.
6. Deploy, then test the main goal: find and save a mild, dairy-free dish in under a minute.
