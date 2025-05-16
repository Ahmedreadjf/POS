#!/usr/bin/env python3
"""
Database Repair Script for MarocPOS

This script diagnoses and repairs common database schema issues:
1. Missing tables
2. Missing columns
3. Schema mismatches
"""

import os
import sys
import sqlite3
import re
from datetime import datetime

# Path to the database file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pos7.db")

def dict_factory(cursor, row):
    """Convert row to dictionary with column names as keys"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_connection():
    """Create a connection to the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = dict_factory
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def check_table_exists(cursor, table_name):
    """Check if a table exists in the database"""
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
        (table_name,)
    )
    return cursor.fetchone() is not None

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    if not check_table_exists(cursor, table_name):
        return False
        
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row['name'] for row in cursor.fetchall()]
    return column_name in columns

def add_column_if_missing(cursor, table_name, column_name, column_type):
    """Add a column to a table if it doesn't exist"""
    if not check_column_exists(cursor, table_name, column_name):
        try:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            return True
        except sqlite3.Error as e:
            print(f"Error adding column {column_name} to {table_name}: {e}")
            return False
    return False

def create_customers_table(cursor):
    """Create the Customers table if it doesn't exist"""
    if not check_table_exists(cursor, "Customers"):
        try:
            cursor.execute("""
                CREATE TABLE Customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created Customers table")
            return True
        except sqlite3.Error as e:
            print(f"Error creating Customers table: {e}")
            return False
    return False

def fix_product_variants_table(cursor):
    """Fix issues with the ProductVariants table"""
    changes = 0
    
    # Add attribute_values column if missing
    if add_column_if_missing(cursor, "ProductVariants", "attribute_values", "TEXT"):
        print("✅ Added attribute_values column to ProductVariants table")
        changes += 1
    
    return changes

def fix_sale_items_table(cursor):
    """Fix issues with the SaleItems table"""
    changes = 0
    
    # Add unit_cost column if missing
    if add_column_if_missing(cursor, "SaleItems", "unit_cost", "REAL DEFAULT 0"):
        print("✅ Added unit_cost column to SaleItems table")
        changes += 1
    
    return changes

def fix_database_schema():
    """Fix common database schema issues"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        changes = 0
        
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Create missing tables
        create_customers_table(cursor)
        
        # Fix issues with ProductVariants table
        changes += fix_product_variants_table(cursor)
        
        # Fix issues with SaleItems table
        changes += fix_sale_items_table(cursor)
        
        # Add any other fixes here
        
        # Commit changes
        conn.commit()
        
        return changes
    except sqlite3.Error as e:
        print(f"Error fixing database schema: {e}")
        conn.rollback()
        return 0
    finally:
        conn.close()

def backup_database():
    """Create a backup of the database file"""
    try:
        import shutil
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{DB_PATH}.backup_{timestamp}"
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Created database backup at: {backup_path}")
        return True
    except Exception as e:
        print(f"Error creating database backup: {e}")
        return False

def populate_sample_data():
    """Add sample data to the database for testing"""
    conn = get_connection()
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
        
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Add sample categories if none exist
        cursor.execute("SELECT COUNT(*) as count FROM Categories")
        if cursor.fetchone()['count'] == 0:
            sample_categories = [
                ("Électronique", "Produits électroniques"),
                ("Vêtements", "Vêtements et accessoires"),
                ("Alimentation", "Produits alimentaires")
            ]
            for name, description in sample_categories:
                cursor.execute(
                    "INSERT INTO Categories (name, description) VALUES (?, ?)",
                    (name, description)
                )
            print("✅ Added sample categories")
        
        # Add sample customers if table is empty
        if check_table_exists(cursor, "Customers"):
            cursor.execute("SELECT COUNT(*) as count FROM Customers")
            if cursor.fetchone()['count'] == 0:
                sample_customers = [
                    ("Mohammed Alami", "mohammed@example.com", "0612345678", "Casablanca", "Client régulier"),
                    ("Fatima Benali", "fatima@example.com", "0687654321", "Rabat", ""),
                    ("Ahmed Tazi", "ahmed@example.com", "0661234567", "Marrakech", "Préfère être contacté par email")
                ]
                for name, email, phone, address, notes in sample_customers:
                    cursor.execute(
                        "INSERT INTO Customers (name, email, phone, address, notes) VALUES (?, ?, ?, ?, ?)",
                        (name, email, phone, address, notes)
                    )
                print("✅ Added sample customers")
        
        # Add a simple product if none exist
        cursor.execute("SELECT COUNT(*) as count FROM Products")
        if cursor.fetchone()['count'] == 0:
            # Get first category ID
            cursor.execute("SELECT id FROM Categories LIMIT 1")
            category = cursor.fetchone()
            if category:
                category_id = category['id']
                cursor.execute("""
                    INSERT INTO Products 
                    (name, barcode, description, unit_price, purchase_price, stock, category_id, has_variants)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, ("Produit Test", "123456789", "Un produit pour tester", 100.0, 70.0, 10, category_id, 0))
                print("✅ Added sample product")
        
        # Commit changes
        conn.commit()
        print("✅ Sample data added successfully")
        return True
    except sqlite3.Error as e:
        print(f"Error adding sample data: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    print("\n=== MarocPOS Database Repair Tool ===\n")
    
    # Check if database file exists
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file not found at: {DB_PATH}")
        print("Please run the application first to create the database.")
        return
    
    print(f"📊 Database found at: {DB_PATH}")
    
    # Create a backup before making changes
    backup_database()
    
    # Fix database schema
    print("\n🔧 Checking and fixing database schema...")
    changes = fix_database_schema()
    
    if changes > 0:
        print(f"\n✅ Fixed {changes} issues with the database schema")
    else:
        print("\n✅ No schema issues found or fixed")
    
    # Offer to add sample data
    add_sample = input("\nDo you want to add sample data for testing? (y/n): ").lower().strip()
    if add_sample == 'y':
        populate_sample_data()
    
    print("\n=== Database Repair Complete ===")
    print("You should now be able to run the application without errors.")
    print("If you still encounter issues, please contact support.")

if __name__ == "__main__":
    main()
