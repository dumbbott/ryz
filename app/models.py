from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<User {self.username}>"

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    group_name = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    grades = relationship("Grade", back_populates="student", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Student {self.first_name} {self.last_name} ({self.group_name})>"

class Subject(Base):
    __tablename__ = 'subjects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now)
    
    grades = relationship("Grade", back_populates="subject", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Subject {self.name}>"

class Grade(Base):
    __tablename__ = 'grades'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    grade = Column(Integer, nullable=False)
    date = Column(Date, nullable=False, default=datetime.now().date)
    created_at = Column(DateTime, default=datetime.now)
    
    student = relationship("Student", back_populates="grades")
    subject = relationship("Subject", back_populates="grades")
    
    def __repr__(self):
        return f"<Grade Student:{self.student_id} Subject:{self.subject_id} Grade:{self.grade}>"