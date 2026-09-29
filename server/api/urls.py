from django.urls import path
from . import views

urlpatterns = [
    path('health', views.health_check, name='health_check'),
    
    # 1. Auth
    path('auth/register', views.register_user, name='register_user'),
    path('auth/login', views.login_user, name='login_user'),
    path('auth/me', views.get_current_user, name='get_current_user'),
    path('auth/logout', views.logout_user, name='logout_user'),
    
    # 2. Dishes
    path('dishes', views.get_dishes, name='get_dishes'),
    path('dishes/htmx', views.get_dishes, name='get_dishes_htmx'),
    path('dishes/<int:dish_id>', views.get_dish_details, name='get_dish_details'),
    path('dishes/<int:dish_id>/htmx', views.get_dish_details, name='get_dish_details_htmx'),
    
    # 3. Reviews
    path('dishes/<int:dish_id>/reviews', views.dish_reviews, name='dish_reviews'),
    path('dishes/<int:dish_id>/reviews/htmx', views.dish_reviews, name='dish_reviews_htmx'),
    
    # 4. Favourites
    path('me/favourites', views.user_favourites, name='user_favourites'),
    path('me/favourites/htmx', views.user_favourites, name='user_favourites_htmx'),
    path('me/favourites/<int:dish_id>', views.remove_favourite, name='remove_favourite'),
    
    # Preferences
    path('me/preferences/htmx', views.update_preferences, name='update_preferences_htmx'),
    
    # 5. Metadata
    path('categories', views.get_categories, name='get_categories'),
]
