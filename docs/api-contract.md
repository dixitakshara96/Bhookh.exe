# Nivaala - API Contract MVP

## Envelope Specifications

All endpoints use a consistent JSON envelope for responses.

### Success Payload Example
```json
{
  "data": { ... },
  "message": "Optional success or descriptive message"
}
```

### Error Payload Example
```json
{
  "error": {
    "code": "ERROR_CODE_IN_UPPER_SNAKE",
    "message": "Human readable error description",
    "fields": {
      "field_name": "Validation error for this field"
    }
  }
}
```

---

## 1. Authentication Endpoints

### 1.1 Register User
- **Method & Path:** `POST /api/v1/auth/register`
- **Auth Required:** None
- **Screen Used In:** Screen 4 (Authentication)
- **Request Body:**
  ```json
  {
    "name": "Asha Rao",
    "email": "asha.rao@example.com",
    "password": "strongpassword123"
  }
  ```
  *Validation:* `name` (string, required), `email` (valid email, required), `password` (string, min 8 chars).
- **Success Response (201 Created):**
  ```json
  {
    "data": {
      "user": {
        "id": 1,
        "name": "Asha Rao",
        "email": "asha.rao@example.com",
        "created_at": "2026-09-25T18:00:00Z"
      },
      "token": "eyJhbGciOiJIUzI1NiIsInR..."
    },
    "message": "Registration successful."
  }
  ```
- **Errors:**
  - `400 Bad Request`: `VALIDATION_ERROR` (e.g., missing fields, invalid email format)
  - `409 Conflict`: `EMAIL_ALREADY_EXISTS`

### 1.2 Login User
- **Method & Path:** `POST /api/v1/auth/login`
- **Auth Required:** None
- **Screen Used In:** Screen 4 (Authentication)
- **Request Body:**
  ```json
  {
    "email": "asha.rao@example.com",
    "password": "strongpassword123"
  }
  ```
  *Validation:* `email` (valid email, required), `password` (string, required).
- **Success Response (200 OK):**
  ```json
  {
    "data": {
      "user": {
        "id": 1,
        "name": "Asha Rao",
        "email": "asha.rao@example.com",
        "created_at": "2026-09-25T18:00:00Z"
      },
      "token": "eyJhbGciOiJIUzI1NiIsInR..."
    },
    "message": "Login successful."
  }
  ```
- **Errors:**
  - `400 Bad Request`: `VALIDATION_ERROR`
  - `401 Unauthorized`: `INVALID_CREDENTIALS`

### 1.3 Get Current User
- **Method & Path:** `GET /api/v1/auth/me`
- **Auth Required:** Logged-in User
- **Screen Used In:** Global State (Header, Favourites, Auth checks)
- **Success Response (200 OK):**
  ```json
  {
    "data": {
      "id": 1,
      "name": "Asha Rao",
      "email": "asha.rao@example.com",
      "created_at": "2026-09-25T18:00:00Z"
    },
    "message": "Current user retrieved."
  }
  ```
- **Errors:**
  - `401 Unauthorized`: `UNAUTHORIZED`

### 1.4 Logout
- **Method & Path:** `DELETE /api/v1/auth/logout`
- **Auth Required:** Logged-in User
- **Screen Used In:** Global State (Header/Menu)
- **Success Response (200 OK):**
  ```json
  {
    "data": null,
    "message": "Successfully logged out."
  }
  ```
- **Errors:**
  - `401 Unauthorized`: `UNAUTHORIZED`

---

## 2. Dishes Endpoints

### 2.1 Get Dishes List
- **Method & Path:** `GET /api/v1/dishes`
- **Auth Required:** None
- **Screen Used In:** Screen 1 (Home and Discovery), Screen 2 (Search Results)
- **Query Params:**
  - `q` (string, optional)
  - `diet` (string, comma-separated, optional)
  - `include` (string, comma-separated, optional)
  - `exclude` (string, comma-separated, optional)
  - `spice` (string, optional)
  - `price_max` (integer in paise, optional)
  - `area` (string, optional)
  - `page` (integer, default: 1)
  - `limit` (integer, default: 20)
- **Success Response (200 OK):**
  ```json
  {
    "data": {
      "items": [
        {
          "id": 101,
          "restaurant_id": 5,
          "category_id": 2,
          "name": "Mushroom Hakka Noodles",
          "description": "Wok-tossed noodles with fresh vegetables and button mushrooms.",
          "price": 22000, 
          "ingredients": ["noodles", "mushroom", "cabbage", "carrot", "soy sauce"],
          "ingredients_to_avoid": ["soy"],
          "dietary_tags": ["vegetarian", "dairy_free"],
          "spice_level": 1,
          "can_be_customised": true,
          "is_active": true,
          "last_updated": "2026-09-24T12:00:00Z",
          "restaurant": {
            "id": 5,
            "name": "Spice House",
            "area": "Koramangala",
            "is_verified": true
          },
          "rating_summary": {
            "average": 4.3,
            "count": 24
          }
        }
      ],
      "pagination": {
        "page": 1,
        "limit": 20,
        "total_items": 45,
        "total_pages": 3
      }
    },
    "message": "Dishes fetched successfully."
  }
  ```
