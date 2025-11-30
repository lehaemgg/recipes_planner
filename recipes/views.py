from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from .models import Recipe, Ingredient, Step, MealPlan, ShoppingListItem, CustomShoppingItem, ActiveShoppingItem, ShoppingHistory
from .forms import RecipeForm, IngredientFormSet, StepFormSet
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from recipe_scraper import scrape_menunedeli_recipe

def login_view(request):
    if request.method == 'POST':
        passcode = request.POST.get('passcode')
        if passcode == '@Weofinsdfon2134':
            request.session['authenticated'] = True
            return redirect('calendar')
        else:
            return render(request, 'recipes/login.html', {'error': 'Invalid passcode'})
    return render(request, 'recipes/login.html')

def hello_world(request):
    if not request.session.get('authenticated'):
        return redirect('login')
    return redirect('calendar')

def require_auth(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('authenticated'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

@require_auth
def calendar_view(request):
    from datetime import datetime, timedelta
    import calendar
    
    # Get week offset from URL parameter
    week_offset = int(request.GET.get('week', 0))
    
    # Calculate current week start (Monday)
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    
    # Generate week days
    week_days = []
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        meal_plans = MealPlan.objects.filter(date=day)
        week_days.append({
            'date': day,
            'day_name': calendar.day_name[day.weekday()],
            'meal_plans': meal_plans,
            'is_past': day < today,
            'is_today': day == today
        })
    
    week_end = start_of_week + timedelta(days=6)
    
    recipes = Recipe.objects.all()
    
    return render(request, 'recipes/calendar.html', {
        'week_days': week_days,
        'recipes': recipes,
        'week_offset': week_offset,
        'prev_week': week_offset - 1,
        'next_week': week_offset + 1,
        'week_start': start_of_week,
        'week_end': week_end
    })

def add_meal_plan(request):
    if request.method == 'POST':
        recipe_id = request.POST.get('recipe_id')
        date = request.POST.get('date')
        portions = int(request.POST.get('portions', 1))
        
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        
        # Create new meal plan (allow multiple recipes per day)
        MealPlan.objects.create(
            recipe=recipe,
            date=date,
            portions=portions
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

def update_meal_plan_portions(request):
    if request.method == 'POST':
        meal_plan_id = request.POST.get('meal_plan_id')
        portions = int(request.POST.get('portions', 1))
        
        meal_plan = get_object_or_404(MealPlan, pk=meal_plan_id)
        meal_plan.portions = portions
        meal_plan.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

def remove_meal_plan(request):
    if request.method == 'POST':
        meal_plan_id = request.POST.get('meal_plan_id')
        meal_plan = get_object_or_404(MealPlan, pk=meal_plan_id)
        
        # If it was in shopping list, remove it first
        if meal_plan.in_shopping_list:
            meal_plan.in_shopping_list = False
            meal_plan.save()
        
        meal_plan.delete()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

def add_to_shopping_list(request):
    if request.method == 'POST':
        try:
            meal_plan_id = request.POST.get('meal_plan_id')
            meal_plan = get_object_or_404(MealPlan, pk=meal_plan_id)
            
            # Mark as in shopping list
            meal_plan.in_shopping_list = True
            meal_plan.status = 'added_to_list'
            meal_plan.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False})

def remove_from_shopping_list(request):
    if request.method == 'POST':
        try:
            meal_plan_id = request.POST.get('meal_plan_id')
            meal_plan = get_object_or_404(MealPlan, pk=meal_plan_id)
            
            # Mark as not in shopping list
            meal_plan.in_shopping_list = False
            meal_plan.status = 'planned'
            meal_plan.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False})

@require_auth
def shopping_list_view(request):
    from datetime import datetime
    from collections import defaultdict
    
    today = datetime.now().date()
    
    # Get all meal plans that are in shopping list and from today onwards
    meal_plans = MealPlan.objects.filter(
        in_shopping_list=True,
        date__gte=today
    )
    
    # Aggregate ingredients
    ingredient_amounts = defaultdict(list)
    
    for meal_plan in meal_plans:
        for ingredient in meal_plan.recipe.ingredients.all():
            if not ingredient.no_need_to_buy:  # Skip ingredients marked as no need to buy
                total_quantity = float(ingredient.quantity * meal_plan.portions)
                ingredient_amounts[ingredient.name].append({
                    'quantity': total_quantity,
                    'unit': ingredient.unit
                })
    
    # Format for display - don't combine different units
    formatted_items = []
    for name, amounts in ingredient_amounts.items():
        # Group by unit and sum quantities of same unit
        unit_totals = defaultdict(float)
        for amount in amounts:
            unit_totals[amount['unit']] += amount['quantity']
        
        # Create separate entries for each unit
        for unit, total_qty in unit_totals.items():
            formatted_items.append({
                'name': name,
                'amounts': f"{total_qty} {unit}"
            })
    
    # Sort by ingredient name
    formatted_items.sort(key=lambda x: x['name'])
    
    # Get custom shopping items
    custom_items = CustomShoppingItem.objects.all().order_by('name')
    
    return render(request, 'recipes/shopping_list.html', {
        'shopping_items': formatted_items,
        'custom_items': custom_items
    })

