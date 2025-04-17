/**
 * Main JavaScript for banking microservices application
 * Contains shared utilities and initialization code
 */

// Show loading spinner
function showLoading() {
    const spinner = document.createElement('div');
    spinner.className = 'spinner-container';
    spinner.innerHTML = `
        <div class="spinner-border text-light" role="status" style="width: 3rem; height: 3rem;">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    document.body.appendChild(spinner);
}

// Hide loading spinner
function hideLoading() {
    const spinner = document.querySelector('.spinner-container');
    if (spinner) {
        spinner.remove();
    }
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

// Format account number (show only last 4 digits)
function formatAccountNumber(accountNumber) {
    if (!accountNumber) return '';
    return `****${accountNumber.slice(-4)}`;
}

// Show toast notification
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.setAttribute('id', toastId);
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Initialize and show toast
    const toastInstance = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 5000
    });
    
    toastInstance.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Handle AJAX errors
function handleAjaxError(error) {
    console.error('AJAX Error:', error);
    
    if (error.status === 401) {
        showToast('Your session has expired. Please log in again.', 'danger');
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
    } else if (error.responseJSON && error.responseJSON.message) {
        showToast(error.responseJSON.message, 'danger');
    } else {
        showToast('An error occurred. Please try again later.', 'danger');
    }
}

// Get transaction CSS class based on type
function getTransactionClass(type) {
    switch(type) {
        case 'deposit':
            return 'deposit';
        case 'withdrawal':
            return 'withdrawal';
        case 'transfer':
            return 'transfer';
        default:
            return '';
    }
}

// Get friendly description for transaction
function getTransactionDescription(transaction) {
    if (transaction.description) {
        return transaction.description;
    }
    
    if (transaction.transaction_type === 'deposit') {
        return 'Deposit';
    } else if (transaction.transaction_type === 'withdrawal') {
        return 'Withdrawal';
    } else if (transaction.transaction_type === 'transfer') {
        return `${transaction.transfer_type.toUpperCase()} Transfer`;
    }
    
    return 'Transaction';
}

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});
