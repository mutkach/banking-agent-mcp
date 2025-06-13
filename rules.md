# Bank Transaction System - Business Rules & Logic

## 1. Transaction Processing Framework

### 1.1 Transaction Lifecycle
- **PENDING**: Initial state when transaction is created but not yet processed
- **COMPLETED**: Transaction successfully processed and account balance updated
- **FAILED**: Transaction attempted but could not be completed due to business rules or technical issues
- **CANCELLED**: Transaction terminated by user request or system timeout before processing

### 1.2 Transaction Recording Principles
- All transaction attempts must be logged, regardless of success or failure
- Failed transactions are recorded with NULL balance_after (no balance impact)
- Each transaction must have a unique reference number for audit trails
- Transaction timestamps must include both date and time for precise ordering
- Balance calculations are only updated for COMPLETED transactions

## 2. Transaction Types & Business Rules

### 2.1 DEPOSIT Transactions
**Purpose**: Add funds to customer account

**Business Rules**:
- Deposits can only increase account balance (amount > 0)
- Minimum deposit amount: $0.01
- Maximum single deposit: $50,000 (anti-money laundering compliance)
- Cash deposits over $10,000 require additional documentation
- Electronic deposits may have a hold period (1-3 business days)

**Failure Conditions**:
- Invalid deposit amount (negative or zero)
- Exceeds daily deposit limits
- Account is frozen or closed
- Source verification fails (for electronic transfers)

### 2.2 WITHDRAWAL Transactions
**Purpose**: Remove funds from customer account

**Business Rules**:
- Withdrawals decrease account balance (amount < 0)
- Must not exceed available account balance
- Daily ATM withdrawal limit: $500
- Daily total withdrawal limit: $2,500
- ATM withdrawal amounts must be multiples of $20
- Minimum withdrawal: $20 (ATM), $1 (branch/online)

**Failure Conditions**:
- **INSUFFICIENT_FUNDS**: Withdrawal amount exceeds available balance
- **DAILY_LIMIT_EXCEEDED**: Exceeds daily withdrawal limits
- **ATM_LIMIT_EXCEEDED**: Exceeds ATM-specific limits
- **INVALID_AMOUNT**: Amount not in valid denominations (ATM)
- **ACCOUNT_FROZEN**: Account temporarily restricted
- **CARD_EXPIRED**: ATM card has expired
- **INCORRECT_PIN**: Too many incorrect PIN attempts

### 2.3 TRANSFER_IN Transactions
**Purpose**: Receive funds from another account

**Business Rules**:
- Increases account balance (amount > 0)
- Requires valid source account verification
- Internal transfers (same bank) process immediately
- External transfers may take 1-3 business days
- Maximum single transfer: $25,000
- Recurring transfers allowed with pre-authorization

**Failure Conditions**:
- **INVALID_SOURCE_ACCOUNT**: Source account doesn't exist or is closed
- **INSUFFICIENT_FUNDS_SOURCE**: Source account lacks sufficient funds
- **TRANSFER_LIMIT_EXCEEDED**: Exceeds daily/monthly transfer limits
- **NETWORK_TIMEOUT**: Connection failure during processing

### 2.4 TRANSFER_OUT Transactions
**Purpose**: Send funds to another account

**Business Rules**:
- Decreases account balance (amount < 0)
- Requires recipient account validation
- Daily transfer limit: $10,000
- Monthly transfer limit: $50,000
- Same-day transfers available for premium accounts
- International transfers require additional compliance checks

**Failure Conditions**:
- **INVALID_RECIPIENT_ACCOUNT**: Recipient account invalid or closed
- **INSUFFICIENT_FUNDS**: Not enough funds in source account
- **TRANSFER_LIMIT_EXCEEDED**: Exceeds daily/monthly limits
- **COMPLIANCE_HOLD**: Transaction flagged for review
- **NETWORK_TIMEOUT**: System communication failure
- **RECIPIENT_BANK_UNAVAILABLE**: Receiving bank systems down

### 2.5 CARD Transactions (Debit/Credit Card Purchases)
**Purpose**: Process point-of-sale and online purchases

**Business Rules**:
- Decreases account balance (amount < 0)
- Real-time authorization required
- Daily card spending limit: $3,000
- International transaction fees may apply
- Contactless limit: $100 without PIN
- Online purchases require CVV verification

