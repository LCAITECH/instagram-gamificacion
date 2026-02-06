from backend import database, models
from sqlalchemy.orm import Session

db = database.SessionLocal()

# Check if exists
user = db.query(models.User).filter(models.User.instagram_username == "leandrobuchter").first()

if not user:
    user = models.User(
        instagram_username="leandrobuchter",
        full_name="Leandro",
        rank="Capitán Crypto 🚀", # Custom rank for demo
        loyalty_score=500,
        main_interest="Metales",
        is_follower=True
    )
    db.add(user)
    db.commit()
    print("User 'leandrobuchter' created!")
else:
    print("User already exists.")

db.close()
