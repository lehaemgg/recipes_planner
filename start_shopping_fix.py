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
        
        # Clear shopping list
        CustomShoppingItem.objects.all().delete()
        MealPlan.objects.filter(in_shopping_list=True).update(in_shopping_list=False)
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})