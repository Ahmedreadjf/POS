from database import get_connection
from datetime import datetime, UTC
import json

class ProductAttribute:
    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    @staticmethod
    def create_tables():
        """Ensure the attribute tables exist"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Create ProductAttributes table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ProductAttributes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create ProductAttributeValues table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ProductAttributeValues (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        attribute_id INTEGER NOT NULL,
                        value TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (attribute_id) REFERENCES ProductAttributes(id) ON DELETE CASCADE,
                        UNIQUE(attribute_id, value)
                    )
                """)
                
                conn.commit()
                return True
            except Exception as e:
                print(f"Error creating attribute tables: {e}")
                return False
            finally:
                conn.close()
        return False

    @staticmethod
    def get_all_attributes():
        """Get all product attributes"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, description, created_at
                    FROM ProductAttributes
                    ORDER BY name
                """)
                
                attributes = []
                for row in cursor.fetchall():
                    attributes.append({
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'created_at': row[3]
                    })
                return attributes
            except Exception as e:
                print(f"Error getting attributes: {e}")
                return []
            finally:
                conn.close()
        return []

    @staticmethod
    def add_attribute(name, description=None):
        """Add a new product attribute"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Check if attribute already exists
                cursor.execute("SELECT id FROM ProductAttributes WHERE name = ?", (name,))
                existing = cursor.fetchone()
                if existing:
                    return existing[0]  # Return existing attribute ID
                
                # Add new attribute
                try:
                    # For Python 3.11+
                    current_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
                except AttributeError:
                    # For older Python versions
                    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""
                    INSERT INTO ProductAttributes (name, description, created_at)
                    VALUES (?, ?, ?)
                """, (name, description, current_time))
                
                attribute_id = cursor.lastrowid
                conn.commit()
                return attribute_id
            except Exception as e:
                print(f"Error adding attribute: {e}")
                return None
            finally:
                conn.close()
        return None

    @staticmethod
    def update_attribute(attribute_id, name, description=None):
        """Update an existing attribute"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE ProductAttributes
                    SET name = ?, description = ?
                    WHERE id = ?
                """, (name, description, attribute_id))
                
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                print(f"Error updating attribute: {e}")
                return False
            finally:
                conn.close()
        return False

    @staticmethod
    def delete_attribute(attribute_id):
        """Delete an attribute and its values"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Start transaction
                cursor.execute("BEGIN TRANSACTION")
                
                # Delete attribute values
                cursor.execute("DELETE FROM ProductAttributeValues WHERE attribute_id = ?", (attribute_id,))
                
                # Delete attribute
                cursor.execute("DELETE FROM ProductAttributes WHERE id = ?", (attribute_id,))
                
                cursor.execute("COMMIT")
                return True
            except Exception as e:
                cursor.execute("ROLLBACK")
                print(f"Error deleting attribute: {e}")
                return False
            finally:
                conn.close()
        return False

    @staticmethod
    def get_attribute_values(attribute_id):
        """Get all values for a specific attribute"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, value
                    FROM ProductAttributeValues
                    WHERE attribute_id = ?
                    ORDER BY value
                """, (attribute_id,))
                
                values = []
                for row in cursor.fetchall():
                    values.append({
                        'id': row[0],
                        'value': row[1]
                    })
                return values
            except Exception as e:
                print(f"Error getting attribute values: {e}")
                return []
            finally:
                conn.close()
        return []

    @staticmethod
    def add_attribute_value(attribute_id, value):
        """Add a new value for an attribute"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Check if value already exists
                cursor.execute("""
                    SELECT id FROM ProductAttributeValues 
                    WHERE attribute_id = ? AND value = ?
                """, (attribute_id, value))
                existing = cursor.fetchone()
                if existing:
                    return existing[0]  # Return existing value ID
                
                # Add new value
                cursor.execute("""
                    INSERT INTO ProductAttributeValues (attribute_id, value)
                    VALUES (?, ?)
                """, (attribute_id, value))
                
                value_id = cursor.lastrowid
                conn.commit()
                return value_id
            except Exception as e:
                print(f"Error adding attribute value: {e}")
                return None
            finally:
                conn.close()
        return None

    @staticmethod
    def delete_attribute_value(value_id):
        """Delete an attribute value"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM ProductAttributeValues WHERE id = ?", (value_id,))
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                print(f"Error deleting attribute value: {e}")
                return False
            finally:
                conn.close()
        return False

    @staticmethod
    def generate_variant_combinations(attributes_values):
        """
        Generate all possible combinations of attribute values
        
        Args:
            attributes_values: A dict where keys are attribute names and values are lists of values
                e.g. {'Color': ['Red', 'Blue'], 'Size': ['S', 'M', 'L']}
        
        Returns:
            A list of dictionaries, each representing a variant combination
        """
        def generate_combinations(attrs, current=None, index=0):
            if current is None:
                current = {}
            
            if index >= len(attrs):
                return [current.copy()]
            
            attr_name = list(attrs.keys())[index]
            combinations = []
            
            for value in attrs[attr_name]:
                current[attr_name] = value
                combinations.extend(generate_combinations(attrs, current, index + 1))
            
            return combinations
        
        return generate_combinations(attributes_values)
