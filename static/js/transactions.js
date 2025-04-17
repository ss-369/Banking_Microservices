/**
 * Transactions JavaScript for banking microservices application
 * Handles transaction-related functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize transfer form
    const transferForm = document.getElementById('transfer-form');
    if (transferForm) {
        transferForm.addEventListener('submit', function(e) {
            e.preventDefault();
            processTransfer();
        });
    }

    // Initialize account selector change events
    const fromAccountSelect = document.getElementById('from_account');
    if (fromAccountSelect) {
        fromAccountSelect.addEventListener('change', function() {
            updateFromAccountDetails(this.value);
        });
        // Initialize with current selection
        if (fromAccountSelect.value) {
            updateFromAccountDetails(fromAccountSelect.value);
        }
    }

    // Initialize transaction date filter form
    const transactionDateFilterForm = document.getElementById('transaction-date-filter-form');
    if (transactionDateFilterForm) {
        transactionDateFilterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            filterTransactionsByDate();
        });
    }
});

// Process a transfer between accounts
function processTransfer() {
    const fromAccountId = document.getElementById('from_account').value;
    const toAccountId = document.getElementById('to_account').value;
    const amount = parseFloat(document.getElementById('amount').value);
    const transferType = document.getElementById('transfer_type').value;
    const description = document.getElementById('description').value;

    // Validate fields
    if (!fromAccountId || !toAccountId) {
        showToast('Please select both source and destination accounts', 'warning');
        return;
    }

    if (fromAccountId === toAccountId) {
        showToast('Source and destination accounts cannot be the same', 'warning');
        return;
    }

    if (isNaN(amount) || amount <= 0) {
        showToast('Please enter a valid positive amount', 'warning');
        return;
    }

    const data = {
        from_account_id: fromAccountId,
        to_account_id: toAccountId,
        amount: amount,
        transfer_type: transferType,
        description: description
    };

    showLoading();

    fetch('/transfer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.message || 'Failed to process transfer');
            });
        }
        return response.json();
    })
    .then(data => {
        hideLoading();
        showToast('Transfer completed successfully!', 'success');
        
        // Redirect to transactions page after a short delay
        setTimeout(() => {
            window.location.href = '/transactions';
        }, 1500);
    })
    .catch(error => {
        hideLoading();
        showToast(error.message, 'danger');
    });
}

// Update from account details when an account is selected
function updateFromAccountDetails(accountId) {
    if (!accountId) return;

    // Find the selected account's balance
    const accountSelectElement = document.getElementById('from_account');
    if (!accountSelectElement) return;

    const selectedOption = accountSelectElement.options[accountSelectElement.selectedIndex];
    if (!selectedOption) return;

    const accountBalance = selectedOption.getAttribute('data-balance');
    const balanceDisplay = document.getElementById('from-account-balance');
    
    if (balanceDisplay && accountBalance) {
        balanceDisplay.textContent = formatCurrency(parseFloat(accountBalance));
        balanceDisplay.parentElement.classList.remove('d-none');
    }
}

// Filter transactions by date range
function filterTransactionsByDate() {
    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;

    if (!startDate || !endDate) {
        showToast('Please select both start and end dates', 'warning');
        return;
    }

    // Redirect to the transactions page with date filter parameters
    window.location.href = `/transactions?start_date=${startDate}&end_date=${endDate}`;
}

// Load transaction details
function loadTransactionDetails(transactionId) {
    if (!transactionId) return;

    showLoading();

    fetch(`/transactions/${transactionId}`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to load transaction details');
        }
        return response.json();
    })
    .then(data => {
        hideLoading();
        updateTransactionDetailsUI(data);
    })
    .catch(error => {
        hideLoading();
        showToast(error.message, 'danger');
    });
}

// Update transaction details UI
function updateTransactionDetailsUI(transactionData) {
    if (!transactionData) return;

    // Update transaction details in the UI
    const transactionIdElement = document.getElementById('transaction-id');
    const transactionTypeElement = document.getElementById('transaction-type');
    const transactionAmountElement = document.getElementById('transaction-amount');
    const transactionDateElement = document.getElementById('transaction-date');
    const transactionStatusElement = document.getElementById('transaction-status');
    const transactionDescriptionElement = document.getElementById('transaction-description');

    if (transactionIdElement) transactionIdElement.textContent = transactionData.id;
    if (transactionTypeElement) transactionTypeElement.textContent = formatTransactionType(transactionData.transaction_type);
    if (transactionAmountElement) {
        transactionAmountElement.textContent = formatCurrency(transactionData.amount);
        transactionAmountElement.classList.add(getTransactionClass(transactionData.transaction_type));
    }
    if (transactionDateElement) transactionDateElement.textContent = formatDate(transactionData.timestamp);
    if (transactionStatusElement) transactionStatusElement.textContent = transactionData.status;
    if (transactionDescriptionElement) transactionDescriptionElement.textContent = transactionData.description || getTransactionDescription(transactionData);
}

// Format transaction type for display
function formatTransactionType(type) {
    if (!type) return '';
    
    // Convert snake_case to Title Case
    return type
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ');
}
