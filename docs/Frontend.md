# NIVAALA Frontend Documentation (Beginner's Guide)

Welcome to the NIVAALA frontend! This document is written specifically for beginners. It explains the technologies we use, how the files are organized, and some basic rules to follow when modifying the code.

## 🛠️ Tech Stack

Unlike traditional Single Page Applications (SPAs) that use complex frameworks like React or Vue, our frontend is designed to be extremely lightweight, fast, and closely tied to our Django backend. 

We use the **HTAL (HTML + Tailwind + Alpine + HTMX)** stack:

1. **Django Templates (HTML):** The foundation of our pages. Django handles injecting backend data (like loops and variables) directly into the HTML using `{% ... %}` and `{{ ... }}` tags.
2. **Tailwind CSS:** A utility-first CSS framework. Instead of writing separate `.css` files, we style elements directly in the HTML using class names (e.g., `class="bg-blue-500 text-white rounded-lg"`).
3. **HTMX:** A powerful library that allows us to make AJAX requests (fetching data without reloading the entire page) directly from HTML attributes. E.g., `hx-post="/api/like"` instead of writing complex JavaScript `fetch()` calls.
4. **Alpine.js:** A rugged, minimal JavaScript framework for handling simple UI interactions (like toggling tabs, opening modals, or removing filter chips) using attributes like `x-data`, `x-show`, and `@click`.

---

## 📂 File Structure

All frontend files are located inside the `server/api/templates/` directory.

```text
Bhookh.exe/
└── server/
    └── api/
        └── templates/
            ├── index.html           # The Home Page (Trending dishes, global search)
            ├── login.html           # Authentication (Sign in & Create Account tabs)
            ├── search-results.html  # Search Page (Active filters and dish lists)
            ├── dish-details.html    # Dish Detail Page (Full dish info, allergies, reviews)
            ├── favourites.html      # User's saved dishes
            ├── review.html          # Form for submitting a new dish review
            └── partials/            # Small HTML chunks used by HTMX to update parts of a page
                ├── dish_list.html       # The grid of dishes returned by search
                ├── favourite_list.html  # The list of saved dishes
                ├── review_list.html     # The list of reviews for a specific dish
                └── review_item.html     # A single review card (appended when a review is submitted)
```

---

## 📝 Which File Does What?

### 1. `index.html` (Home Page)
- Displays the main search bar, dietary baselines, spice level toggles, and allergy exclusions.
- Shows the "Trending Near You" dishes at the bottom.
- Driven by Alpine.js to store user filter inputs in the browser before redirecting to the search results page.

### 2. `login.html` (Authentication)
- Contains both the "Sign In" and "Create Account" forms.
- Uses Alpine.js (`x-data="{ tab: 'signin' }"`) to seamlessly switch between the two forms without reloading the page.
- Handles backend login errors (like "Invalid password") using HTMX and Alpine toasts.

### 3. `search-results.html` (Search Page)
- Takes the filters from the Home page and executes a search.
- Displays dynamic filter "chips" at the top. Clicking the "X" on a chip removes it from the URL and automatically triggers an HTMX update to fetch new dishes.
- The actual list of dishes is fetched from the server and loaded into `#results-container` using HTMX.

### 4. `dish-details.html` & `review.html` (Dish Info)
- `dish-details.html` shows deep allergy data (Zero Cashew, Vegan, etc.) and allows users to save dishes to their Dietary Passport.
- `review.html` contains the form where users leave star ratings and dietary feedback.

### 5. `partials/` Directory
- When you use HTMX to click "Load More" or "Search", the backend doesn't send a full HTML page. It sends a small snippet of HTML (a "partial"). These partials (like `dish_list.html`) are injected directly into the DOM.

---

## 🚦 Basic Rules for Beginners

When making changes to the frontend, follow these golden rules:

### 1. Style with Tailwind, not custom CSS
Do not add `<style>` blocks or create new `.css` files unless absolutely necessary. If you want to make text bold and red, add `class="font-bold text-red-500"` to the element. 

### 2. Let HTMX handle server communication
If you need to submit a form or fetch data, do not write a JS `fetch()` request. Use HTMX attributes:
- `hx-get="/endpoint"` to fetch data.
- `hx-post="/endpoint"` to send data.
- `hx-target="#element-id"` to tell HTMX where to put the server response.

### 3. Let Alpine.js handle simple UI state
If you need to toggle a dropdown, open a modal, or keep track of a checkbox, use Alpine.js.
```html
<!-- Example of a simple toggle -->
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    <div x-show="open">This is hidden until clicked!</div>
</div>
```

### 4. Avoid writing `<script>` tags
Because we use HTMX for backend syncing and Alpine.js for frontend interactivity, you should almost never need to write raw vanilla JavaScript inside `<script>` tags. Keep the logic declarative within the HTML elements.

### 5. Use absolute URLs for HTMX
When writing `hx-get` or `hx-post`, always use the full relative path starting with a slash (e.g., `hx-post="/api/v1/me/favourites"`).

### 6. Respect the Design System
Our UI relies heavily on predefined theme colors from our Tailwind config (e.g., `bg-primary`, `text-on-surface`, `bg-error-container`). Stick to these semantic variables rather than using hardcoded colors (like `bg-blue-600`) to ensure dark mode and theme consistency work perfectly.