**Failure Conditions**:
- **CARD_DECLINED_FRAUD_PROTECTION**: Suspicious activity detected
- **INSUFFICIENT_FUNDS**: Inadequate account balance
- **DAILY_LIMIT_EXCEEDED**: Exceeds daily spending limits
- **CARD_EXPIRED**: Card past expiration date
- **INVALID_MERCHANT**: Merchant not authorized
- **CVV_MISMATCH**: Security code verification failed
- **GEOGRAPHIC_RESTRICTION**: Transaction outside allowed regions

### 2.6 FEE Transactions
**Purpose**: Bank-imposed charges for services

**Business Rules**:
- Decreases account balance (amount < 0)
- Automatically processed by system
- Fee structure varies by account type (see Section 9: Account Type Fee Structure)
- Overdraft fees apply per incident with account-type variations
- ATM fees depend on network and account tier
- Wire transfer fees vary by account type and destination

**Failure Conditions**:
- **INSUFFICIENT_FUNDS**: Cannot collect fee due to low balance
- **ACCOUNT_CLOSED**: Cannot charge fees on closed accounts
- **FEE_WAIVER_ACTIVE**: Customer has fee waiver in effect

### 2.7 INTEREST Transactions
**Purpose**: Credit interest earnings to account

**Business Rules**:
- Increases account balance (amount > 0)
- Calculated monthly on average daily balance
- Interest rates vary by account type (see Section 9: Account Type Interest Rates)
- Minimum balance requirements differ by account tier
- Interest compounds monthly
- Automatically processed on last business day of month

**Failure Conditions**:
- **ACCOUNT_BELOW_MINIMUM**: Balance too low to earn interest (varies by account type)
- **ACCOUNT_CLOSED**: Cannot credit interest to closed accounts
- **CALCULATION_ERROR**: System error in interest computation

## 3. Channel-Specific Rules

### 3.1 ATM Transactions
- Available 24/7 (except during maintenance)
- Maximum 6 transactions per session
- Cash dispensing in $20 denominations only
- Receipt printing required for amounts over $100
- System maintenance window: 2:00 AM - 4:00 AM daily

### 3.2 ONLINE Banking
- Available 24/7 with scheduled maintenance windows
- Multi-factor authentication required for high-value transactions
- Session timeout after 15 minutes of inactivity
- Enhanced security for new device logins
- Transaction history available for 24 months

### 3.3 MOBILE Banking
- Biometric authentication supported
- GPS verification for security
- Push notifications for all transactions
- Mobile deposit limits: $5,000 per day
- Requires app-specific PIN for transactions over $1,000

### 3.4 BRANCH Transactions
- Available during business hours only
- Teller verification required for large transactions
- No daily limits for in-person transactions
- Documentation required for transactions over $10,000
- Customer identification always required

### 3.5 AUTO (Automated) Transactions
- Pre-authorized recurring transactions
- Scheduled on specific dates
- Automatic retry on failure (up to 3 attempts)
- Customer notification required for failures
- Can be cancelled with 1 business day notice

## 4. Account Balance Rules

### 4.1 Balance Calculation
- Balance updates only for COMPLETED transactions
- Real-time balance updates for all channels
- Pending transactions show as "holds" but don't affect available balance
- End-of-day balance reconciliation required
- Balance history maintained for regulatory compliance

### 4.2 Overdraft Protection
- Overdraft limit: $500 (eligible accounts only)
- Overdraft fee: $35 per transaction
- Maximum 3 overdraft fees per day
- Automatic transfer from linked savings account if available
- Overdraft privileges can be revoked for excessive use

## 5. Security & Fraud Prevention

### 5.1 Fraud Detection Rules
- Transactions over $2,000 require additional verification
- Multiple failed PIN attempts lock card for 24 hours
- Unusual spending patterns trigger temporary holds
- Geographic anomalies flag transactions for review
- Velocity checks prevent rapid successive transactions

### 5.2 Transaction Monitoring
- Real-time monitoring for suspicious patterns
- Machine learning algorithms assess risk scores
- Manual review required for high-risk transactions
- Customer notification for all declined transactions
- 30-day transaction pattern analysis

## 6. System Operational Rules

### 6.1 Processing Windows
- Real-time processing during business hours
- Batch processing for overnight reconciliation
- Cut-off times: 6:00 PM for same-day processing
- Weekend processing limited to essential services
- Holiday schedule affects processing times

### 6.2 System Maintenance
- Scheduled maintenance: Sundays 2:00 AM - 6:00 AM
- Emergency maintenance with 2-hour customer notification
- Read-only access during maintenance windows
- Automatic retry for failed transactions post-maintenance
- Service level agreement: 99.9% uptime