def add_custom_item(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        amount = request.POST.get('amount', '').strip()
        
        if name:
            CustomShoppingItem.objects.create(name=name, amount=amount)
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': False, 'error': 'Name is required'})
    
    return JsonResponse({'success': False})

def toggle_custom_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item = get_object_or_404(CustomShoppingItem, pk=item_id)
        item.is_completed = not item.is_completed
        item.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

def delete_custom_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item = get_object_or_404(CustomShoppingItem, pk=item_id)
        item.delete()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

def meal_plan_detail(request, pk):
    meal_plan = get_object_or_404(MealPlan, pk=pk)
    
    # Calculate ingredients with portions
    ingredients_with_portions = []
    for ingredient in meal_plan.recipe.ingredients.all():
        ingredients_with_portions.append({
            'name': ingredient.name,
            'quantity': ingredient.quantity * meal_plan.portions,
            'unit': ingredient.unit
        })
    
    return render(request, 'recipes/meal_plan_detail.html', {
        'meal_plan': meal_plan,
        'ingredients_with_portions': ingredients_with_portions
    })

@require_auth
def recipe_list(request):
    recipes = Recipe.objects.all().order_by('-created_at')
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})

def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})

def recipe_create(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        ingredient_formset = IngredientFormSet(request.POST, prefix='ingredients')
        step_formset = StepFormSet(request.POST, request.FILES, prefix='steps')
        
        print(f"Form valid: {form.is_valid()}")
        print(f"Ingredient formset valid: {ingredient_formset.is_valid()}")
        print(f"Step formset valid: {step_formset.is_valid()}")
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        if not ingredient_formset.is_valid():
            print(f"Ingredient errors: {ingredient_formset.errors}")
        if not step_formset.is_valid():
            print(f"Step errors: {step_formset.errors}")
        
        if form.is_valid() and ingredient_formset.is_valid() and step_formset.is_valid():
            recipe = form.save()
            
            # Save ingredients
            ingredients = ingredient_formset.save(commit=False)
            for ingredient in ingredients:
                ingredient.recipe = recipe
                ingredient.save()
            
            # Save steps with proper ordering
            steps = step_formset.save(commit=False)
            for i, step in enumerate(steps):
                step.recipe = recipe
                step.order = i + 1
                step.save()
            
            # Handle save and close vs save
            if 'save_and_close' in request.POST:
                return redirect('recipe_list')
            else:
                return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm()
        ingredient_formset = IngredientFormSet(prefix='ingredients', queryset=Ingredient.objects.none())
        step_formset = StepFormSet(prefix='steps', queryset=Step.objects.none())
    
    return render(request, 'recipes/recipe_form.html', {
        'form': form,
        'ingredient_formset': ingredient_formset,
        'step_formset': step_formset,
        'action': 'Create'
    })

def recipe_edit(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    
    if request.method == 'POST':
        form = RecipeForm(request.POST, instance=recipe)
        ingredient_formset = IngredientFormSet(request.POST, instance=recipe, prefix='ingredients')
        step_formset = StepFormSet(request.POST, request.FILES, instance=recipe, prefix='steps')
        
        if form.is_valid() and ingredient_formset.is_valid() and step_formset.is_valid():
            recipe = form.save()
            ingredient_formset.save()
            
            # Save steps with proper ordering
            steps = step_formset.save(commit=False)
            for i, step in enumerate(steps):
                step.recipe = recipe
                step.order = i + 1
                step.save()
            step_formset.save_m2m()
            
            # Handle save and close vs save
            if 'save_and_close' in request.POST:
                return redirect('recipe_list')
            else:
                return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm(instance=recipe)
        ingredient_formset = IngredientFormSet(instance=recipe, prefix='ingredients')
        step_formset = StepFormSet(instance=recipe, prefix='steps')
    
    return render(request, 'recipes/recipe_form.html', {
        'form': form,
        'ingredient_formset': ingredient_formset,
        'step_formset': step_formset,
        'recipe': recipe,
        'action': 'Edit'
    })

def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        recipe.delete()
        return redirect('recipe_list')
    return render(request, 'recipes/recipe_confirm_delete.html', {'recipe': recipe})

def import_recipe(request):
    """Import recipe data from external URL"""
    if request.method == 'POST':
        url = request.POST.get('url', '').strip()
        
        if not url:
            return JsonResponse({'success': False, 'error': 'URL is required'})
        
        # Currently only supports menunedeli.ru
        if 'menunedeli.ru' not in url:
            return JsonResponse({'success': False, 'error': 'Only menunedeli.ru is supported'})
        
        result = scrape_menunedeli_recipe(url)
        return JsonResponse(result)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def start_shopping(request):
    if request.method == 'POST':
        import json
        from datetime import datetime
        from collections import defaultdict
        
        today = datetime.now().date()
        
        # Get all meal plans that are in shopping list and from today onwards
        meal_plans = MealPlan.objects.filter(
            in_shopping_list=True,
            date__gte=today
        )
        
        # Aggregate ingredients (excluding "Got it" checked ones)
        ingredient_amounts = defaultdict(list)
        
        for meal_plan in meal_plans:
            for ingredient in meal_plan.recipe.ingredients.all():
                if not ingredient.no_need_to_buy:
                    total_quantity = float(ingredient.quantity * meal_plan.portions)
                    ingredient_amounts[ingredient.name].append({
                        'quantity': total_quantity,
                        'unit': ingredient.unit
                    })
        
        # Format items
        for name, amounts in ingredient_amounts.items():
            unit_totals = defaultdict(float)
            for amount in amounts:
                unit_totals[amount['unit']] += amount['quantity']
            
            for unit, total_qty in unit_totals.items():
                ActiveShoppingItem.objects.create(
                    name=name,
                    amount=f"{total_qty} {unit}"
                )
        
        # Add custom items (not completed)
        for custom_item in CustomShoppingItem.objects.filter(is_completed=False):
            ActiveShoppingItem.objects.create(
                name=custom_item.name,
                amount=custom_item.amount or ''
            )
        
        # Clear shopping list and update status
        CustomShoppingItem.objects.all().delete()
        MealPlan.objects.filter(in_shopping_list=True).update(in_shopping_list=False, status='in_shopping')
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

def shopping_tab(request):
    items = ActiveShoppingItem.objects.all().order_by('name')
    return render(request, 'recipes/shopping_tab.html', {'items': items})

def toggle_shopping_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item = get_object_or_404(ActiveShoppingItem, pk=item_id)
        item.is_purchased = not item.is_purchased
        item.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def finish_shopping(request):
    if request.method == 'POST':
        import json
        
        items = ActiveShoppingItem.objects.all()
        unpurchased = items.filter(is_purchased=False)
        
        if not unpurchased.exists():
            # All items purchased - move to history and update meal plan status
            items_data = json.dumps([{'name': item.name, 'amount': item.amount, 'purchased': item.is_purchased} for item in items])
            ShoppingHistory.objects.create(status='completed', items_data=items_data)
            MealPlan.objects.filter(status='in_shopping').update(status='shopped')
            items.delete()
            return JsonResponse({'success': True, 'all_purchased': True})
        else:
            # Some items not purchased - ask user
            return JsonResponse({'success': True, 'all_purchased': False, 'unpurchased_count': unpurchased.count()})
    
    return JsonResponse({'success': False})

def handle_unpurchased(request):
    if request.method == 'POST':
        import json
        
        action = request.POST.get('action')  # 'return' or 'discard'
        items = ActiveShoppingItem.objects.all()
        unpurchased = items.filter(is_purchased=False)
        
        if action == 'return':
            # Add unpurchased items back to custom shopping list
            for item in unpurchased:
                CustomShoppingItem.objects.create(name=item.name, amount=item.amount)
            
            items_data = json.dumps([{'name': item.name, 'amount': item.amount, 'purchased': item.is_purchased} for item in items])
            ShoppingHistory.objects.create(status='returned', items_data=items_data)
        else:
            # Discard unpurchased items
            items_data = json.dumps([{'name': item.name, 'amount': item.amount, 'purchased': item.is_purchased} for item in items])
            ShoppingHistory.objects.create(status='never_purchased', items_data=items_data)
        
        items.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

def shopping_history(request):
    history = ShoppingHistory.objects.all().order_by('-date')
    return render(request, 'recipes/shopping_history.html', {'history': history})

def shopping_history_detail(request, pk):
    import json
    history = get_object_or_404(ShoppingHistory, pk=pk)
    items = json.loads(history.items_data)
    return render(request, 'recipes/shopping_history_detail.html', {'history': history, 'items': items})

def back_to_list(request):
    if request.method == 'POST':
        from datetime import datetime
        
        today = datetime.now().date()
        
        # Move active shopping items back to shopping list
        for item in ActiveShoppingItem.objects.all():
            # Check if it's a recipe ingredient - add back to meal plan
            meal_plans = MealPlan.objects.filter(
                recipe__ingredients__name=item.name,
                date__gte=today
            ).distinct()
            
            if meal_plans.exists():
                # Mark meal plans as in shopping list
                meal_plans.update(in_shopping_list=True, status='added_to_list')
            else:
                # Add as custom item if not from recipe
                CustomShoppingItem.objects.create(
                    name=item.name,
                    amount=item.amount
                )
        
        # Clear active shopping items
        ActiveShoppingItem.objects.all().delete()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})