#!/usr/bin/env python3
"""
Database migration script to add new columns to existing exercise_tracker.db
"""
import sqlite3
import os

def migrate_database():
    db_path = 'exercise_tracker.db'
    
    if not os.path.exists(db_path):
        print("No existing database found. New database will be created automatically.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("Creating users table...")
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        # Check if new columns exist in exercises table
        cursor.execute("PRAGMA table_info(exercises)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_id' not in columns:
            print("Adding user_id column...")
            cursor.execute("ALTER TABLE exercises ADD COLUMN user_id INTEGER")
        
        if 'hiking_place' not in columns:
            print("Adding hiking_place column...")
            cursor.execute("ALTER TABLE exercises ADD COLUMN hiking_place TEXT")
        
        if 'weather_info' not in columns:
            print("Adding weather_info column...")
            cursor.execute("ALTER TABLE exercises ADD COLUMN weather_info TEXT")
        
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
