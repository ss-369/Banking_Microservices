import os
import subprocess
import time
import signal
import sys

# Define the services to start
services = [
    {
        "name": "Auth Service",
        "command": ["python", "-m", "auth_service.auth_service"],
        "process": None
    },
    {
        "name": "Account Service",
        "command": ["python", "-m", "account_service.account_service"],
        "process": None
    },
    {
        "name": "Transaction Service",
        "command": ["python", "-m", "transaction_service.transaction_service"],
        "process": None
    },
    {
        "name": "Reporting Service",
        "command": ["python", "-m", "reporting_service.reporting_service"],
        "process": None
    },
    {
        "name": "API Gateway",
        "command": ["gunicorn", "--bind", "0.0.0.0:5000", "--reuse-port", "--reload", "main:app"],
        "process": None
    }
]

# Set environment variables for service communication
os.environ["AUTH_SERVICE_URL"] = "http://localhost:8001"
os.environ["ACCOUNT_SERVICE_URL"] = "http://localhost:8002"
os.environ["TRANSACTION_SERVICE_URL"] = "http://localhost:8003"
os.environ["REPORTING_SERVICE_URL"] = "http://localhost:8004"

# Handle clean shutdown
def signal_handler(sig, frame):
    print("\nShutting down all services...")
    for service in services:
        if service["process"] and service["process"].poll() is None:
            print(f"Stopping {service['name']}...")
            service["process"].terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    
    # Start all services
    try:
        for service in services:
            print(f"Starting {service['name']}...")
            # Use subprocess.STDOUT to merge stderr into stdout for easier monitoring
            service["process"] = subprocess.Popen(
                service["command"],
                stdout=None,  # Display directly to console
                stderr=None,  # Display directly to console
                text=True
            )
            # Give a moment for the service to start
            time.sleep(1)
            
            # Check if process is still running
            if service["process"].poll() is not None:
                stdout, stderr = service["process"].communicate()
                print(f"Failed to start {service['name']}!")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                signal_handler(None, None)
            else:
                print(f"{service['name']} started successfully!")
        
        print("\nAll services are running. Press Ctrl+C to stop all services.")
        
        # Monitor processes and keep them running
        while True:
            for service in services:
                if service["process"].poll() is not None:
                    stdout, stderr = service["process"].communicate()
                    print(f"{service['name']} has stopped unexpectedly!")
                    print(f"STDOUT: {stdout}")
                    print(f"STDERR: {stderr}")
                    
                    # Restart the service
                    print(f"Restarting {service['name']}...")
                    service["process"] = subprocess.Popen(
                        service["command"],
                        stdout=None,  # Display directly to console
                        stderr=None,  # Display directly to console
                        text=True
                    )
            
            time.sleep(5)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        signal_handler(None, None)

if __name__ == "__main__":
    main()