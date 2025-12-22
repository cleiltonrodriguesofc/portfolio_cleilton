# Portfolio Core (Internal App)

## 🧩 Architectural Role
The **Core** app is the heart of the portfolio project. It serves as the orchestrator for the entire site, managing the landing page (`home`), the project gallery (`project_list`), and the "About Me" section. It defines the base templates (`base.html`, `_header_shell.html`) that all specific project apps inherit from, ensuring consistent layout, navigation, and styling across the entire portfolio.

## 🔑 Key Components
- **`base.html`:** The master template containing the `<head>`, global navigation bar, and footer. All other pages extend this template.
- **`views.py`**: Handles logic for the homepage (fetching featured projects) and the comprehensive project list.
- **`static/core/css/style.css`**: The global stylesheet that defines the portfolio's color palette, typography, and component styles.
- **`urls.py`**: Serves as the main entry point for routing, delegating specific project paths (e.g., `/projects/xyz`) to their respective apps.

