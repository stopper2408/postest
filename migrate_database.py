#!/usr/bin/env python3
"""
Database Migration Script
Adds new columns to existing database tables
"""
import sqlite3
import os

def migrate_database():
    db_path = 'posTable.db'
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. No migration needed - will be created fresh.")
        return
    
    print(f"Migrating database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if created_at column exists
        cursor.execute("PRAGMA table_info(orders)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add missing columns to orders table
        # SQLite doesn't support adding columns with non-constant defaults or NOT NULL without defaults
        # We need to use a workaround
        if 'created_at' not in columns:
            print("Adding 'created_at' column to orders table...")
            cursor.execute("ALTER TABLE orders ADD COLUMN created_at DATETIME")
            # Update existing rows to have timestamps with slight increments to preserve order
            # This uses rowid to create incremental timestamps (1 second apart)
            cursor.execute("""
                UPDATE orders 
                SET created_at = datetime('now', '-' || (
                    (SELECT MAX(rowid) FROM orders) - rowid
                ) || ' seconds')
                WHERE created_at IS NULL
            """)
            print("✓ Added 'created_at' column with preserved order")
        
        if 'seat_number' not in columns:
            print("Adding 'seat_number' column to orders table...")
            cursor.execute("ALTER TABLE orders ADD COLUMN seat_number INTEGER")
            print("✓ Added 'seat_number' column")
        
        if 'voided' not in columns:
            print("Adding 'voided' column to orders table...")
            cursor.execute("ALTER TABLE orders ADD COLUMN voided INTEGER DEFAULT 0")
            print("✓ Added 'voided' column")
        
        # Create settings table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key VARCHAR NOT NULL UNIQUE,
                value VARCHAR NOT NULL
            )
        """)
        print("✓ Settings table ensured")
        
        # Create receipts table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_id INTEGER NOT NULL,
                total_amount FLOAT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                receipt_data VARCHAR NOT NULL
            )
        """)
        print("✓ Receipts table ensured")
        
        # Create indexes
        print("Creating indexes...")
        
        # Check if indexes already exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        existing_indexes = [row[0] for row in cursor.fetchall()]
        
        if 'ix_orders_table_id' not in existing_indexes:
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_orders_table_id ON orders (table_id)")
            print("✓ Created index on orders.table_id")
        
        if 'ix_orders_status' not in existing_indexes:
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_orders_status ON orders (status)")
            print("✓ Created index on orders.status")
        
        if 'ix_orders_created_at' not in existing_indexes:
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_orders_created_at ON orders (created_at)")
            print("✓ Created index on orders.created_at")
        
        if 'idx_table_status' not in existing_indexes:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_table_status ON orders (table_id, status)")
            print("✓ Created compound index on orders(table_id, status)")
        
        if 'idx_created_status' not in existing_indexes:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_status ON orders (created_at, status)")
            print("✓ Created compound index on orders(created_at, status)")
        
        if 'ix_receipts_created_at' not in existing_indexes:
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_receipts_created_at ON receipts (created_at)")
            print("✓ Created index on receipts.created_at")
        
        conn.commit()
        print("\n✅ Database migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
