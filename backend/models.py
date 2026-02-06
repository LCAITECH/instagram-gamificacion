from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    instagram_username = Column(String, unique=True, index=True)  # Username IG
    full_name = Column(String)                                    # Nombre
    main_interest = Column(String, default="General")             # Interés Principal
    is_follower = Column(Boolean, default=False)                  # ¿seguidor?
    loyalty_score = Column(Integer, default=0)                    # Score de lealtad
    rank = Column(String, default="Recién Llegado")               # rango
    join_date = Column(DateTime, default=datetime.utcnow)         # Fecha de entrada
    
    # Internal fields for validation/cross-platform
    telegram_id = Column(String, nullable=True, index=True)

    transactions = relationship("Transaction", back_populates="user")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    points_change = Column(Integer)
    reason = Column(String) # e.g., "Answer correct: Platino", "Onboarding"
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")
