from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, role='user'):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'users'

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    area = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    is_verified = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'restaurants'

class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'categories'

class Dish(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='dishes')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='dishes')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    price = models.IntegerField(help_text="Price in paise", db_index=True)
    image_url = models.URLField(blank=True, null=True)
    ingredients = models.JSONField(default=list, blank=True)
    ingredients_to_avoid = models.JSONField(default=list, blank=True)
    dietary_tags = models.JSONField(default=list, blank=True)
    spice_level = models.IntegerField(default=0, db_index=True)
    sweet_level = models.IntegerField(default=0, db_index=True)
    can_be_customised = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, db_index=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dishes'

class Review(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = models.TextField(blank=True, default='')
    spice_feedback = models.CharField(max_length=50, blank=True, null=True)
    taste_feedback = models.CharField(max_length=50, blank=True, null=True)
    portion_feedback = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews'
        constraints = [
            models.UniqueConstraint(fields=['dish', 'user'], name='unique_dish_user_review')
        ]

class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourites')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='favourites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favourites'
        constraints = [
            models.UniqueConstraint(fields=['user', 'dish'], name='unique_user_dish_favourite')
        ]
