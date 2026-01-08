# Mail (SPA) - CS50W

## 🎓 Academic Context
This project was developed as part of **CS50’s Web Programming with Python and JavaScript** (Harvard University) curriculum. The challenge was to design a front-end for an email client that makes API calls to send and receive emails, creating a seamless **Single Page Application (SPA)** experience without page reloads.

## ✨ Features Implemented
- **Compose Mail:** Users can send emails using a form; the sent email is saved to the backend database.
- **Mailbox Views:** Separate views for Inbox, Sent, and Archived emails.
- **Read/Unread Status:** Unread emails appear with a white background, read ones with gray.
- **Archive Functionality:** Users can archive/unarchive received emails.
- **Reply:** Pre-fills the composition form with the recipient, subject (prefixed with "Re:"), and timestamped body.

## 💻 Tech Highlights
- **JavaScript (Vanilla):** Extensive extensive use of `fetch` for API calls and DOM manipulation to swap views dynamically.
- **History API:** Updates the URL programmatically to allow browser back/forward navigation within the SPA.
- **Django Rest Framework (Concept):** While not using DRF, the backend serves JSON data, mimicking a RESTful API structure.

## 📋 How to Access
1.  Navigate to `/projects/mail` (or select "Mail" from the project dropdown).
2.  **Register/Login:** Dedicated login for the mail app (separate from main portfolio auth).
3.  **Inbox:** View received messages.
4.  **Compose:** Send email to other registered users.


