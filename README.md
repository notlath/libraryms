# Library Management System

A modern web-based library management system built with Flask and enhanced with Natural Language Processing (NLP) capabilities for intelligent book search and sentiment analysis of user reviews. The system uses Supabase as a cloud database backend for reliable, scalable data storage.

## 🚀 Features

### Core Library Management

- **Book Management**: Add, update, delete, and track library books with real-time availability
- **Borrower Management**: Register and manage library members with unique IDs
- **Circulation System**: Handle book borrowing and returning with automated due date tracking
- **Transaction History**: Complete audit trail of all library transactions stored in Supabase

### Advanced NLP Features

- **Intelligent Search**: NLP-powered book search using text preprocessing, tokenization, and similarity scoring
- **Sentiment Analysis**: Automatic sentiment analysis of book reviews using NLTK's VADER sentiment analyzer
- **Smart Text Processing**: Stopword removal, stemming, and advanced text preprocessing for better search results

### Web Interface

- **Responsive Design**: Bootstrap-powered responsive web interface
- **Real-time Statistics**: Dashboard with library overview and key metrics
- **User-friendly Forms**: Easy-to-use forms for all library operations
- **Flash Messages**: Real-time feedback for user actions

## 🛠️ Technology Stack

- **Backend**: Python 3.x with Flask web framework
- **Frontend**: HTML5, CSS3, Bootstrap 5, Jinja2 templating
- **Database**: Supabase (PostgreSQL-based cloud database)
- **NLP**: Natural Language Toolkit (NLTK)
- **Environment Management**: python-dotenv for configuration
- **Sentiment Analysis**: VADER (Valence Aware Dictionary and sEntiment Reasoner)

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Supabase account and project setup
- Internet connection for Supabase database operations

## 🔧 Installation & Setup

### 1. Project Setup

```cmd
cd c:\Users\USer\Downloads\lib_ms
```

### 2. Install Dependencies

```cmd
pip install -r requirements.txt
```

### 3. Supabase Database Setup

**Create a Supabase Project:**

