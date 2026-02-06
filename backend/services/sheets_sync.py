import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from .. import models, database
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

# Setup GSpread
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "configs/credentials.json")
SHEET_ID = os.getenv("SHEET_ID")

def get_sheet():
    try:
        # Check if creds exist
        if not os.path.exists(CREDS_PATH):
            print(f"[Sheets Error] Credentials file not found at {CREDS_PATH}")
            return None
            
        gc = gspread.service_account(filename=CREDS_PATH)
        sh = gc.open_by_key(SHEET_ID)
        return sh.sheet1 # or sh.get_worksheet(0)
    except Exception as e:
        print(f"[Sheets Error] Failed to connect: {e}")
        return None

def sync_user_to_sheets(user_id: int):
    """
    Syncs a user's data to Google Sheets.
    Finds row by Instagram Username (Col A) or appends new one.
    """
    print(f"[Sheets Sync] Starting sync for User ID {user_id}...")
    
    # Create a new DB session for this thread
    db = database.SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            print(f"[Sheets Sync] User {user_id} not found in DB.")
            return False

        ws = get_sheet()
        if not ws:
            return False
            
        # Prepare row data based on User Screenshot
        # Columns: [Username IG, Nombre, Interés Principal, ¿seguidor?, Score de lealtad, Fecha de entrada, rango]
        
        is_follower_str = "SÍ" if user.is_follower else "NO"
        
        row_data = [
            user.instagram_username,       # A
            user.full_name,                # B
            user.main_interest,            # C
            is_follower_str,               # D
            user.loyalty_score,            # E
            str(user.join_date.date()),    # F (Just date usually looks cleaner)
            user.rank                      # G
        ]
        
        # Search for user in sheet (column 1 is Username in the screenshot)
        try:
            cell = ws.find(user.instagram_username, in_column=1)
            if cell:
                # Update existing row
                row_num = cell.row
                # We update columns A through G
                ws.update(f"A{row_num}:G{row_num}", [row_data])
                print(f"[Sheets Sync] Updated row {row_num} for {user.instagram_username}")
            else:
                # Append new row
                ws.append_row(row_data)
                print(f"[Sheets Sync] Appended new row for {user.instagram_username}")
                
        except Exception as e:
            print(f"[Sheets Sync] Error during find/update: {e}")
            return False

    except Exception as e:
        print(f"[Sheets Sync] Critical Error: {e}")
    finally:
        db.close()
    
    return True
