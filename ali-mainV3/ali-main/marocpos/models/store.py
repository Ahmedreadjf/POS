from database import get_connection

class Store:
    def __init__(self, name, location, active=1):
        self.name = name
        self.location = location
        self.active = active

    @staticmethod
    def create_table():
     """Create the Stores table if it doesn't exist."""
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Stores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                location TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_stores():
        """Fetch all stores from the database."""
        conn = get_connection()
        stores = []
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, location, active FROM Stores;")
            rows = cursor.fetchall()
            for row in rows:
                stores.append({
                    "id": row[0],
                    "name": row[1],
                    "location": row[2],
                    "active": row[3]
                })
            conn.close()
        return stores

    @staticmethod
    def add_store(store):
        """Add a new store to the database."""
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO Stores (name, location, active)
                    VALUES (?, ?, ?);
                """, (store.name, store.location, store.active))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error adding store: {e}")
                return False
            finally:
                conn.close()

    @staticmethod
    def update_store(store_id, name, location, active):
        """Update a store's details."""
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE Stores
                    SET name = ?, location = ?, active = ?
                    WHERE id = ?;
                """, (name, location, active, store_id))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error updating store: {e}")
                return False
            finally:
                conn.close()

    @staticmethod
    def delete_store(store_id):
        """Delete a store by its ID."""
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM Stores WHERE id = ?;", (store_id,))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error deleting store: {e}")
                return False
            finally:
                conn.close()