from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date, time
from decimal import Decimal
import sqlite3
import os
from contextlib import contextmanager

app = FastAPI(title="Mock Bank API", version="1.0.0")
security = HTTPBearer()

# Database configuration
DATABASE_PATH = "bank_transactions.db"

# Pydantic models
class TransactionResponse(BaseModel):
    transaction_id: int
    account_number: str
    transaction_date: date
    transaction_time: time
    transaction_type: str
    amount: Decimal
    balance_after: Optional[Decimal]
    description: Optional[str]
    reference_number: Optional[str]
    counterparty_account: Optional[str]
    counterparty_name: Optional[str]
    channel: Optional[str]
    location: Optional[str]
    status: str
    failure_reason: Optional[str]
    created_at: datetime

class TransactionCreate(BaseModel):
    account_number: str
    transaction_type: str = Field(..., pattern="^(DEPOSIT|WITHDRAWAL|TRANSFER_IN|TRANSFER_OUT|FEE|INTEREST|CARD)$")
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None
    counterparty_account: Optional[str] = None
    counterparty_name: Optional[str] = None
    channel: str = Field(..., pattern="^(ATM|ONLINE|MOBILE|BRANCH|CARD|AUTO)$")
    location: Optional[str] = None

class BalanceResponse(BaseModel):
    account_number: str
    current_balance: Decimal
    available_balance: Decimal
    last_updated: datetime

class RetryResponse(BaseModel):
    transaction_id: int
    old_status: str
    new_status: str
    message: str

# Database context manager
@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Authentication (simple token validation for demo)
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # In production, implement proper JWT validation
    if credentials.credentials != "demo-token-123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    return credentials.credentials

# Initialize database
def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_number TEXT NOT NULL,
                transaction_date DATE NOT NULL,
                transaction_time TIME NOT NULL,
                transaction_type TEXT NOT NULL CHECK (transaction_type IN ('DEPOSIT', 'WITHDRAWAL', 'TRANSFER_IN', 'TRANSFER_OUT', 'FEE', 'INTEREST', 'CARD')),
                amount DECIMAL(10, 2) NOT NULL,
                balance_after DECIMAL(10, 2),
                description TEXT,
                reference_number TEXT UNIQUE,
                counterparty_account TEXT,
                counterparty_name TEXT,
                channel TEXT CHECK (channel IN ('ATM', 'ONLINE', 'MOBILE', 'BRANCH', 'CARD', 'AUTO')),
                location TEXT,
                status TEXT NOT NULL DEFAULT 'COMPLETED' CHECK (status IN ('COMPLETED', 'FAILED', 'PENDING', 'CANCELLED')),
                failure_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/account/{account_number}/balance", response_model=BalanceResponse)
async def get_account_balance(account_number: str, token: str = Depends(verify_token)):
    """Get current account balance"""
    with get_db() as conn:
        # Get the most recent transaction to determine current balance
        cursor = conn.execute("""
            SELECT balance_after, created_at 
            FROM transactions 
            WHERE account_number = ? AND status = 'COMPLETED' AND balance_after IS NOT NULL
            ORDER BY created_at DESC, transaction_id DESC
            LIMIT 1
        """, (account_number,))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Account not found or no completed transactions")
        
        # For simplicity, available balance equals current balance (no holds/pending)
        current_balance = Decimal(str(result['balance_after']))
        
        return BalanceResponse(
            account_number=account_number,
            current_balance=current_balance,
            available_balance=current_balance,
            last_updated=datetime.fromisoformat(result['created_at'])
        )

@app.get("/account/{account_number}/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    account_number: str,
    limit: int = 50,
    status_filter: Optional[str] = None,
    token: str = Depends(verify_token)
):
    """Get account transactions with optional filtering"""
    with get_db() as conn:
        query = "SELECT * FROM transactions WHERE account_number = ?"
        params = [account_number]
        
        if status_filter:
            query += " AND status = ?"
            params.append(status_filter)
        
        query += " ORDER BY created_at DESC, transaction_id DESC LIMIT ?"
        params.append(limit)
        
        cursor = conn.execute(query, params)
        transactions = cursor.fetchall()
        
        if not transactions:
            return []
        
        return [TransactionResponse(**dict(t)) for t in transactions]

@app.get("/transactions/failed", response_model=List[TransactionResponse])
async def get_failed_transactions(token: str = Depends(verify_token)):
    """Get all failed transactions that can be retried"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT * FROM transactions 
            WHERE status = 'FAILED'
            ORDER BY created_at DESC
        """)
        transactions = cursor.fetchall()
        
        return [TransactionResponse(**dict(t)) for t in transactions]

