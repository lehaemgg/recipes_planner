# Recipe Export/Import Guide

## Export Recipe (Local)

To export a recipe from your local database to a portable JSON file:

```bash
python export_recipe.py <recipe_url>
```

Example:
```bash
python export_recipe.py https://menunedeli.ru/recipe/ovoshhi-zapechennye-v-duxovke/
```

This creates a `recipe_<id>.json` file with all recipe data including photos (base64 encoded).

## Import Recipe (PythonAnywhere)

1. Go to "My Recipes" page
2. Click the blue upload button (📤)
3. Select the exported JSON file
4. Click "Import"

The recipe will be imported with all ingredients, steps, and photos.

## Workflow

1. **Local**: Import from URL → `python manage.py import_recipes --urls <url>`
2. **Local**: Export to file → `python export_recipe.py <url>`
3. **Upload**: Transfer `recipe_<id>.json` to PythonAnywhere
4. **PythonAnywhere**: Import via UI button

No database upload or migrations needed!
