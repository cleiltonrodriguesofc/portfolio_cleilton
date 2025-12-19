# Email Client Project

## Overview
This project is part of **CS50’s Web Programming with Python and JavaScript**, where a single-page email client was developed using **JavaScript, HTML, and CSS**. Below is a breakdown of the project structure and features.

## Folder and File Structure

### 1. mail
This folder contains the core application files, including:

- **static/mail/**
  - `styles.css` – Defines the styling for the entire project.
  - `inbox.js` – Contains all JavaScript logic for the email client.
- **templates/mail/**
  - `inbox.html` – Displays the user’s inbox.
  - `layout.html` – Defines the base layout of the pages.
  - `login.html` – Handles user authentication.
  - `register.html` – Allows users to create an account.

### 2. Project Configuration
The project includes additional Django-related files:

- `models.py` – Defines the database models for emails and users.
- `views.py` – Contains the logic for handling user requests and API calls.
- `urls.py` – Maps the application's URL paths.
- `admin.py` – Configures the Django admin interface.
- `apps.py` – Manages application settings.
- `tests.py` – Contains test cases for the project.
- `db.sqlite3` – Stores the application data.
- `manage.py` – Django’s management script.

## Features
- **Send Mail**: Users can compose and send emails.
- **Mailbox Views**: Inbox, Sent, and Archived emails are displayed.
- **Email Display**: Users can view the full content of an email.
- **Read & Unread Status**: Emails change background color based on read status.
- **Archiving**: Users can archive and unarchive emails.
- **Reply Functionality**: Users can reply to emails with pre-filled fields.

## Technology Stack
- **Django** – Backend framework for handling data and API requests.
- **SQLite** – Database for storing application data.
- **JavaScript** – Frontend logic for interactivity.
- **HTML** – Structuring the web pages.
- **CSS** – Styling the application.


## Additional Notes
This project demonstrates how to build a single-page email client that interacts with a backend API to manage email sending, reading, archiving, and replying. It was developed as part of **CS50’s Web Programming with Python and JavaScript** course.

