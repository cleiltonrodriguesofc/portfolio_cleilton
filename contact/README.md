# Contact App (Internal App)

## 🧩 Architectural Role
The **Contact** app handles user inquiries and messages from the portfolio's "Contact" page. It provides a standard Django form interface for visitors to get in touch with you, ensuring that messages are validated and (optionally) stored or emailed.

## 🔑 Key Components
- **`forms.py` (ContactForm):** Defines the fields (Name, Email, Subject, Message) and validation logic (e.g., ensuring email format is correct).
- **`views.py`:** Processes the POST request when a user submits the form. It handles successful submissions (showing a success message/toast) and errors.
- **`templates/contact/contact.html`:** The frontend template that renders the form and displays feedback to the user.

