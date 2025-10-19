# init_db.py
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Clinic

def init_db():
    # 데이터베이스에 모든 테이블 생성
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    # 파일럿 병원 정보가 이미 존재하는지 확인
    pilot_clinic = db.query(Clinic).filter(Clinic.clinic_id == "happy-clinic-seoul").first()

    if not pilot_clinic:
        # 정보가 없으면 새로 추가
        new_clinic = Clinic(
            clinic_id="happy-clinic-seoul",
            clinic_name="행복가정의학과의원",
            kakao_channel_id="@행복의원"
        )
        db.add(new_clinic)
        db.commit()
        print("✅ 파일럿 병원 정보가 성공적으로 추가되었습니다.")
    else:
        print("ℹ️ 파일럿 병원 정보가 이미 존재합니다.")

    db.close()

if __name__ == "__main__":
    print("데이터베이스 초기화를 시작합니다...")
    init_db()
    print("데이터베이스 초기화가 완료되었습니다.")
