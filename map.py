import numpy as np
from scipy.optimize import fsolve

# 定义目标函数f(r)，即等式右边的表达式与6074.08的差值
def f(r):
    return (- 243.1466372 / (1 + r) + 257.4922888 / (1 + r) ** 2 + 272.684334 / (1 + r) ** 3 +
            288.77271 / (1 + r) ** 4 + 305.8102994 / (1 + r) ** 5 - 6074.08)

# 初始猜测值
initial_guess = 0.01  
# 使用fsolve函数求解r的值，需要提供目标函数f和初始猜测值initial_guess
r_solution = fsolve(f, initial_guess)
print("隐含折现率r的值约为:", r_solution)