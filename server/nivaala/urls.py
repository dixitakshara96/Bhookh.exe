from django.urls import path, include
from django.http import JsonResponse
from api import frontend_views

def custom_404(request, exception=None):
    return JsonResponse({
        "error": {
            "code": "NOT_FOUND",
            "message": "The requested endpoint was not found.",
            "fields": {}
        }
    }, status=404)

handler404 = custom_404

urlpatterns = [
    path('api/v1/', include('api.urls')),
    
    # Frontend Routes
    path('', frontend_views.index_page, name='home'),
    path('login', frontend_views.login_page, name='login'),
    path('search-results', frontend_views.search_results_page, name='search'),
    path('favourites', frontend_views.favourites_page, name='favourites'),
    path('profile', frontend_views.profile_page, name='profile'),
    path('dishes/<int:dish_id>', frontend_views.dish_details_page, name='dish-details'),
    path('dishes/<int:dish_id>/reviews', frontend_views.dish_reviews_page, name='dish-reviews'),
]