- **Errors:**
  - `400 Bad Request`: `INVALID_QUERY_PARAMETERS`

### 2.2 Get Dish Details
- **Method & Path:** `GET /api/v1/dishes/{dish_id}`
- **Auth Required:** None
- **Screen Used In:** Screen 3 (Dish Details)
- **Success Response (200 OK):**
  ```json
  {
    "data": {
      "id": 101,
      "restaurant_id": 5,
      "category_id": 2,
      "name": "Mushroom Hakka Noodles",
      "description": "Wok-tossed noodles with fresh vegetables and button mushrooms.",
      "price": 22000,
      "ingredients": ["noodles", "mushroom", "cabbage", "carrot", "soy sauce"],
      "ingredients_to_avoid": ["soy"],
      "dietary_tags": ["vegetarian", "dairy_free"],
      "spice_level": 1,
      "can_be_customised": true,
      "is_active": true,
      "last_updated": "2026-09-24T12:00:00Z",
      "restaurant": {
        "id": 5,
        "name": "Spice House",
        "area": "Koramangala",
        "address": "123, 80 Feet Road, 4th Block, Koramangala",
        "phone": "+919876543210",
        "is_verified": true,
        "last_updated": "2026-09-10T12:00:00Z"
      }
    },
    "message": "Dish details fetched."
  }
  ```
- **Errors:**
  - `404 Not Found`: `DISH_NOT_FOUND`
  - `400 Bad Request`: `INVALID_ID_FORMAT`

---

## 3. Reviews Endpoints

### 3.1 Get Dish Reviews
- **Method & Path:** `GET /api/v1/dishes/{dish_id}/reviews`
- **Auth Required:** None
- **Screen Used In:** Screen 3 (Dish Details)
- **Query Params:**
  - `page` (integer, default: 1)
  - `limit` (integer, default: 10)
- **Success Response (200 OK):**
  ```json
  {
    "data": {
      "items": [
        {
          "id": 501,
          "dish_id": 101,
          "user_id": 1,
          "rating": 5,
          "comment": "Perfectly balanced taste and not too spicy.",
          "spice_feedback": "mild",
          "taste_feedback": "tasty",
          "portion_feedback": "good",
          "created_at": "2026-09-25T19:30:00Z",
          "user": {
            "name": "Asha Rao"
          }
        }
      ],
      "pagination": {
        "page": 1,
        "limit": 10,
        "total_items": 24,
        "total_pages": 3
      }
    },
    "message": "Reviews fetched successfully."
  }
  ```
- **Errors:**
  - `404 Not Found`: `DISH_NOT_FOUND`
  - `400 Bad Request`: `INVALID_QUERY_PARAMETERS`

### 3.2 Add Dish Review
- **Method & Path:** `POST /api/v1/dishes/{dish_id}/reviews`
- **Auth Required:** Logged-in User
- **Screen Used In:** Screen 6 (Write Review)
- **Request Body:**
  ```json
  {
    "rating": 5,
    "comment": "Perfectly balanced taste and not too spicy.",
    "spice_feedback": "mild",
    "taste_feedback": "tasty",
    "portion_feedback": "good"
  }
  ```
  *Validation:* `rating` (int, 1-5, required), `comment` (string, max 500 chars), `spice_feedback`, `taste_feedback`, `portion_feedback` (string, optional).
- **Success Response (201 Created):**
  ```json
  {
    "data": {
      "id": 501,
      "dish_id": 101,
      "user_id": 1,
      "rating": 5,
      "comment": "Perfectly balanced taste and not too spicy.",
      "spice_feedback": "mild",
      "taste_feedback": "tasty",
      "portion_feedback": "good",
      "created_at": "2026-09-25T19:30:00Z"
    },
    "message": "Review submitted successfully."
  }
  ```
- **Errors:**
  - `400 Bad Request`: `VALIDATION_ERROR`
  - `401 Unauthorized`: `UNAUTHORIZED`
  - `404 Not Found`: `DISH_NOT_FOUND`
  - `409 Conflict`: `REVIEW_ALREADY_EXISTS`

---

## 4. Favourites Endpoints

### 4.1 Get My Favourites
- **Method & Path:** `GET /api/v1/me/favourites`
- **Auth Required:** Logged-in User
- **Screen Used In:** Screen 5 (Favourites)
- **Query Params:**
  - `page` (integer, default: 1)
  - `limit` (integer, default: 20)
