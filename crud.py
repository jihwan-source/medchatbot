# crud.py
from sqlalchemy.orm import Session
import models

def get_clinic_by_clinic_id(db: Session, clinic_id: str):
    """
    고유 clinic_id를 사용하여 병원 정보를 조회합니다.
    """
    return db.query(models.Clinic).filter(models.Clinic.clinic_id == clinic_id).first()
