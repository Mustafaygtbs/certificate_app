from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
import uuid
import datetime
from .database import Base

class User(Base):
    """Kullanıcı tablosu"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.username}>"

class Course(Base):
    """Eğitim tablosu"""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    instructor_name = Column(String(200), nullable=True)  # Eğitmen adı
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_completed = Column(Boolean, default=False)
    certificate_template_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # İlişki: Bir eğitimin birden çok öğrencisi olabilir
    students = relationship("Student", back_populates="course", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Course {self.name}>"

class Student(Base):
    """Öğrenci tablosu"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)  # E-posta zorunlu
    phone_number = Column(String(20), nullable=True)
    has_completed_course = Column(Boolean, default=False)
    certificate_url = Column(String(255), nullable=True)
    certificate_access_token = Column(String(36), default=lambda: str(uuid.uuid4()), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # İlişki: Bir öğrenci bir eğitime katılabilir
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    course = relationship("Course", back_populates="students")
    
    # E-posta ve kurs ID kombinasyonunun benzersiz olmasını sağla
    __table_args__ = (
        UniqueConstraint('email', 'course_id', name='uq_student_email_course'),
    )
    
    def __repr__(self):
        return f"<Student {self.first_name} {self.last_name}>"
