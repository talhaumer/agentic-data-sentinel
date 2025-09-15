"""Generate sample data for testing and demonstration - FIXED VERSION."""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import sqlite3
import uuid

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)


def generate_fake_email():
    """Generate a simple fake email without Faker dependency."""
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "example.com", "company.com"]
    names = ["john", "jane", "mike", "sara", "david", "lisa", "robert", "emily"]
    return f"{random.choice(names)}{random.randint(1, 1000)}@{random.choice(domains)}"


def generate_fake_name():
    """Generate a simple fake name without Faker dependency."""
    first_names = [
        "John",
        "Jane",
        "Mike",
        "Sarah",
        "David",
        "Lisa",
        "Robert",
        "Emily",
        "Michael",
        "Jennifer",
        "William",
        "Elizabeth",
        "Christopher",
        "Jessica",
    ]
    last_names = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Miller",
        "Davis",
        "Garcia",
        "Rodriguez",
        "Wilson",
        "Martinez",
        "Anderson",
        "Taylor",
        "Thomas",
    ]
    return random.choice(first_names), random.choice(last_names)


def generate_events_data(num_rows=10000):
    """Generate sample events data with some quality issues."""
    print("Generating events data...")

    rows = []
    for i in range(num_rows):
        # Introduce some data quality issues
        if i % 100 == 0:  # 1% of rows have issues
            # High null rate
            status = None
        elif i % 50 == 0:  # 2% of rows have issues
            # Invalid price
            price = -1.0
            status = "invalid"
        else:
            # Normal data
            price = float(np.round(np.random.exponential(50), 2))
            status = np.random.choice(["ok", "failed"], p=[0.9, 0.1])

        rows.append(
            {
                "user_id": str(uuid.uuid4()),
                "event_time": datetime.now() - timedelta(days=random.randint(0, 365)),
                "price": (
                    price
                    if "price" in locals()
                    else float(np.round(np.random.exponential(50), 2))
                ),
                "status": status,
                "category": np.random.choice(
                    ["electronics", "clothing", "books", "home", "sports"]
                ),
                "region": np.random.choice(["US", "EU", "APAC", "LATAM"]),
                "device_type": np.random.choice(["mobile", "desktop", "tablet"]),
                "session_id": str(uuid.uuid4()),
            }
        )

    df = pd.DataFrame(rows)
    df.to_parquet("data/sample_events.parquet", index=False)
    print(f"Generated {len(df)} events records")
    return df


def generate_users_data(num_rows=5000):
    """Generate sample users data."""
    print("Generating users data...")

    rows = []
    for i in range(num_rows):
        # Introduce some data quality issues
        if i % 200 == 0:  # 0.5% of rows have issues
            # Missing email
            email = None
        else:
            email = generate_fake_email()

        first_name, last_name = generate_fake_name()

        rows.append(
            {
                "user_id": str(uuid.uuid4()),
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "created_at": datetime.now() - timedelta(days=random.randint(365, 730)),
                "last_login": datetime.now() - timedelta(days=random.randint(0, 30)),
                "is_active": np.random.choice([True, False], p=[0.8, 0.2]),
                "country": np.random.choice(["US", "UK", "CA", "AU", "DE", "FR", "JP"]),
                "age": np.random.randint(18, 80),
                "subscription_type": np.random.choice(
                    ["free", "premium", "enterprise"], p=[0.6, 0.3, 0.1]
                ),
            }
        )

    df = pd.DataFrame(rows)
    df.to_parquet("data/sample_users.parquet", index=False)
    print(f"Generated {len(df)} users records")
    return df


def generate_transactions_data(num_rows=15000):
    """Generate sample transactions data with anomalies."""
    print("Generating transactions data...")

    rows = []
    for i in range(num_rows):
        # Introduce some data quality issues
        if i % 300 == 0:  # 0.33% of rows have issues
            # Duplicate transaction ID
            transaction_id = f"TXN_{i-1:06d}"
        else:
            transaction_id = f"TXN_{i:06d}"

        if i % 150 == 0:  # 0.67% of rows have issues
            # Outlier amount
            amount = np.random.exponential(1000)  # Very high amounts
        else:
            amount = float(np.round(np.random.exponential(100), 2))

        rows.append(
            {
                "transaction_id": transaction_id,
                "user_id": str(uuid.uuid4()),
                "amount": amount,
                "currency": np.random.choice(
                    ["USD", "EUR", "GBP", "JPY"], p=[0.5, 0.3, 0.15, 0.05]
                ),
                "transaction_time": datetime.now()
                - timedelta(days=random.randint(0, 180)),
                "payment_method": np.random.choice(
                    ["credit_card", "debit_card", "paypal", "bank_transfer"]
                ),
                "status": np.random.choice(
                    ["completed", "pending", "failed"], p=[0.85, 0.1, 0.05]
                ),
                "merchant_id": str(uuid.uuid4()),
                "category": np.random.choice(
                    ["retail", "food", "transport", "entertainment", "utilities"]
                ),
            }
        )

    df = pd.DataFrame(rows)
    df.to_parquet("data/sample_transactions.parquet", index=False)
    print(f"Generated {len(df)} transactions records")
    return df


def load_to_sqlite():
    """Load sample data into SQLite instead of DuckDB."""
    print("Loading data into SQLite...")

    try:
        # Connect to SQLite
        conn = sqlite3.connect("data/dw.db")

        # Load events data
        events_df = pd.read_parquet("data/sample_events.parquet")
        events_df.to_sql("events", conn, if_exists="replace", index=False)

        # Load users data
        users_df = pd.read_parquet("data/sample_users.parquet")
        users_df.to_sql("users", conn, if_exists="replace", index=False)

        # Load transactions data
        transactions_df = pd.read_parquet("data/sample_transactions.parquet")
        transactions_df.to_sql("transactions", conn, if_exists="replace", index=False)

        # Show table info
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        print("Tables created in SQLite:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  - {table[0]}: {count} rows")

        conn.close()
        print("Data loaded successfully into SQLite!")
        return True

    except Exception as e:
        print(f"Error loading data into SQLite: {e}")
        return False


def main():
    """Generate all sample data."""
    print("🚀 Generating sample data for Data Sentinel...")

    try:
        # Generate data files
        events_df = generate_events_data()
        users_df = generate_users_data()
        transactions_df = generate_transactions_data()

        # Load into SQLite
        success = load_to_sqlite()

        if success:
            print("✅ Sample data generation completed!")
            print("\nData files created:")
            print("  - data/sample_events.parquet")
            print("  - data/sample_users.parquet")
            print("  - data/sample_transactions.parquet")
            print("  - data/dw.db (SQLite database)")

            print("\nData quality issues introduced:")
            print("  - Events: 1% null status, 2% invalid prices")
            print("  - Users: 0.5% missing emails")
            print("  - Transactions: 0.33% duplicate IDs, 0.67% outlier amounts")
        else:
            print("❌ Sample data generation failed!")

    except Exception as e:
        print(f"❌ Error generating sample data: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