### 6.3 Error Handling
- **NETWORK_TIMEOUT**: Retry up to 3 times with exponential backoff
- **SYSTEM_MAINTENANCE**: Queue transactions for processing after maintenance
- **DATABASE_ERROR**: Log error and notify operations team immediately
- **INVALID_DATA**: Return specific error codes to customer interface
- All system errors logged with unique error IDs

## 7. Compliance & Regulatory Rules

### 7.1 Anti-Money Laundering (AML)
- Transactions over $10,000 require CTR (Currency Transaction Report)
- Suspicious activity monitoring and SAR (Suspicious Activity Report) filing
- Customer due diligence for high-value transactions
- Enhanced monitoring for Politically Exposed Persons (PEPs)
- Record retention: 5 years minimum

### 7.2 Know Your Customer (KYC)
- Customer identity verification required for account opening
- Periodic customer information updates
- Enhanced due diligence for high-risk customers
- Transaction monitoring against customer profile
- Documentation requirements for beneficial ownership

### 7.3 Audit Requirements
- Complete transaction trail with timestamps
- Immutable transaction records (no deletions allowed)
- Regular audit log reviews
- Segregation of duties for high-value transactions
- External audit compliance reporting

## 8. Customer Communication Rules

### 8.1 Transaction Notifications
- SMS alerts for transactions over $500
- Email confirmations for online transactions
- Push notifications for mobile app users
- Immediate notification for declined transactions
- Monthly statement generation

### 8.2 Dispute Resolution
- 60-day window for transaction disputes
- Provisional credit for disputed card transactions
- Investigation timeline: 10 business days
- Documentation requirements for dispute claims
- Customer liability limits per regulation

## 9. Account Type Fee Structure & Interest Rates

### 9.1 Account Classifications
The bank offers three distinct account types, each with different fee structures and interest rates designed to reward customer loyalty and account balances.

### 9.2 NORMAL Account (Standard Banking)
**Target Audience**: Entry-level customers, students, basic banking needs

**Monthly Maintenance Fee**:
- $12 per month
- **Waived if**: Average daily balance ≥ $1,500 OR Direct deposit ≥ $500/month

**Transaction Fees**:
- Overdraft fee: $35 per incident (maximum 3 per day = $105)
- ATM fee (out-of-network): $3.50 per transaction
- Excessive transaction fee: $1.50 after 15 transactions per month
- Wire transfer fee: $30 domestic, $50 international
- Stop payment fee: $30
- Paper statement fee: $5 per month (waived for e-statements)

**Interest Rates**:
- Savings APY: 0.05%
- Checking APY: 0.01%
- **Minimum balance for interest**: $500
- Certificate of Deposit (12-month): 1.25% APY

**Transaction Limits**:
- Daily ATM withdrawal: $500
- Daily debit card spending: $2,000
- Daily transfer limit: $5,000
- Monthly transfer limit: $25,000

### 9.3 BENEFIT Account (Premium Banking)
**Target Audience**: Mid-tier customers, professionals, growing account balances

**Monthly Maintenance Fee**:
- $25 per month
- **Waived if**: Average daily balance ≥ $10,000 OR Combined relationship balance ≥ $25,000

**Transaction Fees**:
- Overdraft fee: $30 per incident (maximum 2 per day = $60)
- ATM fee (out-of-network): $2.50 per transaction (2 fee rebates per month)
- No excessive transaction fees
- Wire transfer fee: $20 domestic, $35 international
- Stop payment fee: $25
- Paper statement fee: **WAIVED**

**Interest Rates**:
- Savings APY: 0.15%
- Checking APY: 0.05%
- **Minimum balance for interest**: $1,000
- Certificate of Deposit (12-month): 1.75% APY
- **Bonus**: Additional 0.05% APY if relationship balance > $50,000

**Transaction Limits**:
- Daily ATM withdrawal: $1,000
- Daily debit card spending: $5,000
- Daily transfer limit: $15,000
- Monthly transfer limit: $75,000

**Additional Benefits**:
- Priority customer service line
- Extended branch hours access
- Free cashier's checks (up to 3 per month)
- Identity theft monitoring

### 9.4 VIP Account (Private Banking)
**Target Audience**: High-net-worth individuals, premium service expectations

**Monthly Maintenance Fee**:
- **WAIVED** (no monthly maintenance fee regardless of balance)

