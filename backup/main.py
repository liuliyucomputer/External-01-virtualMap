import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# 创建图
G = nx.Graph()

# 添加建筑物节点和位置
buildings = {
    "左岸宿舍A": {"pos": (0, 8)},
    "左岸宿舍B": {"pos": (0, 6)},
    "左岸宿舍C": {"pos": (0, 4)},
    "D食堂": {"pos": (2, 6)},
    "右岸宿舍D": {"pos": (8, 8)},
    "右岸宿舍E": {"pos": (8, 6)},
    "右岸宿舍F": {"pos": (8, 4)},
    "F食堂": {"pos": (6, 6)},
    "教学楼1": {"pos": (6, 2)},
    "教学楼2": {"pos": (7, 1)},
    "教学楼3": {"pos": (8, 0)},
    "教学楼4": {"pos": (9, -1)}
}

# 添加节点
for building, attr in buildings.items():
    G.add_node(building, pos=attr['pos'])

# 添加路径（边），示例数据
edges = [
    ("左岸宿舍A", "D食堂", {"capacity": 10, "length": 100, "difficulty": 1}),
    ("左岸宿舍B", "D食堂", {"capacity": 10, "length": 100, "difficulty": 1}),
    ("左岸宿舍C", "D食堂", {"capacity": 10, "length": 100, "difficulty": 1}),
    ("右岸宿舍D", "F食堂", {"capacity": 10, "length": 100, "difficulty": 1}),
    ("右岸宿舍E", "F食堂", {"capacity": 10, "length": 100, "difficulty": 1}),
    ("右岸宿舍F", "F食堂", {"capacity": 10, "length": 100, "difficulty": 1}),
    ("D食堂", "教学楼1", {"capacity": 10, "length": 200, "difficulty": 2}),
    ("F食堂", "教学楼1", {"capacity": 10, "length": 200, "difficulty": 2}),
    ("教学楼1", "教学楼2", {"capacity": 10, "length": 150, "difficulty": 1}),
    ("教学楼2", "教学楼3", {"capacity": 10, "length": 150, "difficulty": 1}),
    ("教学楼3", "教学楼4", {"capacity": 10, "length": 150, "difficulty": 1}),
    # 添加更多路径
]
G.add_edges_from(edges)

# 定义学生类
class Student:
    def __init__(self, name, building):
        self.name = name
        self.building = building
        self.path = []
        self.current_position = buildings[building]['pos']

    def move_to(self, destination):
        self.path = nx.dijkstra_path(G, self.building, destination, weight='length')
        self.building = destination

# 定义班级
class Class:
    def __init__(self, name, students):
        self.name = name
        self.students = students
        self.schedule = {}

    def add_schedule(self, time, destination):
        self.schedule[time] = destination

    def move_students(self, time):
        if time in self.schedule:
            destination = self.schedule[time]
            for student in self.students:
                student.move_to(destination)

# 创建学生
students = [
    Student("Alice", "左岸宿舍A"),
    Student("Bob", "左岸宿舍B"),
    Student("Charlie", "左岸宿舍C"),
    Student("David", "右岸宿舍D"),
    Student("Eva", "右岸宿舍E"),
    Student("Frank", "右岸宿舍F"),
    # 添加更多学生
]

# 创建班级
classes = [
    Class("Class1", students[:2]),
    Class("Class2", students[2:4]),
    Class("Class3", students[4:6]),
    # 添加更多班级
]

# 设置课程表
classes[0].add_schedule("9:00", "教学楼1")
classes[0].add_schedule("12:00", "D食堂")
classes[1].add_schedule("9:00", "教学楼2")
classes[1].add_schedule("12:00", "F食堂")
classes[2].add_schedule("9:00", "教学楼3")
classes[2].add_schedule("12:00", "D食堂")

# 模拟时间
times = ["9:00", "12:00"]

# 绘制校园地图
def draw_campus():
    pos = nx.get_node_attributes(G, 'pos')
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=700)
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos)

# 更新可视化
def update(frame):
    plt.clf()
    draw_campus()
    current_time = times[frame]
    for class_ in classes:
        class_.move_students(current_time)
    for student in students:
        if student.path:
            student.current_position = buildings[student.building]['pos']
            plt.plot(student.current_position[0], student.current_position[1], 'ro')
    plt.title(f'Time: {current_time}')

# 创建动画
fig, ax = plt.subplots(figsize=(12, 8))
ani = FuncAnimation(fig, update, frames=len(times), repeat=False)
plt.show()

# 显示学生路径
for student in students:
    print(f"{student.name}: {' -> '.join(student.path)}")