# Banking System Technical Report

## 1. Executive Summary

This report provides a comprehensive technical overview of the microservices-based banking system implementation. The system is designed to provide core banking functionalities through a collection of specialized services that work together to deliver a robust and scalable banking platform.

Our banking system offers a complete solution for financial institutions, implementing essential banking operations including user management, account management, transaction processing, and financial reporting. The system follows modern software architecture practices, leveraging microservices, RESTful APIs, and a responsive web interface to deliver a flexible and maintainable platform.

Key features of the banking system include:

- **User Management**: Secure registration, authentication, and profile management
- **Account Operations**: Creation and management of different account types
- **Transaction Processing**: Secure handling of deposits, withdrawals, and transfers
- **Financial Reporting**: Generation of account statements and financial analytics
- **Administrative Tools**: Management interfaces for system administrators
- **Security**: Comprehensive authentication, authorization, and data protection

The system is built using modern technologies including Python, Flask, SQLAlchemy, and SQLite, with a service-oriented architecture that ensures modularity, scalability, and maintainability.

This document outlines the system architecture, design patterns, key components, and implementation details to provide a comprehensive understanding of the banking platform.

## 2. System Overview

### 2.1 System Description

The Banking Microservices System is a comprehensive financial platform designed to handle core banking operations through a collection of specialized services. The system simulates a real-world banking environment with features that would be expected in a modern digital banking solution.

#### Purpose and Scope

The system serves as a demonstration of microservices architecture applied to the banking domain, showcasing how complex financial systems can be decomposed into manageable, independently deployable services. It is designed to support common banking operations while maintaining the high standards of security, reliability, and performance required in financial applications.

#### Target Users

The system is designed for three main user types:

1. **Customers**: End users who access banking services like account management and transactions
2. **Bank Employees**: Staff who need tools to assist customers and manage accounts
3. **System Administrators**: Technical users who monitor and maintain the system

#### Key Capabilities

1. **Account Management**
   - Creation of various account types (checking, savings, investment)
   - Account balance inquiries
   - Account statements and history
   - Account closure procedures

2. **Financial Transactions**
   - Deposits and withdrawals
   - Fund transfers between accounts
   - Transaction history and details
   - Automated transaction validation

3. **User Management**
   - Customer registration and profile management
   - Role-based access control
   - Authentication and authorization
   - Password management

4. **Financial Reporting**
   - Account statements and summaries
   - Transaction reports
   - System-wide financial analytics
   - Custom report generation

5. **Administrative Functions**
   - User administration
   - System monitoring
   - Service health checks
   - Data management

The banking system represents a realistic implementation of a financial platform, with careful attention to security, data integrity, and user experience considerations that would be critical in a production banking environment.

## 3. System Architecture

### 3.1 Microservices Architecture

The banking system employs a microservices architecture, dividing functionality into five distinct services:

1. **API Gateway** - Entry point for all client requests, handling routing and authentication
2. **Auth Service** - Manages user authentication, authorization, and profile management
3. **Account Service** - Handles account creation, management, and balance operations
4. **Transaction Service** - Processes financial transactions (deposits, withdrawals, transfers)
5. **Reporting Service** - Generates financial reports and analytics

Each microservice operates independently with its own data storage, business logic, and API endpoints, communicating with other services through HTTP/REST APIs.

### 3.2 System Component Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│ API Gateway │────▶│ Auth Service│
│  (Browser)  │     │  (Port 5000)│     │ (Port 8001) │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
           ┌───────────────┼────────────────┐
           ▼               ▼                ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Account   │    │ Transaction │    │  Reporting  │
