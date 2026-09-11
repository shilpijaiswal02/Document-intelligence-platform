# Document Intelligence Platform

An AI-powered document processing platform that extracts structured information from financial documents, performs financial validation, stores processing results, and presents the results through a web dashboard and REST APIs.

The platform combines OCR, Google Gemini-based extraction, structured JSON responses, financial validation, PostgreSQL persistence, and Docker-based deployment.

---

##  Live Application

**Frontend / Dashboard:**  
https://document-intelligence-platform-zwf0.onrender.com

**Swagger / OpenAPI Documentation:**  
https://document-intelligence-platform-zwf0.onrender.com/docs

**Health Check:**  
https://document-intelligence-platform-zwf0.onrender.com/api/v1/health

**GitHub Repository:**  
https://github.com/shilpijaiswal02/Document-intelligence-platform

---

## 🎯 Problem Statement

Financial documents such as invoices and financial statements are often received as PDFs or scanned images with different layouts and varying document quality.

Manually extracting information from these documents is time-consuming and error-prone.

This project provides an end-to-end document intelligence workflow that:

- Accepts PDF and image-based documents
- Validates uploaded files
- Extracts text using OCR where required
- Uses Google Gemini for structured information extraction
- Extracts fields and financial tables/line items
- Performs financial consistency checks
- Stores processed results in PostgreSQL
- Provides a dashboard for viewing processed documents
- Exposes REST APIs with Swagger documentation

---

## ✨ Features

- PDF / JPG / PNG document upload
- Invoice and financial statement processing
- OCR using Tesseract
- AI-powered extraction using Google Gemini
- Structured JSON output
- Key-value field extraction
- Invoice line-item/table extraction
- Financial validation
- Validation status: `PASS`, `FAIL`, `NOT_APPLICABLE`
- Evidence/source text for extracted values
- Processing metadata
- Persistent document history
- PostgreSQL database integration
- REST API
- Swagger/OpenAPI documentation
- HTML/CSS/JavaScript frontend
- Dockerized application
- Render cloud deployment
- Environment-based secret configuration

---

## 🔄 System Architecture

```text
                     ┌─────────────────────┐
                     │       User          │
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │ Frontend Dashboard  │
                     │   HTML/CSS/JS       │
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │    FastAPI API      │
                     └──────────┬──────────┘
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
       ┌──────────────────┐          ┌──────────────────┐
       │ File Validation  │          │  Document Type   │
       │ PDF/JPG/PNG      │          │     Metadata     │
       └────────┬─────────┘          └──────────────────┘
                │
                ▼
       ┌──────────────────┐
       │ Tesseract OCR    │
       │ Text Extraction  │
       └────────┬─────────┘
                │
                ▼
       ┌──────────────────┐
       │ Google Gemini    │
       │ AI Extraction    │
       └────────┬─────────┘
                │
                ▼
       ┌──────────────────┐
       │ Structured Data  │
       │ JSON / Tables    │
       └────────┬─────────┘
                │
                ▼
       ┌──────────────────┐
       │ Financial        │
       │ Validation       │
       └────────┬─────────┘
                │
                ▼
       ┌──────────────────┐
       │ PostgreSQL /     │
       │ Neon Database    │
       └────────┬─────────┘
                │
                ▼
       ┌──────────────────┐
       │ Dashboard / REST │
       │ API Response     │
       └──────────────────┘

```
## 🛠️ Technology Stack

Python | FastAPI | Uvicorn | Pydantic | SQLAlchemy | Google Gemini API | Tesseract OCR | PDF/Image Processing | PostgreSQL | Neon PostgreSQL | HTML | CSS | JavaScript | Docker | Render | GitHub

