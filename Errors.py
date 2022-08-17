class InvalidGradeError(Exception):
    #throw an error letting the user know the grade they entered in invalid and write comments to explain the code
    def __init__(self, grade): #grade is the grade that the user entered
        self.grade = grade
    def __str__(self):
        error = ""
        if (self.grade < 0):
            error = "Grade cannot be negative!?"
        elif (self.grade > 100):
            error = "Grade cannot be greater than 100!?"
        return f"""Invalid Grade: The grade you entered is: {str(self.grade)}. {error}"""