1. Go to [Supabase](https://supabase.com) and create a new project
2. Get your project URL and API key from the project settings

**Create Environment File:**
Create a `.env` file in the project root with your Supabase credentials:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SECRET_KEY=your_flask_secret_key
```

**Create Database Tables:**
Run the following SQL commands in your Supabase SQL Editor:

```sql
-- Books table
CREATE TABLE books (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  author VARCHAR(255) NOT NULL,
  isbn VARCHAR(20),
  genre VARCHAR(100),
  copies INTEGER DEFAULT 1,
  available INTEGER DEFAULT 1,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Borrowers table
CREATE TABLE borrowers (
  id VARCHAR(20) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE,
  phone VARCHAR(20),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Transactions table
CREATE TABLE transactions (
  id SERIAL PRIMARY KEY,
  book_id INTEGER REFERENCES books(id),
  borrower_id VARCHAR(20) REFERENCES borrowers(id),
  borrow_date TIMESTAMP DEFAULT NOW(),
  due_date TIMESTAMP,
  return_date TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Reviews table
CREATE TABLE reviews (
  id SERIAL PRIMARY KEY,
  book_id INTEGER REFERENCES books(id),
  borrower_id VARCHAR(20) REFERENCES borrowers(id),
  review_text TEXT,
  rating INTEGER CHECK (rating >= 1 AND rating <= 5),
  sentiment VARCHAR(20),
  sentiment_scores JSONB,
  timestamp TIMESTAMP DEFAULT NOW()
);
```

### 4. Test Supabase Connection

Create a test file to verify your connection:

```python
# test_supabase_connection.py
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table("books").select("*").limit(1).execute()
    print("✅ Successfully connected to Supabase!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

Run the test:

```cmd
python test_supabase_connection.py
```

## 🚀 Usage

### Starting the Application

```cmd
python app.py
```

The application will:

- Automatically download required NLTK data on first run (punkt, stopwords, vader_lexicon)
- Start the Flask development server
- Be accessible at `http://localhost:5000`

### Testing the Application

Visit `http://localhost:5000/test_connection` to verify Supabase connectivity and table setup.

### Key Functionalities

#### 1. Dashboard (`/`)

- View library statistics
- Quick access to main features
- Overview of books, borrowers, and active transactions

#### 2. Book Management (`/books`, `/add_book`)

- Add new books with title, author, ISBN, genre, and copy count
- View all books in the library
- Track available vs. total copies

#### 3. Borrower Management (`/borrowers`, `/add_borrower`)

- Register new library members
- Store contact information (name, email, phone)
- Track borrowing history

#### 4. Circulation System (`/circulation`)

- Process book borrowing with automatic due date calculation
- Return books and update availability
- View active transactions

#### 5. Intelligent Search (`/search`)

- Search books by title, author, genre, or all fields
- NLP-powered fuzzy matching
- Relevance-based result ranking

#### 6. Review System (`/reviews/<book_id>`, `/add_review/<book_id>`)

- Add book reviews with ratings
- Automatic sentiment analysis (positive, negative, neutral)
- View sentiment summaries for books

## 📁 Project Structure

```
lib_ms/
├── app.py                 # Main Flask application with Supabase integration
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (Supabase credentials)
├── README.md             # Project documentation
└── templates/            # HTML templates
    ├── base.html         # Base template with Bootstrap
    ├── index.html        # Dashboard/home page
    ├── books.html        # Book listing page
    ├── add_book.html     # Add new book form
    ├── borrowers.html    # Borrower listing page
    ├── add_borrower.html # Add new borrower form
    ├── circulation.html  # Circulation management
    ├── search.html       # Search interface and results
    ├── reviews.html      # Book reviews display
    └── add_review.html   # Add review form
```

## 💾 Data Storage

The system uses **Supabase** (PostgreSQL) for cloud-based data storage with the following schema:

### Database Tables

**books**

- `id` (SERIAL PRIMARY KEY)
- `title` (VARCHAR(255))
- `author` (VARCHAR(255))
- `isbn` (VARCHAR(20))
- `genre` (VARCHAR(100))
- `copies` (INTEGER)
- `available` (INTEGER)
- `created_at` (TIMESTAMP)

**borrowers**

- `id` (VARCHAR(20) PRIMARY KEY)
- `name` (VARCHAR(255))
- `email` (VARCHAR(255) UNIQUE)
- `phone` (VARCHAR(20))
- `created_at` (TIMESTAMP)

**transactions**

- `id` (SERIAL PRIMARY KEY)
- `book_id` (INTEGER, FOREIGN KEY)
- `borrower_id` (VARCHAR(20), FOREIGN KEY)
- `borrow_date` (TIMESTAMP)
- `due_date` (TIMESTAMP)
- `return_date` (TIMESTAMP)
- `created_at` (TIMESTAMP)

**reviews**

- `id` (SERIAL PRIMARY KEY)
- `book_id` (INTEGER, FOREIGN KEY)
- `borrower_id` (VARCHAR(20), FOREIGN KEY)
- `review_text` (TEXT)
- `rating` (INTEGER 1-5)
- `sentiment` (VARCHAR(20))
- `sentiment_scores` (JSONB)
- `timestamp` (TIMESTAMP)

## 🔍 Search Algorithm

The search functionality uses advanced NLP techniques:

1. **Text Preprocessing**:

   - Convert to lowercase
   - Remove punctuation
   - Tokenization using NLTK
   - Remove stopwords
   - Word stemming using Porter Stemmer

2. **Similarity Calculation**:
   - Jaccard similarity coefficient
   - Token intersection over union
   - Relevance-based ranking

## 📊 Sentiment Analysis

Book reviews are automatically analyzed using NLTK's VADER sentiment analyzer:

- **Positive**: Compound score > 0.05
- **Negative**: Compound score < -0.05
- **Neutral**: Compound score between -0.05 and 0.05

Sentiment summaries provide counts of positive, negative, and neutral reviews.

## ⚙️ Configuration

### Environment Variables

Configure the application through the `.env` file:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# Flask Configuration
SECRET_KEY=your-production-secret-key

# Optional: Custom Port
PORT=5000
```

### Application Settings

Modify settings in `app.py`:

```python
# Default loan period (days)
due_date = datetime.now() + timedelta(days=14)

# Flask debug mode
app.run(debug=True, port=5000)
```

## 🐛 Troubleshooting

### Common Issues

1. **Supabase Connection Failed**

   ```cmd
   python test_supabase_connection.py
   ```

   - Verify your `.env` file has correct SUPABASE_URL and SUPABASE_KEY
   - Check internet connectivity
   - Ensure Supabase project is active

2. **Database Tables Don't Exist**

   - Run the SQL commands in Supabase SQL Editor to create required tables
   - Check table names match exactly: `books`, `borrowers`, `transactions`, `reviews`

3. **NLTK Data Not Found**

   - The app automatically downloads required NLTK data on first run
   - If issues persist, manually run:
     ```python
     import nltk
     nltk.download('punkt')
     nltk.download('stopwords')
     nltk.download('vader_lexicon')
     ```

4. **Port Already in Use**

   - Change the port in app.py:
     ```python
     app.run(debug=True, port=5001)
     ```

5. **Environment Variables Not Loading**
   - Ensure `.env` file is in the project root directory
   - Check file encoding (should be UTF-8)
   - Verify no extra spaces around `=` in environment variables

### Connection Test Endpoint

Visit `http://localhost:5000/test_connection` to verify:

- Supabase connectivity
- Database table existence
- Environment variable loading

## 🔮 Future Enhancements

- **User Authentication**: Add login system for librarians and members
- **Advanced Analytics**: Generate reports and statistics from Supabase data
- **Email Notifications**: Automated overdue notices using Supabase Edge Functions
- **Book Recommendations**: ML-based recommendation system
- **API Endpoints**: RESTful API for mobile app integration
- **Barcode Scanning**: Physical book management with ISBN lookup
- **Multi-library Support**: Support for multiple library branches
- **Real-time Updates**: WebSocket integration for live updates
- **Advanced Search**: Full-text search using Supabase's PostgreSQL capabilities
- **Data Backup**: Automated backup solutions using Supabase features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 📧 Support

For support, please open an issue in the repository or contact the development team.

## 🎯 Getting Started Example

### Quick Start Guide

1. **Setup Supabase Database**:

   ```sql
   -- Run in Supabase SQL Editor
   -- Copy the database creation scripts from the Installation section
   ```

2. **Configure Environment**:

   ```env
   # Create .env file
   SUPABASE_URL=your_project_url
   SUPABASE_KEY=your_anon_key
   SECRET_KEY=your_secret_key
   ```

3. **Start the application**:

   ```cmd
   python app.py
   ```

4. **Test the connection**:

   - Visit `http://localhost:5000/test_connection`
   - Verify all tables show "✅ Connected"

5. **Add your first book**:

   - Navigate to `http://localhost:5000`
   - Click "Add New Book"
   - Fill in book details (Title, Author, ISBN, Genre, Copies)

6. **Register a borrower**:

   - Click "Add New Borrower"
   - Enter member information (ID, Name, Email, Phone)

7. **Process a transaction**:

   - Go to "Circulation"
   - Select book and borrower
   - Click "Borrow Book"

8. **Search for books**:

   - Use the search feature
   - Try different search terms to see NLP in action

9. **Add a review**:
   - View any book details
   - Add a review to see automatic sentiment analysis

### Sample Data

For testing, you can add these sample records:

**Sample Book:**

- Title: "The Great Gatsby"
- Author: "F. Scott Fitzgerald"
- ISBN: "9780743273565"
- Genre: "Fiction"
- Copies: 3

**Sample Borrower:**

- ID: "B001"
- Name: "John Doe"
- Email: "john.doe@email.com"
- Phone: "555-0123"

---

**Happy Library Management!** 📚✨
