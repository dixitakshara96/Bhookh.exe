from django.shortcuts import render
from .decorators import optional_auth

@optional_auth
def index_page(request):
    from .models import Dish, UserPreference
    from django.db.models import Avg
    trending_dishes = Dish.objects.select_related('restaurant').annotate(avg_rating=Avg('reviews__rating')).all()[:6]
    prefs = None
    if request.user and request.user.is_authenticated:
        prefs, _ = UserPreference.objects.get_or_create(user=request.user)
    return render(request, 'index.html', {'trending_dishes': trending_dishes, 'prefs': prefs})

@optional_auth
def login_page(request):
    return render(request, 'login.html')

@optional_auth
def search_results_page(request):
    return render(request, 'search-results.html')

@optional_auth
def favourites_page(request):
    return render(request, 'favourites.html')

@optional_auth
def dish_details_page(request, dish_id):
    return render(request, 'dish-details.html', {'dish_id': dish_id})

@optional_auth
def dish_reviews_page(request, dish_id):
    from .models import Dish
    dish = Dish.objects.filter(id=dish_id).first()
    return render(request, 'review.html', {'dish': dish})

@optional_auth
def profile_page(request):
    from .models import UserPreference
    prefs = None
    if request.user and request.user.is_authenticated:
        prefs, _ = UserPreference.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {'prefs': prefs})
