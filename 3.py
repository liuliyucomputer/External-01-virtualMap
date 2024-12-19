import turtle

# 定义颜色列表
colors = ["purple", "red", "yellow", "green"]

# 初始化turtle
t = turtle.Turtle()
t.speed(1)  # 设置绘图速度

# 设置初始位置
t.penup()
t.goto(-100, 0)
t.pendown()

# 绘制蟒蛇
for color in colors:
    t.pencolor(color)
    t.circle(40, 90)
    t.circle(-40, 90)

# 绘制蟒蛇头部
t.pencolor("pink")
t.circle(40, 90)
t.circle(-40, 90)
t.circle(40, 90)
t.circle(-40, 90)

# 隐藏turtle
t.hideturtle()

# 保持图形窗口显示
turtle.done()