from Student import Student

class StudentData:
    students: Student = []
    def __init__(self, cursor):
        student_data = list[Student](cursor)
        for student_row in student_data:
            StudentData.students.append(Student(student_row[0], student_row[1], student_row[2], student_row[3]))
