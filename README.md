# MicroBank - Microservices Banking System

A comprehensive banking system built using a microservices architecture with Python and Flask.

<p align="center">
  <img src="generated-icon.png" alt="MicroBank" width="500"/>
</p>

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

- **Backend**: Python 3.12, Flask 2.x
- **Database**: SQLite (with SQLAlchemy ORM)
- **Frontend**: HTML, Bootstrap 5, JavaScript
- **Authentication**: JWT (JSON Web Tokens)
- **Inter-service Communication**: RESTful APIs
- **Process Management**: Custom orchestration via `run_services.py`
- **Package Management**: Python's standard pip (with uv acceleration)

## Running Locally

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Consul (optional, for service discovery)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/microbank.git
cd microbank

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
export AUTH_SERVICE_URL="http://localhost:8001"
export ACCOUNT_SERVICE_URL="http://localhost:8002"
export TRANSACTION_SERVICE_URL="http://localhost:8003"
export REPORTING_SERVICE_URL="http://localhost:8004"
export SESSION_SECRET="your_secret_key_here"
export AUTH_DATABASE_URL="sqlite:///auth_service/auth.db"
export ACCOUNT_DATABASE_URL="sqlite:///account_service/account.db"
export TRANSACTION_DATABASE_URL="sqlite:///transaction_service/transaction.db"
export REPORTING_DATABASE_URL="sqlite:///reporting_service/reporting.db"

# Run all services
python run_services.py
```

Then visit <http://localhost:5000> in your browser to access the application.

### Complete Environment Variable Reference

Here's a complete list of environment variables used by the system:

#### Service URLs (Used by the API Gateway)

```
AUTH_SERVICE_URL="http://localhost:8001"
ACCOUNT_SERVICE_URL="http://localhost:8002" 
TRANSACTION_SERVICE_URL="http://localhost:8003"
REPORTING_SERVICE_URL="http://localhost:8004"
```

#### Database URLs (Used by each service)

```
AUTH_DATABASE_URL="sqlite:///auth_service/auth.db"
ACCOUNT_DATABASE_URL="sqlite:///account_service/account.db"
TRANSACTION_DATABASE_URL="sqlite:///transaction_service/transaction.db"
REPORTING_DATABASE_URL="sqlite:///reporting_service/reporting.db"
```

#### Security

```
SESSION_SECRET="your_secret_key_here"  # Used for JWT token signing
```

#### Consul Service Discovery (Optional)

```
CONSUL_HOST="localhost"
CONSUL_PORT="8500"
USE_CONSUL="true"  # Enable Consul service discovery
```

### Detailed Installation Steps

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
   export AUTH_DATABASE_URL="sqlite:///auth_service/auth.db"
   export ACCOUNT_DATABASE_URL="sqlite:///account_service/account.db"
   export TRANSACTION_DATABASE_URL="sqlite:///transaction_service/transaction.db"
   export REPORTING_DATABASE_URL="sqlite:///reporting_service/reporting.db"
   ```

5. Run the application:

   ```bash
   python run_services.py
   ```

   This will start all services in a coordinated manner.

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
   export AUTH_DATABASE_URL="sqlite:///auth_service/auth.db"
   export ACCOUNT_DATABASE_URL="sqlite:///account_service/account.db"
   export TRANSACTION_DATABASE_URL="sqlite:///transaction_service/transaction.db"
   export REPORTING_DATABASE_URL="sqlite:///reporting_service/reporting.db"
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
   set AUTH_DATABASE_URL=sqlite:///auth_service/auth.db
   set ACCOUNT_DATABASE_URL=sqlite:///account_service/account.db
   set TRANSACTION_DATABASE_URL=sqlite:///transaction_service/transaction.db
   set REPORTING_DATABASE_URL=sqlite:///reporting_service/reporting.db
   ```

5. Run the application:

   ```cmd
   python run_services.py
   ```

### Configuration Options

The application can be configured using environment variables:

#### Basic Configuration

```bash
# Service URLs
export AUTH_SERVICE_URL="http://localhost:8001"
export ACCOUNT_SERVICE_URL="http://localhost:8002"
export TRANSACTION_SERVICE_URL="http://localhost:8003"
export REPORTING_SERVICE_URL="http://localhost:8004"

# Database URLs
export AUTH_DATABASE_URL="sqlite:///auth_service/auth.db"
export ACCOUNT_DATABASE_URL="sqlite:///account_service/account.db"
export TRANSACTION_DATABASE_URL="sqlite:///transaction_service/transaction.db"
export REPORTING_DATABASE_URL="sqlite:///reporting_service/reporting.db"

