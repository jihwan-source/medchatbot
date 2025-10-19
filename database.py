# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite 데이터베이스 파일 경로 설정
DATABASE_URL = "sqlite:///./pi_database.db"

# SQLAlchemy 엔진 생성
# connect_args는 SQLite 사용 시에만 필요하며, 다중 스레드 환경에서의 충돌을 방지합니다.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# 데이터베이스 세션을 생성하는 클래스
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델 클래스들이 상속받을 기본 클래스
Base = declarative_base()

# 의존성 주입을 위한 함수 (FastAPI 엔드포인트에서 사용)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
