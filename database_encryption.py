import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import sqlite3

# Load the encryption key from .env
load_dotenv()
encryption_key = os.getenv('ENCRYPTION_KEY')

# If no key exists, generate one and save it (do this once)
if not encryption_key:
    encryption_key = Fernet.generate_key()
    with open('.env', 'w') as f:
        f.write(f'ENCRYPTION_KEY={encryption_key.decode()}')

# Check if the key is already in bytes
if isinstance(encryption_key, str):
    encryption_key = encryption_key.encode()  # Convert to bytes only if it's a string

# Create Fernet instance
fernet = Fernet(encryption_key)

# Connect to SQLite database
conn = sqlite3.connect('secure_users.db')
cursor = conn.cursor()

# Create a table with an encrypted field
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        encrypted_ssn TEXT NOT NULL
    )
''')

# Encryption helper functions
def encrypt_data(data: str) -> str:
    """Encrypt a string."""
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt an encrypted string."""
    return fernet.decrypt(encrypted_data.encode()).decode()

# Example operations
def add_user(username: str, ssn: str):
    """Add a user with encrypted SSN."""
    encrypted_ssn = encrypt_data(ssn)
    cursor.execute(
        'INSERT INTO users (username, encrypted_ssn) VALUES (?, ?)',
        (username, encrypted_ssn)
    )
    conn.commit()
    print(f"User {username} added with encrypted SSN.")

def get_user(username: str) -> dict:
    """Retrieve a user and decrypt the SSN."""
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    if user:
        return {
            'id': user[0],
            'username': user[1],
            'ssn': decrypt_data(user[2])  # Decrypt SSN before returning
        }
    return None

def show_raw_data():
    """Display raw database content."""
    cursor.execute('SELECT * FROM users')
    raw_data = cursor.fetchall()
    print(f"Raw database content: {raw_data}")

# Demo usage
if __name__ == '__main__':
    # Add a user with encrypted SSN
    add_user('john_doe', '123-45-6789')
    
    # Retrieve and decrypt the user's SSN
    user = get_user('john_doe')
    print(f"Retrieved user: {user}")

    # Show the encrypted data in the database
    show_raw_data()

    conn.close()