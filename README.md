# FastAPI Voucher Management API

A comprehensive REST API for managing vouchers with CRUD operations, built with FastAPI, SQLAlchemy, and MySQL.

## Features

- ✅ Create vouchers with auto-generated unique codes
- ✅ List vouchers with pagination
- ✅ Retrieve vouchers by code (validates active status and expiration)
- ✅ Update voucher details
- ✅ Deactivate vouchers
- ✅ Delete vouchers
- ✅ Input validation using Pydantic v2
- ✅ SQLAlchemy ORM with MySQL
- ✅ CORS enabled
- ✅ Health check endpoint

## Prerequisites

- Python 3.9+
- MySQL Server 5.7+
- pip (Python package manager)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd fastapi-voucher-api
```

### 2. Create and Activate Virtual Environment

#### On UNIX-based systems (macOS, Linux):

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

#### On Windows:

```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up MySQL Database

#### On UNIX-based systems (macOS, Linux):

```bash
# Access MySQL
mysql -u root -p

# Then paste the contents of sql/create_database.sql
```

Or use this command:

```bash
mysql -u root -p < sql/create_database.sql
```

#### On Windows:

Open MySQL Command Line Client or MySQL Workbench and execute the SQL script:

```bash
mysql -u root -p < sql/create_database.sql
```

Or manually copy and paste the contents of `sql/create_database.sql` into your MySQL client.

### 5. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your database credentials
# For example:
# DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/voucher_db
```

Edit the `.env` file and update the `DATABASE_URL` with your MySQL credentials:

```
DATABASE_URL=mysql+pymysql://<username>:<password>@<host>:<port>/<database>
```

## Running the Application

### On UNIX-based systems:

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### On Windows:

```cmd
# Activate virtual environment (if not already active)
venv\Scripts\activate

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once the server is running, visit:

- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### Create a Voucher
```
POST /api/v1/vouchers/
Content-Type: application/json

{
  "discount_percentage": 15.5,
  "expiration_date": "2026-12-31T23:59:59"
}
```

**Response:**
```json
{
  "code": "ABC123DEF456",
  "discount_percentage": 15.5,
  "expiration_date": "2026-12-31T23:59:59",
  "active": true,
  "created_at": "2026-02-16T10:30:00",
  "updated_at": "2026-02-16T10:30:00"
}
```

### List Vouchers
```
GET /api/v1/vouchers/?page=1&page_size=10
```

**Response:**
```json
{
  "items": [
    {
      "code": "ABC123DEF456",
      "discount_percentage": 15.5,
      "expiration_date": "2026-12-31T23:59:59",
      "active": true,
      "created_at": "2026-02-16T10:30:00",
      "updated_at": "2026-02-16T10:30:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

### Get Voucher by Code (Valid Only)
```
GET /api/v1/vouchers/{code}
```

Returns the voucher only if it's active and not expired.

### Check Voucher by Code (Admin)
```
GET /api/v1/vouchers/check/{code}
```

Returns the voucher regardless of status (admin endpoint).

### Update Voucher
```
PUT /api/v1/vouchers/{code}
Content-Type: application/json

{
  "discount_percentage": 20.0,
  "expiration_date": "2027-12-31T23:59:59"
}
```

### Deactivate Voucher
```
PATCH /api/v1/vouchers/{code}/deactivate
```

### Delete Voucher
```
DELETE /api/v1/vouchers/{code}
```

## Database Schema

### Vouchers Table

| Column | Type | Description |
|--------|------|-------------|
| code | VARCHAR(50) | Primary key, auto-generated unique voucher code |
| discount_percentage | FLOAT | Discount percentage (0-100) |
| expiration_date | DATETIME | Voucher expiration date |
| active | BOOLEAN | Active status (default: true) |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Last update timestamp |

## Project Structure

```
fastapi-voucher-api/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI app initialization
│   ├── database.py           # Database configuration and session
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas (v2)
│   ├── crud.py               # CRUD operations
│   └── routes.py             # API route handlers
├── sql/
│   └── create_database.sql   # Database creation script
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore file
└── README.md                 # This file
```

## Development

### Activate Virtual Environment

#### UNIX-based:
```bash
source venv/bin/activate
```

#### Windows:
```cmd
venv\Scripts\activate
```

### Run with Auto-reload

```bash
uvicorn app.main:app --reload
```

### Deactivate Virtual Environment

```bash
deactivate
```

## Troubleshooting

### MySQL Connection Error

**Problem:** `Can't connect to MySQL server`

**Solution:**
1. Ensure MySQL server is running
2. Check your `DATABASE_URL` in `.env` file
3. Verify database credentials and host
4. Ensure the database exists (run `sql/create_database.sql`)

### Port Already in Use

**Problem:** `Address already in use`

**Solution:**
```bash
# Run on a different port
uvicorn app.main:app --port 8001
```

### Module Not Found

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
1. Activate virtual environment
2. Install dependencies: `pip install -r requirements.txt`

## License

MIT License - feel free to use this project as you wish.

## Support

For issues or questions, please open an issue in the repository.