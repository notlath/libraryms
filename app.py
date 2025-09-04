# app.py with Supabase Integration
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import string
from datetime import datetime, timedelta
import supabase
from supabase import create_client, Client
import os
import ssl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Download required NLTK data (run once)
try:
    nltk.data.find("tokenizers/punkt")
    nltk.data.find("corpora/stopwords")
    nltk.data.find("vader_lexicon")
except LookupError:
    try:
        # Try normal download first
        nltk.download("punkt")
        nltk.download("stopwords")
        nltk.download("vader_lexicon")
    except Exception:
        # If SSL fails, create unverified context
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context

        # Download with unverified context
        nltk.download("punkt")
        nltk.download("stopwords")
        nltk.download("vader_lexicon")

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class LibraryManagementSystem:
    def __init__(self):
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words("english"))

    # Book Entry and Management
    def add_book(self, title, author, isbn, genre, copies=1):
        """Add a new book to the library"""
        try:
            response = (
                supabase_client.table("books")
                .insert(
                    {
                        "title": title,
                        "author": author,
                        "isbn": isbn,
                        "genre": genre,
                        "copies": copies,
                        "available": copies,
                    }
                )
                .execute()
            )

            return response.data[0]["id"] if response.data else None
        except Exception as e:
            print(f"Error adding book: {e}")
            return None

    def get_all_books(self):
        """Get all books from the database"""
        try:
            response = supabase_client.table("books").select("*").execute()
            return {book["id"]: book for book in response.data}
        except Exception as e:
            print(f"Error fetching books: {e}")
            return {}

    def update_book(self, book_id, **kwargs):
        """Update book information"""
        try:
            response = (
                supabase_client.table("books")
                .update(kwargs)
                .eq("id", book_id)
                .execute()
            )
            return len(response.data) > 0
        except Exception as e:
            print(f"Error updating book: {e}")
            return False

    def delete_book(self, book_id):
        """Remove a book from the library"""
        try:
            response = (
                supabase_client.table("books").delete().eq("id", book_id).execute()
            )
            return len(response.data) > 0
        except Exception as e:
            print(f"Error deleting book: {e}")
            return False

    # Borrowers Management
    def add_borrower(self, name, email, phone):
        """Register a new borrower"""
        try:
            response = (
                supabase_client.table("borrowers")
                .insert({"name": name, "email": email, "phone": phone})
                .execute()
            )

            return response.data[0]["id"] if response.data else None
        except Exception as e:
            print(f"Error adding borrower: {e}")
            return None

    def get_all_borrowers(self):
        """Get all borrowers from the database"""
        try:
            response = supabase_client.table("borrowers").select("*").execute()
            return {borrower["id"]: borrower for borrower in response.data}
        except Exception as e:
            print(f"Error fetching borrowers: {e}")
            return {}

    def update_borrower(self, borrower_id, **kwargs):
        """Update borrower information"""
        try:
            response = (
                supabase_client.table("borrowers")
                .update(kwargs)
                .eq("id", borrower_id)
                .execute()
            )
            return len(response.data) > 0
        except Exception as e:
            print(f"Error updating borrower: {e}")
            return False

    def delete_borrower(self, borrower_id):
        """Remove a borrower from the system"""
        try:
            response = (
                supabase_client.table("borrowers")
                .delete()
                .eq("id", borrower_id)
                .execute()
            )
            return len(response.data) > 0
        except Exception as e:
            print(f"Error deleting borrower: {e}")
            return False

    # Circulation (Borrowing and Returning)
    def borrow_book(self, book_id, borrower_id, days=14):
        """Process book borrowing"""
        # Check if book exists and is available
        try:
            book_response = (
                supabase_client.table("books")
                .select("available")
                .eq("id", book_id)
                .execute()
            )
            if not book_response.data or book_response.data[0]["available"] <= 0:
                return False, "No copies available"

            due_date = datetime.now() + timedelta(days=days)
            response = (
                supabase_client.table("transactions")
                .insert(
                    {
                        "book_id": book_id,
                        "borrower_id": borrower_id,
                        "borrow_date": datetime.now().isoformat(),
                        "due_date": due_date.isoformat(),
                        "return_date": None,
                    }
                )
                .execute()
            )

            # Update book availability
            supabase_client.table("books").update(
                {"available": book_response.data[0]["available"] - 1}
            ).eq("id", book_id).execute()

            return (
                True,
                f"Book borrowed successfully. Due date: {due_date.strftime('%Y-%m-%d')}",
            )
        except Exception as e:
            print(f"Error borrowing book: {e}")
            return False, "Error processing borrowing"

    def return_book(self, transaction_id):
        """Process book returning"""
        try:
            # Get transaction details
            transaction_response = (
                supabase_client.table("transactions")
                .select("book_id, borrower_id, return_date")
                .eq("id", transaction_id)
                .execute()
            )

            if (
                not transaction_response.data
                or transaction_response.data[0]["return_date"]
            ):
                return False, "Invalid transaction or book already returned"

            transaction = transaction_response.data[0]

            # Update transaction with return date
            supabase_client.table("transactions").update(
                {"return_date": datetime.now().isoformat()}
            ).eq("id", transaction_id).execute()

            # Update book availability
            book_response = (
                supabase_client.table("books")
                .select("available")
                .eq("id", transaction["book_id"])
                .execute()
            )

            if book_response.data:
                supabase_client.table("books").update(
                    {"available": book_response.data[0]["available"] + 1}
                ).eq("id", transaction["book_id"]).execute()

            return True, "Book returned successfully"
        except Exception as e:
            print(f"Error returning book: {e}")
            return False, "Error processing return"

    def get_active_transactions(self):
        """Get all active (not returned) transactions"""
        try:
            response = (
                supabase_client.table("transactions")
                .select("*")
                .is_("return_date", "null")
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return []

    def get_all_transactions(self):
        """Get all transactions"""
        try:
            response = supabase_client.table("transactions").select("*").execute()
            return response.data
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return []

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
        try:
            # Get all books
            books_response = supabase_client.table("books").select("*").execute()
            books = {book["id"]: book for book in books_response.data}

            query_tokens = set(self.preprocess_text(query))
            results = []

            for book_id, book in books.items():
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
        except Exception as e:
            print(f"Error searching books: {e}")
            return []

    # Sentiment Analysis for User Reviews
    def add_review(self, book_id, borrower_id, review_text, rating):
        """Add a review with sentiment analysis"""
        try:
            # Perform sentiment analysis
            sentiment_scores = self.sentiment_analyzer.polarity_scores(review_text)
            sentiment = (
                "positive"
                if sentiment_scores["compound"] > 0.05
                else "negative" if sentiment_scores["compound"] < -0.05 else "neutral"
            )

            response = (
                supabase_client.table("reviews")
                .insert(
                    {
                        "book_id": book_id,
                        "borrower_id": borrower_id,
                        "review_text": review_text,
                        "rating": rating,
                        "sentiment": sentiment,
                        "sentiment_scores": sentiment_scores,
                        "created_at": datetime.now().isoformat(),
                    }
                )
                .execute()
            )

            return True, f"Review added with {sentiment} sentiment"
        except Exception as e:
            print(f"Error adding review: {e}")
            return False, "Error adding review"

    def get_book_reviews(self, book_id):
        """Get all reviews for a book"""
        try:
            response = (
                supabase_client.table("reviews")
                .select("*, borrowers(name)")
                .eq("book_id", book_id)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"Error fetching reviews: {e}")
            return []

    def get_sentiment_summary(self, book_id):
        """Get sentiment summary for a book"""
        try:
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
        except Exception as e:
            print(f"Error getting sentiment summary: {e}")
            return "Error calculating sentiment"


# Flask App
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key-change-in-production")
library = LibraryManagementSystem()


@app.route("/")
def index():
    books = library.get_all_books()
    borrowers = library.get_all_borrowers()
    transactions = library.get_active_transactions()
    return render_template(
        "index.html", books=books, borrowers=borrowers, transactions=transactions
    )


@app.route("/books")
def books():
    books = library.get_all_books()
    return render_template("books.html", books=books)


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        isbn = request.form["isbn"]
        genre = request.form["genre"]
        copies = int(request.form["copies"])

        book_id = library.add_book(title, author, isbn, genre, copies)
        if book_id:
            flash(f"Book added successfully with ID: {book_id}", "success")
        else:
            flash("Error adding book", "error")
        return redirect(url_for("books"))

    return render_template("add_book.html")


@app.route("/borrowers")
def borrowers():
    borrowers = library.get_all_borrowers()
    return render_template("borrowers.html", borrowers=borrowers)


@app.route("/add_borrower", methods=["GET", "POST"])
def add_borrower():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]

        borrower_id = library.add_borrower(name, email, phone)
        if borrower_id:
            flash(f"Borrower added successfully with ID: {borrower_id}", "success")
        else:
            flash("Error adding borrower", "error")
        return redirect(url_for("borrowers"))

    return render_template("add_borrower.html")