**Transaction Fees**:
- Overdraft fee: $25 per incident (maximum 1 per day = $25)
- ATM fee (out-of-network): **WAIVED GLOBALLY**
- No excessive transaction fees
- Wire transfer fee: $15 domestic, $25 international
- Stop payment fee: $15
- Paper statement fee: **WAIVED**

**Interest Rates**:
- Savings APY: 0.35%
- Checking APY: 0.15%
- **No minimum balance requirement for interest**
- Certificate of Deposit (12-month): 2.25% APY
- **Bonus**: Additional 0.10% APY if relationship balance > $100,000
- **Premium**: Additional 0.15% APY if relationship balance > $500,000

**Transaction Limits**:
- Daily ATM withdrawal: $2,500
- Daily debit card spending: $10,000
- Daily transfer limit: $50,000
- Monthly transfer limit: $250,000
- **Override capability**: Can request temporary limit increases

**Exclusive Benefits**:
- Dedicated relationship manager
- 24/7 concierge banking services
- Free safe deposit box (small size)
- Unlimited cashier's checks
- Priority loan processing
- Complimentary financial planning consultation (annual)
- Airport lounge access (limited locations)
- Enhanced fraud protection with immediate resolution

### 9.5 Account Type Upgrade/Downgrade Rules

**Automatic Upgrades**:
- Normal → Benefit: Maintain $10,000+ average balance for 3 consecutive months
- Benefit → VIP: Maintain $100,000+ relationship balance for 6 consecutive months

**Promotional Upgrades**:
- **Promotional Code "UPGRADE"**: Customers can request temporary plan upgrade through virtual assistant
- Valid for 90 days from activation date
- Does not require meeting standard balance criteria
- Limited to one promotional upgrade per customer per calendar year
- Upgrade level: Normal → Benefit or Benefit → VIP (one tier up only)
- After promotional period expires, account reverts to original tier unless standard upgrade criteria are met
- Customer must specifically request upgrade using promotional code "UPGRADE" via virtual assistant

**Automatic Downgrades**:
- VIP → Benefit: Relationship balance below $50,000 for 6 consecutive months
- Benefit → Normal: Average balance below $5,000 for 6 consecutive months

**Grace Periods**:
- 90-day grace period before downgrade takes effect
- Customers notified 30 days before any account type changes
- One-time courtesy reversal available per calendar year

### 9.6 Fee Processing Logic in System

**Monthly Fee Assessment**:
```
IF account_type = 'NORMAL' THEN
    IF avg_daily_balance >= 1500 OR direct_deposit >= 500 THEN
        monthly_fee = 0
    ELSE
        monthly_fee = 12
    END IF

ELSIF account_type = 'BENEFIT' THEN
    IF avg_daily_balance >= 10000 OR relationship_balance >= 25000 THEN
        monthly_fee = 0
    ELSE
        monthly_fee = 25
    END IF

ELSIF account_type = 'VIP' THEN
    monthly_fee = 0  -- Always waived
END IF
```

**Interest Calculation Logic**:
```
base_rate = get_base_rate_by_account_type(account_type)
bonus_rate = 0

IF account_type = 'BENEFIT' AND relationship_balance > 50000 THEN
    bonus_rate = 0.05
ELSIF account_type = 'VIP' THEN
    IF relationship_balance > 500000 THEN
        bonus_rate = 0.15
    ELSIF relationship_balance > 100000 THEN
        bonus_rate = 0.10
    END IF
END IF

final_rate = base_rate + bonus_rate
```

### 9.7 Implementation in Transaction Schema

To support this account type structure, the transaction schema would need an additional table:

```sql
-- Account types and their current fee structures
CREATE TABLE account_types (
    account_number VARCHAR(50) PRIMARY KEY,
    account_type account_type_enum NOT NULL DEFAULT 'NORMAL',
    created_date DATE NOT NULL,
    last_upgrade_date DATE,
    relationship_balance NUMERIC(15,2) DEFAULT 0,
    average_daily_balance NUMERIC(12,2) DEFAULT 0,
    direct_deposit_amount NUMERIC(10,2) DEFAULT 0,
    fee_waiver_expiry DATE,
    FOREIGN KEY (account_number) REFERENCES accounts(account_number)
);

-- New ENUM type for account classification
CREATE TYPE account_type_enum AS ENUM ('NORMAL', 'BENEFIT', 'VIP');
```

This tiered fee structure incentivizes customers to maintain higher balances and develop deeper banking relationships while providing clear value propositions for each account level.