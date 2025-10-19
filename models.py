# models.py
from sqlalchemy import Column, Integer, String
from database import Base

class Clinic(Base):
    __tablename__ = "clinics"

    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(String, unique=True, index=True, nullable=False)
    clinic_name = Column(String, nullable=False)
    kakao_channel_id = Column(String, nullable=True)
