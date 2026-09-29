import json
import re
import math
import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
from django.db.models import Avg, Count
from django.core.cache import cache
from .models import User, Restaurant, Category, Dish, Review, Favourite
from .decorators import get_authenticated_user, unauthorized_response, forbidden_response, require_auth, require_role, check_ownership

def parse_json_body(request):
    try:
        data = getattr(request, 'data', None)
        if data is None:
            return json.loads(request.body) if request.body else {}
        return data
    except Exception:
        # Fallback for form-encoded data (often used by HTMX)
        if request.POST:
            return request.POST.dict()
        return {}

def format_iso_datetime(dt):
    if not dt:
        return None
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

def serialize_user(user):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "created_at": format_iso_datetime(user.created_at)
    }

def is_htmx(request):
    return request.headers.get('HX-Request') == 'true'

# --- 0. Health Check ---

def health_check(request):
    return JsonResponse({"data": {"ok": True}})

# --- 1. Authentication Endpoints ---

@csrf_exempt
@require_http_methods(["POST"])
def register_user(request):
    data = parse_json_body(request)
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    role = 'user'

    errors = {}
    if not name:
        errors['name'] = 'Name is required.'
    if not email or not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        errors['email'] = 'Valid email is required.'
    if not password or len(password) < 8:
        errors['password'] = 'Password must be at least 8 characters long.'

    if errors:
        return JsonResponse({"error": {"code": "VALIDATION_ERROR", "message": "Invalid fields", "fields": errors}}, status=400)

    try:
        user = User.objects.create_user(email=email, name=name, password=password, role=role)
    except IntegrityError:
        return JsonResponse({"error": {"code": "EMAIL_ALREADY_EXISTS", "message": "Email already exists", "fields": {"email": "Email already in use"}}}, status=409)

    payload = {'user_id': user.id, 'role': user.role, 'exp': datetime.now(timezone.utc) + timedelta(days=7), 'iat': datetime.now(timezone.utc)}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    if is_htmx(request):
        response = HttpResponse()
        response['HX-Redirect'] = '/'
        # Setting a cookie for HTMX auth since HTMX doesn't easily handle Bearer tokens without JS interception
        response.set_cookie('jwt_token', token, httponly=True, max_age=7*24*3600, secure=not settings.DEBUG, samesite='Lax')
        return response

    return JsonResponse({"data": {"user": serialize_user(user), "token": token}, "message": "Registration successful."}, status=201)

@csrf_exempt
@require_http_methods(["POST"])
def login_user(request):
    data = parse_json_body(request)
    email = data.get('email', '').strip()
    password = data.get('password', '')

    errors = {}
    if not email or not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        errors['email'] = 'Valid email is required.'
    if not password:
        errors['password'] = 'Password is required.'

    if errors:
        return JsonResponse({"error": {"code": "VALIDATION_ERROR", "message": "Invalid fields", "fields": errors}}, status=400)

    # Rate Limiting
    ip = request.META.get('REMOTE_ADDR')
    cache_key = f"login_attempts_{ip}"
    attempts = cache.get(cache_key, 0)
    if attempts >= 5:
        return JsonResponse({"error": {"code": "RATE_LIMITED", "message": "Too many failed login attempts", "fields": {}}}, status=429)

    try:
        user = User.objects.get(email=email)
        if not user.check_password(password):
            cache.set(cache_key, attempts + 1, timeout=300)
            raise User.DoesNotExist
    except User.DoesNotExist:
        cache.set(cache_key, attempts + 1, timeout=300)
        return JsonResponse({"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid email or password", "fields": {}}}, status=401)
    
    # Reset limit on success
    cache.delete(cache_key)

    payload = {'user_id': user.id, 'role': user.role, 'exp': datetime.now(timezone.utc) + timedelta(days=7), 'iat': datetime.now(timezone.utc)}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    if is_htmx(request):
        response = HttpResponse()
        response['HX-Redirect'] = '/'
        response.set_cookie('jwt_token', token, httponly=True, max_age=7*24*3600, secure=not settings.DEBUG, samesite='Lax')
        return response

    return JsonResponse({"data": {"user": serialize_user(user), "token": token}, "message": "Login successful."}, status=200)

@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def get_current_user(request):
    return JsonResponse({"data": serialize_user(request.user), "message": "Current user retrieved."}, status=200)

@csrf_exempt
@require_http_methods(["DELETE"])
@require_auth
def logout_user(request):
    response = JsonResponse({"data": None, "message": "Successfully logged out."}, status=200)
    response.delete_cookie('jwt_token', samesite='Lax')
    if is_htmx(request):
        response['HX-Redirect'] = '/'
    return response

