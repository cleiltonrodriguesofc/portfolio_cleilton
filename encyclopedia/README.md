# Encyclopedia (Wiki) - CS50W

## 🎓 Academic Context
This project was developed as part of **CS50’s Web Programming with Python and JavaScript** (Harvard University) curriculum. The goal was to build a Wikipedia-like online encyclopedia where users can search for, read, create, and edit encyclopedia entries using Markdown.

## ✨ Features Implemented
- **Entry Pages:** Renders Markdown content into HTML for each encyclopedia entry.
- **Index Page:** Lists all available encyclopedia entries.
- **Search:** Allows users to query entries; exact matches redirect to the page, while partial matches show a list of results.
- **New Page:** Users can create new entries with a Markdown editor.
- **Edit Page:** Users can edit existing entries through a pre-populated textarea.
- **Random Page:** Redirects the user to a random entry in the encyclopedia.
- **Markdown Conversion:** Backend logic to convert Markdown title/content to HTML.

## 💻 Tech Highlights
- **Regular Expressions:** Used in the conversion logic to process Markdown syntax.
- **File I/O:** Entries are stored as flat Markdown files (`.md`) on the disk, not a database, demonstrating file manipulation fundamentals.
- **Django Forms:** Handling user input for search and content creation.

## 📋 How to Access
1.  Navigate to `/projects/encyclopedia` (or click "Wiki" in navbar).
2.  **Search:** Use the sidebar to find entries.
3.  **Create New Page:** Add your own markdown entry.
4.  **Random Page:** Explore content serendipitously.


