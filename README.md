# Portfolio Cleilton Rodrigues

![Build Status](https://github.com/cleiltonrodriguesofc/portfolio_cleilton/actions/workflows/ci.yml/badge.svg)

This repository contains the personal portfolio and projects developed by Cleilton Rodrigues. The project is built with **Django** and integrates multiple applications to demonstrate skills in web development, data science, and software engineering via **clean architecture**.

## 🚀 Features

- **Modern Design**: Clean, professional interface with a blue color palette and responsive layout.
- **Project Integration**: Modular structure to seamlessly incorporate existing Django projects as apps.
- **Internal Navigation**: All projects accessible without external redirects.
- **Fully Responsive**: Optimized for desktop, tablet, and mobile devices.
- **Professional Layout**: Organized sections for a complete profile presentation.


## 📂 Project Showcase & Business Value

### 📊 Brokerage Analyzer (Investment Tool)
**Business Problem:** Manually calculating taxes for Brazilian investments (Stocks, FIIs, Futures) from PDF notes is error-prone and takes hours per month.
**Solution:** Automated the extraction of financial data from C6 Bank PDF notes using `pdfminer` and `correpy`, generating compliance-ready Excel reports. Reduced tax preparation time by 90%.

### 🌾 ProGrãos (Agro-Industry)
**Business Problem:** Grain weighting and sampling in warehouses requires manual logging, leading to data inconsistency and fraud risks.
**Solution:** Integrated directly with weighing scales via serial port (`pyserial`) to capture real-time weight data, ensuring 100% data integrity for grain reception.

### 📚 Reforço Escolar (SaaS)
**Business Problem:** Private teachers struggle to track student payments and attendance using spreadsheets.
**Solution:** Built a multi-tenant management system with automated WhatsApp billing messages and attendance tracking.

### 🎓 Academic Projects
- **Encyclopedia:** A CS50W implementation of a Wikipedia-like clone to demonstrate mastery of Django basics and Markdown parsing.

## 🧪 Quality Assurance
- **CI/CD:** GitHub Actions pipeline runs tests and linting on every commit.
- **Testing:** Comprehensive unit tests for business logic (e.g., tax calculations).
- **Code Quality:** PEP8 enforcement via Flake8.

## 📁 Project Structure

```
portfolio_cleilton/                         # Main project folder
├── core/                                   # Portfolio core (home, about, projects)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py                             # Homepage, project list, about
│   ├── views.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── static/core/                        # Core static files
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── img/
│   │   │   ├── PERFIL.png
│   │   │   ├── profile-placeholder.jpg
│   │   │   ├── profile-placeholder1.jpg
│   │   │   ├── project-cs50w.jpg
│   │   │   ├── project-encyclopedia.png
│   │   │   ├── project-prograos.png
│   │   │   ├── project-reforco.png
│   │   │   ├── project-sindseb.jpg
│   │   │   └── project-taquanto.jpg
│   │   └── js/
│   │       └── main.js
│   └── templates/
│       ├── _header_shell.html
│       ├── base.html
│       └── core/
│           ├── about.html
│           ├── home.html
│           └── project_list.html
│
├── brokerage_analyzer/                     # Brokerage Note Analyzer (PDF/Excel)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── src/                                # Core Business Logic
│   │   ├── use_cases/
│   │   │   └── data_aggregator.py
│   │   └── infrastructure/
│   │       ├── pdf_parser.py
│   │       └── excel_exporter.py
│   └── templates/brokerage_analyzer/
│       ├── dashboard.html
│       └── upload.html
│
├── encyclopedia/                           # CS50Wiki (Markdown-based Encyclopedia)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── entries/                            # Markdown entries stored locally
│   │   ├── Css.md
│   │   ├── Django.md
│   │   ├── Git.md
│   │   ├── HTML.md
│   │   ├── Python.md
│   │   ├── Tcp.md
│   │   └── Wiki.md
│   ├── migrations/
│   │   └── __init__.py
│   ├── models.py
│   ├── storage.py                          # Custom FileSystemStorage
│   ├── tests.py
│   ├── urls.py                             # /projects/encyclopedia/
│   ├── util.py                             # Entry helpers (list, get, save)
│   ├── views.py
│   ├── static/
│   │   ├── encyclopedia/
│   │   │   └── styles.css
│   │   └── images/
│   │       ├── favicon.ico
│   │       └── wikipedia-logo.png
│   └── templates/encyclopedia/
│       ├── edit.html
│       ├── entry.html
│       ├── error.html
│       ├── index.html
│       ├── layout.html
│       ├── newpage.html
│       └── search.html
│
├── reforco/                                # Student Academic Management System
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   ├── static/reforco/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── img/
│   │   │   └── logo-reforco.png
│   │   └── js/
│   │       └── script.js
│   └── templates/reforco/
│       ├── aluno_detail.html
│       ├── aluno_form.html
│       ├── aluno_list.html
│       ├── base.html
│       ├── dashboard.html
│       ├── mensagens.html
│       ├── pagamento_form.html
│       ├── pagamento_list.html
│       ├── presenca_form.html
│       ├── presenca_list.html
│       ├── relatorio_pagamentos.html
│       └── relatorio_presenca.html
│
├── prograos/                               # ProGrãos (Grain Management System)
│   ├── __pycache__/
│   ├── apps.py
│   ├── forms.py
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   ├── models.py
│   ├── reports.py
│   ├── scale_integration.py
│   ├── scale_views.py
│   ├── serializers.py
│   ├── signals.py
│   ├── static/prograos/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── img/
│   │   └── js/
│   │       └── main.js
│   ├── templates/prograos/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── amostra_*                      # (list, detail, form, delete)
│   │   ├── nota_*                         # (list, detail, form, delete)
│   │   ├── pagamento_*                    # (list, form, delete)
│   │   ├── pesagem_*                      # (list, form, update, delete)
│   │   └── financeiro_*                   # (list, detail, form)
│   ├── test_views.py
│   ├── tests.py
│   ├── tests_simple.py
│   ├── urls.py
│   ├── utils.py
│   ├── utils_demo.py
│   └── views.py
│
├── contact/                                # Contact system
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   └── templates/contact/
│       └── contact.html
│
├── portfolio_cleilton/                     # Global settings module
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── manage.py                               # Django management script
├── db.sqlite3                              # Local database
└── README.md                                # Project documentation
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
- `/projetos/reforco/` → Reforço Escolar (Academic Management System)
- `/projetos/prograos/` → ProgGrãos (Grain Management System)
- `/projetos/brokerage_analyzer/` → Brokerage Analyzer (Investment Reports)
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