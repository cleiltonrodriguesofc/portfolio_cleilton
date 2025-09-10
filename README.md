# Cleilton's Professional Portfolio

A professional portfolio built with Django, featuring a modern blue-themed design to integrate and showcase development projects.

## 🚀 Features

- **Modern Design**: Clean, professional interface with a blue color palette and responsive layout.
- **Project Integration**: Modular structure to seamlessly incorporate existing Django projects as apps.
- **Internal Navigation**: All projects accessible without external redirects.
- **Fully Responsive**: Optimized for desktop, tablet, and mobile devices.
- **Professional Layout**: Organized sections for a complete profile presentation.

## 📁 Project Structure

```
portfolio_cleilton/                  # Main project folder
├── core/                            # Core portfolio app (home, about pages)
│   ├── __init__.py                  # App initializer
│   ├── admin.py                     # Admin panel configuration
│   ├── apps.py                      # App configuration
│   ├── models.py                    # Database models
│   ├── tests.py                     # Unit tests
│   ├── urls.py                      # Main URLs
│   ├── views.py                     # Home page views
│   ├── migrations/                  # Database migrations
│   │   └── __init__.py
│   ├── static/                      # Static files (CSS, JS, images)
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── img/                     # Profile and project images
│   │   │   ├── profile-placeholder.jpg
│   │   │   ├── profile-placeholder1.jpg
│   │   │   ├── project-cs50w.jpg
│   │   │   ├── project-sindseb.jpg
│   │   │   └── project-taquanto.jpg
│   │   └── js/
│   │       └── main.js
│   └── templates/                   # Core templates
│       ├── _footer_shell.html
│       ├── _header_shell.html
│       ├── base.html
│       ├── portfolio_base.html
│       └── core/
│           ├── about.html
│           └── home.html
├── reforco/                         # App for student/project management
│   ├── __init__.py                  # App initializer
│   ├── admin.py                     # Admin configuration
│   ├── apps.py                      # App configuration
│   ├── forms.py                     # Forms for data input
│   ├── models.py                    # Models (students, payments, attendance)
│   ├── tests.py                     # Tests
│   ├── urls.py                      # App-specific URLs
│   ├── views.py                     # Views for lists, details, reports
│   ├── migrations/                  # Database migrations
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   ├── static/reforco/              # App-specific static files
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── img/
│   │   │   └── logo-reforco.png
│   │   └── js/
│   │       └── script.js
│   └── templates/reforco/           # App templates
│       ├── aluno_detail.html        # Student detail view
│       ├── aluno_form.html          # Student form
│       ├── aluno_list.html          # Student list
│       ├── base.html
│       ├── dashboard.html           # Main dashboard
│       ├── mensagens.html           # Messages
│       ├── pagamento_form.html      # Payment form
│       ├── pagamento_list.html      # Payment list
│       ├── presenca_form.html       # Attendance form
│       ├── presenca_list.html       # Attendance list
│       ├── relatorio_pagamentos.html # Payment report
│       └── relatorio_presenca.html  # Attendance report
├── contact/                         # Contact app
│   ├── __init__.py                  # App initializer
│   ├── admin.py                     # Admin configuration
│   ├── apps.py                      # App configuration
│   ├── forms.py                     # Contact forms
│   ├── models.py                    # Contact models
│   ├── tests.py                     # Tests
│   ├── urls.py                      # Contact URLs
│   ├── views.py                     # Contact views
│   ├── migrations/                  # Migrations
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   └── templates/contact/           # Contact templates
│       └── contact.html
├── portfolio_cleilton/              # Django settings
│   ├── __init__.py
│   ├── asgi.py                      # ASGI config for async
│   ├── settings.py                  # Main settings (databases, apps)
│   ├── urls.py                      # Root URLs
│   └── wsgi.py                      # WSGI config for deployment
├── db.sqlite3                       # Local database file
├── manage.py                        # Django management script
└── README.md                        # Project description
```

## 🛠️ Technologies Used

- **Backend**: Django 5.2.5
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLite (development)
- **Styling**: Custom CSS with a professional blue palette
- **Icons**: Font Awesome
- **Responsiveness**: Bootstrap Grid System

## 🎨 Design

### Color Palette
- **Dark Blue**: #0A192F (main backgrounds)
- **Medium Blue**: #4A90E2 (highlight elements)
- **Light Blue**: #CCD6F6 (secondary text)
- **White**: #FFFFFF (card backgrounds)
- **Gray**: #8892B0 (supporting text)

### Portfolio Sections
1. **Hero Section**: Professional introduction with photo and summary
2. **About Me**: Professional experience and career goals
3. **Technical Skills**: Technologies categorized for clarity
4. **Featured Projects**: Showcase of key projects
5. **Contact**: Form and social media links

## 🚀 How to Run

### Prerequisites
- Python 3.11+
- pip

### Installation
```bash
# Clone or download the project
cd portfolio_cleilton

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Start the server
python manage.py runserver
```

### Access
- **Portfolio**: http://localhost:8000
- **Admin**: http://localhost:8000/admin (create superuser with `python manage.py createsuperuser`)

## 📝 Integrating Projects

### 1. Existing Django Projects
To integrate a project (e.g., a student management system):
```bash
# Copy project files to a new app
python manage.py startapp new_project
cp your_project/models.py new_project/models.py
cp your_project/views.py new_project/views.py
cp -r your_project/templates/* templates/new_project/
cp -r your_project/static/* static/new_project/

# Update URLs in new_project/urls.py
# Add to INSTALLED_APPS in settings.py
# Run migrations
python manage.py makemigrations new_project
python manage.py migrate
```

### 2. Frontend/React Projects
```bash
# Option A: Static build
npm run build
cp -r build/* static/new_project/

# Option B: Embed via iframe for live projects
# Add iframe in Django template
```

## 🔧 Customization

### Update Personal Information
Edit `core/views.py` to modify:
- Name and title
- Professional summary
- Social media links

### Add New Projects
1. Create a new Django app:
```bash
python manage.py startapp new_project
```
2. Add to `INSTALLED_APPS` in `settings.py`.
3. Configure URLs in `portfolio_cleilton/urls.py`.
4. Create views and templates.

### Modify Design
- **CSS**: Update `static/css/style.css`.
- **Colors**: Adjust CSS variables in `style.css`.
- **Layout**: Edit templates in `templates/`.

## 📱 Project URLs
- `/` → Homepage
- `/projects/` → Project list
- `/projects/reforco/` → Reforço Escolar (Academic Management System)
- `/projects/prograos/` → ProgGrãos (Grain Management System)
- `/contact/` → Contact page


## 🎯 Next Steps
1. **Integrate Projects**: Follow `INTEGRACAO_PROJETOS.md` for existing projects.
2. **Personalize**: Update with your real details.
3. **Add Photo**: Replace `static/img/profile-placeholder.jpg`.
4. **Test Projects**: Verify each project locally.
5. **Prepare for Deployment**: Configure for production (e.g., PostgreSQL, static file hosting).

## 📞 Support
For help with integration or customization:
1. Refer to Django documentation.
2. Test locally before making changes.

## 📄 License
This project is a personal portfolio created by Cleilton.

---

**Built with ❤️ using Django and plenty of coffee ☕**