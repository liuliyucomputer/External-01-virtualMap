import turtle

# 定义颜色列表
colors = ["red", "blue", "green", "black", "yellow"]

# 初始化turtle
t = turtle.Turtle()
t.speed(0)  # 设置绘图速度为最快

# 设置初始半径和半径增量
radius = 10
radius_increment = 20

# 循环绘制同心圆
for color in colors:
    t.pencolor(color)
    t.penup()
    t.goto(0, -radius)
    t.pendown()
    t.circle(radius)
    radius += radius_increment

# 绘制最外层的黄色边框
t.pencolor("yellow")
t.penup()
t.goto(0, -(radius))
t.pendown()
t.circle(radius)

# 隐藏turtle
t.hideturtle()

# 保持图形窗口显示
turtle.done()