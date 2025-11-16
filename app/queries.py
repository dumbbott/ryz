from sqlalchemy import func, desc, and_, or_
from datetime import datetime, date, timedelta
from database import SessionLocal
from models import Student, Subject, Grade

class JournalQueries:
    
    def get_all_students(self):
        with SessionLocal() as session:
            return session.query(Student).order_by(Student.last_name, Student.first_name).all()
    
    def get_student_by_id(self, student_id):
        with SessionLocal() as session:
            return session.query(Student).filter(Student.id == student_id).first()
    
    def add_student(self, first_name, last_name, group_name):
        with SessionLocal() as session:
            student = Student(first_name=first_name, last_name=last_name, group_name=group_name)
            session.add(student)
            session.commit()
            return student
    
    def delete_student(self, student_id):
        with SessionLocal() as session:
            student = session.query(Student).filter(Student.id == student_id).first()
            if student:
                session.delete(student)
                session.commit()
                return True
            return False
    
    def get_all_subjects(self):
        with SessionLocal() as session:
            return session.query(Subject).order_by(Subject.name).all()
    
    def get_subject_by_name(self, subject_name):
        with SessionLocal() as session:
            return session.query(Subject).filter(Subject.name == subject_name).first()
    
    def add_subject(self, name):
        with SessionLocal() as session:
            subject = Subject(name=name)
            session.add(subject)
            session.commit()
            return subject
    
    def add_grade(self, student_id, subject_id, grade_value, grade_date=None):
        with SessionLocal() as session:
            if grade_date is None:
                grade_date = date.today()
            
            grade = Grade(
                student_id=student_id,
                subject_id=subject_id,
                grade=grade_value,
                date=grade_date
            )
            session.add(grade)
            session.commit()
            return grade
    
    def get_student_grades(self, student_id):
        with SessionLocal() as session:
            grades = (session.query(Grade, Subject.name)
                     .join(Subject, Grade.subject_id == Subject.id)
                     .filter(Grade.student_id == student_id)
                     .order_by(desc(Grade.date))
                     .all())
            
            return [{
                'id': grade.id,
                'subject': subject_name,
                'grade': grade.grade,
                'date': grade.date
            } for grade, subject_name in grades]
    
    def get_student_average(self, student_id):
        with SessionLocal() as session:
            average = (session.query(func.avg(Grade.grade))
                      .filter(Grade.student_id == student_id)
                      .scalar())
            return round(average, 2) if average else 0.0
    
    def get_subject_statistics(self, subject_id):
        with SessionLocal() as session:
            stats = (session.query(
                func.count(Grade.id).label('total_grades'),
                func.avg(Grade.grade).label('average_grade'),
                func.min(Grade.grade).label('min_grade'),
                func.max(Grade.grade).label('max_grade')
            ).filter(Grade.subject_id == subject_id).first())
            
            return {
                'total_grades': stats.total_grades or 0,
                'average_grade': round(stats.average_grade, 2) if stats.average_grade else 0.0,
                'min_grade': stats.min_grade or 0,
                'max_grade': stats.max_grade or 0
            }
    
    def get_top_students(self, limit=10):
        with SessionLocal() as session:
            top_students = (session.query(
                Student.id,
                Student.first_name,
                Student.last_name,
                Student.group_name,
                func.avg(Grade.grade).label('average_grade')
            )
            .join(Grade, Student.id == Grade.student_id)
            .group_by(Student.id)
            .having(func.count(Grade.id) >= 3)
            .order_by(desc('average_grade'))
            .limit(limit)
            .all())
            
            return [{
                'id': student_id,
                'name': f"{last_name} {first_name}",
                'group': group_name,
                'average_grade': round(avg_grade, 2)
            } for student_id, first_name, last_name, group_name, avg_grade in top_students]
    
    def search_students(self, search_term):
        with SessionLocal() as session:
            search_pattern = f"%{search_term}%"
            students = (session.query(Student)
                       .filter(or_(
                           Student.first_name.ilike(search_pattern),
                           Student.last_name.ilike(search_pattern),
                           Student.group_name.ilike(search_pattern)
                       ))
                       .order_by(Student.last_name, Student.first_name)
                       .all())
            return students
def get_student_by_id(self, student_id):
    with SessionLocal() as session:
        return session.query(Student).filter(Student.id == student_id).first()

def get_subject_by_name(self, subject_name):
    with SessionLocal() as session:
        return session.query(Subject).filter(Subject.name == subject_name).first()        