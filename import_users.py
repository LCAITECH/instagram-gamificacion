import sys
import os
from datetime import datetime

# Ensure backend can be imported
sys.path.append(os.getcwd())

from backend import database, models
from backend.services import sheets_sync

def import_users():
    print("--- 📥 Importing Users from Google Sheets ---")
    
    # 1. Connect to Sheet
    ws = sheets_sync.get_sheet()
    if not ws:
        print("❌ Could not connect to Sheet. Check .env config.")
        return

    # 2. Get all data
    print("Reading rows from Sheet...")
    rows = ws.get_all_values()
    
    # Header is row 0: [Username IG, Nombre, Interés Principal, ¿seguidor?, Score, Fecha, rango]
    # We skip header
    headers = rows[0]
    data_rows = rows[1:]
    
    # 3. Setup DB
    db = database.SessionLocal()
    
    count = 0
    for row in data_rows:
        try:
            # Safe get by index
            username = row[0].strip() if len(row) > 0 else ""
            if not username: continue
            
            full_name = row[1].strip() if len(row) > 1 else "Unknown"
            interest = row[2].strip() if len(row) > 2 else "General"
            follower_str = row[3].strip().upper() if len(row) > 3 else "NO"
            is_follower = True if "SÍ" in follower_str or "SI" in follower_str else False
            
            try:
                score = int(row[4]) if len(row) > 4 and row[4].strip().isdigit() else 0
            except:
                score = 0
                
            join_date_str = row[5].strip() if len(row) > 5 else ""
            # Parse date? Let's just keep it simple or default to now if parse fails
            # For this simple engine, we might not strictly parse it back to datetime obj perfectly yet
            # forcing a default for now to avoid errors
            join_date = datetime.utcnow() 
            
            rank = row[6].strip() if len(row) > 6 else "Novato"
            
            # Upsert
            user = db.query(models.User).filter(models.User.instagram_username == username).first()
            if not user:
                user = models.User(instagram_username=username)
                db.add(user)
                print(f"Creating new user: {username}")
            else:
                print(f"Updating existing user: {username}")
                
            user.full_name = full_name
            user.main_interest = interest
            user.is_follower = is_follower
            user.loyalty_score = score
            user.rank = rank
            # user.join_date = join_date # Skip overwriting date for complex format reasons for now
            
            count += 1
            
        except Exception as e:
            print(f"⚠️ Error processing row {row}: {e}")
            
    db.commit()
    db.close()
    print(f"--- ✅ Import Finished. Processed {count} users. ---")

if __name__ == "__main__":
    import_users()
