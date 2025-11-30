from django.contrib import admin
from .models import Recipe, Ingredient, Step

class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1

class StepInline(admin.TabularInline):
    model = Step
    extra = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title']
    inlines = [IngredientInline, StepInline]

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'unit', 'recipe']
    list_filter = ['unit', 'recipe']
    search_fields = ['name', 'recipe__title']

@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'order', 'description']
    list_filter = ['recipe']
    ordering = ['recipe', 'order']