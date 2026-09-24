# MVP Backend API Plan

## Architecture decision

Using a Django monolith for this project. Keep the frontend, backend, database access, authentication, and admin tools in one Django project.

## Guest and account rules

- Guests can open the home page, search, filter dishes, view dish details, and read reviews.
- Registration and login are required only for favourites and submitting reviews.
- Restaurant menu data can be entered through Django Admin for the MVP.
- A user does not need an account to call a restaurant or view its address.

## API conventions

- Base path: `/api/v1`.
- JSON is used for request and response data.
- Protected endpoints use `Authorization: Bearer <token>`.
- `GET` endpoints do not need a request body; filters are query parameters.
- Use ISO date values such as `2026-09-24`.

## 1. Account and access

| Feature | Method and endpoint | Request body | Tables affected |
|---|---|---|---|
| User registration | `POST /api/v1/auth/register` | ```json
{"name":"Asha Rao","email":"asha@example.com","password":"secret123"}
``` | `users` |
| User login | `POST /api/v1/auth/login` | ```json
{"email":"abc@example.com","password":"secret123"}
``` | `users`, `sessions` |
| Current session/user | `GET /api/v1/auth/me` | None; uses the login token. | `sessions`, `users` |
| Logout | `DELETE /api/v1/auth/logout` | None; uses the login token. | `sessions` |

## 2. Menu and dishes

Restaurant, category, and dish records can be created in Django Admin during the sprint. Diners only need read access through the API.

| Feature | Method and endpoint | Request body | Tables affected |
|---|---|---|---|
| Add dish | `POST /api/v1/dishes` | ```json
{"restaurant_id":1,"category_id":2,"name":"Mushroom Hakka Noodles","description":"Noodles with vegetables and mushroom","price":220,"ingredients":["noodles","mushroom","cabbage","carrot","soy sauce"],"ingredients_to_avoid":["soy"],"dietary_tags":["vegetarian","dairy_free"],"spice_level":"mild","can_be_customised":true}
``` | `dishes`, `restaurants`, `categories` |
| Dish details | `GET /api/v1/dishes/{dish_id}` | None | `dishes`, `restaurants`, `categories` |
| Dish list | `GET /api/v1/dishes` | None; supports the filters below. | `dishes`, `restaurants`, `categories` |
| Categories | `GET /api/v1/categories` | None | `categories` |

## 3. Search and filters

Use one list endpoint instead of separate endpoints for every filter.

```text
GET /api/v1/dishes?q=mushroom&diet=vegetarian&exclude=dairy&spice=mild&price_max=300&area=koramangala
```

| Feature | Method and endpoint | Request body | Tables affected |
|---|---|---|---|
| Search by dish, restaurant, ingredient, or area | `GET /api/v1/dishes?q={search_text}` | None; use the `q` query parameter. | `dishes`, `restaurants` |
| Dietary filter | `GET /api/v1/dishes?diet=vegetarian,vegan,jain` | None; use the `diet` query parameter. | `dishes` |
| Include/exclude ingredients | `GET /api/v1/dishes?include=mushroom&exclude=peanut,dairy` | None; use `include` and `exclude` query parameters. | `dishes` |


## 4. Reviews

| Feature | Method and endpoint | Request body | Tables affected |
|---|---|---|---|
| Submit dish review | `POST /api/v1/dishes/{dish_id}/reviews` | ```json
{"rating":5,"comment":"Tasty and not too spicy.","spice_feedback":"mild","taste_feedback":"tasty","portion_feedback":"good"}
``` | `reviews`, `users`, `dishes` |
| View dish reviews | `GET /api/v1/dishes/{dish_id}/reviews` | None | `reviews`, `users`, `dishes` |

A logged-in user can submit one review per dish in the simplest MVP version. The review date is created by the server.

## 5. Favourites

| Feature | Method and endpoint | Request body | Tables affected |
|---|---|---|---|
| Add favourite | `POST /api/v1/me/favourites` | ```json
{"dish_id":123}
``` | `favourites`, `users`, `dishes` |
| View my favourites | `GET /api/v1/me/favourites` | None; requires login. | `favourites`, `dishes`, `restaurants` |
| Remove favourite | `DELETE /api/v1/me/favourites/{dish_id}` | None; requires login. | `favourites` |

## Minimal database tables

| Table | Main fields |
|---|---|
| `users` | `id`, `name`, `email`, `password_hash`, `created_at` |
| `sessions` | `id`, `user_id`, `token`, `expires_at` |
| `restaurants` | `id`, `name`, `area`, `address`, `phone`, `is_verified`, `last_updated` |
| `categories` | `id`, `name` |
| `dishes` | `id`, `restaurant_id`, `category_id`, `name`, `description`, `price`, `ingredients`, `ingredients_to_avoid`, `dietary_tags`, `spice_level`, `can_be_customised`, `is_active`, `last_updated` |
| `reviews` | `id`, `dish_id`, `user_id`, `rating`, `comment`, `spice_feedback`, `taste_feedback`, `portion_feedback`, `created_at` |
| `favourites` | `user_id`, `dish_id`, `created_at` |
| `reports` *(optional if time allows)* | `id`, `dish_id`, `reason`, `message`, `created_at` |

## Authentication summary

| Action | Guest allowed? | Login required? |
|---|---:|---:|
| Search and filter dishes | Yes | No |
| View dish details | Yes | No |
| View reviews | Yes | No |
| Call restaurant or view address | Yes | No |
| Add favourite | No | Yes |
| View favourites | No | Yes |
| Remove favourite | No | Yes |
| Submit review | No | Yes |

## Keep out of the 7-day MVP

not adding online ordering, payments, delivery, restaurant subscriptions, POS integration, automatic ingredient detection, AI health claims, loyalty points, or live stock updates. Will Add them in future versions.