@app.post("/transactions/{transaction_id}/retry", response_model=RetryResponse)
async def retry_failed_transaction(transaction_id: int, token: str = Depends(verify_token)):
    """Retry a failed transaction"""
    with get_db() as conn:
        # Check if transaction exists and is failed
        cursor = conn.execute("""
            SELECT * FROM transactions WHERE transaction_id = ? AND status = 'FAILED'
        """, (transaction_id,))
        
        transaction = cursor.fetchone()
        if not transaction:
            raise HTTPException(
                status_code=404, 
                detail="Transaction not found or not in failed status"
            )
        
        # Simulate retry logic - in real implementation, this would involve
        # actual payment processing, balance checks, etc.
        new_status = "COMPLETED"  # Simulate successful retry
        
        # Update transaction status
        conn.execute("""
            UPDATE transactions 
            SET status = ?, failure_reason = NULL
            WHERE transaction_id = ?
        """, (new_status, transaction_id))
        
        # If it's a balance-affecting transaction, update balance_after
        if transaction['transaction_type'] in ['DEPOSIT', 'WITHDRAWAL', 'TRANSFER_IN', 'TRANSFER_OUT']:
            # Get current balance
            balance_cursor = conn.execute("""
                SELECT balance_after FROM transactions 
                WHERE account_number = ? AND status = 'COMPLETED' AND balance_after IS NOT NULL
                ORDER BY created_at DESC, transaction_id DESC
                LIMIT 1
            """, (transaction['account_number'],))
            
            current_balance_row = balance_cursor.fetchone()
            current_balance = Decimal('0.00') if not current_balance_row else Decimal(str(current_balance_row['balance_after']))
            
            # Calculate new balance
            if transaction['transaction_type'] in ['DEPOSIT', 'TRANSFER_IN']:
                new_balance = current_balance + Decimal(str(transaction['amount']))
            else:  # WITHDRAWAL, TRANSFER_OUT
                new_balance = current_balance - Decimal(str(transaction['amount']))
            
            conn.execute("""
                UPDATE transactions 
                SET balance_after = ?
                WHERE transaction_id = ?
            """, (str(new_balance), transaction_id))
        
        conn.commit()
        
        return RetryResponse(
            transaction_id=transaction_id,
            old_status="FAILED",
            new_status=new_status,
            message="Transaction retried successfully"
        )

@app.post("/transactions", response_model=TransactionResponse)
async def create_transaction(transaction: TransactionCreate, token: str = Depends(verify_token)):
    """Create a new transaction"""
    with get_db() as conn:
        # Get current balance for balance calculation
        cursor = conn.execute("""
            SELECT balance_after FROM transactions 
            WHERE account_number = ? AND status = 'COMPLETED' AND balance_after IS NOT NULL
            ORDER BY created_at DESC, transaction_id DESC
            LIMIT 1
        """, (transaction.account_number,))
        
        current_balance_row = cursor.fetchone()
        current_balance = Decimal('0.00') if not current_balance_row else Decimal(str(current_balance_row['balance_after']))
        
        # Calculate new balance
        if transaction.transaction_type in ['DEPOSIT', 'TRANSFER_IN', 'INTEREST']:
            new_balance = current_balance + transaction.amount
        elif transaction.transaction_type in ['WITHDRAWAL', 'TRANSFER_OUT', 'FEE']:
            new_balance = current_balance - transaction.amount
            if new_balance < 0:
                raise HTTPException(status_code=400, detail="Insufficient funds")
        else:  # CARD transactions
            new_balance = current_balance - transaction.amount
        
        # Insert transaction
        now = datetime.now()
        cursor = conn.execute("""
            INSERT INTO transactions (
                account_number, transaction_date, transaction_time, transaction_type,
                amount, balance_after, description, counterparty_account, counterparty_name,
                channel, location, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'COMPLETED', ?)
        """, (
            transaction.account_number,
            now.date(),
            now.time(),
            transaction.transaction_type,
            str(transaction.amount),
            str(new_balance),
            transaction.description,
            transaction.counterparty_account,
            transaction.counterparty_name,
            transaction.channel,
            transaction.location,
            now
        ))
        
        transaction_id = cursor.lastrowid
        conn.commit()
        
        # Return the created transaction
        cursor = conn.execute("SELECT * FROM transactions WHERE transaction_id = ?", (transaction_id,))
        created_transaction = cursor.fetchone()
        
        return TransactionResponse(**dict(created_transaction))

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)