# Security
export SESSION_SECRET="your_secret_key_here"
```

#### Consul Configuration (Optional)

The system supports service discovery using Consul. If you want to use Consul:

1. Install and run Consul:

   ```bash
   # On Linux/macOS
   wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
   echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
   sudo apt update && sudo apt install consul
   
   # Start Consul
   consul agent -dev
   ```

2. Configure the application to use Consul:

   ```bash
   export CONSUL_HOST="localhost"
   export CONSUL_PORT="8500"
   export USE_CONSUL="true"  # Enable Consul service discovery
   ```

When Consul is enabled, services will register themselves with Consul at startup and query Consul for service discovery, providing a more production-ready setup.

### Running with Service Orchestration

For production-like environments, use the service orchestrator:

```bash
# Run all services with default settings
python run_services.py

# Run services with specific options
python run_services.py --no-auth  # Skip auth service
python run_services.py --port 5001  # Run API Gateway on port 5001
```

### Running Services Individually

You can also run each service individually in separate terminals:

```bash
# Terminal 1 - Auth Service
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m auth_service.auth_service

# Terminal 2 - Account Service
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m account_service.account_service

# Terminal 3 - Transaction Service
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m transaction_service.transaction_service

# Terminal 4 - Reporting Service
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m reporting_service.reporting_service

# Terminal 5 - API Gateway
source venv/bin/activate  # or venv\Scripts\activate on Windows
export AUTH_SERVICE_URL="http://localhost:8001"
export ACCOUNT_SERVICE_URL="http://localhost:8002"
export TRANSACTION_SERVICE_URL="http://localhost:8003"
export REPORTING_SERVICE_URL="http://localhost:8004"
export SESSION_SECRET="your_secret_key_here"
export AUTH_DATABASE_URL="sqlite:///auth_service/auth.db"
export ACCOUNT_DATABASE_URL="sqlite:///account_service/account.db"
export TRANSACTION_DATABASE_URL="sqlite:///transaction_service/transaction.db"
export REPORTING_DATABASE_URL="sqlite:///reporting_service/reporting.db"
python main.py
```

### Access the Application

Once all services are running, access the application at `http://localhost:5000`

### Default Admin Login

To access admin features, use the following credentials:

- **Username**: `admin`
- **Password**: `admin123`

## Database Structure

Each microservice maintains its own SQLite database:

- **Auth Service**: `auth_service/auth.db`
- **Account Service**: `account_service/account.db`
- **Transaction Service**: `transaction_service/transaction.db`
- **Reporting Service**: `reporting_service/reporting.db`

These databases are initialized automatically on first run.

## Troubleshooting

### Common Issues and Solutions

1. **Service connection errors**
   - Verify that all services are running on their expected ports
   - Check that environment variables for service URLs are correctly set
   - Look for firewall issues that might be blocking the ports

2. **JWT authentication failures**
   - Ensure the `SESSION_SECRET` environment variable is set consistently
   - Check that the token hasn't expired
   - Verify that the token is correctly formatted in the request header

3. **Module not found errors**
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
│   ├── account_storage.py     # Account data storage
│   └── account.db             # Account SQLite database
├── auth_service/              # Authentication microservice
│   ├── auth_models.py         # Auth-specific models
│   ├── auth_service.py        # Auth API endpoints
│   ├── auth_storage.py        # User data storage
│   └── auth.db                # Auth SQLite database
├── reporting_service/         # Reporting microservice
│   ├── reporting_models.py    # Report-specific models
│   ├── reporting_service.py   # Reporting API endpoints
│   ├── reporting_storage.py   # Report data storage
│   └── reporting.db           # Reporting SQLite database
├── static/                    # Static assets
│   ├── css/                   # CSS stylesheets
│   └── js/                    # JavaScript files
├── templates/                 # HTML templates
├── transaction_service/       # Transaction microservice
│   ├── transaction_models.py  # Transaction-specific models
│   ├── transaction_service.py # Transaction API endpoints
│   ├── transaction_storage.py # Transaction data storage
│   └── transaction.db         # Transaction SQLite database
├── data/                      # Additional data storage directory
├── api_gateway.py             # API Gateway helper functions
├── main.py                    # API Gateway implementation
├── models.py                  # Core data models
├── run_services.py            # Service orchestration
├── storage.py                 # Base storage functionality
├── utils.py                   # Utility functions
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Python project metadata
└── uv.lock                    # Dependency lock file for uv
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

For a smoother development experience, consider setting up environment variables in a `.env` file:

```
AUTH_SERVICE_URL=http://localhost:8001
ACCOUNT_SERVICE_URL=http://localhost:8002
TRANSACTION_SERVICE_URL=http://localhost:8003
REPORTING_SERVICE_URL=http://localhost:8004
SESSION_SECRET=dev_secret_key
AUTH_DATABASE_URL=sqlite:///auth_service/auth.db
ACCOUNT_DATABASE_URL=sqlite:///account_service/account.db
TRANSACTION_DATABASE_URL=sqlite:///transaction_service/transaction.db
REPORTING_DATABASE_URL=sqlite:///reporting_service/reporting.db
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

## License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- This project was developed as a demonstration of microservices architecture principles
- Built with Flask and Python, leveraging their simplicity and power
