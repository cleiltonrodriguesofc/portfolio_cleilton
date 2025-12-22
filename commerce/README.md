# Commerce (Auctions) - CS50W

## 🎓 Academic Context
This project was developed as part of **CS50’s Web Programming with Python and JavaScript** (Harvard University) curriculum. The challenge was to design and implement an eBay-like e-commerce auction site where users can post auction listings, place bids, comment on listings, and manage a watchlist.

## ✨ Features Implemented
- **Create Listings:** Users can post new items with title, description, starting bid, and category.
- **Active Listings Page:** Displays all currently active auctions.
- **Bidding System:** Users can place bids; the system validates that the bid is higher than the current price.
- **Watchlist:** Users can add/remove items to their personal watchlist.
- **Comments:** Authenticated users can comment on listings.
- **Categories:** Listings are filtered by category (e.g., Fashion, Toys, Electronics).
- **Admin Interface:** Full administrative control via Django Admin to manage listings, comments, and bids.

## 💻 Tech Highlights
- **Django Models:** utilization of foreign keys to link Listings, Bids, and Comments.
- **Forms:** implementation of model-based forms for data validation.
- **Authentication:** standard Django auth system for user management.

