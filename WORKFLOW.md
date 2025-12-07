# Recipe Import Workflow

## Step 1: Import from URL (Local)
```bash
python manage.py import_recipes --urls https://menunedeli.ru/recipe/ovoshhi-zapechennye-v-duxovke/
```

## Step 2: Export to JSON (Local)
```bash
python export_recipe.py https://menunedeli.ru/recipe/ovoshhi-zapechennye-v-duxovke/
```
Creates `recipe_<id>.json` with all data including photos (base64 encoded)

## Step 3: Upload to PythonAnywhere
Upload the `recipe_<id>.json` file via PythonAnywhere Files tab

## Step 4: Import on PythonAnywhere
1. Go to "My Recipes" page
2. Click blue upload button (📤)
3. Select the JSON file
4. Click "Import"

Done! No database sync or migrations needed.
