"""
Run this once to create all database tables.
Usage: python init_db.py
"""
from app.database.db import create_tables

if __name__ == "__main__":
    create_tables()
    print("✅ Database tables created successfully!")
