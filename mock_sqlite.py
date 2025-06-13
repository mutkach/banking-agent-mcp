import sqlite3
from datetime import datetime, date
import random

# Connect to SQLite database (creates file if it doesn't exist)
conn = sqlite3.connect('bank_transactions.db')
cursor = conn.cursor()

# Create the transactions table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_number TEXT NOT NULL,
        client_name TEXT NOT NULL,
        transaction_date DATE NOT NULL,
        transaction_time TIME NOT NULL,
        transaction_type TEXT NOT NULL CHECK (transaction_type IN ('DEPOSIT', 'WITHDRAWAL', 'TRANSFER_IN', 'TRANSFER_OUT', 'FEE', 'INTEREST', 'CARD')),
        amount DECIMAL(10, 2) NOT NULL,
        balance_after DECIMAL(10, 2),
        description TEXT,
        reference_number TEXT,
        counterparty_account TEXT,
        counterparty_name TEXT,
        channel TEXT CHECK (channel IN ('ATM', 'ONLINE', 'MOBILE', 'BRANCH', 'CARD', 'AUTO')),
        location TEXT,
        status TEXT NOT NULL DEFAULT 'COMPLETED' CHECK (status IN ('COMPLETED', 'FAILED', 'PENDING', 'CANCELLED')),
        failure_reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        client_id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT NOT NULL,
        account_number TEXT NOT NULL,
        interest_rate DECIMAL(10, 2) NOT NULL,
        daily_limit DECIMAL(10, 2) NOT NULL DEFAULT 500,
        normal_fee DECIMAL(10, 2),
        tariff_type TEXT CHECK (tariff_type IN ('NORMAL', 'BENEFIT', 'VIP')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create index for faster queries
cursor.execute('CREATE INDEX IF NOT EXISTS idx_transaction_date ON transactions(transaction_date)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_account_number ON transactions(account_number)')

# Sample data for a single client
account_num = "ACC-123456789"
account_name = "Nikita Savelev"
sample_transactions = [
    # Successful transactions
    (account_num, '2024-06-01', '09:15:00', 'DEPOSIT', 2500.00, 2500.00, 'Initial deposit', 'DEP-001', None, None, 'BRANCH', 'Main Branch', 'COMPLETED', None),
    (account_num, '2024-06-02', '14:30:00', 'WITHDRAWAL', -50.00, 2450.00, 'ATM withdrawal', 'WTH-001', None, None, 'ATM', 'Downtown ATM', 'COMPLETED', None),
    (account_num, '2024-06-03', '11:45:00', 'TRANSFER_IN', 300.00, 2750.00, 'Transfer from savings', 'TRF-001', 'SAV-123456789', 'Own Account', 'ONLINE', None, 'COMPLETED', None),
    
    # Failed transaction - insufficient funds
    (account_num, '2024-06-04', '18:22:00', 'WITHDRAWAL', -3000.00, None, 'ATM withdrawal attempt', 'WTH-002', None, None, 'ATM', 'Mall ATM', 'FAILED', 'INSUFFICIENT_FUNDS'),
    
    (account_num, '2024-06-05', '16:20:00', 'CARD', -25.50, 2724.50, 'Coffee shop purchase', 'CRD-001', 'MERCH-789', 'Starbucks #1234', 'CARD', 'New York, NY', 'COMPLETED', None),
    
    # Failed transaction - daily limit exceeded
    (account_num, '2024-06-06', '20:15:00', 'WITHDRAWAL', -500.00, None, 'ATM withdrawal attempt', 'WTH-003', None, None, 'ATM', 'Airport ATM', 'FAILED', 'DAILY_LIMIT_EXCEEDED'),
    
    (account_num, '2024-06-07', '10:00:00', 'TRANSFER_OUT', -1000.00, 1724.50, 'Rent payment', 'TRF-002', 'EXT-987654321', 'ABC Property Management', 'ONLINE', None, 'COMPLETED', None),
    
    # Failed transaction - network timeout
    (account_num, '2024-06-08', '13:45:00', 'TRANSFER_OUT', -200.00, None, 'Utility bill payment', 'TRF-003', 'EXT-456789123', 'Electric Company', 'MOBILE', None, 'FAILED', 'NETWORK_TIMEOUT'),
    
    # Failed transaction - invalid account
    (account_num, '2024-06-09', '11:30:00', 'TRANSFER_OUT', -150.00, None, 'Transfer to friend', 'TRF-004', 'EXT-999999999', 'John Smith', 'ONLINE', None, 'FAILED', 'INVALID_RECIPIENT_ACCOUNT'),
    
    (account_num, '2024-06-10', '08:30:00', 'FEE', -5.00, 1719.50, 'Monthly maintenance fee', 'FEE-001', None, None, 'AUTO', None, 'COMPLETED', None),
    
    # Failed transaction - card declined
    (account_num, '2024-06-12', '19:45:00', 'CARD', -89.99, None, 'Online purchase attempt', 'CRD-002', 'MERCH-456', 'Amazon.com', 'CARD', 'Online', 'FAILED', 'CARD_DECLINED_FRAUD_PROTECTION'),
    
    # Failed transaction - system maintenance
    (account_num, '2024-06-13', '02:15:00', 'TRANSFER_OUT', -75.00, None, 'Bill payment attempt', 'TRF-005', 'EXT-111222333', 'Phone Company', 'AUTO', None, 'FAILED', 'SYSTEM_MAINTENANCE'),
    
    (account_num, '2024-06-15', '12:00:00', 'INTEREST', 2.85, 1722.35, 'Monthly interest credit', 'INT-001', None, None, 'AUTO', None, 'COMPLETED', None),
    
    # Cancelled transaction - user cancelled
    (account_num, '2024-06-16', '14:20:00', 'TRANSFER_OUT', -300.00, None, 'Transfer cancelled by user', 'TRF-006', 'EXT-555666777', 'Investment Account', 'ONLINE', None, 'CANCELLED', 'USER_CANCELLED'),
]


# Insert sample data
cursor.executemany('''
    INSERT INTO transactions 
    (account_number, transaction_date, transaction_time, transaction_type, amount, balance_after, 
     description, reference_number, counterparty_account, counterparty_name, channel, location, status, failure_reason)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', sample_transactions)


sample_client = [
    ('Nikita Savelev', account_num, 0.01, 500, 5, 'NORMAL'),
    ('Kaiser X', "ACC-987654321", 0.05, 1500, 5, 'BENEFIT')
]
cursor.executemany('''
    INSERT INTO clients
               (client_name, account_number, interest_rate, daily_limit, normal_fee, tariff_type)
    VALUES (?, ?, ?, ?, ?, ?)
''', sample_client
)

# Commit changes
conn.commit()

# Query examples
print("=== Bank Transaction Database Schema Created ===\n")

# Show table structure
cursor.execute("PRAGMA table_info(transactions)")
columns = cursor.fetchall()
print("Table Structure:")
for col in columns:
    print(f"  {col[1]} - {col[2]} {'(Primary Key)' if col[5] else ''}")

print(f"\n=== Sample Transactions for Account {account_num} ===")
cursor.execute("""
    SELECT transaction_date, transaction_type, amount, balance_after, description, channel, status, failure_reason
    FROM transactions 
    WHERE account_number = ?
    ORDER BY transaction_date, transaction_time
""", (account_num,))

transactions = cursor.fetchall()
for txn in transactions:
    date_str, txn_type, amount, balance, desc, channel, status, failure = txn
    balance_str = f"${balance:8.2f}" if balance else "    N/A   "
    status_info = f" | {status}"
    if failure:
        status_info += f" ({failure})"
    print(f"{date_str} | {txn_type:12} | ${amount:8.2f} | Balance: {balance_str}{status_info}")
    print(f"           {desc} ({channel})")
    print()

print(f"\n=== Account Summary ===")
cursor.execute("""
    SELECT 
        COUNT(*) as total_transactions,
        COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed_transactions,
        COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed_transactions,
        COUNT(CASE WHEN status = 'CANCELLED' THEN 1 END) as cancelled_transactions,
        SUM(CASE WHEN amount > 0 AND status = 'COMPLETED' THEN amount ELSE 0 END) as total_credits,
        SUM(CASE WHEN amount < 0 AND status = 'COMPLETED' THEN amount ELSE 0 END) as total_debits,
        (SELECT balance_after FROM transactions WHERE account_number = ? AND status = 'COMPLETED' ORDER BY transaction_date DESC, transaction_time DESC LIMIT 1) as current_balance
    FROM transactions 
    WHERE account_number = ?
""", (account_num, account_num))

summary = cursor.fetchone()
total_txns, completed, failed, cancelled, credits, debits, current_balance = summary
print(f"Total Transactions: {total_txns}")
print(f"  - Completed: {completed}")
print(f"  - Failed: {failed}")
print(f"  - Cancelled: {cancelled}")
print(f"Total Credits: ${credits:.2f}")
print(f"Total Debits: ${debits:.2f}")
print(f"Current Balance: ${current_balance:.2f}")

print(f"\n=== Failed Transaction Analysis ===")
cursor.execute("""
    SELECT failure_reason, COUNT(*) as count
    FROM transactions 
    WHERE account_number = ? AND status = 'FAILED'
    GROUP BY failure_reason
    ORDER BY count DESC
""", (account_num,))

failure_stats = cursor.fetchall()
for reason, count in failure_stats:
    print(f"{reason}: {count} transaction(s)")

# Close connection
conn.close()

print("\n=== Database Schema Notes ===")
print("- transaction_id: Auto-incrementing primary key")
print("- Amounts are stored as DECIMAL(10,2) for precision")
print("- CHECK constraints ensure data integrity for transaction_type, channel, and status")
print("- Indexes on transaction_date and account_number for performance")
print("- Reference numbers are unique to prevent duplicate transactions")
print("- Balance tracking after each transaction for easy reconciliation (NULL for failed transactions)")
print("- Status field tracks transaction state (COMPLETED, FAILED, PENDING, CANCELLED)")
print("- Failure_reason provides specific error details for failed transactions")
print("- Supports various transaction types and channels")
print("- Failed transactions are logged but don't affect account balance")