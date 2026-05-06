from calculator import calculator

# 7+5
numbers1 = calculator(7, 5)
print("7+5 =", numbers1.addition())

# 34-21
numbers2 = calculator(34, 21)
print("34-21 =",numbers2.subtraction())

# 54*2
numbers3 = calculator(54, 2)
print("54*2 =", numbers3.multiplication())

# 144/2
numbers4 = calculator(144, 2)
print("144/2 =", numbers4.division())

# 45/0
numbers5 = calculator(45, 0)
print("45/0 =", numbers5.division())