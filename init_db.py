from app import app, db
from models import Group, GroupMessage, GroupMessageLike, Post, Comment, UserLike

def init_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
