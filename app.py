# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import string
from datetime import datetime, timedelta
import json
import os

# Download required NLTK data (run once)
try:
    nltk.data.find("tokenizers/punkt")
    nltk.data.find("corpora/stopwords")
    nltk.data.find("vader_lexicon")
except LookupError:
    nltk.download("punkt")
    nltk.download("stopwords")
    nltk.download("vader_lexicon")


class LibraryManagementSystem:
    def __init__(self, data_file="library_data.json"):
        self.data_file = data_file
        self.books = {}
        self.borrowers = {}
        self.transactions = []
        self.reviews = {}
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words("english"))
        self.load_data()

    def save_data(self):
        """Save all data to JSON file"""
        data = {
            "books": self.books,
            "borrowers": self.borrowers,
            "transactions": self.transactions,
            "reviews": self.reviews,
        }
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)

    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                data = json.load(f)
                self.books = {int(k): v for k, v in data.get("books", {}).items()}
                self.borrowers = data.get("borrowers", {})
                self.transactions = data.get("transactions", [])
                self.reviews = {int(k): v for k, v in data.get("reviews", {}).items()}

    # Book Entry and Management
    def add_book(self, title, author, isbn, genre, copies=1):
        """Add a new book to the library"""
        book_id = len(self.books) + 1
        self.books[book_id] = {
            "title": title,
            "author": author,
            "isbn": isbn,
            "genre": genre,
            "copies": copies,
            "available": copies,
        }
        self.save_data()
        return book_id

    def update_book(self, book_id, **kwargs):
        """Update book information"""
        if book_id in self.books:
            for key, value in kwargs.items():
                if key in self.books[book_id]:
                    self.books[book_id][key] = value
            self.save_data()
            return True
        return False

    def delete_book(self, book_id):
        """Remove a book from the library"""
        if book_id in self.books:
            del self.books[book_id]
            self.save_data()
            return True
        return False

    # Borrowers Management
    def add_borrower(self, name, email, phone):
        """Register a new borrower"""
        borrower_id = f"B{len(self.borrowers) + 1:04d}"
        self.borrowers[borrower_id] = {
            "name": name,
            "email": email,
            "phone": phone,
            "borrowed_books": [],
        }
        self.save_data()
        return borrower_id

    def update_borrower(self, borrower_id, **kwargs):
        """Update borrower information"""
        if borrower_id in self.borrowers:
            for key, value in kwargs.items():
                if key in self.borrowers[borrower_id]:
                    self.borrowers[borrower_id][key] = value
            self.save_data()
            return True
        return False

    def delete_borrower(self, borrower_id):
        """Remove a borrower from the system"""
        if borrower_id in self.borrowers:
            del self.borrowers[borrower_id]
            self.save_data()
            return True
        return False

    # Circulation (Borrowing and Returning)
    def borrow_book(self, book_id, borrower_id, days=14):
        """Process book borrowing"""
        if book_id not in self.books or borrower_id not in self.borrowers:
            return False, "Invalid book or borrower ID"

        if self.books[book_id]["available"] <= 0:
            return False, "No copies available"

        due_date = datetime.now() + timedelta(days=days)
        transaction = {
            "transaction_id": len(self.transactions) + 1,
            "book_id": book_id,
            "borrower_id": borrower_id,
            "borrow_date": datetime.now().isoformat(),
            "due_date": due_date.isoformat(),
            "return_date": None,
        }

        self.transactions.append(transaction)
        self.books[book_id]["available"] -= 1
        self.borrowers[borrower_id]["borrowed_books"].append(
            transaction["transaction_id"]
        )
        self.save_data()
        return (
            True,
            f"Book borrowed successfully. Due date: {due_date.strftime('%Y-%m-%d')}",
        )

    def return_book(self, transaction_id):
        """Process book returning"""
        transaction = None
        for t in self.transactions:
            if t["transaction_id"] == transaction_id:
                transaction = t
                break

        if not transaction or transaction["return_date"]:
            return False, "Invalid transaction or book already returned"

        transaction["return_date"] = datetime.now().isoformat()
        book_id = transaction["book_id"]
        borrower_id = transaction["borrower_id"]

        self.books[book_id]["available"] += 1
        if transaction_id in self.borrowers[borrower_id]["borrowed_books"]:
            self.borrowers[borrower_id]["borrowed_books"].remove(transaction_id)

        self.save_data()
        return True, "Book returned successfully"

    # Search Functionality with NLP
    def preprocess_text(self, text):
        """Preprocess text for search"""
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation
        text = text.translate(str.maketrans("", "", string.punctuation))
        # Tokenize
        tokens = word_tokenize(text)
        # Remove stopwords
        tokens = [t for t in tokens if t not in self.stop_words]
        # Stem words
        tokens = [self.stemmer.stem(t) for t in tokens]
        return tokens

    def search_books(self, query, search_type="all"):
        """
        Search books using NLP techniques
        search_type: 'title', 'author', 'genre', 'all'
        """
        query_tokens = set(self.preprocess_text(query))
        results = []

        for book_id, book in self.books.items():
            search_fields = []
            if search_type in ["title", "all"]:
                search_fields.append(book["title"])
            if search_type in ["author", "all"]:
                search_fields.append(book["author"])
            if search_type in ["genre", "all"]:
                search_fields.append(book["genre"])

            # Combine all search fields
            combined_text = " ".join(search_fields)
            field_tokens = set(self.preprocess_text(combined_text))

            # Calculate similarity (Jaccard similarity)
            intersection = query_tokens.intersection(field_tokens)
            union = query_tokens.union(field_tokens)

            if union:
                similarity = len(intersection) / len(union)
                if similarity > 0:
                    results.append((book_id, similarity))

        # Sort by similarity score
        results.sort(key=lambda x: x[1], reverse=True)
        return [book_id for book_id, _ in results]

    # Sentiment Analysis for User Reviews
    def add_review(self, book_id, borrower_id, review_text, rating):
        """Add a review with sentiment analysis"""
        if book_id not in self.books:
            return False, "Invalid book ID"

        # Perform sentiment analysis
        sentiment_scores = self.sentiment_analyzer.polarity_scores(review_text)
        sentiment = (
            "positive"
            if sentiment_scores["compound"] > 0.05
            else "negative" if sentiment_scores["compound"] < -0.05 else "neutral"
        )

        if book_id not in self.reviews:
            self.reviews[book_id] = []

        review = {
            "review_id": len(self.reviews[book_id]) + 1,
            "borrower_id": borrower_id,
            "review_text": review_text,
            "rating": rating,
            "sentiment": sentiment,
            "sentiment_scores": sentiment_scores,
            "timestamp": datetime.now().isoformat(),
        }

        self.reviews[book_id].append(review)
        self.save_data()
        return True, f"Review added with {sentiment} sentiment"

    def get_book_reviews(self, book_id):
        """Get all reviews for a book"""
        return self.reviews.get(book_id, [])

    def get_sentiment_summary(self, book_id):
        """Get sentiment summary for a book"""
        reviews = self.get_book_reviews(book_id)
        if not reviews:
            return "No reviews available"

        sentiments = [review["sentiment"] for review in reviews]
        positive = sentiments.count("positive")
        negative = sentiments.count("negative")
        neutral = sentiments.count("neutral")

        return {
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "total": len(sentiments),
        }


