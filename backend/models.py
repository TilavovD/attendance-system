from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the database URL (use SQLite here; change for MySQL/PostgreSQL)
DATABASE_URL = "sqlite:///attendance.db"

# Initialize SQLAlchemy components
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the Student model
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    photo = Column(String, nullable=False)  # Path to the student's photo

# Define the AttendanceLog model
class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)

# Create tables in the database
Base.metadata.create_all(bind=engine)
