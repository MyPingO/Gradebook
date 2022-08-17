# import MySQL library
from datetime import datetime
import mysql.connector
from pathlib import Path
import json
from mysql.connector import errorcode

from Errors import InvalidGradeError
from Student import Student
from StudentData import StudentData

from termcolor import colored
# establish and connect to a MySQL database

#MySQL login information should be stored in a JSON file, in my case called login.json
json_login_file_path = Path("login.json")
with json_login_file_path.open() as json_login_file:
    login_data = json.load(json_login_file)
    json_login_file.close()
try:
    db = mysql.connector.connect(
    host=login_data["host"],
    user=login_data["user"],
    passwd=login_data["password"],
    database=login_data["database"]
)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Could not connect: Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Could not connect: Database does not exist")
    else:
        print(f"Could not connect: {err.msg}")
    exit()

def get_letter_grade(grade):
    if (grade < 0): 
        raise InvalidGradeError(grade)
    if (grade <= 59):
        return "F"
    elif (grade <= 62):
        return "D-"
    elif (grade <= 66):
        return "D"
    elif (grade <= 69):
        return "D+"
    elif (grade <= 72):
        return "C-"
    elif (grade <= 76):
        return "C"
    elif (grade <= 79):
        return "C+"
    elif (grade <= 82):
        return "B-"
    elif (grade <= 86):
        return "B"
    elif (grade <= 89):
        return "B+"
    elif (grade <= 92):
        return "A-"
    elif (grade <= 96):
        return "A"
    else:
        return "A+"
        
def add_student_to_gradebook(students: list[Student]):
    while True:
        first_name = input("Enter first name: ")
        last_name = input("Enter last name: ")
        test_number = int(input("Enter test number: "))
        grade = int(input("Input a grade: "))
        try:
            letter_grade = get_letter_grade(grade)
            break
        except InvalidGradeError as err:
            print(err)

    insert_student_to_gradebook(first_name, last_name, grade, letter_grade, test_number)

def insert_student_to_gradebook(first_name, last_name, grade, letter_grade, test_number):
    try:
        # insert a row into the table
        cursor.execute("insert into students (first_name, last_name, average, letter_grade) values (%s, %s, %s, %s)", (first_name, last_name, grade, letter_grade))
        cursor.execute("insert into grades (student_id, test_number, grade, letter_grade, date) values (%s, %s, %s, %s, %s)", (cursor.lastrowid, test_number, grade, letter_grade, datetime.now()))
        db.commit()
        cursor.execute("select * from students")
        print("STUDENTS:")
        for row in cursor:
            print(row)
        print("Updated database!")
    except mysql.connector.Error as err:
        print(f"Could not insert row: {err.msg}")
        exit()

def add_new_student_grade(students: list[Student]):
    print_student_ID_and_names(students)
    student_id = int(input("Please enter the ID of the student you want to add a grade to: "))
    test_number = int(input("Please enter the test number: "))
    new_grade = float(input("Please enter the grade you want to give: "))
    try:
        #insert new grade entry for specified student
        cursor.execute("insert into grades (student_id, test_number, grade, letter_grade, date) values (%s, %s, %s, %s, %s)", (student_id, test_number, new_grade, get_letter_grade(new_grade), datetime.now()))
        cursor.execute("select grade from grades where student_id = %s", (student_id,))
        
        #calculate the average grade for the student
        grade_average = round(sum([row[0] for row in cursor]) / cursor.rowcount)

        #update the specified student's average in the students table
        cursor.execute("update students set average = %s, letter_grade = %s where id = %s", (grade_average, get_letter_grade(grade_average), student_id))
        cursor.execute("select * from students")
        for row in cursor:
            print(row)
        db.commit()
        print("Updated database!")
    except mysql.connector.Error as err:
        print(f"Could not insert row: {err.msg}")
        exit()

def print_student_ID_and_names(students: list[Student]):
    student_names = {}
    for student in students:
        student_names[student.id] = student.first_name + " " + student.last_name
    for id, name in sorted(student_names.items()):
        print(f"{id}: {name}")

def get_studentID_from_gradebook(): #TODO: make this function work
    cursor.execute("select * from students")
    for row in cursor:
        print(row)
    pass

def retrieve_all_students_data() -> StudentData:
    cursor.execute("select * from students")
    return StudentData(cursor)

def retrieve_student_info(students: list[Student]):
    print_student_ID_and_names(students)
    student_id = int(input("Please enter the ID of the student you want to retrieve: "))
    cursor.execute("select * from students where id = %s", (student_id,))
    for row in cursor:
        print(f"\nInformation for Student {student_id}: {row}\n")
    
    # get the column names of the table to display them with the row information
    cursor.execute("select * from grades where student_id = %s", (student_id,))
    print(f"Test grades from Student {student_id}:")
    print_table_info(cursor)
     
def get_class_average(students: list[Student]):
    print()
    for student in students:
        print(f"{student.first_name} {student.last_name} has an average grade of {student.average}")
    print(f"\nClass average: {sum([student.average for student in students]) / len(students)}")

def get_all_student_info(students: list[Student]):
    for student in students:
        print(f"\nStudent #{student.id}: {student.first_name} {student.last_name} - Average: {student.average} | {get_letter_grade(student.average)}\n")
        cursor.execute("select * from grades where student_id = %s", (student.id,))
        print(f"{student.first_name} {student.last_name}'s test grades:")
        print_table_info(cursor)

def print_table_info(cursor: mysql.connector.cursor):
    # get the column names of the table to display them with the row information
    columns = cursor.description
    result = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
    for row in result:
        print(row)

cursor = db.cursor(buffered=True)
# cheetsheet for SQL commands
# cursor.execute("alter table students add column last_name varchar(255) after name") // add column
# cursor.execute("alter table students rename column name to first_name") // rename column
# cursor.execute("truncate table students") // truncate table

db.commit()


while True:
    student_data = retrieve_all_students_data()
    cursor.execute("describe students")
    # A. done
    # B. done
    option = input(
    """Choose an option (type "Exit" to exit):\n
    A. Add a student to the gradebook\n
    B. Give an existing student a new grade\n
    C. Retrieve a student's information\n
    D. Get the average of all students\n
    E. Retrieve every student's information\n""").upper()
    
    options = {
        "A": add_student_to_gradebook,
        "B": add_new_student_grade,
        "C": retrieve_student_info,
        "D": get_class_average,
        "E": get_all_student_info
    }

    try:
        if option == "EXIT":
            exit()
        options[option](student_data.students)
        input("\nPress enter to continue...\n")
    except KeyError:
        print(f"Invalid option: {option} \n Error: {KeyError}")
        exit()