- **Success Response (200 OK):**
  ```json
  {
    "data": {
      "items": [
        {
          "user_id": 1,
          "dish_id": 101,
          "created_at": "2026-09-25T18:45:00Z",
          "dish": {
            "id": 101,
            "name": "Mushroom Hakka Noodles",
            "price": 22000,
            "dietary_tags": ["vegetarian", "dairy_free"],
            "spice_level": 1,
            "is_active": true,
            "restaurant": {
              "id": 5,
              "name": "Spice House"
            },
            "rating_summary": {
              "average": 4.3,
              "count": 24
            }
          }
        }
      ],
      "pagination": {
        "page": 1,
        "limit": 20,
        "total_items": 5,
        "total_pages": 1
      }
    },
    "message": "Favourites fetched successfully."
  }
  ```
- **Errors:**
  - `401 Unauthorized`: `UNAUTHORIZED`

### 4.2 Add to Favourites
- **Method & Path:** `POST /api/v1/me/favourites`
- **Auth Required:** Logged-in User
- **Screen Used In:** Screen 3 (Dish Details) & Screen 2 (Search Results - Heart Icon)
- **Request Body:**
  ```json
  {
    "dish_id": 101
  }
  ```
  *Validation:* `dish_id` (integer, required).
- **Success Response (201 Created):**
  ```json
  {
    "data": {
      "user_id": 1,
      "dish_id": 101,
      "created_at": "2026-09-25T18:45:00Z"
    },
    "message": "Dish added to favourites."
  }
  ```
- **Errors:**
  - `400 Bad Request`: `VALIDATION_ERROR`
  - `401 Unauthorized`: `UNAUTHORIZED`
  - `404 Not Found`: `DISH_NOT_FOUND`
  - `409 Conflict`: `ALREADY_FAVOURITED`

### 4.3 Remove from Favourites
- **Method & Path:** `DELETE /api/v1/me/favourites/{dish_id}`
- **Auth Required:** Logged-in User
- **Screen Used In:** Screen 3 (Dish Details) & Screen 5 (Favourites)
- **Success Response (200 OK):**
  ```json
  {
    "data": null,
    "message": "Dish removed from favourites."
  }
  ```
- **Errors:**
  - `401 Unauthorized`: `UNAUTHORIZED`
  - `404 Not Found`: `FAVOURITE_NOT_FOUND`

---

## 5. Metadata  
<!-- Admin Endpoints I am not including this in v1-->

### 5.1 Get Categories
- **Method & Path:** `GET /api/v1/categories`
- **Auth Required:** None
- **Screen Used In:** Background / Global
- **Query Params:**
  - `page` (integer, default: 1)
  - `limit` (integer, default: 50)
- **Success Response (200 OK):**
  ```json
  {
    "data": {
      "items": [
        {
          "id": 2,
          "name": "Noodles & Rice"
        },
        {
          "id": 3,
          "name": "North Indian Mains"
        }
      ],
      "pagination": {
        "page": 1,
        "limit": 50,
        "total_items": 12,
        "total_pages": 1
      }
    },
    "message": "Categories fetched successfully."
  }
  ```
- **Errors:**
  - `400 Bad Request`: `INVALID_QUERY_PARAMETERS`

<!-- ### 5.2 Add Dish (Admin)
- **Method & Path:** `POST /api/v1/dishes`
- **Auth Required:** Admin
- **Screen Used In:** Admin Dashboard
- **Request Body:**
  ```json
  {
    "restaurant_id": 5,
    "category_id": 2,
    "name": "Mushroom Hakka Noodles",
    "description": "Wok-tossed noodles with fresh vegetables and button mushrooms",
    "price": 22000,
    "ingredients": ["noodles", "mushroom", "cabbage", "carrot", "soy sauce"],
    "ingredients_to_avoid": ["soy"],
    "dietary_tags": ["vegetarian", "dairy_free"],
    "spice_level": 1,
    "can_be_customised": true,
    "is_active": true
  }
  ```
  *Validation:* `restaurant_id`, `name`, `price`, `ingredients` are required.
- **Success Response (201 Created):**
  ```json
  {
    "data": {
      "id": 101,
      "restaurant_id": 5,
      "category_id": 2,
      "name": "Mushroom Hakka Noodles",
      "description": "Wok-tossed noodles with fresh vegetables and button mushrooms",
      "price": 22000,
      "ingredients": ["noodles", "mushroom", "cabbage", "carrot", "soy sauce"],
      "ingredients_to_avoid": ["soy"],
      "dietary_tags": ["vegetarian", "dairy_free"],
      "spice_level": 1,
      "can_be_customised": true,
      "is_active": true,
      "last_updated": "2026-09-25T20:00:00Z"
    },
    "message": "Dish created successfully."
  }
  ```
- **Errors:**
  - `400 Bad Request`: `VALIDATION_ERROR`
  - `401 Unauthorized`: `UNAUTHORIZED`
  - `403 Forbidden`: `FORBIDDEN` (Requires Admin role) -->
