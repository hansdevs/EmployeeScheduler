"""
User Service
Handles user account management and authentication
"""

import os
import json
import hashlib
import secrets
import time
from typing import Dict, List, Optional, Any, Union

# File paths for data storage
USERS_FILE = 'data/users.json'
SESSIONS_FILE = 'data/sessions.json'

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

class UserService:
   def __init__(self):
       """Initialize the user service"""
       # Create users file if it doesn't exist
       if not os.path.exists(USERS_FILE):
           with open(USERS_FILE, 'w') as f:
               json.dump([], f)
       
       # Create sessions file if it doesn't exist
       if not os.path.exists(SESSIONS_FILE):
           with open(SESSIONS_FILE, 'w') as f:
               json.dump({}, f)
   
   def get_all_users(self) -> List:
       """Get all users (admin function)"""
       try:
           with open(USERS_FILE, 'r') as f:
               return json.load(f)
       except Exception as e:
           print(f"Error loading users: {e}")
           return []
   
   def get_user_by_email(self, email: str) -> Optional[Dict]:
       """Get a user by email"""
       users = self.get_all_users()
       
       for user in users:
           if user.get("email", "").lower() == email.lower():
               return user
       
       return None
   
   def get_user_by_id(self, user_id: int) -> Optional[Dict]:
       """Get a user by ID"""
       users = self.get_all_users()
       
       for user in users:
           if user.get("id") == user_id:
               return user
       
       return None
   
   def create_user(self, user_data: Dict) -> Dict:
       """Create a new user account"""
       users = self.get_all_users()
       
       # Check if email already exists
       if self.get_user_by_email(user_data.get("email", "")):
           return {"error": "Email already in use"}
       
       # Generate a new ID
       new_id = 1
       if users:
           new_id = max(user.get("id", 0) for user in users) + 1
       
       # Hash the password
       password = user_data.get("password", "")
       salt = secrets.token_hex(16)
       password_hash = self._hash_password(password, salt)
       
       # Create the user object
       new_user = {
           "id": new_id,
           "email": user_data.get("email", "").lower(),
           "name": user_data.get("name", ""),
           "company_name": user_data.get("company_name", ""),
           "password_hash": password_hash,
           "salt": salt,
           "role": user_data.get("role", "user"),
           "created_at": int(time.time()),
           "theme": "light"
       }
       
       # Add the user to the list
       users.append(new_user)
       
       # Save the updated list
       try:
           with open(USERS_FILE, 'w') as f:
               json.dump(users, f, indent=2)
           
           # Create a session for the new user
           session_id = self._create_session(new_id)
           
           # Return the user without sensitive data, but with session_id
           sanitized_user = self._sanitize_user(new_user)
           sanitized_user["session_id"] = session_id
           
           return sanitized_user
       except Exception as e:
           print(f"Error saving user: {e}")
           return {"error": f"Failed to create user: {str(e)}"}
   
   def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
       """Authenticate a user with email and password"""
       user = self.get_user_by_email(email)
       
       if not user:
           return None
       
       # Check the password
       salt = user.get("salt", "")
       stored_hash = user.get("password_hash", "")
       
       if self._hash_password(password, salt) == stored_hash:
           # Create a session
           session_id = self._create_session(user.get("id"))
           
           # Return the user with session ID
           sanitized_user = self._sanitize_user(user)
           sanitized_user["session_id"] = session_id
           
           return sanitized_user
       
       return None
   
   def validate_session(self, session_id: str) -> Optional[Dict]:
       """Validate a session and return the user if valid"""
       try:
           with open(SESSIONS_FILE, 'r') as f:
               sessions = json.load(f)
           
           session = sessions.get(session_id)
           if not session:
               return None
           
           # Check if session is expired
           if session.get("expires_at", 0) < int(time.time()):
               # Remove expired session
               del sessions[session_id]
               with open(SESSIONS_FILE, 'w') as f:
                   json.dump(sessions, f, indent=2)
               return None
           
           # Get the user
           user = self.get_user_by_id(session.get("user_id"))
           if not user:
               return None
           
           # Return sanitized user
           return self._sanitize_user(user)
       except Exception as e:
           print(f"Error validating session: {e}")
           return None
   
   def logout(self, session_id: str) -> bool:
       """Log out a user by invalidating their session"""
       try:
           with open(SESSIONS_FILE, 'r') as f:
               sessions = json.load(f)
           
           if session_id in sessions:
               del sessions[session_id]
               
               with open(SESSIONS_FILE, 'w') as f:
                   json.dump(sessions, f, indent=2)
               
               return True
           
           return False
       except Exception as e:
           print(f"Error logging out: {e}")
           return False
   
   def update_user_theme(self, user_id: int, theme: str) -> bool:
       """Update a user's theme preference"""
       users = self.get_all_users()
       
       for i, user in enumerate(users):
           if user.get("id") == user_id:
               users[i]["theme"] = theme
               
               try:
                   with open(USERS_FILE, 'w') as f:
                       json.dump(users, f, indent=2)
                   
                   return True
               except Exception as e:
                   print(f"Error updating user theme: {e}")
                   return False
       
       return False
   
   def _hash_password(self, password: str, salt: str) -> str:
       """Hash a password with the given salt"""
       # Combine password and salt
       salted = password + salt
       
       # Hash using SHA-256
       return hashlib.sha256(salted.encode()).hexdigest()
   
   def _create_session(self, user_id: int) -> str:
       """Create a new session for a user"""
       try:
           with open(SESSIONS_FILE, 'r') as f:
               sessions = json.load(f)
           
           # Generate a session ID
           session_id = secrets.token_hex(32)
           
           # Create the session
           sessions[session_id] = {
               "user_id": user_id,
               "created_at": int(time.time()),
               "expires_at": int(time.time()) + (7 * 24 * 60 * 60)  # 7 days
           }
           
           # Save the sessions
           with open(SESSIONS_FILE, 'w') as f:
               json.dump(sessions, f, indent=2)
           
           return session_id
       except Exception as e:
           print(f"Error creating session: {e}")
           return ""
   
   def _sanitize_user(self, user: Dict) -> Dict:
       """Remove sensitive data from a user object"""
       sanitized = user.copy()
       
       # Remove sensitive fields
       if "password_hash" in sanitized:
           del sanitized["password_hash"]
       if "salt" in sanitized:
           del sanitized["salt"]
       
       return sanitized