│   Service   │◀──▶│   Service   │◀──▶│   Service   │
│ (Port 8002) │    │ (Port 8003) │    │ (Port 8004) │
└─────────────┘    └─────────────┘    └─────────────┘
```

### 3.3 Technology Stack

#### Backend Technologies

- **Python 3.12**: Core programming language
- **Flask 2.x**: Web framework for all microservices
- **Flask-SQLAlchemy 3.x**: ORM for database interactions
- **Flask-Login 0.7.x**: User session management
- **PyJWT 2.x**: JSON Web Token implementation for authentication
- **SQLite**: Database engine for all microservices
- **Consul**: Used for service discovery and registration

#### API & Communication

- **RESTful APIs**: For inter-service communication
- **Requests 2.x**: HTTP library for service-to-service communication
- **JSON**: Data interchange format

#### Deployment & Operations

- **Python Multiprocessing**: Used in the service orchestration system
- **Process-based service orchestration**: Custom orchestration in `run_services.py`
- **Signal Handling**: For graceful shutdown of services

#### Frontend Technologies

- **HTML/CSS/JavaScript**: Core frontend technologies
- **Bootstrap 5**: CSS framework for responsive UI components
- **Flask Templates**: Server-side rendering of HTML
- **Client-side JavaScript**: For enhanced UI interactivity

#### Development Tools

- **pip**: Package management
- **uv**: Accelerated package installation
- **pyproject.toml**: Modern Python project metadata

## 4. Design Patterns

### 4.1 API Gateway Pattern

The system implements the API Gateway pattern through `main.py` and `api_gateway.py`. This component:

- Serves as the single entry point for all client requests
- Routes requests to appropriate microservices
- Handles authentication via JWT tokens
- Transforms data between clients and services
- Implements UI rendering through Flask templates

### 4.2 Service Layer Pattern

Each microservice implements a service layer pattern, separating:

- API endpoints (controllers)
- Business logic (services)
- Data access (repositories/storage)

This pattern enables clean separation of concerns and improves testability.

### 4.3 Repository Pattern

The system uses a repository pattern for data access:

- Each service has dedicated storage components (`auth_storage.py`, `account_storage.py`, etc.)
- Abstract data access logic from business logic
- Provides a consistent interface for data operations

### 4.4 Model-View-Controller (MVC) Pattern

The API Gateway implements an MVC architecture:

- **Models**: Defined in service-specific model files (e.g., `auth_models.py`)
- **Views**: HTML templates in the `/templates` directory
- **Controllers**: Request handlers in the API Gateway and service endpoints

### 4.5 Factory Pattern

The system uses factory methods to create model instances:

- `from_dict` static methods for model creation from data dictionaries
- Encapsulation of object creation logic
- Standardized instance creation

### 4.6 Service Registry Pattern

The system implements a service registry pattern:

- Services register themselves with Consul during startup
- Services deregister on shutdown
- Health checks ensure service availability
- Environment variables provide fallback service discovery

### 4.7 Decorator Pattern

Extensively used for cross-cutting concerns:

- Authentication and authorization checks
- Request validation
- Response formatting
- Error handling

## 5. Implementation Details

### 5.1 Core Services Overview

#### Auth Service (`auth_service/auth_service.py`)

- **Functionality**: User authentication, authorization, and profile management
- **Key Endpoints**:
  - `/api/auth/register` - New user registration
  - `/api/auth/login` - User authentication
  - `/api/auth/verify_token` - Token validation
  - `/api/auth/users` - User management (admin only)
  - `/api/auth/update_profile` - Profile updates
- **Data Models**: User
- **Storage**: SQLite database (`auth.db`)

#### Account Service (`account_service/account_service.py`)

- **Functionality**: Account creation, management, and balance operations
- **Key Endpoints**:
  - `/api/accounts/create` - Create new account
  - `/api/accounts/list` - List user accounts
  - `/api/accounts/details/:id` - Get account details
  - `/api/accounts/close/:id` - Close account
  - `/api/accounts/all` - List all accounts (admin only)
- **Data Models**: Account
- **Storage**: SQLite database (`account.db`)

#### Transaction Service (`transaction_service/transaction_service.py`)

- **Functionality**: Process financial transactions
- **Key Endpoints**:
  - `/api/transactions/deposit` - Create deposit
  - `/api/transactions/withdraw` - Create withdrawal
  - `/api/transactions/transfer` - Create transfer
  - `/api/transactions/list` - List user transactions
  - `/api/transactions/details/:id` - Get transaction details
- **Data Models**: Transaction
- **Storage**: SQLite database (`transaction.db`)

#### Reporting Service (`reporting_service/reporting_service.py`)

- **Functionality**: Generate financial reports and analytics
- **Key Endpoints**:
  - `/api/reports/account/:id` - Generate account report
  - `/api/reports/transactions` - Generate transaction report
  - `/api/reports/system` - Generate system report (admin only)
  - `/api/reports/list` - List user reports
- **Data Models**: Report
- **Storage**: SQLite database (`reporting.db`)

### 5.2 Data Models

Each service implements its own data models using SQLAlchemy:

#### Auth Service Models

```python
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='customer')
    created_at = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='active')
