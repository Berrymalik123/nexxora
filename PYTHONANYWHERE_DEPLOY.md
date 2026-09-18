# Helogram on PythonAnywhere Free

PythonAnywhere free hosting can run this Django project at:

`https://YOUR_USERNAME.pythonanywhere.com`

## 1. Create the account

Create a free PythonAnywhere account and open a **Bash console**.

## 2. Upload the project

The simplest method is to upload the project ZIP through the **Files** tab and extract it into:

`/home/YOUR_USERNAME/helogram`

The folder must contain `manage.py` directly:

`/home/YOUR_USERNAME/helogram/manage.py`

Alternatively, upload the project through GitHub and clone it into the same folder.

## 3. Create a virtual environment

Use the Python version supported by your PythonAnywhere account:

```bash
cd /home/YOUR_USERNAME/helogram
python3.12 -m venv ~/.virtualenvs/helogram
source ~/.virtualenvs/helogram/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

If `python3.12` is unavailable, select a newer Python version supported by your account. Django 6 requires Python 3.12 or newer.

## 4. Prepare Django

```bash
cd /home/YOUR_USERNAME/helogram
source ~/.virtualenvs/helogram/bin/activate
export DJANGO_DEBUG=False
export DJANGO_SECRET_KEY="replace-with-a-long-random-secret"
export DJANGO_ALLOWED_HOSTS="YOUR_USERNAME.pythonanywhere.com"
export CSRF_TRUSTED_ORIGINS="https://YOUR_USERNAME.pythonanywhere.com"
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Use a different strong secret in the real deployment. Do not commit it to GitHub.

## 5. Configure the Web app

In the **Web** tab:

1. Click **Add a new web app**.
2. Choose **Manual configuration**.
3. Select the same Python version used for the virtual environment.
4. Set **Virtualenv** to:

   `/home/YOUR_USERNAME/.virtualenvs/helogram`

5. Open the **WSGI configuration file** and replace its contents with the project WSGI example after changing `YOUR_USERNAME`:

```python
import os
import sys

project_path = "/home/YOUR_USERNAME/helogram"
if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("DJANGO_DEBUG", "False")
os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "YOUR_USERNAME.pythonanywhere.com")
os.environ.setdefault("CSRF_TRUSTED_ORIGINS", "https://YOUR_USERNAME.pythonanywhere.com")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
```

6. Add these static mappings in the **Web** tab:

| URL | Directory |
| --- | --- |
| `/static/` | `/home/YOUR_USERNAME/helogram/staticfiles/` |
| `/media/` | `/home/YOUR_USERNAME/helogram/media/` |

7. Click **Reload**.

## 6. Verify the deployment

Open:

`https://YOUR_USERNAME.pythonanywhere.com/`

Then test registration, login, profile avatar upload, post upload, reel upload, messaging, and admin at `/admin/`.

## Free-plan limitations

- The free site uses the PythonAnywhere subdomain unless a paid plan is used.
- SQLite is suitable for this small deployment, but it is not ideal for high traffic or concurrent writes.
- Uploaded media stays on the account filesystem. Keep regular backups.
- The free plan may restrict outbound email. Helogram's 2FA sends email through Django's configured backend, so configure an allowed SMTP provider before production login. The local console backend is not suitable for live users.
- FFmpeg may not be available on the free plan; reel duration validation may therefore be limited to browser/form checks.