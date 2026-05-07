# class to calculate numbers (addition/subtraction/multiplication/division)
class calculator:

    def __init__(self, number1, number2):
        self.num1 = number1
        self.num2 = number2

    # addition: adds one number to another and returns the result
    def addition(self):
        return self.num1 + self.num2

    # subtraction: subtracts num2 from num1 and returns the result
    def subtraction(self):
        return self.num1 - self.num2

    # multiplication: multipies two numbers
    def multiplication(self):
        return self.num1 * self.num2

    # division: divides num1 by num2
    def division(self):
        # if the second number is a 0, throw an error
        if (self.num2 == 0):
            return "ERROR: You can't divide by 0"
        return self.num1 / self.num2