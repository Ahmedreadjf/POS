import sqlite3
from datetime import datetime
from database import get_connection
import json

class Payment:
    """Class to manage payment methods and payment transactions"""
    
    @staticmethod
    def create_tables():
        """Create the payment-related tables if they don't exist"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Create PaymentMethods table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS PaymentMethods (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        code TEXT,
                        is_active INTEGER DEFAULT 1,
                        requires_reference INTEGER DEFAULT 0,
                        reference_label TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create SalePayments table to track payment details for sales
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS SalePayments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sale_id INTEGER NOT NULL,
                        payment_method_id INTEGER,
                        amount REAL NOT NULL,
                        reference TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (sale_id) REFERENCES Sales(id) ON DELETE CASCADE,
                        FOREIGN KEY (payment_method_id) REFERENCES PaymentMethods(id)
                    )
                """)
                
                # Check if default payment methods exist
                cursor.execute("SELECT COUNT(*) as count FROM PaymentMethods")
                result = cursor.fetchone()
                
                if result['count'] == 0:
                    # Insert default payment methods
                    default_methods = [
                        ("Espèces", "CASH", 1, 0, ""),
                        ("Carte", "CARD", 1, 1, "N° Transaction"),
                        ("Chèque", "CHECK", 1, 1, "N° Chèque"),
                        ("Virement", "TRANSFER", 1, 1, "Référence"),
                        ("Crédit", "CREDIT", 1, 0, "")
                    ]
                    
                    for method in default_methods:
                        cursor.execute("""
                            INSERT INTO PaymentMethods (name, code, is_active, requires_reference, reference_label)
                            VALUES (?, ?, ?, ?, ?)
                        """, method)
                
                conn.commit()
                print("Payment tables created successfully")
                
            except Exception as e:
                print(f"Error creating payment tables: {e}")
            finally:
                conn.close()
    
    @staticmethod
    def get_all_payment_methods():
        """Get all payment methods"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM PaymentMethods
                    WHERE is_active = 1
                    ORDER BY name
                """)
                
                methods = cursor.fetchall()
                return methods
            except Exception as e:
                print(f"Error getting payment methods: {e}")
                return []
            finally:
                conn.close()
        return []
    
    @staticmethod
    def get_payment_method_by_id(method_id):
        """Get a specific payment method by ID"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM PaymentMethods
                    WHERE id = ?
                """, (method_id,))
                
                method = cursor.fetchone()
                return method
            except Exception as e:
                print(f"Error getting payment method: {e}")
                return None
            finally:
                conn.close()
        return None
    
    @staticmethod
    def add_payment_method(name, code, requires_reference=False, reference_label=""):
        """Add a new payment method"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO PaymentMethods (
                        name, code, is_active, requires_reference, reference_label
                    ) VALUES (?, ?, 1, ?, ?)
                """, (name, code, 1 if requires_reference else 0, reference_label))
                
                conn.commit()
                return cursor.lastrowid
            except Exception as e:
                print(f"Error adding payment method: {e}")
                return None
            finally:
                conn.close()
        return None
    
    @staticmethod
    def update_payment_method(method_id, name=None, code=None, is_active=None, requires_reference=None, reference_label=None):
        """Update an existing payment method"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Build update query with only provided fields
                update_fields = []
                params = []
                
                if name is not None:
                    update_fields.append("name = ?")
                    params.append(name)
                    
                if code is not None:
                    update_fields.append("code = ?")
                    params.append(code)
                    
                if is_active is not None:
                    update_fields.append("is_active = ?")
                    params.append(1 if is_active else 0)
                    
                if requires_reference is not None:
                    update_fields.append("requires_reference = ?")
                    params.append(1 if requires_reference else 0)
                    
                if reference_label is not None:
                    update_fields.append("reference_label = ?")
                    params.append(reference_label)
                
                if not update_fields:
                    return False
                    
                params.append(method_id)
                
                query = f"""
                    UPDATE PaymentMethods
                    SET {', '.join(update_fields)}
                    WHERE id = ?
                """
                
                cursor.execute(query, params)
                conn.commit()
                
                return cursor.rowcount > 0
            except Exception as e:
                print(f"Error updating payment method: {e}")
                return False
            finally:
                conn.close()
        return False
    
    @staticmethod
    def add_payment_to_sale(sale_id, payments):
        """
        Add payment details to a sale
        
        Args:
            sale_id: The ID of the sale to add payments to
            payments: List of payment dictionaries with method_id, amount, and reference
        """
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Start transaction
                cursor.execute("BEGIN TRANSACTION")
                
                for payment in payments:
                    method_id = payment.get('method_id')
                    amount = payment.get('amount', 0)
                    reference = payment.get('reference', '')
                    
                    if amount <= 0:
                        continue
                        
                    cursor.execute("""
                        INSERT INTO SalePayments (
                            sale_id, payment_method_id, amount, reference
                        ) VALUES (?, ?, ?, ?)
                    """, (sale_id, method_id, amount, reference))
                
                # Commit transaction
                cursor.execute("COMMIT")
                return True
            except Exception as e:
                cursor.execute("ROLLBACK")
                print(f"Error adding payment to sale: {e}")
                return False
            finally:
                conn.close()
        return False
    
    @staticmethod
    def get_sale_payments(sale_id):
        """Get all payments for a specific sale"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        sp.id, sp.sale_id, sp.payment_method_id, 
                        pm.name as payment_method, pm.code,
                        sp.amount, sp.reference, sp.created_at
                    FROM SalePayments sp
                    LEFT JOIN PaymentMethods pm ON sp.payment_method_id = pm.id
                    WHERE sp.sale_id = ?
                    ORDER BY sp.id
                """, (sale_id,))
                
                payments = cursor.fetchall()
                return payments
            except Exception as e:
                print(f"Error getting sale payments: {e}")
                return []
            finally:
                conn.close()
        return []
    
    @staticmethod
    def get_payment_summary(start_date=None, end_date=None):
        """Get summary of payments by method within date range"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                query = """
                    SELECT 
                        COALESCE(pm.name, 'Autre') as payment_method,
                        COUNT(sp.id) as transaction_count,
                        SUM(sp.amount) as total_amount
                    FROM SalePayments sp
                    LEFT JOIN PaymentMethods pm ON sp.payment_method_id = pm.id
                    LEFT JOIN Sales s ON sp.sale_id = s.id
                """
                
                params = []
                where_clauses = []
                
                if start_date:
                    where_clauses.append("s.created_at >= ?")
                    params.append(f"{start_date} 00:00:00")
                    
                if end_date:
                    where_clauses.append("s.created_at <= ?")
                    params.append(f"{end_date} 23:59:59")
                
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
                
                query += """
                    GROUP BY payment_method
                    ORDER BY total_amount DESC
                """
                
                cursor.execute(query, params)
                payment_summary = cursor.fetchall()
                
                return payment_summary
            except Exception as e:
                print(f"Error getting payment summary: {e}")
                return []
            finally:
                conn.close()
        return []