# --- 2. Dishes Endpoints ---

@csrf_exempt
@require_http_methods(["GET"])
def get_dishes(request):
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        if page < 1 or limit < 1:
            raise ValueError()
        limit = min(limit, 100)
    except ValueError:
        return JsonResponse({"error": {"code": "INVALID_QUERY_PARAMETERS", "message": "Page/limit must be positive.", "fields": {}}}, status=400)

    q = request.GET.get('q')
    diet = request.GET.get('diet')
    include = request.GET.get('include')
    exclude = request.GET.get('exclude')
    spice = request.GET.get('spice')
    sweet = request.GET.get('sweet')
    price_max = request.GET.get('price_max')
    area = request.GET.get('area')
    
    qs = Dish.objects.filter(is_active=True).select_related('restaurant')

    if q:
        qs = qs.filter(name__icontains=q) | qs.filter(description__icontains=q)
    if diet:
        for d in diet.split(','):
            qs = qs.filter(dietary_tags__contains=[d.strip()])
    if include:
        for i in include.split(','):
            qs = qs.filter(ingredients__contains=[i.strip()])
    if exclude:
        for e in exclude.split(','):
            qs = qs.exclude(ingredients__contains=[e.strip()])
    if spice:
        try:
            qs = qs.filter(spice_level__lte=int(spice))
        except ValueError:
            return JsonResponse({"error": {"code": "INVALID_QUERY_PARAMETERS", "message": "Invalid spice parameter", "fields": {}}}, status=400)
    if sweet:
        try:
            qs = qs.filter(sweet_level__lte=int(sweet))
        except ValueError:
            return JsonResponse({"error": {"code": "INVALID_QUERY_PARAMETERS", "message": "Invalid sweet parameter", "fields": {}}}, status=400)
    if price_max:
        try:
            qs = qs.filter(price__lte=int(price_max))
        except ValueError:
            return JsonResponse({"error": {"code": "INVALID_QUERY_PARAMETERS", "message": "Invalid price parameter", "fields": {}}}, status=400)
    if area:
        qs = qs.filter(restaurant__area__icontains=area)

    total_items = qs.count()
    total_pages = math.ceil(total_items / limit) if total_items > 0 else 0
    dishes = qs[(page - 1) * limit : page * limit]

    items = []
    for dish in dishes:
        reviews_agg = dish.reviews.aggregate(avg=Avg('rating'), count=Count('id'))
        items.append({
            "id": dish.id, "restaurant_id": dish.restaurant_id, "category_id": dish.category_id,
            "name": dish.name, "description": dish.description, "price": dish.price, 
            "ingredients": dish.ingredients, "ingredients_to_avoid": dish.ingredients_to_avoid,
            "dietary_tags": dish.dietary_tags, "spice_level": dish.spice_level, "sweet_level": dish.sweet_level,
            "can_be_customised": dish.can_be_customised, "is_active": dish.is_active,
            "last_updated": format_iso_datetime(dish.last_updated) if hasattr(dish, 'last_updated') else None,
            "restaurant": {
                "id": dish.restaurant.id,
                "name": dish.restaurant.name,
                "area": dish.restaurant.area,
                "is_verified": dish.restaurant.is_verified
            },
            "rating_summary": {"average": round(reviews_agg['avg'], 1) if reviews_agg['avg'] else 0.0, "count": reviews_agg['count']}
        })

    if is_htmx(request) or request.path.endswith('/htmx'):
        # Pass full objects to template for easy rendering
        return render(request, 'partials/dish_list.html', {'dishes': dishes})

    return JsonResponse({"data": {"items": items, "pagination": {"page": page, "limit": limit, "total_items": total_items, "total_pages": total_pages}}, "message": "Dishes fetched successfully."}, status=200)