## Why these technologies?
Technology	Purpose
Python	Core application and AI/document-processing logic
FastAPI	REST API development and automatic Swagger documentation
Pydantic	Structured request/response validation
SQLAlchemy	Database interaction and persistence layer
Google Gemini	AI-based document field and table extraction
Tesseract OCR	Text extraction from scanned/image-based documents
PostgreSQL	Persistent storage for processed document results
Neon PostgreSQL	Cloud-hosted PostgreSQL database
HTML/CSS/JavaScript	Lightweight frontend dashboard
Docker	Reproducible application packaging
Render	Cloud deployment
GitHub	Source-code management and public repository

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
```

## ⚙️ Environment Variables

Create a .env file in the project root:

GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=your_postgresql_connection_string

Never commit real credentials to GitHub.

The project uses environment variables for API keys and database credentials.

A safe configuration template is provided in:

.env.example

The .env file is excluded through .gitignore.

## 💻 Local Setup
1. Clone the Repository
git clone https://github.com/shilpijaiswal02/Document-intelligence-platform.git
cd Document-intelligence-platform
2. Create a Virtual Environment
python -m venv .venv
Windows PowerShell
.venv\Scripts\Activate.ps1
3. Install Dependencies
pip install -r backend/requirements.txt
4. Configure Environment Variables

Create .env:

GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=your_postgresql_connection_string
5. Run the Application
uvicorn backend.app.main:app --reload

Open:

http://localhost:8000
🐳 Docker Setup
Build the Docker Image
docker build -t document-intelligence-platform .
Run the Container
docker run --env-file .env -p 8000:8000 document-intelligence-platform

Open:

http://localhost:8000

The Docker image installs Tesseract OCR and runs the FastAPI application using Uvicorn.

☁️ Deployment

The application is deployed using Render.

GitHub
   ↓
Render
   ↓
Docker
   ↓
FastAPI
   ↓
Neon PostgreSQL

The Dockerfile installs the required dependencies, including Tesseract OCR, and starts the FastAPI application on port 8000.

Environment variables are configured in the Render service rather than stored in the repository.

🔌 REST API
Available Endpoints
Method	Endpoint	Description
POST	/api/v1/documents/process	Upload and process a document
GET	/api/v1/documents	List processed documents
GET	/api/v1/documents/{document_name}	Retrieve a processed document
GET	/document/{document_name}	Display document result
GET	/api/v1/health	Health check
GET	/	Dashboard

## Swagger documentation:

https://document-intelligence-platform-zwf0.onrender.com/docs

## Process Document API
Request
POST /api/v1/documents/process
Content-Type: multipart/form-data

The request contains:

file
document_type

Example document types:

invoice
balance_sheet
profit_and_loss
cash_flow_statement
Example using cURL
curl -X POST \
  "https://document-intelligence-platform-zwf0.onrender.com/api/v1/documents/process" \
  -F "file=@sample_invoice.pdf" \
  -F "document_type=invoice"
📋 List Processed Documents
GET /api/v1/documents

Example response:

[
  {
    "document_name": "sample_invoice.pdf",
    "document_type": "invoice",
    "processing_status": "PASS",
    "created_at": "2026-09-11T21:52:11"
  }
]
🔎 Get Document by Name
GET /api/v1/documents/{document_name}

The endpoint retrieves the latest stored processing result for the requested document.

❤️ Health Check
GET /api/v1/health

Example:

{
  "status": "healthy"
}
🤖 Document Processing Pipeline
1. File Validation

Before OCR or AI extraction, the uploaded document is checked for:

Supported file type
File readability
Basic file integrity
Page limitations

Unsupported or invalid documents are rejected before further processing.

2. OCR

Tesseract OCR is used when text needs to be extracted from scanned or image-based documents.

The extracted text becomes an input for the document extraction stage.

3. AI-Based Extraction

Google Gemini is used to analyze the extracted document content and return structured information.

The extraction process is designed to preserve:

Document fields
Dates
Parties
Currency
Financial values
Tables
Invoice line items
Supporting evidence

Missing values should be represented as null rather than invented.

4. Structured Output

Processed information is returned as structured JSON.

Example:

{
  "document_name": "sample_invoice.pdf",
  "document_type": "invoice",
  "processing_status": "PASS",
  "extracted_data": {
    "invoice_number": {
      "value": "INV-23891"
    },
    "invoice_date": {
      "value": "2026-08-15"
    },
    "vendor_name": {
      "value": "ABC Technologies"
    },
    "currency": {
      "value": "USD"
    },
    "subtotal": {
      "value": 12500.00
    },
    "tax_amount": {
      "value": 625.00
    },
    "total_amount": {
      "value": 13125.00
    }
  }
}
```
 ## Evidence / Grounding

Where available, extracted values can be associated with supporting source text.

Example:

{
  "field": "total_amount",
  "value": 13125.00,
  "evidence": {
    "source_text": "Total Amount Due: USD 13,125.00",
    "page_number": 1
  }
}

This allows important extracted values to be traced back to the source document.

## Financial Validation

The platform performs financial consistency checks based on the values actually present in the document.

Invoice Validation

Examples include:

Quantity × Unit Price ≈ Line Total
Sum of Line Totals ≈ Subtotal
Taxable Amount + Tax ≈ Total

Where the required fields are unavailable, the validation returns:

NOT_APPLICABLE

The system does not assume missing values for financial calculations.

Balance Sheet Validation

The primary relationship is:

Total Capital & Liabilities ≈ Total Assets

