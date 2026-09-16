import sqlite3

DATABASE = "skillgap.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def create_table():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            district TEXT,
            training TEXT
        )
    """)

    try:
        cursor.execute("""
            ALTER TABLE students
            ADD COLUMN employment_status TEXT DEFAULT 'Not Employed'
        """)
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("""
            ALTER TABLE students
            ADD COLUMN skills TEXT DEFAULT ''
        """)
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("""
        ALTER TABLE students
        ADD COLUMN training_status TEXT DEFAULT 'In Progress'
    """)
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("""
        ALTER TABLE students
        ADD COLUMN certification_status TEXT DEFAULT 'Not Certified'
    """)
    except sqlite3.OperationalError:
         pass

    connection.commit()
    connection.close()