import sys
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.services.user import create_admin_user
from app.core.logging import logger

def create_admin(email: str, username: str, password: str):
    """
    Create an admin user
    """
    db = SessionLocal()
    try:
        admin = create_admin_user(db, email, username, password)
        print(f"Admin user created or updated: {admin.username} (ID: {admin.id})")
        return admin
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        logger.error(f"Error creating admin user: {str(e)}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python create_admin.py <email> <username> <password>")
        sys.exit(1)
        
    email = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    
    create_admin(email, username, password)