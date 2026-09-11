# 📄 Document Intelligence Platform

An AI-powered document processing platform that extracts structured information from invoices and balance sheets, performs financial validation, and presents the results through a web interface.

## 🚀 Live Demo

**Application:** https://document-intelligence-platform-zwf0.onrender.com

**API Documentation:** https://document-intelligence-platform-zwf0.onrender.com/docs

## 📌 Features

- Upload PDF and image-based documents
- Support for invoices and balance sheets
- OCR-based text extraction using Tesseract
- AI-powered document analysis using Google Gemini
- Structured extraction of important document fields
- Financial validation and consistency checks
- Evidence/source text for extracted information
- Document processing history
- REST API with Swagger/OpenAPI documentation
- PostgreSQL database integration
- Dockerized application
- Cloud deployment using Render

## 🔄 System Workflow

User Uploads Document
        ↓
File Validation
        ↓
OCR / Text Extraction
        ↓
Gemini AI Analysis
        ↓
Structured Information Extraction
        ↓
Financial Validation
        ↓
Store Result in PostgreSQL
        ↓
Display Result on Dashboard

## 🛠️ Tech Stack

**Python | FastAPI | Uvicorn | Pydantic | SQLAlchemy | Google Gemini API | Tesseract OCR | PDF/Image Processing | PostgreSQL | Neon PostgreSQL | HTML | CSS | JavaScript | Docker | Render | GitHub**

## 📂 Project Structure

Document-intelligence-platform/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── core/
│   │   ├── services/
│   │   ├── tests/
│   │   └── main.py
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│       ├── dashboard.html
│       └── document_result.html
│
├── sample_outputs/
├── test_documents/
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── README.md
└── documents.db

## ⚙️ Environment Variables

Create a `.env` file in the project root:

GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=your_postgresql_connection_string

Do not commit `.env` to GitHub.

A template is provided in:

.env.example

## 💻 Run Locally

### 1. Clone the Repository

git clone https://github.com/shilpijaiswal02/Document-intelligence-platform.git
cd Document-intelligence-platform

### 2. Create a Virtual Environment

python -m venv .venv

Activate on Windows:

.venv\Scripts\Activate.ps1

### 3. Install Dependencies

pip install -r backend/requirements.txt

### 4. Configure Environment Variables

Create `.env` using `.env.example` and add:

GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=your_postgresql_connection_string

### 5. Run the Application

uvicorn backend.app.main:app --reload

Open:

http://localhost:8000

## 🐳 Run with Docker

### Build the Docker Image

docker build -t document-intelligence-platform .

### Run the Container

docker run --env-file .env -p 8000:8000 document-intelligence-platform

Open:

http://localhost:8000

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/documents/process` | Process a document |
| GET | `/api/v1/documents` | Get all processed documents |
| GET | `/api/v1/documents/{document_name}` | Get a specific document |
| GET | `/document/{document_name}` | Display document result |
| GET | `/api/v1/health` | Health check |
| GET | `/` | Dashboard |

**Swagger Documentation:**  
https://document-intelligence-platform-zwf0.onrender.com/docs

## 📊 Document Processing

### Invoices

- Invoice number
- Invoice date
- Due date
- Seller and buyer information
- Currency
- Subtotal
- Tax
- Shipping and handling
- Total amount
- Line items
- Supporting evidence

### Balance Sheets

- Company information
- Reporting date
- Units of measurement
- Capital and liabilities
- Assets
- Comparative financial periods
- Financial tables
- Supporting evidence

## 🔍 Financial Validation

The platform performs financial consistency checks on extracted information.

Examples:

- Sum of Line Totals ≈ Subtotal
- Taxable Amount + Tax ≈ Total
- Total Capital & Liabilities ≈ Total Assets

Validation results:

- PASS
- FAIL
- NOT_APPLICABLE

## 🔐 Security

- API keys are stored using environment variables.
- Database credentials are stored using environment variables.
- `.env` is excluded from Git using `.gitignore`.
- Sensitive configuration is not included in the Docker image.

## 🚀 Deployment

The application is deployed using:

GitHub
   ↓
Render
   ↓
Docker
   ↓
FastAPI Application
   ↓
Neon PostgreSQL

Render builds the application from the repository's Dockerfile and runs the FastAPI application on the configured web service port.

## 🧪 Testing

The project includes backend tests covering:

- API functionality
- Document extraction
- Extraction quality
- Invoice recovery
- Validation

Run tests using:

pytest

## 🔮 Future Improvements

- Improve extraction of complex invoice line items
- Add authentication and user accounts
- Add document deletion and management
- Improve validation for edge-case invoices
- Add support for more document types
- Add batch document processing
- Improve OCR accuracy for low-quality images
- Add monitoring and analytics

## 👩‍💻 Author

**Shilpi Jaiswal**

GitHub: https://github.com/shilpijaiswal02