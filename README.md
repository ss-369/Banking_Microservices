# MicroBank - Microservices Banking System

A comprehensive banking system built using a microservices architecture with Python and Flask.

![MicroBank](generated-icon.png)

## Overview

MicroBank is a fully-featured banking system implemented using a microservices architecture. The application allows users to manage accounts, process transactions (deposits, withdrawals, transfers), and generate various financial reports. It also includes administrative tools for system-wide management.

## Features

- **User Authentication & Authorization**
  - Registration and login
  - JWT-based authentication
  - Role-based access control (customer/admin)

- **Account Management**
  - Create different account types
  - View account details
  - Close accounts
  - Track account balances

- **Transaction Processing**
  - Deposits
  - Withdrawals
  - Account transfers
  - Transaction history

- **Financial Reporting**
  - Account reports
  - Transaction reports
  - System-wide reports (admin only)

- **Admin Dashboard**
  - User management
  - Account oversight
  - System health monitoring
  - Statistics and analytics

## Architecture

The system is built using a microservices architecture with the following components:

1. **API Gateway** (`main.py`)
   - Entry point for all client requests
   - Handles routing to appropriate microservices
   - Manages authentication and session state

2. **Auth Service** (`auth_service/`)
   - User authentication and authorization
   - User account management
   - Token generation and validation

3. **Account Service** (`account_service/`)
   - Account creation and management
   - Balance operations
   - Account status handling

4. **Transaction Service** (`transaction_service/`)
   - Process financial transactions
   - Maintain transaction history
   - Ensure transaction integrity

5. **Reporting Service** (`reporting_service/`)
   - Generate account reports
   - Generate transaction reports
   - Provide system-wide analytics (for admin)

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, Bootstrap, JavaScript
- **Authentication**: JWT (JSON Web Tokens)
- **Data Storage**: SQLite (file-based) for development, with support for PostgreSQL in production
- **Service Communication**: RESTful APIs

## Running Locally

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Installation Steps

First, clone the repository:

```bash
git clone https://github.com/yourusername/microbank.git
cd microbank
```

### Setting Up on Different Operating Systems

#### Linux

1. Create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create the database directory:

   ```bash
   mkdir -p data
   ```

4. Set environment variables:

   ```bash
   export AUTH_SERVICE_URL="http://localhost:8001"
   export ACCOUNT_SERVICE_URL="http://localhost:8002"
   export TRANSACTION_SERVICE_URL="http://localhost:8003"
   export REPORTING_SERVICE_URL="http://localhost:8004"
   export SESSION_SECRET="your_secret_key_here"
   export DATABASE_URL="sqlite:///data/microbank.db"
   ```

5. Run the application:

   ```bash
   python run_services.py
   ```

#### macOS

1. Create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create the database directory:

   ```bash
   mkdir -p data
   ```

4. Set environment variables:

   ```bash
   export AUTH_SERVICE_URL="http://localhost:8001"
   export ACCOUNT_SERVICE_URL="http://localhost:8002"
   export TRANSACTION_SERVICE_URL="http://localhost:8003"
   export REPORTING_SERVICE_URL="http://localhost:8004"
   export SESSION_SECRET="your_secret_key_here"
   export DATABASE_URL="sqlite:///data/microbank.db"
   ```

5. Run the application:

   ```bash
   python run_services.py
   ```

#### Windows

1. Create a virtual environment:

   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install dependencies:

   ```cmd
   pip install -r requirements.txt
   ```

3. Create the database directory:

   ```cmd
   mkdir data
   ```

4. Set environment variables:

   ```cmd
   set AUTH_SERVICE_URL=http://localhost:8001
   set ACCOUNT_SERVICE_URL=http://localhost:8002
   set TRANSACTION_SERVICE_URL=http://localhost:8003
   set REPORTING_SERVICE_URL=http://localhost:8004
   set SESSION_SECRET=your_secret_key_here
   set DATABASE_URL=sqlite:///data/microbank.db
   ```

5. Run the application:

   ```cmd
   python run_services.py
   ```

### Running Services Individually

