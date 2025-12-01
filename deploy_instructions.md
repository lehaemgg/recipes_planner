# PythonAnywhere Deployment Instructions

## 1. Upload Files
- Upload all project files to `/home/yourusername/foodplanner/`
- Replace `yourusername` with your actual PythonAnywhere username

## 2. Install Requirements
```bash
pip3.11 install --user -r requirements.txt
```

## 3. Update Settings
- Edit `foodplanner/settings.py`
- Replace `yourusername` with your actual username in:
  - `ALLOWED_HOSTS`
  - `STATIC_ROOT`
  - `MEDIA_ROOT`

## 4. Run Migrations
```bash
python3.11 manage.py migrate
```

## 5. Collect Static Files
```bash
python3.11 manage.py collectstatic --noinput
```

## 6. Configure Web App
- Go to PythonAnywhere Web tab
- Create new web app (Django)
- Set source code: `/home/yourusername/foodplanner`
- Set WSGI file: `/home/yourusername/foodplanner/wsgi.py`
- Add static files mapping: `/static/` → `/home/yourusername/foodplanner/static`
- Add media files mapping: `/media/` → `/home/yourusername/foodplanner/media`

## 7. Reload Web App
Click "Reload" button in Web tab

Your Food Planner will be available at: `https://yourusername.pythonanywhere.com`