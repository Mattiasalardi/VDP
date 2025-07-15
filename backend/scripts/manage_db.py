#!/usr/bin/env python3
"""
Database management script
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import create_tables, drop_tables
from app.core.seed_data import create_seed_data

def main():
    if len(sys.argv) < 2:
        print("Usage: python manage_db.py <command>")
        print("Commands:")
        print("  create-tables    Create all database tables")
        print("  drop-tables      Drop all database tables")
        print("  seed-data        Create seed data for testing")
        print("  reset-db         Drop, create, and seed database")
        return
    
    command = sys.argv[1]
    
    if command == "create-tables":
        print("Creating database tables...")
        create_tables()
        print("✅ Tables created successfully!")
        
    elif command == "drop-tables":
        print("Dropping database tables...")
        drop_tables()
        print("✅ Tables dropped successfully!")
        
    elif command == "seed-data":
        print("Creating seed data...")
        create_seed_data()
        
    elif command == "reset-db":
        print("Resetting database...")
        drop_tables()
        create_tables()
        create_seed_data()
        print("✅ Database reset completed!")
        
    else:
        print(f"Unknown command: {command}")
        return

if __name__ == "__main__":
    main()