```

#### Account Service Models

```python
class Account(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), nullable=False)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    account_type = db.Column(db.String(50), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.now)
```

#### Transaction Service Models

```python
class Transaction(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), nullable=False)
    account_id = db.Column(db.String(36), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    status = db.Column(db.String(20), default='completed')
    timestamp = db.Column(db.DateTime, default=datetime.now)
```

#### Reporting Service Models

```python
class Report(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)
    parameters = db.Column(db.JSON)
    report_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.now)
```

### 5.3 Transaction Processing Flows

The transaction service implements several key transaction flows:

1. **Deposit Flow**
   - Validate user account access
   - Update account balance through Account Service
   - Create transaction record
   - Return success/failure response

2. **Withdrawal Flow**
   - Validate user account access
   - Check sufficient balance
   - Update account balance through Account Service
   - Create transaction record
   - Return success/failure response

3. **Transfer Flow**
   - Validate user access to source account
   - Check sufficient balance in source account
   - Update both source and destination accounts
   - Create transaction record
   - Return success/failure response

### 5.4 Reporting System

The Reporting Service generates various financial reports:

1. **Account Reports**
   - Transaction history
   - Balance trends
   - Income/expense analysis

2. **Transaction Reports**
   - Filtered by date range
   - Categorized by transaction type
   - Summary statistics

3. **System Reports (Admin)**
   - User statistics
   - Account type distribution
   - Total system balance
   - Transaction volume metrics

## 6. Frontend Implementation

### 6.1 Web Interface

The system provides a responsive web interface using:

- Bootstrap 5 for UI components and responsive layout
- Flask templates for server-side rendering
- JavaScript for client-side interactivity

### 6.2 Key UI Screens

1. **Dashboard** (`dashboard.html`)
   - Account summary
   - Recent transactions
   - Quick action buttons

2. **Account Management**
   - Account details (`account_details.html`)
   - Account listing (`accounts.html`)
   - Create account form (`create_account.html`)

3. **Transaction Operations**
   - Transfer funds (`transfer.html`)
   - Deposit (`deposit.html`)
   - Withdrawal (`withdraw.html`)

4. **Reporting**
   - Report listing (`reports.html`)
   - Report details (`report_details.html`)
   - Account-specific reports (`account_report.html`)

### 6.3 Template Structure

The application uses a hierarchical template structure:

- `base.html` - Main layout template with common structure
- `layout.html` - Alternative layout implementation
- Content-specific templates for individual views
- Reusable partial templates for common components

## 7. Service Communication

### 7.1 Inter-Service Communication

Services communicate with each other through HTTP/REST APIs:

1. **Request Forwarding**
   - API Gateway forwards client requests to appropriate services
   - Requests include JWT for authentication

2. **Service-to-Service Calls**
   - Direct HTTP calls between services using the Requests library
   - Authentication forwarded via JWT tokens

3. **Response Handling**
   - Services return JSON responses
   - API Gateway formats responses for client consumption

### 7.2 API Patterns

The system follows RESTful API conventions:

- Resource-based URL structure
- Appropriate HTTP verbs (GET, POST, PUT, DELETE)
- JSON request and response bodies
- Standard HTTP status codes
- Error response format standardization

### 7.3 Service Registry

The system uses a dual approach for service registry:

1. **Environment Variables**

   ```python
   # Service URLs with fallbacks
   AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://localhost:8001")
   ACCOUNT_SERVICE_URL = os.environ.get("ACCOUNT_SERVICE_URL", "http://localhost:8002")
   TRANSACTION_SERVICE_URL = os.environ.get("TRANSACTION_SERVICE_URL", "http://localhost:8003")
   REPORTING_SERVICE_URL = os.environ.get("REPORTING_SERVICE_URL", "http://localhost:8004")
   ```

2. **Consul Integration**

   ```python
   # Consul configuration
   CONSUL_HOST = os.environ.get("CONSUL_HOST", "localhost")
   CONSUL_PORT = int(os.environ.get("CONSUL_PORT", 8500))
   SERVICE_NAME = "auth-service"
   SERVICE_ID = f"{SERVICE_NAME}-{os.urandom(8).hex()}"
   
   # Register service with Consul
   def register_service():
       consul_client.agent.service.register(
           name=SERVICE_NAME,
           service_id=SERVICE_ID,
           address="localhost",
           port=SERVICE_PORT,
           check=consul.Check.http(
               f"http://localhost:{SERVICE_PORT}/api/health",
               interval="10s",
               timeout="5s",
           ),
       )
   ```

## 8. Error Handling

### 8.1 Error Handling Strategy

The system implements a multi-layered error handling approach:

1. **Service-level error handling**
   - Try-except blocks for catching exceptions
   - Appropriate HTTP status codes for different error conditions
   - Structured error responses with clear messages

2. **Gateway-level error handling**
   - Error response formatting for client consumption
   - Error page rendering for user-friendly error display
   - Logging of service failures

3. **Client-side error handling**
   - Form validation
   - Error message display
   - Toast notifications for operation status

### 8.2 Error Response Format

All error responses follow a standardized format:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "details": {}
}
```

