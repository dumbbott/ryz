from database import SessionLocal, init_db
from models import Student, Subject, Grade, User
from auth import AuthManager
from datetime import datetime, date
import random

def populate_test_data():
    init_db()
    
    auth_manager = AuthManager()
    auth_manager.create_admin_user()
    
    with SessionLocal() as session:
        session.query(Grade).delete()
        session.query(Student).delete()
        session.query(Subject).delete()
        session.commit()
        
        subjects_data = [
            'Математика', 'Физика', 'Информатика', 
            'История', 'Английский язык', 'Химия'
        ]
        
        subjects = []
        for name in subjects_data:
            subject = Subject(name=name)
            session.add(subject)
            subjects.append(subject)
        
        session.commit()
        
        students_data = [
            ('Иван', 'Иванов', 'ИТ-101'),
            ('Петр', 'Петров', 'ИТ-101'),
            ('Мария', 'Сидорова', 'ИТ-102'),
            ('Анна', 'Кузнецова', 'ИТ-102'),
            ('Сергей', 'Смирнов', 'ФИЗ-201'),
            ('Елена', 'Попова', 'ФИЗ-201'),
            ('Дмитрий', 'Васильев', 'ХИМ-301'),
            ('Ольга', 'Новикова', 'ХИМ-301'),
            ('Алексей', 'Морозов', 'ИТ-101'),
            ('Наталья', 'Волкова', 'ИТ-102')
        ]
        
        students = []
        for first_name, last_name, group_name in students_data:
            student = Student(first_name=first_name, last_name=last_name, group_name=group_name)
            session.add(student)
            students.append(student)
        
        session.commit()
        

        for student in students:
            for subject in subjects:
                for _ in range(random.randint(3, 5)):
                    grade = Grade(
                        student_id=student.id,
                        subject_id=subject.id,
                        grade=random.randint(3, 5),
                        date=date(2024, random.randint(1, 12), random.randint(1, 28))
                    )
                    session.add(grade)
        
        session.commit()
        print("Тестовые данные успешно добавлены!")

if __name__ == "__main__":
    populate_test_data()