from calculator import calculator
from shoppingCart import shoppingCart

# numbers1 = calculator(7, 5)
# print("7+5 =", numbers1.addition())

# numbers2 = calculator(34, 21)
# print("34-21 =",numbers2.subtraction())

# numbers3 = calculator(54, 2)
# print("54*2 =", numbers3.multiplication())

# numbers4 = calculator(144, 2)
# print("144/2 =", numbers4.division())

# numbers5 = calculator(45, 0)
# print("45/0 =", numbers5.division())

myShoppingCart = shoppingCart()

myShoppingCart.addItem("apples", 3)
myShoppingCart.addItem("bananas", 2)
myShoppingCart.addItem("oranges", 15)

for item in myShoppingCart.items:
    print(item)

print("Number of Items:", myShoppingCart.calculateTotalItems())

myShoppingCart.removeItem("bananas")

for item in myShoppingCart.items:
    print(item)