@csrf_exempt
@require_http_methods(["GET"])
def get_dish_details(request, dish_id):
    try:
        dish = Dish.objects.select_related('restaurant').get(id=int(dish_id))
    except (ValueError, Dish.DoesNotExist):
        return JsonResponse({"error": {"code": "DISH_NOT_FOUND", "message": "Dish not found", "fields": {}}}, status=404)

    if is_htmx(request) or request.path.endswith('/htmx'):
        reviews_agg = dish.reviews.aggregate(count=Count('id'))
        dish.rating_summary = {'count': reviews_agg['count']}
        return render(request, 'partials/dish_details.html', {'dish': dish})

    return JsonResponse({
        "data": {
            "id": dish.id, "restaurant_id": dish.restaurant_id, "category_id": dish.category_id,
            "name": dish.name, "description": dish.description, "price": dish.price,
            "ingredients": dish.ingredients, "ingredients_to_avoid": dish.ingredients_to_avoid,
            "dietary_tags": dish.dietary_tags, "spice_level": dish.spice_level, "sweet_level": dish.sweet_level, 
            "can_be_customised": dish.can_be_customised, "is_active": dish.is_active,
            "last_updated": format_iso_datetime(dish.last_updated) if hasattr(dish, 'last_updated') else None,
            "restaurant": {
                "id": dish.restaurant.id, "name": dish.restaurant.name, 
                "area": dish.restaurant.area, "address": getattr(dish.restaurant, 'address', ''), 
                "phone": getattr(dish.restaurant, 'phone', ''), "is_verified": dish.restaurant.is_verified,
                "last_updated": format_iso_datetime(dish.restaurant.last_updated) if hasattr(dish.restaurant, 'last_updated') else None
            }
        },
        "message": "Dish details fetched."
    }, status=200)

# --- 3. Reviews Endpoints ---

@csrf_exempt
@require_http_methods(["GET", "POST"])
def dish_reviews(request, dish_id):
    try:
        dish = Dish.objects.get(id=dish_id)
    except Dish.DoesNotExist:
        return JsonResponse({"error": {"code": "DISH_NOT_FOUND", "message": "Dish not found", "fields": {}}}, status=404)

    if request.method == "GET":
        try:
            page = max(1, int(request.GET.get('page', 1)))
            limit = min(100, max(1, int(request.GET.get('limit', 10))))
        except ValueError:
            return JsonResponse({"error": {"code": "INVALID_QUERY_PARAMETERS", "message": "Invalid pagination", "fields": {}}}, status=400)
            
        qs = Review.objects.filter(dish=dish).select_related('user').order_by('-created_at')
        total_items = qs.count()
        reviews = qs[(page - 1) * limit : page * limit]
        
        if is_htmx(request) or request.path.endswith('/htmx'):
            return render(request, 'partials/review_list.html', {'reviews': reviews, 'dish': dish})
        
        items = [{
            "id": r.id, "dish_id": r.dish_id, "user_id": r.user_id, "rating": r.rating, "comment": r.comment,
            "spice_feedback": r.spice_feedback, "taste_feedback": r.taste_feedback, "portion_feedback": r.portion_feedback,
            "created_at": format_iso_datetime(r.created_at) if hasattr(r, 'created_at') else None,
            "user": {"name": r.user.name}
        } for r in reviews]
        total_pages = math.ceil(total_items / limit) if total_items > 0 else 0
        return JsonResponse({"data": {"items": items, "pagination": {"page": page, "limit": limit, "total_items": total_items, "total_pages": total_pages}}, "message": "Reviews fetched successfully."}, status=200)

    elif request.method == "POST":
        user = get_authenticated_user(request)
        if not user:
            return unauthorized_response()

        data = parse_json_body(request)
        try:
            rating = int(data.get('rating'))
        except (TypeError, ValueError):
            rating = None

        if rating is None or rating < 1 or rating > 5:
            return JsonResponse({"error": {"code": "VALIDATION_ERROR", "message": "Invalid rating", "fields": {"rating": "Must be 1-5"}}}, status=400)

        comment = data.get('comment', '')
        if len(comment) > 500:
            return JsonResponse({"error": {"code": "VALIDATION_ERROR", "message": "Comment too long", "fields": {"comment": "Max 500 chars"}}}, status=400)

        for field in ['spice_feedback', 'taste_feedback', 'portion_feedback']:
            val = data.get(field)
            if val and len(str(val)) > 50:
                return JsonResponse({"error": {"code": "VALIDATION_ERROR", "message": f"{field} too long", "fields": {field: "Max 50 chars"}}}, status=400)

        try:
            review = Review.objects.create(
                dish=dish, user=user, rating=rating, comment=comment,
                spice_feedback=data.get('spice_feedback'),
                taste_feedback=data.get('taste_feedback'),
                portion_feedback=data.get('portion_feedback')
            )
        except IntegrityError:
            return JsonResponse({"error": {"code": "REVIEW_ALREADY_EXISTS", "message": "Already reviewed", "fields": {}}}, status=409)

        if is_htmx(request) or request.path.endswith('/htmx'):
            return render(request, 'partials/review_item.html', {'review': review})

        return JsonResponse({"data": {
            "id": review.id, "dish_id": review.dish_id, "user_id": review.user_id, 
            "rating": review.rating, "comment": review.comment,
            "spice_feedback": review.spice_feedback, "taste_feedback": review.taste_feedback, "portion_feedback": review.portion_feedback,
            "created_at": format_iso_datetime(review.created_at) if hasattr(review, 'created_at') else None
        }, "message": "Review submitted successfully."}, status=201)

