# Digital Restaurant Menu — MVP Features

## What the app does

It helps diners quickly find dishes that match their food needs, such as vegetarian dishes or mild-spice meals. Diners can view dish details, read reviews, and save dishes they like.

```text
Search or filter → View dish details → Read reviews → Save favorite / add review
```

## Modules and features

| Module | Features included | What users can do |
|---|---|---|
| **1. Account** | Sign up, log in, log out | Create an account and use the app safely. |
| **2. Menu** | Add dishes, view dishes, view categories | Restaurant owners add dishes; diners see dish name, price, ingredients, spice level, food tags, photo, and restaurant name. |
| **3. Find Dishes** | Search, dietary filter, spice filter | Search by dish or ingredient and narrow results by food type and spice level. |
| **4. Reviews** | Add review, view reviews | Give a dish a 1–5 star rating and comment; see reviews with their dates. |
| **5. Favorites** | Save favorite, view favorites, remove favorite | Save dishes for later and remove them when no longer needed. |

## Main diner journey

1. **Sign up or log in**
2. **Search for a dish** or use filters such as Vegetarian, Vegan, Mild, or Hot
3. **Open a dish** to see its full details and restaurant information
4. **Read reviews** from other diners
5. **Save it as a favorite** or **write a review**

## Simple feature map

```text
DINER
  ├── Account
  ├── Find dishes
  │     ├── Search by name or ingredient
  │     ├── Filter by dietary need
  │     └── Filter by spice level
  ├── View dish details and reviews
  ├── Save favorites
  └── Add a review

RESTAURANT OWNER
  └── Add dishes to the menu
```

## Not included in this first version

- Editing or deleting dishes from the app
- Editing or deleting reviews
- Restaurant replies to reviews
- Price filters and advanced sorting
- Personalized dish suggestions

These can be added after the first working version is launched.
