# Food Planner - Django Recipe Management App

## Project Structure
```
food planner/
├── foodplanner/          # Main Django project
│   ├── settings.py       # Project settings
│   ├── urls.py          # Main URL configuration
│   └── wsgi.py          # WSGI configuration
├── hello/               # Recipe management app
│   ├── models.py        # Recipe, Ingredient, Step models
│   ├── views.py         # CRUD views for recipes
│   ├── forms.py         # Django forms and formsets
│   ├── urls.py          # App URL patterns
│   ├── admin.py         # Admin interface configuration
│   └── templates/hello/ # HTML templates
│       ├── base.html    # Base template with Material Design
│       ├── recipe_list.html
│       ├── recipe_detail.html
│       ├── recipe_form.html
│       └── recipe_confirm_delete.html
├── static/              # CSS, JS, images
├── media/               # User uploaded files
├── manage.py            # Django management script
└── requirements.txt     # Python dependencies

## Database Models

### Recipe
- title: CharField(200)
- created_at: DateTimeField(auto_now_add=True)
- updated_at: DateTimeField(auto_now=True)

### Ingredient
- recipe: ForeignKey(Recipe)
- name: CharField(100)
- quantity: DecimalField(10,2)
- unit: CharField(50)

### Step
- recipe: ForeignKey(Recipe)
- order: PositiveIntegerField
- description: TextField
- photo: ImageField(upload_to='step_photos/')

## Features
- CRUD operations for recipes
- Dynamic ingredient/step forms
- Photo uploads for steps
- Material Design UI (Materialize CSS)
- Admin interface
- Responsive design

## URLs
- / - Recipe list
- /recipe/<id>/ - Recipe detail
- /recipe/new/ - Create recipe
- /recipe/<id>/edit/ - Edit recipe
- /recipe/<id>/delete/ - Delete recipe
- /admin/ - Admin interface

## Dependencies
- Django 5.2.8
- Pillow 12.0.0 (for image handling)
- Materialize CSS (CDN)

## Admin Credentials
- Username: admin
- Password: admin123