You can also run each service individually in separate terminals:

```bash
# Terminal 1 - Auth Service
source venv/bin/activate  # or venv\Scripts\activate on Windows
export DATABASE_URL="sqlite:///data/microbank.db"  # or set DATABASE_URL=sqlite:///data/microbank.db on Windows
python -m auth_service.auth_service

# Terminal 2 - Account Service
source venv/bin/activate  # or venv\Scripts\activate on Windows
export DATABASE_URL="sqlite:///data/microbank.db"  # or set DATABASE_URL=sqlite:///data/microbank.db on Windows
python -m account_service.account_service

# Terminal 3 - Transaction Service
source venv/bin/activate  # or venv\Scripts\activate on Windows
export DATABASE_URL="sqlite:///data/microbank.db"  # or set DATABASE_URL=sqlite:///data/microbank.db on Windows
python -m transaction_service.transaction_service

# Terminal 4 - Reporting Service
source venv/bin/activate  # or venv\Scripts\activate on Windows
export DATABASE_URL="sqlite:///data/microbank.db"  # or set DATABASE_URL=sqlite:///data/microbank.db on Windows
python -m reporting_service.reporting_service

# Terminal 5 - API Gateway
source venv/bin/activate  # or venv\Scripts\activate on Windows
export AUTH_SERVICE_URL="http://localhost:8001"
export ACCOUNT_SERVICE_URL="http://localhost:8002"
export TRANSACTION_SERVICE_URL="http://localhost:8003"
export REPORTING_SERVICE_URL="http://localhost:8004"
export SESSION_SECRET="your_secret_key_here"
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

### Access the Application

Once all services are running, access the application at `http://localhost:5000`

### Default Admin Login

To access admin features, use the following credentials:

- **Username**: `admin`
- **Password**: `admin123`

## Database Setup

The application uses SQLite by default for development purposes. The database file is automatically created when you start the services, located at `data/microbank.db`.

### Using a Different Database

To use a different database system like PostgreSQL or MySQL:

1. Install the appropriate database driver:

   ```bash
   pip install psycopg2-binary  # For PostgreSQL
   # or
   pip install mysqlclient      # For MySQL
   ```

2. Update the DATABASE_URL environment variable:

   ```bash
   # PostgreSQL
   export DATABASE_URL="postgresql://username:password@localhost/microbank"
   
   # MySQL
   export DATABASE_URL="mysql://username:password@localhost/microbank"
   ```

3. Create the database before starting the application:

   ```bash
   # PostgreSQL
   createdb microbank
   
   # MySQL
   mysql -u root -p -e "CREATE DATABASE microbank CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   ```

## Troubleshooting

### Common Issues and Solutions

1. **Unable to open database file**
   - Make sure the `data` directory exists
   - Check file permissions for the `data` directory
   - Ensure the environment variable `DATABASE_URL` is correctly set

2. **Service connection errors**
   - Verify that all services are running on their expected ports
   - Check that environment variables for service URLs are correctly set
   - Look for firewall issues that might be blocking the ports

3. **JWT authentication failures**
   - Ensure the `SESSION_SECRET` environment variable is set consistently
   - Check that the token hasn't expired
   - Verify that the token is correctly formatted in the request header

4. **Module not found errors**
   - Make sure all dependencies are installed with `pip install -r requirements.txt`
   - Verify that you're running the commands from the project root directory
   - Check that your virtual environment is activated

### Service Logs

If you encounter issues, check the service logs for more detailed error information. When running with `run_services.py`, logs are output to the console. You can redirect them to files for persistence:

```bash
python run_services.py > microbank.log 2>&1
```

## Project Structure