### 8.3 HTTP Status Codes

The system uses appropriate HTTP status codes:

- 200: Successful operation
- 201: Resource created
- 400: Bad request
- 401: Unauthorized
- 403: Forbidden
- 404: Not found
- 500: Internal server error
- 503: Service unavailable

## 9. Security Implementation

### 9.1 Authentication & Authorization

The system implements comprehensive security measures:

1. **JWT-based Authentication**
   - JSON Web Tokens (PyJWT) for secure user sessions
   - Token-based authentication between microservices
   - Expiration and refresh token mechanism

2. **Role-based Access Control**
   - User roles (customer, admin) with different permissions
   - Decorators for role-specific endpoint protection
   - Fine-grained access control to resources

3. **Password Security**
   - Password hashing using Werkzeug's security functions
   - Salt-based password storage
   - Password complexity requirements

### 9.2 Service Security

1. **API Gateway Protection**
   - CSRF protection
   - Rate limiting
   - Request validation

2. **Microservice Isolation**
   - Each service runs on a separate port
   - JWT validation for service-to-service calls
   - Principle of least privilege

### 9.3 Data Security

1. **Sensitive Data Handling**
   - Password hashing
   - Account number masking
   - Transaction data protection

2. **Access Control**
   - User can only access their own data
   - Admin-specific endpoints protected
   - Explicit permission checks

## 10. Operations & Monitoring

### 10.1 Service Orchestration

The system includes a service orchestrator in `run_services.py` that:

- Starts all microservices in separate Python processes
- Configures environment variables for inter-service communication
- Monitors service health and restarts failed services
- Provides graceful shutdown using signal handling

