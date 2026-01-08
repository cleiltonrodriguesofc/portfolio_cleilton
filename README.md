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

### 🏢 Professional Projects
Real-world solutions solving actual business problems.

#### 📊 Brokerage Analyzer (Investment Tool)
**Business Problem:** Manually calculating taxes for Brazilian investments (Stocks, FIIs, Futures) from PDF notes is error-prone and takes hours per month.
**Solution:** Automated the extraction of financial data from C6 Bank PDF notes using `pdfminer` and `correpy`, generating compliance-ready Excel reports. Reduced tax preparation time by 90%.

#### 🌾 ProGrãos (Agro-Industry)
**Business Problem:** Grain weighting and sampling in warehouses requires manual logging, leading to data inconsistency and fraud risks.
**Solution:** Integrated directly with weighing scales via serial port (`pyserial`) to capture real-time weight data, ensuring 100% data integrity for grain reception.

#### 📚 Reforço Escolar (SaaS)
**Business Problem:** Private teachers struggle to track student payments and attendance using spreadsheets.
**Solution:** Built a multi-tenant management system with automated WhatsApp billing messages and attendance tracking.

### 🎓 Academic Projects (CS50W)
Projects developed for Harvard's CS50 Web Programming certification.

#### 🛍️ Commerce (Auctions)
An eBay-like auction site where users can post listings, place bids, comment on auctions, and manage a watchlist. Features active listing filtering and category organization.

#### 🌐 Network (Social Media)
A Twitter-like social network featuring asynchronous posts, likes, and a following system. Demonstrates single-page-like interactions using Vanilla JS and Django.

#### 🔍 Search (Google Clone)
A faithful recreation of Google's Search, Image Search, and Advanced Search front-end logic, including "I'm Feeling Lucky" redirect functionality.

#### 📧 Mail (SPA)
A single-page email client where users can send, reply, and archive emails without page reloads, using a JSON API backend and extensive JavaScript DOM manipulation.

#### 📖 Encyclopedia (Wiki)
A Wikipedia clone that allows users to create and edit encyclopedia entries using Markdown, featuring search functionality and random page discovery.

## 🧪 Quality Assurance
- **CI/CD:** GitHub Actions pipeline runs tests and linting on every commit.
- **Testing:** Comprehensive unit tests for business logic (e.g., tax calculations).
- **Code Quality:** PEP8 enforcement via Flake8.

## 📁 Project Structure

```
portfolio_cleilton/                         # Main project folder
├── core/                                   # Portfolio Framework (Home, About, Layout)
├── brokerage_analyzer/                     # Investment Tax Calculator
├── commerce/                               # Auction Site (CS50W)
├── contact/                                # Contact Form Handler
├── encyclopedia/                           # Wiki System (CS50W)
├── mail/                                   # Single Page Email Client (CS50W)
├── network/                                # Social Media Platform (CS50W)
├── prograos/                               # Grain Management System
├── reforco/                                # Student Management SaaS
├── search/                                 # Google Search Clone (CS50W)
├── portfolio_cleilton/                     # Project Settings
├── manage.py
├── db.sqlite3
└── README.md
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

### Security & Deployment Envs

For production deployment, ensure the following environment variables are set:

| Variable | Description | Example |
|----------|-------------|---------|
| `DEBUG` | **Must** be `False` in production | `False` |
| `SECRET_KEY` | Strong random string (50+ chars) | `django-insecure-...` |
| `RENDER_EXTERNAL_HOSTNAME` | Your app's public hostname | `myapp.onrender.com` |

**Security Note:**
When `DEBUG=False`, the application automatically enables:
- SSL Redirect (HTTPS enforcement)
- Secure Cookies (Session & CSRF)
- HSTS (HTTP Strict Transport Security)

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
- `/projects/` → Project list (All Projects)
- `/projetos/reforco/` → Reforço Escolar
- `/projetos/prograos/` → ProGrãos
- `/projetos/brokerage_analyzer/` → Brokerage Analyzer
- `/projetos/commerce/` → Commerce (Auctions)
- `/projetos/network/` → Network
- `/projetos/search/` → Search
- `/projetos/mail/` → Mail
- `/projetos/encyclopedia/` → Encyclopedia
- `/contact/` → Contact page


## 🎯 Next Steps
1. **Integrate Projects**: See the Integration Guide below.
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

---
