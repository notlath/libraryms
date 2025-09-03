# Library Management System

A modern web-based library management system built with Flask and enhanced with Natural Language Processing (NLP) capabilities for intelligent book search and sentiment analysis of user reviews.

## 🚀 Features

### Core Library Management

- **Book Management**: Add, update, delete, and track library books
- **Borrower Management**: Register and manage library members
- **Circulation System**: Handle book borrowing and returning with due date tracking
- **Transaction History**: Complete audit trail of all library transactions

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
- **NLP**: Natural Language Toolkit (NLTK)
- **Data Storage**: JSON file-based persistence
- **Sentiment Analysis**: VADER (Valence Aware Dictionary and sEntiment Reasoner)

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## 🔧 Installation

1. **Clone or download the project**

   ```bash
   cd lib_ms
   ```

2. **Install required dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Download NLTK data** (automatically handled on first run)
   - The application will automatically download required NLTK datasets:
     - punkt (tokenizer)
     - stopwords (common words to filter)
     - vader_lexicon (sentiment analysis)

## 🚀 Usage

### Starting the Application

```bash
python app.py
```

The application will start on `http://localhost:5000` by default.

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
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── library_data.json     # Data storage (auto-generated)
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

The system uses JSON file-based storage (`library_data.json`) with the following structure:

```json
{
  "books": {
    "1": {
      "title": "Book Title",
      "author": "Author Name",
      "isbn": "1234567890",
      "genre": "Fiction",
      "copies": 3,
      "available": 2
    }
  },
  "borrowers": {
    "B0001": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "123-456-7890",
      "borrowed_books": [1, 2]
    }
  },
  "transactions": [...],
  "reviews": {...}
}
```

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

### Secret Key

Change the Flask secret key in production:

```python
app.secret_key = "your-production-secret-key"
```

### Default Loan Period

Books are loaned for 14 days by default. Modify in the `borrow_book` method:

```python
def borrow_book(self, book_id, borrower_id, days=14):
```

### Data File Location

Change the data storage file location:

```python
library = LibraryManagementSystem("custom_data_file.json")
```

## 🐛 Troubleshooting

### Common Issues

1. **NLTK Data Not Found**

   - The app automatically downloads required NLTK data on first run
   - If issues persist, manually run:
     ```python
     import nltk
     nltk.download('punkt')
     nltk.download('stopwords')
     nltk.download('vader_lexicon')
     ```

2. **Port Already in Use**

   - Change the port in app.py:
     ```python
     app.run(debug=True, port=5001)
     ```

3. **Permission Errors**
   - Ensure write permissions for the application directory
   - The app needs to create/modify `library_data.json`

## 🔮 Future Enhancements

- **Database Integration**: Replace JSON with SQLite/PostgreSQL
- **User Authentication**: Add login system for librarians and members
- **Email Notifications**: Automated overdue notices
- **Advanced Analytics**: Generate reports and statistics
- **Book Recommendations**: ML-based recommendation system
- **API Endpoints**: RESTful API for mobile app integration
- **Barcode Scanning**: Physical book management
- **Multi-library Support**: Support for multiple library branches

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

1. **Start the application**:

   ```bash
   python app.py
   ```

2. **Add your first book**:

   - Navigate to http://localhost:5000
   - Click "Add New Book"
   - Fill in book details

3. **Register a borrower**:

   - Click "Add New Borrower"
   - Enter member information

4. **Process a transaction**:

   - Go to "Circulation"
   - Select book and borrower
   - Click "Borrow Book"

5. **Search for books**:

   - Use the search feature
   - Try different search terms to see NLP in action

6. **Add a review**:
   - View any book
   - Add a review to see sentiment analysis

---

**Happy Library Management!** 📚✨
