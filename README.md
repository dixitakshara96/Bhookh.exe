# NIVAALA (Bhookh.exe)

NIVAALA is an ingredient-level food discovery platform designed to reduce uncertainty for diners with dietary restrictions, spice preferences, and ingredient allergies. It helps users find restaurant dishes that strictly fit their personal "Dietary Passport".

## Features

- **Ingredient-Level Discovery:** Search for dishes by name, restaurant, or ingredient.
- **Strict Allergy Shield:** Filter out dishes containing specific allergens (checks both ingredients and cross-contact risks).
- **Dietary & Spice Filters:** Filter for Vegetarian, Vegan, Jain, Dairy-Free, Gluten-Free, and precise spice/sweetness levels.
- **Dietary Passport:** Authenticated users can save their safety preferences (allergies, spice tolerance) directly to their profile, which automatically filters their future searches.
- **Community Reviews:** Read and write dish-specific reviews to share dietary experiences.
- **Favourites:** Save dishes for quick access across devices.
- **Actionable Restaurant Info:** View dish prices, verified ingredients, and direct restaurant contact information.

## Technology Stack

- **Backend:** Django (Monolith) + PostgreSQL (via Supabase)
- **Frontend:** HTMX + Alpine.js + Tailwind CSS
- **Authentication:** Supabase Auth (JWT based session management)

## Getting Started

1. Clone the repository
2. Install Python dependencies: `pip install -r requirements.txt`
3. Set up your `.env` variables for Supabase (`SUPABASE_URL`, `SUPABASE_KEY`)
4. Apply migrations: `python manage.py migrate`
5. Run the development server: `python manage.py runserver`

## Architecture Highlights

This project utilizes an SPA-like architecture without the heavy payload of a frontend framework. By combining **Django Templates** with **HTMX**, NIVAALA dynamically swaps HTML fragments (`/templates/partials/`) without full page reloads, ensuring lightning-fast performance and a seamless user experience.

> **Disclaimer:** Menu details come from the restaurant and can change. If you have an allergy or a medical condition, please confirm with the restaurant before ordering.
