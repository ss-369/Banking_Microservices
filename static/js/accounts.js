/**
 * Accounts JavaScript for banking microservices application
 * Handles account-related functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize account creation form
    const createAccountForm = document.getElementById('create-account-form');
    if (createAccountForm) {
        createAccountForm.addEventListener('submit', function(e) {
            e.preventDefault();
            createAccount();
        });
    }

    // Initialize close account form
    const closeAccountForm = document.getElementById('close-account-form');
    if (closeAccountForm) {
        closeAccountForm.addEventListener('submit', function(e) {
            e.preventDefault();
            closeAccount();
        });
    }

    // Initialize account type selector (for create account form)
    const accountTypeSelect = document.getElementById('account_type');
    if (accountTypeSelect) {
        accountTypeSelect.addEventListener('change', function() {
            updateAccountTypeInfo(this.value);
        });
        // Initialize with current selection
        if (accountTypeSelect.value) {
            updateAccountTypeInfo(accountTypeSelect.value);
        }
    }
});

// Function to create a new account
function createAccount() {
    const accountType = document.getElementById('account_type').value;
    const initialDeposit = parseFloat(document.getElementById('initial_deposit').value);

    if (!accountType) {
        showToast('Please select an account type', 'warning');
        return;
    }

    const validAccountTypes = ['checking', 'savings', 'fixed_deposit'];
    if (!validAccountTypes.includes(accountType)) {
        showToast('Please select a valid account type', 'warning');
        return;
    }

    if (isNaN(initialDeposit) || initialDeposit < 0) {
        showToast('Initial deposit must be a non-negative number', 'warning');
        return;
    }

    const data = {
        account_type: accountType,
        initial_deposit: initialDeposit
    };

    showLoading();

    fetch('/accounts/create', {
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
                throw new Error(data.message || 'Failed to create account');
            });
        }
        return response.json();
    })
    .then(data => {
        hideLoading();
        showToast('Account created successfully!', 'success');
        
        // Redirect to accounts page after a short delay
        setTimeout(() => {
            window.location.href = '/accounts';
        }, 1500);
    })
    .catch(error => {
        hideLoading();
        showToast(error.message, 'danger');
    });
}

// Function to close an account
function closeAccount() {
    const accountId = document.getElementById('account_id').value;
    const confirmation = document.getElementById('confirmation').value;

    if (confirmation !== 'CLOSE') {
        showToast('Please type CLOSE to confirm', 'warning');
        return;
    }

    showLoading();

    // Use form submission to handle the close request
    document.getElementById('close-account-form').submit();
}

// Function to update account type information based on selection
function updateAccountTypeInfo(accountType) {
    const infoContainer = document.getElementById('account-type-info');
    if (!infoContainer) return;

    let infoHtml = '';
    switch(accountType) {
        case 'checking':
            infoHtml = `
                <div class="alert alert-info">
                    <h5>Checking Account</h5>
                    <p>A standard checking account with no minimum balance requirement.</p>
                    <ul>
                        <li>No monthly maintenance fee</li>
                        <li>Unlimited transactions</li>
                        <li>Online banking and mobile access</li>
                    </ul>
                </div>
            `;
            break;
        case 'savings':
            infoHtml = `
                <div class="alert alert-info">
                    <h5>Savings Account</h5>
                    <p>A basic savings account that earns interest on your deposits.</p>
                    <ul>
                        <li>Competitive interest rates</li>
                        <li>No minimum balance requirement</li>
                        <li>Limited to 6 withdrawals per month</li>
                    </ul>
                </div>
            `;
            break;
        case 'fixed_deposit':
            infoHtml = `
                <div class="alert alert-info">
                    <h5>Fixed Deposit Account</h5>
                    <p>Lock in your money for a fixed period and earn higher interest.</p>
                    <ul>
                        <li>Higher interest rates than regular savings</li>
                        <li>Terms range from 3 months to 5 years</li>
                        <li>Early withdrawal penalties may apply</li>
                    </ul>
                </div>
            `;
            break;
        default:
            infoHtml = '<div class="alert alert-secondary">Please select an account type to see details.</div>';
    }

    infoContainer.innerHTML = infoHtml;
}

// Function to load account details
function loadAccountDetails(accountId) {
    if (!accountId) return;

    showLoading();

    fetch(`/accounts/${accountId}`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to load account details');
        }
        return response.json();
    })
    .then(data => {
        hideLoading();
        updateAccountDetailsUI(data);
    })
    .catch(error => {
        hideLoading();
        showToast(error.message, 'danger');
    });
}

// Function to update account details UI
function updateAccountDetailsUI(accountData) {
    if (!accountData) return;

    // Update account details in the UI
    const accountNumberElement = document.getElementById('account-number');
    const accountTypeElement = document.getElementById('account-type');
    const accountBalanceElement = document.getElementById('account-balance');
    const accountStatusElement = document.getElementById('account-status');
    const accountCreatedElement = document.getElementById('account-created');

    if (accountNumberElement) accountNumberElement.textContent = accountData.account_number;
    if (accountTypeElement) accountTypeElement.textContent = formatAccountType(accountData.account_type);
    if (accountBalanceElement) accountBalanceElement.textContent = formatCurrency(accountData.balance);
    if (accountStatusElement) accountStatusElement.textContent = accountData.status;
    if (accountCreatedElement) accountCreatedElement.textContent = formatDate(accountData.created_at);
}

// Format account type for display
function formatAccountType(type) {
    if (!type) return '';
    
    // Convert snake_case to Title Case
    return type
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ');
}