```python
def run_services(args):
    """Run services based on arguments"""
    processes = []
    
    # Setup signal handler
    def signal_handler(sig, frame):
        print('Stopping all services...')
        for process in processes:
            if process.poll() is None:  # If process is still running
                process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Run Auth Service
        if not args.no_auth:
            auth_cmd = [sys.executable, "-m", "auth_service.auth_service"]
            auth_process = subprocess.Popen(auth_cmd)
            processes.append(auth_process)
            time.sleep(1)  # Give it a moment to start
        
        # Run other services...
    except KeyboardInterrupt:
        # Handle graceful shutdown
        pass
```

### 10.2 Health Monitoring

Each service exposes a `/api/health` endpoint that:

- Reports service status
- Checks dependencies
- Validates database connections

The API Gateway aggregates health status from all services through the `/health` endpoint:

```python
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    # Check all services
    auth_health, auth_status = make_service_request(AUTH_SERVICE_URL, '/api/health')
    account_health, account_status = make_service_request(ACCOUNT_SERVICE_URL, '/api/health')
    transaction_health, transaction_status = make_service_request(TRANSACTION_SERVICE_URL, '/api/health')
    reporting_health, reporting_status = make_service_request(REPORTING_SERVICE_URL, '/api/health')

    all_healthy = all(status == 200 for status in [auth_status, account_status, transaction_status, reporting_status])

    return jsonify({
        'status': 'healthy' if all_healthy else 'degraded',
        'services': {
            'api-gateway': 'healthy',
            'auth-service': 'healthy' if auth_status == 200 else 'unhealthy',
            'account-service': 'healthy' if account_status == 200 else 'unhealthy',
            'transaction-service': 'healthy' if transaction_status == 200 else 'unhealthy',
            'reporting-service': 'healthy' if reporting_status == 200 else 'unhealthy'
        }
    }), 200 if all_healthy else 503
```

### 10.3 Logging

The system implements comprehensive logging:

- Standard Python logging module
- Service-specific loggers
- Error logging with stack traces
- Request/response logging

Example logging configuration:

```python
# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Later in code
logger.error(f"Service request failed: {str(e)}")
```

## 11. Key Files and Their Roles

### 11.1 Core System Files

| File | Description |
|------|-------------|
| `main.py` | API Gateway implementation, handling client requests and service communication |
| `api_gateway.py` | Support functions for the API Gateway |
| `run_services.py` | Service orchestration, starting and monitoring all microservices |
| `models.py` | Legacy core data models (replaced by service-specific models) |
| `storage.py` | Base storage functionality for file-based operations |
| `utils.py` | Utility functions for common operations |
| `requirements.txt` | Python dependencies list |
| `pyproject.toml` | Modern Python project metadata and build system configuration |
| `uv.lock` | Dependency lock file for the uv package installer |

### 11.2 Service Implementations

| Service | Key Files |
|---------|-----------|
| Auth Service | `auth_service/auth_service.py`, `auth_service/auth_models.py`, `auth_service/auth_storage.py`, `auth_service/auth.db` |
| Account Service | `account_service/account_service.py`, `account_service/account_models.py`, `account_service/account_storage.py`, `account_service/account.db` |
| Transaction Service | `transaction_service/transaction_service.py`, `transaction_service/transaction_models.py`, `transaction_service/transaction_storage.py`, `transaction_service/transaction.db` |
| Reporting Service | `reporting_service/reporting_service.py`, `reporting_service/reporting_models.py`, `reporting_service/reporting_storage.py`, `reporting_service/reporting.db` |

### 11.3 Frontend Templates

| Category | Key Files |
|----------|-----------|
| Base Templates | `templates/base.html`, `templates/layout.html` |
| Account Management | `templates/accounts.html`, `templates/account_details.html`, `templates/create_account.html`, `templates/account_close.html`, `templates/account_view.html`, `templates/account_create.html` |
| Transaction Management | `templates/transactions.html`, `templates/transaction_details.html`, `templates/transaction_detail.html`, `templates/transfer.html`, `templates/deposit.html`, `templates/withdraw.html` |
| User Management | `templates/login.html`, `templates/register.html`, `templates/profile.html`, `templates/settings.html` |
| Reporting | `templates/reports.html`, `templates/report_details.html`, `templates/account_report.html`, `templates/transaction_report.html` |
| General | `templates/dashboard.html`, `templates/index.html`, `templates/error.html`, `templates/admin.html` |

