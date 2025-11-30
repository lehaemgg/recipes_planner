from django import forms
from django.forms import inlineformset_factory
from .models import Recipe, Ingredient, Step

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'source_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'validate'}),
            'source_url': forms.URLInput(attrs={'class': 'validate'})
        }

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'quantity', 'unit', 'no_need_to_buy']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'validate'}),
            'quantity': forms.NumberInput(attrs={'class': 'validate', 'step': '0.01'}),
            'unit': forms.TextInput(attrs={'class': 'validate'}),
            'no_need_to_buy': forms.CheckboxInput()
        }

class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ['description', 'photo']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'materialize-textarea'})
        }

IngredientFormSet = inlineformset_factory(
    Recipe, Ingredient, form=IngredientForm, extra=0, can_delete=True
)

StepFormSet = inlineformset_factory(
    Recipe, Step, form=StepForm, extra=0, can_delete=True
)