# Adonis Group - Greek Residency & Immigration Website

A luxury, professional Django-based website for real estate and Golden Visa immigration services, inspired by [adonisgroup.gr](https://adonisgroup.gr/).

## Features

- **Modern Luxury Design** - Dark theme with gold accents, elegant typography
- **Responsive Layout** - Mobile-first design that works on all devices
- **Property Listings** - Dynamic property cards with filtering and pagination
- **Contact Forms** - AJAX-powered contact form with validation
- **WhatsApp Integration** - Floating button and direct links
- **Admin Panel** - Full Django admin for content management
- **AOS Animations** - Smooth scroll animations

## Project Structure

```
adonis_site/
├── adonis/                 # Main Django project
│   ├── settings.py         # Project settings
│   ├── urls.py             # Main URL configuration
│   ├── templates/          # HTML templates
│   │   ├── base.html       # Base template
│   │   ├── index.html      # Homepage
│   │   ├── about.html      # About page
│   │   ├── contact.html    # Contact page
│   │   ├── partnerships.html
│   │   └── properties/     # Property templates
│   └── static/             # Static files
│       ├── css/
│       │   └── style.css   # Main stylesheet
│       ├── js/
│       │   └── main.js     # JavaScript
│       └── images/
├── core/                   # Core app (services, contact, etc.)
│   ├── models.py           # Site settings, services, contacts
│   ├── views.py            # Homepage, about, contact views
│   ├── admin.py            # Admin configuration
│   └── forms.py            # Contact form
├── properties/             # Properties app
│   ├── models.py           # Property, Category models
│   ├── views.py            # Property list/detail views
│   └── admin.py            # Property admin
├── manage.py
└── requirements.txt
```

## Installation

1. **Clone or navigate to the project:**
   ```bash
   cd /root/adonis_site
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser for admin access:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Collect static files (for production):**
   ```bash
   python manage.py collectstatic
   ```

7. **Run development server (on port 8001):**
   ```bash
   python manage.py runserver 8001
   # or use the run script:
   ./run.sh
   ```

8. **Access the website:**
   - Homepage: http://127.0.0.1:8001/
   - Admin: http://127.0.0.1:8001/admin/

## Configuration

Edit `adonis/settings.py` to customize:

```python
# Site Settings
SITE_NAME = 'Your Company Name'
SITE_TAGLINE = 'Your Tagline'
WHATSAPP_NUMBER = '+1234567890'
SITE_EMAIL = 'your@email.com'
SITE_ADDRESS = 'Your Address'
```

## Adding Content via Admin

1. **Properties:**
   - Go to Admin > Properties > Add Property
   - Fill in all details including images
   - Set `is_featured=True` to show on homepage

2. **Services:**
   - Go to Admin > Core > Services
   - Add benefits/features shown on homepage

3. **Process Steps:**
   - Go to Admin > Core > Process Steps
   - Add numbered steps for the residency process

4. **Contact Submissions:**
   - View all form submissions in Admin > Core > Contact Submissions

## Technologies Used

- **Backend:** Django 4.2+
- **Database:** SQLite (default), PostgreSQL-ready
- **Frontend:** HTML5, CSS3, JavaScript
- **Fonts:** Google Fonts (Playfair Display, Inter)
- **Icons:** Font Awesome 6
- **Animations:** AOS (Animate on Scroll)

## Deployment

For production deployment:

1. Set `DEBUG = False` in settings.py
2. Configure a proper `SECRET_KEY`
3. Set `ALLOWED_HOSTS`
4. Use PostgreSQL or MySQL for database
5. Configure WhiteNoise for static files
6. Use Gunicorn with Nginx

Example with Gunicorn:
```bash
gunicorn adonis.wsgi:application --bind 0.0.0.0:8000
```

## Customization

### Changing Colors

Edit CSS variables in `static/css/style.css`:
```css
:root {
    --color-gold: #c9a227;        /* Primary accent color */
    --color-black: #0a0a0a;       /* Background */
    --color-dark: #1a1a1a;        /* Secondary background */
}
```

### Adding New Pages

1. Create a view in `core/views.py`
2. Add URL pattern in `core/urls.py`
3. Create template in `adonis/templates/`
4. Add navigation link in `base.html`

## Admin UI Setup

The admin panel uses **[django-unfold](https://github.com/unfoldadmin/django-unfold)** — a modern
Tailwind-based Django admin theme.

### Key files

| File | Purpose |
|------|---------|
| `adonis/settings.py` — `UNFOLD` block | All theme config: title, colors, sidebar nav |
| `core/admin_base.py` | Single import point for `ModelAdmin`, `TabularInline`, `StackedInline` |
| `adonis/static/css/admin-unfold.css` | Custom overrides (thumbnails, badges, row highlights) |

### How it works

All admin classes import their base from `core/admin_base.py` instead of Django directly:

```python
# Every admin.py in the project
from core.admin_base import ModelAdmin, TabularInline, StackedInline
```

`admin_base.py` re-exports from unfold:

```python
from unfold.admin import ModelAdmin, TabularInline, StackedInline
```

To **swap the theme** (e.g. revert to plain Django admin), edit only `admin_base.py`:

```python
# Plain Django — no theme
from django.contrib.admin import ModelAdmin, TabularInline, StackedInline
```

### Reusing in MEDIVEST

1. Copy `core/admin_base.py` to the new project's `core/` folder.
2. Copy the `UNFOLD` block from `settings.py`, then update:
   - `SITE_TITLE`, `SITE_HEADER`, `SITE_SUBHEADER`
   - `COLORS` → pick a different accent color (same 50–950 RGB scale)
   - `SIDEBAR.navigation` → replace app/model URLs with MEDIVEST ones
3. Add to `INSTALLED_APPS` before `django.contrib.admin`:
   ```python
   'unfold',
   'unfold.contrib.filters',
   'unfold.contrib.forms',
   'unfold.contrib.inlines',
   ```
4. Run `pip install django-unfold>=0.81.0` and `collectstatic`.

### Color palette

The current palette is **teal** (RGB scale, Tailwind format).  
To switch to a blue navy palette for MEDIVEST, replace the `COLORS.primary` values:

```python
# Example: deep navy blue
"primary": {
    "50":  "239 246 255",
    "500": "59 130 246",
    "600": "37 99 235",
    "900": "30 58 138",
    "950": "23 37 84",
    # ... fill all 11 shades
},
```

### Property Admin tabs

`PropertyAdmin` in `properties/admin.py` uses unfold's tab feature.
Tabs are declared with the `tabs` list; each fieldset and inline has a `tab` key:

```python
tabs = [
    {"id": "basic",    "title": "Basic Info"},
    {"id": "location", "title": "Location"},
    {"id": "pricing",  "title": "Pricing & Status"},
    {"id": "features", "title": "Features"},
    {"id": "media",    "title": "Media"},       # PropertyMediaInline
    {"id": "units",    "title": "Units"},       # PropertyUnitInline
    {"id": "settings", "title": "Settings"},
]
```

### Thumbnail previews

`PropertyAdmin.thumbnail()` and `PropertyMediaInline.thumb()` render clickable
`<img>` tags styled by `.admin-thumb` in `admin-unfold.css`.

---

## Admin Dashboard — Quick Access & Role-Based Navigation

### Dashboard

The admin home page is a custom template at `adonis/templates/admin/index.html`.
It extends unfold's `admin/base.html` and renders:
- A welcome banner with the user's name and a live clock
- A **Quick Access** card grid with live counters (unread chats, leads today, …)
- The standard unfold app list + recent history below

The card data is injected by `core/admin_dashboard.py:dashboard_callback`, which is
referenced in `UNFOLD["DASHBOARD_CALLBACK"]`.

### Adding or editing dashboard cards

Open `core/admin_dashboard.py` and edit `CARD_DEFINITIONS`:

```python
DashboardCard(
    title="My New Card",
    icon="material_icon_name",     # Material Symbols icon
    link="/admin/app/model/",
    color="teal",                  # teal|blue|violet|amber|rose|emerald|sky
    counter_fn=my_counter_fn,      # callable(request) → int | None
    description="items today",
    roles={ROLE_ADMIN, ROLE_SALES},  # empty set = all staff
),
```

### Role-based sidebar visibility

Each sidebar nav item has a `permission` key — a callable that receives the Django
`request` and returns `True`/`False`. These are built with `_perm(*roles)` in
`settings.py`:

| Helper | Who can see the group |
|--------|-----------------------|
| `_props_staff` | Admin, Content, ContentManager, Sales |
| `_leads_staff` | Admin, Sales, Support |
| `_content_staff` | Admin, Content, ContentManager |
| `_settings_staff` | Admin, ContentManager |
| `_admin_only` | SuperAdmin, Admin |
| `_any_staff` | Any is_staff user |

Superusers always bypass all permission checks.

### Admin roles summary

| Role | Properties | Leads | Content | Settings | Users |
|------|-----------|-------|---------|----------|-------|
| SuperAdmin | ✅ | ✅ | ✅ | ✅ | ✅ |
| Admin | ✅ | ✅ | ✅ | ✅ | ✅ |
| ContentManager | ✅ edit | ✅ view | ✅ | ✅ | ✗ |
| Sales | ✅ view | ✅ | ✗ | ✗ | ✗ |
| Support | ✅ view | ✅ view | ✗ | ✗ | ✗ |
| Content | ✅ edit | ✗ | ✅ | ✗ | ✗ |
| Viewer | ✅ view | ✗ | ✗ | ✗ | ✗ |

Groups are managed via Admin → Users & Access → Roles / Groups.
Assign a user to a group to grant the corresponding role.

### Replicating in MEDIVEST

1. **Copy files:**
   ```
   core/admin_base.py          → theme base imports
   core/admin_dashboard.py     → dashboard cards + badge counters
   adonis/templates/admin/index.html              → dashboard template
   adonis/templates/unfold/helpers/app_list.html  → sidebar icon_class support
   adonis/static/css/admin-unfold.css             → custom styles
   ```

2. **In `settings.py`**, copy the `UNFOLD` block and change:
   - `SITE_TITLE`, `SITE_HEADER`, `SITE_SUBHEADER`
   - `COLORS.primary` (swap to MEDIVEST brand color)
   - `SIDEBAR.navigation` — update all `reverse_lazy(...)` links and `permission` callables

3. **In `admin_dashboard.py`**, update `CARD_DEFINITIONS` to point to MEDIVEST
   models and URLs.

4. **In `core/rbac.py`**, reuse the same role constants — or add project-specific ones.

5. **Run:**
   ```bash
   pip install django-unfold>=0.81.0
   python manage.py collectstatic
   sudo systemctl restart medivest
   ```

---

## License

This project is for educational/demonstration purposes.

## Support

For questions or customization requests, feel free to contact the developer.