## 12. Code Structure and Organization

### 12.1 Project Structure

The project follows a service-oriented structure:

```
├── account_service/           # Account microservice
│   ├── account_models.py      # Account-specific models
│   ├── account_service.py     # Account API endpoints
│   ├── account_storage.py     # Account data storage
│   └── account.db             # SQLite database for accounts
├── auth_service/              # Authentication microservice
│   ├── auth_models.py         # Auth-specific models
│   ├── auth_service.py        # Auth API endpoints
│   ├── auth_storage.py        # User data storage
│   └── auth.db                # SQLite database for users
├── reporting_service/         # Reporting microservice
│   ├── reporting_models.py    # Report-specific models
│   ├── reporting_service.py   # Reporting API endpoints
│   ├── reporting_storage.py   # Report data storage
│   └── reporting.db           # SQLite database for reports
├── static/                    # Static assets
│   ├── css/                   # CSS stylesheets
│   │   └── custom.css         # Custom styling
│   └── js/                    # JavaScript files
│       ├── accounts.js        # Account-specific functionality
│       ├── main.js            # Core JavaScript functionality
│       └── transactions.js    # Transaction-specific functionality
├── templates/                 # HTML templates
│   ├── base.html             # Base template with common structure
│   ├── layout.html           # Alternative layout implementation
│   ├── account_*.html        # Account management templates
│   ├── transaction_*.html    # Transaction management templates
│   └── [other templates]     # Various other templates
├── transaction_service/       # Transaction microservice
│   ├── transaction_models.py  # Transaction-specific models
│   ├── transaction_service.py # Transaction API endpoints
│   ├── transaction_storage.py # Transaction data storage
│   └── transaction.db         # SQLite database for transactions
├── data/                      # Additional data storage directory
├── api_gateway.py             # API Gateway helper functions
├── main.py                    # API Gateway implementation
├── models.py                  # Legacy core data models
├── pyproject.toml             # Python project metadata
├── requirements.txt           # Python dependencies
├── run_services.py            # Service orchestration
├── storage.py                 # Base storage functionality
├── utils.py                   # Utility functions
├── README.md                  # Project documentation
├── Banking_System_Technical_Report.md  # This technical report
├── LICENSE                    # Project license
└── uv.lock                    # Dependency lock file
```

### 12.2 Code Organization Principles

The codebase follows several key principles:

1. **Separation of Concerns**
   - Each service handles specific business domain
   - Clear separation between data models, business logic, and API endpoints

2. **Modular Design**
   - Independent microservices
   - Self-contained functionality
   - Minimal dependencies between services

3. **Consistent Patterns**
   - Standard API response format
   - Similar code structure across services
   - Common utility functions

### 12.3 Common Design Patterns in Code

Several design patterns are used consistently throughout the codebase:

1. **Decorator Pattern**
   - Used for authentication and authorization checks:

   ```python
   @app.route('/admin')
   @login_required
   def admin_dashboard():
       # Admin dashboard implementation
   ```

2. **Factory Methods**
   - Used for model creation from dictionaries:

   ```python
   @classmethod
   def from_dict(cls, data):
       """Create User object from dictionary"""
       user = cls(
           username=data.get('username'),
           email=data.get('email'),
           password_hash=data.get('password_hash'),
           role=data.get('role', 'customer'),
           id=data.get('id')
       )
       return user
   ```

3. **Service Helper Functions**
   - Used for common service operations:

   ```python
   def make_service_request(service_url, endpoint, method='GET', data=None, params=None, headers=None):
       """Helper function to make requests to microservices"""
       url = f"{service_url}{endpoint}"
       # Implementation details
   ```