```
├── account_service/           # Account microservice
│   ├── account_models.py      # Account-specific models
│   ├── account_service.py     # Account API endpoints
│   └── account_storage.py     # Account data storage
├── auth_service/              # Authentication microservice
│   ├── auth_models.py         # Auth-specific models
│   ├── auth_service.py        # Auth API endpoints
│   └── auth_storage.py        # User data storage
├── reporting_service/         # Reporting microservice
│   ├── reporting_models.py    # Report-specific models
│   ├── reporting_service.py   # Reporting API endpoints
│   └── reporting_storage.py   # Report data storage
├── static/                    # Static assets
│   ├── css/                   # CSS stylesheets
│   └── js/                    # JavaScript files
├── templates/                 # HTML templates
├── transaction_service/       # Transaction microservice
│   ├── transaction_models.py  # Transaction-specific models
│   ├── transaction_service.py # Transaction API endpoints
│   └── transaction_storage.py # Transaction data storage
├── data/                      # Data storage directory
├── api_gateway.py             # API Gateway helper functions
├── main.py                    # API Gateway implementation
├── models.py                  # Core data models
├── run_services.py            # Service orchestration
└── utils.py                   # Utility functions
```

## API Endpoints

### Auth Service API (Port 8001)

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/auth/register` | POST | Register new user | Public |
| `/api/auth/login` | POST | Authenticate user | Public |
| `/api/auth/verify_token` | GET | Verify JWT token | Private |
| `/api/auth/users` | GET | List all users | Admin |
| `/api/auth/verify_admin` | GET | Verify admin role | Private |
| `/api/health` | GET | Service health check | Public |

### Account Service API (Port 8002)

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/accounts/create` | POST | Create new account | Private |
| `/api/accounts/list` | GET | List user accounts | Private |
| `/api/accounts/details/<account_id>` | GET | Get account details | Private |
| `/api/accounts/close/<account_id>` | DELETE | Close account | Private |
| `/api/accounts/all` | GET | List all accounts | Admin |
| `/api/health` | GET | Service health check | Public |

### Transaction Service API (Port 8003)

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/transactions/deposit` | POST | Create deposit | Private |
| `/api/transactions/withdraw` | POST | Create withdrawal | Private |
| `/api/transactions/transfer` | POST | Create transfer | Private |
| `/api/transactions/list` | GET | List user transactions | Private |
| `/api/transactions/account/<account_id>` | GET | Get account transactions | Private |
| `/api/health` | GET | Service health check | Public |

### Reporting Service API (Port 8004)

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/reports/account/<account_id>` | GET | Generate account report | Private |
| `/api/reports/transactions` | GET | Generate transaction report | Private |
| `/api/reports/system` | GET | Generate system report | Admin |
| `/api/reports/list` | GET | List user reports | Private |
| `/api/health` | GET | Service health check | Public |

## Error Handling

The system implements a multi-layered error handling approach:

1. **Service-level error handling**
   - Try-except blocks for catching exceptions
   - Appropriate HTTP status codes for different error conditions
   - Structured error responses with clear messages

2. **Gateway-level error handling**
   - Error response formatting for client consumption
   - Error page rendering for user-friendly error display
   - Logging of service failures

All error responses follow a standardized format:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "details": {}
}
```

## Health Monitoring

Each service exposes a `/api/health` endpoint for monitoring. The API Gateway aggregates health status from all services at the `/health` endpoint.

## Security Implementation

- **JWT-based Authentication**: Secure user sessions with token-based auth
- **Role-based Access Control**: Different permissions for customer and admin roles
- **Password Security**: Password hashing with salt-based storage
- **Microservice Isolation**: Each service runs on a separate port

## Development and Testing

### Development Environment Setup

For development work, it's recommended to set up environment variables in a `.env` file:

```
AUTH_SERVICE_URL=http://localhost:8001
ACCOUNT_SERVICE_URL=http://localhost:8002
TRANSACTION_SERVICE_URL=http://localhost:8003
REPORTING_SERVICE_URL=http://localhost:8004
SESSION_SECRET=dev_secret_key
DATABASE_URL=sqlite:///data/microbank.db
```

Then use python-dotenv to load them:

```bash
pip install python-dotenv
```

And at the top of your run script:

```python
from dotenv import load_dotenv
load_dotenv()
```

### Running Tests

To run the test suite, use the following command:

```bash
python -m unittest discover
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This project was developed as a demonstration of microservices architecture principles
- Built with Flask and Python, leveraging their simplicity and power