@app.route("/circulation")
def circulation():
    # Get active transactions (not returned)
    active_transactions = library.get_active_transactions()
    books = library.get_all_books()
    borrowers = library.get_all_borrowers()

    print(active_transactions)
    return render_template(
        "circulation.html",
        transactions=active_transactions,
        books=books,
        borrowers=borrowers,
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
    books = library.get_all_books()

    if request.method == "POST":
        query = request.form["query"]
        search_type = request.form["search_type"]
        book_ids = library.search_books(query, search_type)
        results = [books[book_id] for book_id in book_ids if book_id in books]

    return render_template("search.html", results=results, query=query, books=books)


@app.route("/reviews/<int:book_id>")
def reviews(book_id):
    books = library.get_all_books()
    if book_id not in books:
        flash("Book not found", "error")
        return redirect(url_for("books"))

    book = books[book_id]
    reviews = library.get_book_reviews(book_id)
    sentiment_summary = library.get_sentiment_summary(book_id)
    borrowers = library.get_all_borrowers()

    return render_template(
        "reviews.html",
        book=book,
        reviews=reviews,
        sentiment_summary=sentiment_summary,
        borrowers=borrowers,
        book_id=book_id,
    )


@app.route("/add_review/<int:book_id>", methods=["GET", "POST"])
def add_review(book_id):
    books = library.get_all_books()
    if book_id not in books:
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

    book = books[book_id]
    borrowers = library.get_all_borrowers()
    return render_template(
        "add_review.html", book=book, borrowers=borrowers, book_id=book_id
    )


@app.route("/test_connection")
def test_connection():
    """Test Supabase connection and table accessibility"""
    try:
        # Test basic connection
        response = supabase_client.table("books").select("id").limit(1).execute()

        # Test each table
        tables_status = {}
        tables = ["books", "borrowers", "transactions", "reviews"]

        for table in tables:
            try:
                test_response = (
                    supabase_client.table(table).select("*").limit(1).execute()
                )
                tables_status[table] = "✅ Connected"
            except Exception as e:
                tables_status[table] = f"❌ Error: {str(e)}"

        return jsonify(
            {
                "status": "success",
                "message": "Supabase connection successful",
                "tables": tables_status,
                "supabase_url": SUPABASE_URL,
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Connection failed: {str(e)}",
                    "supabase_url": SUPABASE_URL,
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(debug=True)