# --- 4. Favourites Endpoints ---

@csrf_exempt
@require_http_methods(["GET", "POST"])
@require_auth
def user_favourites(request):
    user = request.user

    if request.method == "GET":
        try:
            page = max(1, int(request.GET.get('page', 1)))
            limit = min(100, max(1, int(request.GET.get('limit', 20))))
        except ValueError:
            return JsonResponse({"error": {"code": "INVALID_QUERY_PARAMETERS", "message": "Invalid pagination", "fields": {}}}, status=400)
            
        qs = Favourite.objects.filter(user=user).select_related('dish', 'dish__restaurant').order_by('-created_at')
        total_items = qs.count()
        favs = qs[(page - 1) * limit : page * limit]
        
        if is_htmx(request) or request.path.endswith('/htmx'):
            return render(request, 'partials/favourite_list.html', {'favourites': favs})
            
        items = [{
            "user_id": f.user_id, "dish_id": f.dish_id, "created_at": format_iso_datetime(f.created_at) if hasattr(f, 'created_at') else None,
            "dish": {
                "id": f.dish.id, "name": f.dish.name, "price": f.dish.price, 
                "dietary_tags": f.dish.dietary_tags, "spice_level": f.dish.spice_level, "is_active": f.dish.is_active,
                "restaurant": {"id": f.dish.restaurant.id, "name": f.dish.restaurant.name},
                "rating_summary": {"average": 0.0, "count": 0}
            }
        } for f in favs]
        total_pages = math.ceil(total_items / limit) if total_items > 0 else 0
        return JsonResponse({"data": {"items": items, "pagination": {"page": page, "limit": limit, "total_items": total_items, "total_pages": total_pages}}, "message": "Favourites fetched successfully."}, status=200)

    elif request.method == "POST":
        data = parse_json_body(request)
        dish_id_raw = data.get('dish_id')
        if dish_id_raw is None:
            return JsonResponse({"error": {"code": "VALIDATION_ERROR", "message": "dish_id required", "fields": {}}}, status=400)
        try:
            dish_id = int(dish_id_raw)
            dish = Dish.objects.get(id=dish_id)
        except (TypeError, ValueError):
            return JsonResponse({"error": {"code": "VALIDATION_ERROR", "message": "Invalid dish_id", "fields": {}}}, status=400)
        except Dish.DoesNotExist:
            return JsonResponse({"error": {"code": "DISH_NOT_FOUND", "message": "Dish not found", "fields": {}}}, status=404)

        try:
            Favourite.objects.create(user=user, dish=dish)
        except IntegrityError:
            pass # Already faved

        if is_htmx(request):
            return HttpResponse(status=200) # Simple success

        return JsonResponse({"data": {"dish_id": dish.id}, "message": "Added to favourites"}, status=201)

@csrf_exempt
@require_http_methods(["DELETE"])
@require_auth
def remove_favourite(request, dish_id):
    user = request.user

    deleted_count, _ = Favourite.objects.filter(user=user, dish_id=dish_id).delete()
    
    if deleted_count == 0:
        return JsonResponse({"error": {"code": "FAVOURITE_NOT_FOUND", "message": "Favourite not found", "fields": {}}}, status=404)
    
    if is_htmx(request):
        return HttpResponse("") # Removes element from DOM if swapped outerHTML
        
    return JsonResponse({"data": None, "message": "Dish removed from favourites."}, status=200)

@csrf_exempt
@require_http_methods(["GET"])
def get_categories(request):
    try:
        page = max(1, int(request.GET.get('page', 1)))
        limit = min(100, max(1, int(request.GET.get('limit', 50))))
    except ValueError:
        return JsonResponse({"error": {"code": "INVALID_QUERY_PARAMETERS", "message": "Invalid pagination", "fields": {}}}, status=400)
        
    qs = Category.objects.all()
    total_items = qs.count()
    categories = qs[(page - 1) * limit : page * limit]
    
    items = [{"id": c.id, "name": c.name} for c in categories]
    total_pages = math.ceil(total_items / limit) if total_items > 0 else 0
    return JsonResponse({"data": {"items": items, "pagination": {"page": page, "limit": limit, "total_items": total_items, "total_pages": total_pages}}, "message": "Categories fetched successfully."}, status=200)