## 13. API Endpoints

### 13.1 Auth Service API

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/auth/register` | POST | Register new user | Public |
| `/api/auth/login` | POST | Authenticate user | Public |
| `/api/auth/verify_token` | GET | Verify JWT token | Private |
| `/api/auth/users` | GET | List all users | Admin |
| `/api/auth/verify_admin` | GET | Verify admin role | Private |
| `/api/health` | GET | Service health check | Public |

### 13.2 Account Service API

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/accounts/create` | POST | Create new account | Private |
| `/api/accounts/list` | GET | List user accounts | Private |
| `/api/accounts/details/<account_id>` | GET | Get account details | Private |
| `/api/accounts/close/<account_id>` | DELETE | Close account | Private |
| `/api/accounts/all` | GET | List all accounts | Admin |
| `/api/health` | GET | Service health check | Public |

### 13.3 Transaction Service API

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/transactions/deposit` | POST | Create deposit | Private |
| `/api/transactions/withdraw` | POST | Create withdrawal | Private |
| `/api/transactions/transfer` | POST | Create transfer | Private |
| `/api/transactions/list` | GET | List user transactions | Private |
| `/api/transactions/recent` | GET | Get recent transactions | Private |
| `/api/transactions/account/<account_id>` | GET | Get account transactions | Private |
| `/api/health` | GET | Service health check | Public |

### 13.4 Reporting Service API

| Endpoint | Method | Description | Access |
|----------|--------|-------------|--------|
| `/api/reports/account/<account_id>` | GET | Generate account report | Private |
| `/api/reports/transactions` | GET | Generate transaction report | Private |
| `/api/reports/system` | GET | Generate system report | Admin |
| `/api/reports/list` | GET | List user reports | Private |
| `/api/health` | GET | Service health check | Public |

## 14. Development Environment

### 14.1 Local Development Setup

The banking system is designed to be developed and run locally with the following environment specifications:

1. **Development Environment**
   - Python 3.12+ runtime
   - pip package manager
   - uv accelerated package installer
   - VSCode or any modern code editor
   - Git for version control

2. **Service Orchestration**
   - Custom service orchestrator (`run_services.py`)
   - Environment variable configuration for inter-service communication
   - Process-based service management with signal handling

3. **Database Configuration**
   - SQLite databases for each service
   - Auto-creation of database schema via SQLAlchemy
   - File-based storage for development simplicity

### 14.2 Development Workflow

The development workflow follows these steps:

1. **Environment Setup**

   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Running the Application**

   ```bash
   # Set environment variables
   export AUTH_SERVICE_URL="http://localhost:8001"
   export ACCOUNT_SERVICE_URL="http://localhost:8002"
   export TRANSACTION_SERVICE_URL="http://localhost:8003"
   export REPORTING_SERVICE_URL="http://localhost:8004"
   export SESSION_SECRET="your_secret_key_here"

   # Run all services
   python run_services.py
   ```

3. **Testing**
   - Manual testing through the web interface
   - API testing using tools like Postman or curl
   - Individual service testing by running services separately

## 15. SQLite Database Implementation

### 15.1 Database Schema

Each service has its own SQLite database:

1. **Auth Service** (`auth.db`)
   - User table
   - Session information
   - Authentication logs

2. **Account Service** (`account.db`)
   - Account records
   - Account types
   - Balance history

3. **Transaction Service** (`transaction.db`)
   - Transaction records
   - Transaction types
   - Transfer records

4. **Reporting Service** (`reporting.db`)
   - Report metadata
   - Report parameters
   - Generated report data

### 15.2 SQLAlchemy Integration

The services use SQLAlchemy for database operations:

```python
# Initialize Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///auth.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db = SQLAlchemy(app)

# Create tables
with app.app_context():
    db.create_all()
