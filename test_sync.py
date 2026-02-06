import sys
import os

# Ensure backend is in path
sys.path.append(os.getcwd())

from backend import database, models
from backend.services import sheets_sync
import uuid

def test_sync():
    print("--- Starting Sheets Sync Test ---")
    
    # 1. Setup DB
    models.Base.metadata.create_all(bind=database.engine)
    db = database.SessionLocal()
    
    # 2. Create Dummy User
    unique_id = str(uuid.uuid4())[:8]
    username = f"test_user_{unique_id}"
    
    print(f"Creating test user: {username}")
    user = models.User(
        instagram_username=username,
        full_name="Test User",
        main_interest="Testing",
        rank="Beta Tester",
        loyalty_score=100,
        telegram_id="123456789"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"User created with ID: {user.id}")
    
    # 3. Call Sync
    print("Calling sync_user_to_sheets...")
    try:
        success = sheets_sync.sync_user_to_sheets(user.id)
        if success:
            print("✅ Sync Success! Check your Google Sheet.")
        else:
            print("❌ Sync Failed. Check logs above.")
    except Exception as e:
        print(f"❌ Exception during sync: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_sync()
