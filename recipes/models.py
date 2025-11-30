from django.db import models
import os
from PIL import Image

class Recipe(models.Model):
    title = models.CharField(max_length=200)
    source_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    def delete(self, *args, **kwargs):
        # Delete associated step photos
        for step in self.steps.all():
            if step.photo and os.path.isfile(step.photo.path):
                os.remove(step.photo.path)
        super().delete(*args, **kwargs)

class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    no_need_to_buy = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} {self.unit} {self.name}"

class Step(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps')
    order = models.PositiveIntegerField()
    description = models.TextField()
    photo = models.ImageField(upload_to='step_photos/', blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Step {self.order}: {self.description[:50]}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.photo:
            img = Image.open(self.photo.path)
            if img.height > 800 or img.width > 800:
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                img.save(self.photo.path, optimize=True, quality=85)
    
    def delete(self, *args, **kwargs):
        # Delete photo file when step is deleted
        if self.photo and os.path.isfile(self.photo.path):
            os.remove(self.photo.path)
        super().delete(*args, **kwargs)

class MealPlan(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('added_to_list', 'Added to List'),
        ('in_shopping', 'In Shopping'),
        ('shopped', 'Shopped'),
    ]
    
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    date = models.DateField()
    portions = models.PositiveIntegerField(default=1)
    in_shopping_list = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'created_at']

    def __str__(self):
        return f"{self.recipe.title} - {self.date} ({self.portions} portions)"

class ShoppingListItem(models.Model):
    ingredient_name = models.CharField(max_length=100)
    amounts = models.TextField()  # JSON field to store different amounts and units
    dont_need = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ingredient_name}: {self.amounts}"

class CustomShoppingItem(models.Model):
    name = models.CharField(max_length=100)
    amount = models.CharField(max_length=50, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.amount}"

class ActiveShoppingItem(models.Model):
    name = models.CharField(max_length=100)
    amount = models.CharField(max_length=50, blank=True)
    is_purchased = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.amount}"

class ShoppingHistory(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('returned', 'Returned to List'),
        ('never_purchased', 'Never Purchased'),
    ]
    
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    items_data = models.TextField()  # JSON field to store items
    
    def __str__(self):
        return f"Shopping {self.date.strftime('%Y-%m-%d %H:%M')} - {self.status}"