```

### 15.3 Database Operations

Example of database operations with SQLAlchemy:

```python
# Create a new user
new_user = User(
    id=str(uuid.uuid4()),
    username=data['username'],
    email=data['email'],
    password_hash=password_hash,
    role='customer'
)
db.session.add(new_user)
db.session.commit()

# Query users
users = User.query.all()
```

## 16. Authentication and Security

### 16.1 JWT Implementation

The system uses JSON Web Tokens (JWT) for authentication:

1. **Token Generation**

   ```python
   def generate_token(user_id, username, role):
       """Generate a JWT token for a user"""
       payload = {
           'exp': datetime.now(timezone.utc) + timedelta(hours=1),
           'iat': datetime.now(timezone.utc),
           'sub': user_id,
           'username': username,
           'role': role
       }
       return jwt.encode(
           payload,
           app.config.get('JWT_SECRET_KEY'),
           algorithm='HS256'
       )
   ```

2. **Token Verification**

   ```python
   def token_required(f):
       """Decorator for endpoints that require a valid JWT token"""
       @wraps(f)
       def decorated(*args, **kwargs):
           token = None
           auth_header = request.headers.get('Authorization')
           
           if auth_header and auth_header.startswith('Bearer '):
               token = auth_header.split(' ')[1]
           
           if not token:
               return jsonify({'message': 'Token is missing'}), 401
           
           try:
               payload = jwt.decode(
                   token, 
                   app.config.get('JWT_SECRET_KEY'),
                   algorithms=['HS256']
               )
               current_user = {
                   'user_id': payload['sub'],
                   'username': payload['username'],
                   'role': payload['role']
               }
           except jwt.ExpiredSignatureError:
               return jsonify({'message': 'Token has expired'}), 401
           except jwt.InvalidTokenError:
               return jsonify({'message': 'Invalid token'}), 401
               
           return f(current_user, *args, **kwargs)
       return decorated
   ```

### 16.2 Password Handling

User passwords are securely stored:

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Hash password during user creation
password_hash = generate_password_hash(data['password'])

# Verify password during login
if not check_password_hash(user.password_hash, password):
    return jsonify({'message': 'Invalid credentials'}), 401
```

## 17. Future Enhancements

Several potential enhancements could further improve the system:

1. **Containerization & Orchestration**
   - Docker containers for each service
   - Docker Compose for local development
   - Kubernetes for production deployment

2. **Advanced Message Queue Integration**
   - RabbitMQ or Kafka for event-driven architecture
   - Asynchronous processing for better scalability
   - Event sourcing for transaction integrity

3. **Enhanced Security**
   - Multi-factor authentication
   - Rate limiting and brute force protection
   - Advanced encryption for sensitive data
   - OAuth 2.0 integration

4. **Performance Optimizations**
   - Caching with Redis
   - Database query optimization
   - Connection pooling
   - Horizontal scaling support

5. **Frontend Modernization**
   - Single-page application (SPA) with React or Vue.js
   - Progressive Web App (PWA) capabilities
   - Improved mobile responsiveness

6. **Advanced Monitoring**
   - Prometheus and Grafana integration
   - Distributed tracing with Jaeger
   - Enhanced logging with ELK stack

## 18. Conclusion

This banking system implementation demonstrates a practical microservices architecture focused on modularity, scalability, and maintainability. The system provides core banking functionality through a set of specialized services that work together to deliver a complete banking platform.

Key strengths of the implementation include:

- Clean separation of concerns through microservices
- SQLite databases for simplified development
- Consistent design patterns across components
- Robust authentication and authorization
- Comprehensive error handling
- Flexible reporting capabilities

The system is designed to be extensible, allowing for future enhancements and feature additions while maintaining the overall architectural integrity. Its process-based orchestration provides a straightforward way to run and manage the services for development purposes, while the architecture can be evolved for more robust deployment options in production environments.

This technical report captures the current state of the system as of April 18, 2025, providing a comprehensive reference for understanding its architecture, design patterns, and implementation details.
