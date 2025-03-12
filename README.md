# Metamorph
MetaMorph 🚀🔄 – Transforming Raw Data into Gold! MetaMorph is your ultimate data alchemist, seamlessly ingesting, normalizing, and enriching data from multiple sources. Track user spending, uncover hot-selling products, and gain deep insights with a single API call! Turn chaos into clarity and make data work for you! 🌟📊💡


Metamorph is a data transformation pipeline built using Django Rest Framework, PostgreSQL, Celery, and Redis. The platform ingests raw event data from multiple public APIs, transforms and normalizes it into a unified format, applies business logic to enrich the data (by joining transaction data with product and user details), and exposes the processed data along with business insights through secure API endpoints.

## Table of Contents
- [Features](#features)
- [Data Pipeline Architecture](#data-pipeline-architecture)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
  - [Authentication](#authentication)
  - [Endpoints](#endpoints)
- [Testing Guidelines](#testing-guidelines)
- [Approach Summary](#approach-summary)
- [Contributing](#contributing)
- [License](#license)

## Features
- **Data Ingestion:** Fetches data from multiple public APIs:
  - **E-commerce Product Data:** [FakeStoreAPI](https://fakestoreapi.com/products)
  - **User Data:** [RandomUser API](https://randomuser.me/api/?results=20)
  - **Transactions Data:** [Mockaroo](https://my.api.mockaroo.com/orders.json?key=e49e6840)
- **Data Transformation:** Normalizes data into a unified JSON format:
  ```json
  {
      "entity_id": "generated-unique-id",
      "entity_type": "product|user|transaction",
      "timestamp": "ISO-8601-format",
      "data": { /* Normalized fields from the source */ },
      "metadata": {
          "source": "which API",
          "processed_at": "processing timestamp"
      }
  }
  ```
- **Business Logic & Enrichment:** Enriches transaction records by joining them with related user and product details.
- **Secure API Endpoints:** Provides endpoints for querying processed data and insights, secured with JWT authentication.
- **Task Scheduling:** Uses Celery with Redis to periodically fetch and process data.

## Data Pipeline Architecture
The project is architected as follows:

1. **Data Ingestion:**
   - Implemented in `core/fetch_data.py`.
   - Fetches raw data from the three public APIs and caches responses in the `APIDataCache` model.
2. **Data Transformation:**
   - Implemented in `core/services.py` (function `transform_data`).
   - Converts raw API data into a unified JSON format.
3. **Data Enrichment:**
   - Implemented in `core/services.py` (function `enrich_transactions`).
   - Joins each transaction with its related user and product details and stores the enriched record in the `UnifiedEntity` model.
4. **API Layer:**
   - Implemented in `core/views.py`.
   - Provides endpoints for:
     - Retrieving unified data by entity type.
     - Viewing user spending insights.
     - Viewing product popularity metrics.
     - Triggering the enrichment process.
   - Endpoints (except the overview) are protected via JWT.
5. **Task Scheduling:**
   - Configured in `metamorph/settings.py` and implemented using Celery (see `core/tasks.py`).
   - Regular tasks (e.g., fetching data every 5–30 minutes) are scheduled via Celery Beat.

## Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis
- Celery (for task scheduling)

### Clone the Repository
```bash
git clone https://github.com/your-username/metamorph.git
cd metamorph
```

### Create a Virtual Environment and Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configure PostgreSQL
Update the database settings in `metamorph/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'metamorph_db',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
Create the PostgreSQL database and user as needed.

### Migrate the Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### Create a Superuser
```bash
python manage.py createsuperuser
```

### Configure and Start Celery & Redis
Ensure Redis is running on `localhost:6379`. Then, start Celery:
```bash
celery -A metamorph worker -l info
celery -A metamorph beat -l info
```

### Run the Development Server
```bash
python manage.py runserver
```

## API Documentation

All API endpoints (except `/api/`) require JWT authentication. Obtain a token via the `/api/token/` endpoint.

### Authentication

#### Obtain JWT Token
**Endpoint:** `POST /api/token/`
  
**Request Body:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "refresh": "your_refresh_token",
  "access": "your_access_token"
}
```

#### Refresh Token
**Endpoint:** `POST /api/token/refresh/`
  
**Request Body:**
```json
{
  "refresh": "your_refresh_token"
}
```

### Endpoints

#### 1. Retrieve Unified Data by Entity Type
**Endpoint:** `GET /api/data/<entity_type>/`  
*Allowed values for `<entity_type>`: `product`, `user`, `transaction`.*

**Headers:**
```
Authorization: Bearer <access_token>
```

**Example Request:**
```http
GET /api/data/product/
```

**Example Response:**
```json
[
  {
    "entity_id": "generated-unique-id",
    "entity_type": "product",
    "timestamp": "2025-03-09T12:34:56.789Z",
    "data": {
      "external_id": 1,
      "title": "Fjallraven - Foldsack No. 1 Backpack",
      "price": "109.95",
      "category": "men's clothing",
      "description": "Your perfect pack for everyday use...",
      "image_url": "https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg"
    },
    "metadata": {
      "source": "FakeStoreAPI",
      "processed_at": "2025-03-09T12:34:56.789Z"
    }
  }
]
```

#### 2. Retrieve User Spending Insights
**Endpoint:** `GET /api/insights/users/`

**Example Request:**
```http
GET /api/insights/users/
Authorization: Bearer <access_token>
```

**Example Response:**
```json
[
  {
    "external_id": "user-uuid",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "total_spent": "350.50"
  }
]
```

#### 3. Retrieve Product Popularity Metrics
**Endpoint:** `GET /api/insights/products/`

**Example Request:**
```http
GET /api/insights/products/
Authorization: Bearer <access_token>
```

**Example Response:**
```json
{
  "product_categories": [
    { "name": "men's clothing", "transaction_count": 20 },
    { "name": "jewelery", "transaction_count": 10 }
  ],
  "average_transaction_value": 45.67
}
```

#### 4. Trigger Transaction Data Enrichment
**Endpoint:** `POST /api/enrich/transactions/`

**Example Request:**
```http
POST /api/enrich/transactions/
Authorization: Bearer <access_token>
```

**Example Response:**
```json
{
  "message": "Successfully enriched X transaction records."
}
```
*`X` represents the number of enriched records based on the current transaction data.*

## Testing Guidelines (Using Postman)
1. **Obtain a JWT Token:**
   - Send a `POST` request to `/api/token/` with your username and password.
   - Copy the `access_token` from the response.

2. **Test Protected Endpoints:**
   - For each endpoint (e.g., `/api/data/product/`, `/api/insights/users/`, `/api/insights/products/`, `/api/enrich/transactions/`), add the header:
     ```
     Authorization: Bearer <access_token>
     ```
   - Send the appropriate GET or POST requests as outlined above.
   - Verify that the responses match the expected JSON structure.

3. **Error Handling:**
   - Test error scenarios, such as using an invalid entity type in `/api/data/invalid/`, and verify that appropriate error messages are returned.

## Approach Summary
The Metamorph project was designed to demonstrate a comprehensive data transformation pipeline:

- **Data Ingestion:**  
  Raw data is fetched from multiple public APIs and cached for efficiency.

- **Data Transformation:**  
  Raw data is converted into a unified JSON format using the `transform_data` function.

- **Business Logic & Enrichment:**  
  Transaction records are enriched by joining them with related user and product details using the `enrich_transactions` function. This enrichment is triggered via a dedicated API endpoint.

- **API Exposure:**  
  Secure RESTful API endpoints (protected by JWT) allow external clients to query processed data and view business insights.

- **Task Scheduling:**  
  Celery and Redis are used to schedule regular data fetching and processing tasks, ensuring the data remains up-to-date.

Throughout the project, extensive error handling, logging, and modular code organization have been implemented to ensure robustness, maintainability, and scalability.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.