Where sufficient component values are available, individual financial line items can also be reconciled against reported totals.

Validation Output

Each validation check records:

Formula
Input values
Calculated value
Reported value
Variance
Status

Possible statuses:

PASS
FAIL
NOT_APPLICABLE
```
## Database & Persistence

Processed document information is stored in PostgreSQL.

The deployed application uses Neon PostgreSQL as the cloud database.

Stored information includes processed-document metadata and extraction results so that processed documents remain available after processing.

The dashboard retrieves the stored records through the backend API.
```
## Dashboard

The frontend dashboard provides:

Document upload
Document type selection
Processing action
Processed document history
Document name
Document type
Processing status
Processing time
Extracted fields
Tables / line items where available
Financial validation results
Structured JSON result

This allows evaluators to inspect both successful and failed document-processing cases.

## 🧪 Testing

The project includes backend tests for areas such as:

API functionality
Document extraction
Extraction quality
Invoice recovery
Financial validation

Run the test suite using:

pytest

Manual testing has also been performed against the deployed application using financial documents and image-based documents.

Examples include:

Invoice documents
Balance sheet PDFs
JPG/image documents
Financial validation failure scenarios
## Testing

Automated tests were executed using pytest.

**Result: 14 tests passed successfully.**

The platform was tested across the supported financial document categories and key application scenarios.

| Test Scenario | Result |
|---|---|
| Invoice processing | PASS |
| Balance Sheet processing | PASS |
| Profit & Loss processing | PASS |
| Cash Flow Statement processing | PASS |
| Scanned/Image document processing | PASS |
| Financial validation failure scenario | PASS |
| API end-to-end flow | PASS |
| PostgreSQL/Neon persistence | PASS |
| Automated tests | Verified with pytest |

### Validation Testing

Financial validation was tested using document-specific checks. A validation failure was observed for a complex invoice where extracted financial values did not fully reconcile, demonstrating that the system can identify inconsistencies instead of blindly accepting extracted values.

### Sample Outputs

Real processed JSON responses are provided in:

`sample_outputs/`

### Invalid / Unreadable Document Testing

The application was tested with an unreadable image document. The system detected that no readable text was available and prevented normal document processing, displaying an appropriate user-facing message instead of producing unreliable extraction results.


## Known Limitations
OCR accuracy can decrease for low-quality or heavily distorted images.
Complex invoice tables may not always be extracted completely.
Financial validation depends on the fields successfully extracted from the source document.
AI extraction quality can vary depending on document layout and OCR quality.
Render free-tier services may experience slower initial responses after periods of inactivity.
Complex real-world financial documents may require additional document-specific extraction strategies.
## Production Improvements

For a production-scale system, the following improvements could be implemented:

Authentication and role-based access control
Background/asynchronous document processing
Queue-based processing for large workloads
Improved OCR using specialized document OCR services
More robust table extraction
Better confidence scoring and calibration
Document versioning
User-specific document storage
Rate limiting
Monitoring and alerting
Centralized structured logging
Retry and timeout strategies for external AI services
Automated deployment pipelines
Object storage for uploaded documents
Stronger validation and schema versioning
## Security

Security practices implemented include:

API keys stored in environment variables
Database credentials stored in environment variables
.env excluded from Git
No real secrets committed to the public repository
Uploaded files validated before processing
Controlled API responses instead of exposing internal credentials
## AI / Tool Usage Declaration

Generative AI tools were used during development as permitted by the case study.

AI assistance was used for:

Understanding implementation approaches
Debugging and troubleshooting
Reviewing code structure
Improving documentation
Supporting development decisions

The final application, architecture, validation logic, API behavior, deployment configuration, and submitted source code are the responsibility of the candidate and can be explained and modified during technical discussion.

## Assumptions
The user selects the document type before processing.
Missing or unavailable document values should not be fabricated.
Financial calculations are performed only when sufficient source fields are available.
Validation may return NOT_APPLICABLE when required fields are missing.
Minor numerical differences may occur due to document formatting, OCR, or rounding.

## Project Evaluation Focus

The implementation is designed around the main areas of the technical case study:

End-to-end deployment
Extraction completeness and accuracy
REST API quality
Frontend and database integration
Financial validation
Code quality and security
Testing and documentation

## Future Improvements
Support more complex financial statement layouts
Improve invoice line-item recovery
Add stronger table extraction
Add confidence scoring
Add authentication
Add batch document processing
Add document search and filtering
Add analytics and monitoring dashboards
Improve OCR handling for poor-quality scans

## Author

Shilpi Jaiswal

GitHub:
https://github.com/shilpijaiswal02

