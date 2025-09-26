#!/usr/bin/env python3
"""Create sample data for Data Sentinel testing."""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

def create_data_directory():
    """Create data directory if it doesn't exist."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    return data_dir

def create_sample_users_data(data_dir: Path):
    """Create sample users data."""
    np.random.seed(42)
    n_users = 1000
    
    users_data = {
        'user_id': range(1, n_users + 1),
        'name': [f'User_{i}' for i in range(1, n_users + 1)],
        'email': [f'user{i}@example.com' for i in range(1, n_users + 1)],
        'age': np.random.randint(18, 80, n_users),
        'city': np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'], n_users),
        'signup_date': [datetime.now() - timedelta(days=np.random.randint(0, 365)) for _ in range(n_users)],
        'is_active': np.random.choice([True, False], n_users, p=[0.8, 0.2])
    }
    
    df = pd.DataFrame(users_data)
    df.to_parquet(data_dir / "sample_users.parquet", index=False)
    print(f"✅ Created sample_users.parquet with {len(df)} records")

def create_sample_transactions_data(data_dir: Path):
    """Create sample transactions data."""
    np.random.seed(42)
    n_transactions = 5000
    
    transactions_data = {
        'transaction_id': range(1, n_transactions + 1),
        'user_id': np.random.randint(1, 1001, n_transactions),
        'amount': np.random.uniform(10, 1000, n_transactions).round(2),
        'currency': np.random.choice(['USD', 'EUR', 'GBP'], n_transactions, p=[0.7, 0.2, 0.1]),
        'transaction_date': [datetime.now() - timedelta(days=np.random.randint(0, 30)) for _ in range(n_transactions)],
        'category': np.random.choice(['Food', 'Transport', 'Shopping', 'Entertainment', 'Utilities'], n_transactions),
        'status': np.random.choice(['completed', 'pending', 'failed'], n_transactions, p=[0.9, 0.08, 0.02])
    }
    
    df = pd.DataFrame(transactions_data)
    df.to_parquet(data_dir / "sample_transactions.parquet", index=False)
    print(f"✅ Created sample_transactions.parquet with {len(df)} records")

def create_sample_events_data(data_dir: Path):
    """Create sample events data."""
    np.random.seed(42)
    n_events = 10000
    
    events_data = {
        'event_id': range(1, n_events + 1),
        'user_id': np.random.randint(1, 1001, n_events),
        'event_type': np.random.choice(['page_view', 'click', 'purchase', 'signup', 'login'], n_events),
        'timestamp': [datetime.now() - timedelta(hours=np.random.randint(0, 168)) for _ in range(n_events)],
        'page_url': [f'/page/{np.random.randint(1, 50)}' for _ in range(n_events)],
        'session_id': [f'session_{np.random.randint(1, 500)}' for _ in range(n_events)],
        'device_type': np.random.choice(['desktop', 'mobile', 'tablet'], n_events, p=[0.5, 0.4, 0.1])
    }
    
    df = pd.DataFrame(events_data)
    df.to_parquet(data_dir / "sample_events.parquet", index=False)
    print(f"✅ Created sample_events.parquet with {len(df)} records")

def create_sample_financial_data(data_dir: Path):
    """Create sample financial data."""
    np.random.seed(42)
    n_records = 2000
    
    financial_data = {
        'record_id': range(1, n_records + 1),
        'account_id': np.random.randint(1, 201, n_records),
        'transaction_type': np.random.choice(['deposit', 'withdrawal', 'transfer', 'fee'], n_records),
        'amount': np.random.uniform(1, 5000, n_records).round(2),
        'balance': np.random.uniform(1000, 50000, n_records).round(2),
        'date': [datetime.now() - timedelta(days=np.random.randint(0, 90)) for _ in range(n_records)],
        'description': [f'Transaction {i}' for i in range(1, n_records + 1)],
        'category': np.random.choice(['Income', 'Expense', 'Transfer', 'Investment'], n_records)
    }
    
    df = pd.DataFrame(financial_data)
    df.to_parquet(data_dir / "financial_data.parquet", index=False)
    print(f"✅ Created financial_data.parquet with {len(df)} records")

def create_sample_sales_data(data_dir: Path):
    """Create sample sales data."""
    np.random.seed(42)
    n_sales = 3000
    
    sales_data = {
        'sale_id': range(1, n_sales + 1),
        'product_id': np.random.randint(1, 101, n_sales),
        'customer_id': np.random.randint(1, 501, n_sales),
        'quantity': np.random.randint(1, 10, n_sales),
        'unit_price': np.random.uniform(10, 500, n_sales).round(2),
        'total_amount': 0,  # Will be calculated
        'sale_date': [datetime.now() - timedelta(days=np.random.randint(0, 60)) for _ in range(n_sales)],
        'salesperson_id': np.random.randint(1, 21, n_sales),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n_sales),
        'discount': np.random.uniform(0, 0.2, n_sales).round(3)
    }
    
    df = pd.DataFrame(sales_data)
    df['total_amount'] = (df['quantity'] * df['unit_price'] * (1 - df['discount'])).round(2)
    df.to_parquet(data_dir / "sales_data.parquet", index=False)
    print(f"✅ Created sales_data.parquet with {len(df)} records")

def create_user_events_data(data_dir: Path):
    """Create user events data with some anomalies."""
    np.random.seed(42)
    n_events = 8000
    
    # Create normal events
    normal_events = {
        'event_id': range(1, n_events + 1),
        'user_id': np.random.randint(1, 1001, n_events),
        'event_type': np.random.choice(['login', 'page_view', 'click', 'search'], n_events),
        'timestamp': [datetime.now() - timedelta(minutes=np.random.randint(0, 1440)) for _ in range(n_events)],
        'session_duration': np.random.uniform(30, 3600, n_events).round(0),
        'page_views': np.random.randint(1, 20, n_events)
    }
    
    # Add some anomalies
    anomaly_indices = np.random.choice(n_events, size=100, replace=False)
    for idx in anomaly_indices:
        if np.random.random() < 0.5:
            # Anomalous session duration
            normal_events['session_duration'][idx] = np.random.uniform(0, 10)  # Very short sessions
        else:
            # Anomalous page views
            normal_events['page_views'][idx] = np.random.randint(100, 1000)  # Very high page views
    
    df = pd.DataFrame(normal_events)
    df.to_parquet(data_dir / "user_events.parquet", index=False)
    print(f"✅ Created user_events.parquet with {len(df)} records (including anomalies)")

def create_database_file(data_dir: Path):
    """Create a comprehensive SQLite database file."""
    import sqlite3
    
    db_path = data_dir / "dw.db"
    conn = sqlite3.connect(db_path)
    
    # Create multiple tables for testing
    conn.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            age INTEGER,
            city TEXT,
            signup_date TIMESTAMP,
            is_active BOOLEAN,
            credit_score INTEGER
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_name TEXT,
            quantity INTEGER,
            price REAL,
            order_date TIMESTAMP,
            status TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            stock_quantity INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS analytics_events (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            event_type TEXT,
            event_data TEXT,
            timestamp TIMESTAMP,
            session_id TEXT
        )
    ''')
    
    # Insert sample data
    np.random.seed(42)
    
    # Insert customers
    for i in range(500):
        conn.execute(
            'INSERT INTO customers (name, email, age, city, signup_date, is_active, credit_score) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (
                f'Customer_{i}',
                f'customer{i}@example.com',
                np.random.randint(18, 80),
                np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
                datetime.now() - timedelta(days=np.random.randint(0, 365)),
                np.random.choice([True, False], p=[0.8, 0.2]),
                np.random.randint(300, 850)
            )
        )
    
    # Insert products
    products = [
        ('Laptop Pro', 'Electronics', 1299.99, 50),
        ('Smartphone X', 'Electronics', 899.99, 100),
        ('Coffee Maker', 'Appliances', 199.99, 75),
        ('Running Shoes', 'Sports', 129.99, 200),
        ('Book Collection', 'Books', 49.99, 150),
        ('Gaming Chair', 'Furniture', 299.99, 30),
        ('Bluetooth Headphones', 'Electronics', 199.99, 80),
        ('Yoga Mat', 'Sports', 39.99, 120),
        ('Desk Lamp', 'Furniture', 79.99, 60),
        ('Water Bottle', 'Sports', 24.99, 300)
    ]
    
    for product in products:
        conn.execute(
            'INSERT INTO products (name, category, price, stock_quantity) VALUES (?, ?, ?, ?)',
            product
        )
    
    # Insert orders
    for i in range(2000):
        conn.execute(
            'INSERT INTO orders (customer_id, product_name, quantity, price, order_date, status) VALUES (?, ?, ?, ?, ?, ?)',
            (
                np.random.randint(1, 501),
                np.random.choice([p[0] for p in products]),
                np.random.randint(1, 5),
                np.random.uniform(10, 1500),
                datetime.now() - timedelta(days=np.random.randint(0, 90)),
                np.random.choice(['completed', 'pending', 'cancelled'], p=[0.85, 0.10, 0.05])
            )
        )
    
    # Insert analytics events
    event_types = ['page_view', 'click', 'purchase', 'signup', 'login', 'logout']
    for i in range(5000):
        conn.execute(
            'INSERT INTO analytics_events (user_id, event_type, event_data, timestamp, session_id) VALUES (?, ?, ?, ?, ?)',
            (
                np.random.randint(1, 501),
                np.random.choice(event_types),
                json.dumps({'page': f'/page_{np.random.randint(1, 20)}', 'duration': np.random.randint(1, 300)}),
                datetime.now() - timedelta(hours=np.random.randint(0, 168)),
                f'session_{np.random.randint(1, 200)}'
            )
        )
    
    conn.commit()
    conn.close()
    print(f"✅ Created dw.db with comprehensive sample data")

def create_csv_datasets(data_dir: Path):
    """Create CSV datasets for testing."""
    np.random.seed(42)
    
    # Create employee data
    n_employees = 200
    employees_data = {
        'employee_id': range(1, n_employees + 1),
        'first_name': [f'Employee_{i}' for i in range(1, n_employees + 1)],
        'last_name': [f'LastName_{i}' for i in range(1, n_employees + 1)],
        'department': np.random.choice(['IT', 'HR', 'Finance', 'Marketing', 'Sales'], n_employees),
        'salary': np.random.randint(40000, 150000, n_employees),
        'hire_date': [datetime.now() - timedelta(days=np.random.randint(30, 365*5)) for _ in range(n_employees)],
        'manager_id': np.random.choice([None] + list(range(1, 21)), n_employees, p=[0.1] + [0.9/20]*20)
    }
    
    df_employees = pd.DataFrame(employees_data)
    df_employees.to_csv(data_dir / "employees.csv", index=False)
    print(f"✅ Created employees.csv with {len(df_employees)} records")
    
    # Create inventory data
    n_products = 100
    inventory_data = {
        'product_id': range(1, n_products + 1),
        'product_name': [f'Product_{i}' for i in range(1, n_products + 1)],
        'category': np.random.choice(['Electronics', 'Clothing', 'Books', 'Home', 'Sports'], n_products),
        'price': np.random.uniform(10, 500, n_products).round(2),
        'stock_quantity': np.random.randint(0, 1000, n_products),
        'supplier': np.random.choice(['Supplier_A', 'Supplier_B', 'Supplier_C', 'Supplier_D'], n_products),
        'last_restocked': [datetime.now() - timedelta(days=np.random.randint(1, 90)) for _ in range(n_products)]
    }
    
    df_inventory = pd.DataFrame(inventory_data)
    df_inventory.to_csv(data_dir / "inventory.csv", index=False)
    print(f"✅ Created inventory.csv with {len(df_inventory)} records")

def create_json_datasets(data_dir: Path):
    """Create JSON datasets for testing."""
    np.random.seed(42)
    
    # Create API logs data
    n_logs = 1000
    logs_data = []
    for i in range(n_logs):
        log_entry = {
            'timestamp': (datetime.now() - timedelta(minutes=np.random.randint(0, 1440))).isoformat(),
            'level': np.random.choice(['INFO', 'WARNING', 'ERROR', 'DEBUG'], p=[0.7, 0.15, 0.1, 0.05]),
            'message': f'API request processed for user {np.random.randint(1, 100)}',
            'endpoint': np.random.choice(['/api/users', '/api/orders', '/api/products', '/api/analytics']),
            'status_code': np.random.choice([200, 201, 400, 401, 404, 500], p=[0.6, 0.1, 0.1, 0.05, 0.1, 0.05]),
            'response_time': np.random.uniform(0.1, 2.0),
            'user_id': np.random.randint(1, 100),
            'ip_address': f'192.168.1.{np.random.randint(1, 255)}'
        }
        logs_data.append(log_entry)
    
    with open(data_dir / "api_logs.json", 'w') as f:
        json.dump(logs_data, f, indent=2)
    print(f"✅ Created api_logs.json with {len(logs_data)} records")

def create_additional_sqlite_databases(data_dir: Path):
    """Create additional SQLite databases for testing."""
    import sqlite3
    
    # Create analytics database
    analytics_db = data_dir / "analytics.db"
    conn = sqlite3.connect(analytics_db)
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS page_views (
            id INTEGER PRIMARY KEY,
            page_url TEXT,
            user_id INTEGER,
            session_id TEXT,
            timestamp TIMESTAMP,
            referrer TEXT,
            user_agent TEXT
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS conversions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            conversion_type TEXT,
            value REAL,
            timestamp TIMESTAMP,
            campaign_id TEXT
        )
    ''')
    
    # Insert page views
    np.random.seed(42)
    for i in range(3000):
        conn.execute(
            'INSERT INTO page_views (page_url, user_id, session_id, timestamp, referrer, user_agent) VALUES (?, ?, ?, ?, ?, ?)',
            (
                f'/page_{np.random.randint(1, 50)}',
                np.random.randint(1, 200),
                f'session_{np.random.randint(1, 100)}',
                datetime.now() - timedelta(hours=np.random.randint(0, 168)),
                np.random.choice(['google.com', 'facebook.com', 'twitter.com', 'direct', None], p=[0.4, 0.2, 0.1, 0.2, 0.1]),
                f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
        )
    
    # Insert conversions
    for i in range(500):
        conn.execute(
            'INSERT INTO conversions (user_id, conversion_type, value, timestamp, campaign_id) VALUES (?, ?, ?, ?, ?)',
            (
                np.random.randint(1, 200),
                np.random.choice(['purchase', 'signup', 'download', 'subscription']),
                np.random.uniform(10, 1000),
                datetime.now() - timedelta(hours=np.random.randint(0, 168)),
                f'campaign_{np.random.randint(1, 10)}'
            )
        )
    
    conn.commit()
    conn.close()
    print(f"✅ Created analytics.db with page views and conversions")
    
    # Create metrics database
    metrics_db = data_dir / "metrics.db"
    conn = sqlite3.connect(metrics_db)
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY,
            metric_name TEXT,
            metric_value REAL,
            timestamp TIMESTAMP,
            tags TEXT
        )
    ''')
    
    # Insert system metrics
    metric_names = ['cpu_usage', 'memory_usage', 'disk_usage', 'network_io', 'response_time']
    for i in range(2000):
        conn.execute(
            'INSERT INTO system_metrics (metric_name, metric_value, timestamp, tags) VALUES (?, ?, ?, ?)',
            (
                np.random.choice(metric_names),
                np.random.uniform(0, 100),
                datetime.now() - timedelta(minutes=np.random.randint(0, 1440)),
                json.dumps({'server': f'server_{np.random.randint(1, 5)}', 'environment': 'production'})
            )
        )
    
    conn.commit()
    conn.close()
    print(f"✅ Created metrics.db with system metrics")

def main():
    """Main function to create all sample data."""
    print("🚀 Creating comprehensive sample data for Data Sentinel...")
    
    data_dir = create_data_directory()
    
    try:
        # File-based datasets
        create_sample_users_data(data_dir)
        create_sample_transactions_data(data_dir)
        create_sample_events_data(data_dir)
        create_sample_financial_data(data_dir)
        create_sample_sales_data(data_dir)
        create_user_events_data(data_dir)
        create_csv_datasets(data_dir)
        create_json_datasets(data_dir)
        
        # Database datasets
        create_database_file(data_dir)
        create_additional_sqlite_databases(data_dir)
        
        print("\n✅ All sample data created successfully!")
        print(f"📁 Data files created in: {data_dir.absolute()}")
        print("\nFiles created:")
        for file in sorted(data_dir.glob("*")):
            print(f"  - {file.name}")
        
        print("\n📊 Dataset Summary:")
        print("  📄 File-based datasets: 8 files (CSV, JSON, Parquet)")
        print("  🗄️  Database datasets: 3 SQLite databases")
        print("  📈 Total records: ~25,000+ records across all datasets")
        print("\n🎯 Ready for comprehensive data quality testing!")
            
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