# Flask App
app = Flask(__name__)
app.secret_key = "your-secret-key-here"  # Change this in production
library = LibraryManagementSystem()


@app.route("/")
def index():
    return render_template(
        "index.html", books=library.books, borrowers=library.borrowers
    )


@app.route("/books")
def books():
    return render_template("books.html", books=library.books)


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        isbn = request.form["isbn"]
        genre = request.form["genre"]
        copies = int(request.form["copies"])

        book_id = library.add_book(title, author, isbn, genre, copies)
        flash(f"Book added successfully with ID: {book_id}", "success")
        return redirect(url_for("books"))

    return render_template("add_book.html")


@app.route("/borrowers")
def borrowers():
    return render_template("borrowers.html", borrowers=library.borrowers)


@app.route("/add_borrower", methods=["GET", "POST"])
def add_borrower():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]

        borrower_id = library.add_borrower(name, email, phone)
        flash(f"Borrower added successfully with ID: {borrower_id}", "success")
        return redirect(url_for("borrowers"))

    return render_template("add_borrower.html")


@app.route("/circulation")
def circulation():
    # Get active transactions (not returned)
    active_transactions = [t for t in library.transactions if not t["return_date"]]
    return render_template(
        "circulation.html",
        transactions=active_transactions,
        books=library.books,
        borrowers=library.borrowers,
    )


@app.route("/borrow_book", methods=["POST"])
def borrow_book():
    book_id = int(request.form["book_id"])
    borrower_id = request.form["borrower_id"]

    success, message = library.borrow_book(book_id, borrower_id)
    if success:
        flash(message, "success")
    else:
        flash(message, "error")

    return redirect(url_for("circulation"))


@app.route("/return_book/<int:transaction_id>")
def return_book(transaction_id):
    success, message = library.return_book(transaction_id)
    if success:
        flash(message, "success")
    else:
        flash(message, "error")

    return redirect(url_for("circulation"))


@app.route("/search", methods=["GET", "POST"])
def search():
    results = []
    query = ""
    if request.method == "POST":
        query = request.form["query"]
        search_type = request.form["search_type"]
        book_ids = library.search_books(query, search_type)
        results = [
            library.books[book_id] for book_id in book_ids if book_id in library.books
        ]

    return render_template(
        "search.html", results=results, query=query, books=library.books
    )


@app.route("/reviews/<int:book_id>")
def reviews(book_id):
    if book_id not in library.books:
        flash("Book not found", "error")
        return redirect(url_for("books"))

    book = library.books[book_id]
    reviews = library.get_book_reviews(book_id)
    sentiment_summary = library.get_sentiment_summary(book_id)

    return render_template(
        "reviews.html", book=book, reviews=reviews, sentiment_summary=sentiment_summary
    )


@app.route("/add_review/<int:book_id>", methods=["GET", "POST"])
def add_review(book_id):
    if book_id not in library.books:
        flash("Book not found", "error")
        return redirect(url_for("books"))

    if request.method == "POST":
        borrower_id = request.form["borrower_id"]
        review_text = request.form["review_text"]
        rating = int(request.form["rating"])

        success, message = library.add_review(book_id, borrower_id, review_text, rating)
        if success:
            flash(message, "success")
        else:
            flash(message, "error")

        return redirect(url_for("reviews", book_id=book_id))

    book = library.books[book_id]
    return render_template("add_review.html", book=book, borrowers=library.borrowers)


if __name__ == "__main__":
    app.run(debug=True)
