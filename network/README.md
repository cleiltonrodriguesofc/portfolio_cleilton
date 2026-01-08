# Network (Social Media) - CS50W

## 🎓 Academic Context
This project was developed as part of **CS50’s Web Programming with Python and JavaScript** (Harvard University) curriculum. It is a Twitter-like social network that demonstrates mastery of full-stack development, specifically combining Django backend logic with asynchronous JavaScript execution (AJAX).

## ✨ Features Implemented
- **New Post:** Users can write and publish text-based posts.
- **Following System:** Users can subscribe to other users' profiles and view a dedicated "Following" feed.
- **Pagination:** Posts are displayed 10 per page, demonstrating server-side pagination with Paginator.
- **Edit Posts:** Authors can edit their posts inline using JavaScript, without a page reload.
- **"Like" System:** Users can toggle "likes" on posts instantly (asynchronously) via fetch API.

## 💻 Tech Highlights
- **Asynchronous JavaScript:** Editing posts and liking them happens asynchronously, updating the DOM and backend simultaneously.
- **Django Pagination:** Efficiently handling large datasets (posts) by retrieving them in chunks.
- **Security:** CSRF protection integrated into AJAX requests.

## 📋 How to Access
1.  Navigate to `/projects/network` (or select "Network" from the project dropdown).
2.  **Register/Login:** Required to post, like, and follow.
3.  **All Posts:** View the global feed of all user posts.
4.  **Profile:** Click on a username to view their profile and follow status.


