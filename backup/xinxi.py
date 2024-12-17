import pygame
import json
import math

# 初始化Pygame
pygame.init()

# 设置屏幕尺寸
screen_width = 650
screen_height = 700
screen = pygame.display.set_mode((screen_width, screen_height))

# 加载背景地图
background_image = pygame.image.load("1.png").convert()

# 获取背景地图的原始尺寸
background_width, background_height = background_image.get_size()

# 存储建筑物坐标点的列表，每个元素以 (相对x坐标, 相对y坐标) 形式保存，范围是0到1之间
building_points = []

# 存储路径的列表，每个元素是一个Path类的对象，表示一条路径
path_list = []

# 存储学生的列表
students = []

# 存储科目的列表
subjects = []

# Path类，用于管理每条路径的相关属性和操作
class Path:
    def __init__(self, id, start_point, end_point, capacity=100, difficulty=0, time_cost=0):
        self.id = id
        self.start_point = start_point
        self.end_point = end_point
        self.capacity = capacity
        self.difficulty = difficulty
        self.length = self.calculate_length()
        self.time_cost = time_cost

    def calculate_length(self):
        # 使用欧几里得距离公式计算两点间的长度（基于背景图实际坐标）
        start_x = self.start_point[0] * background_width
        start_y = self.start_point[1] * background_height
        end_x = self.end_point[0] * background_width
        end_y = self.end_point[1] * background_height
        return math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)

    def get_info(self):
        return f"ID: {self.id}, 起点: {self.start_point}, 终点: {self.end_point}, 长度: {self.length:.2f}, 容量: {self.capacity}, 难度: {self.difficulty}, 耗费时间: {self.time_cost}"

    def to_dict(self):
        return {
            "id": self.id,
            "start_point": self.start_point,
            "end_point": self.end_point,
            "length": self.length,
            "capacity": self.capacity,
            "difficulty": self.difficulty,
            "time_cost": self.time_cost
        }

# 学生类
class Student:
    def __init__(self, id, name, class_name, dormitory):
        self.id = id
        self.name = name
        self.class_name = class_name
        self.dormitory = dormitory

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "class_name": self.class_name,
            "dormitory": self.dormitory
        }

# 科目类
class Subject:
    def __init__(self, id, name, start_time, end_time, building):
        self.id = id
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.building = building

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "building": self.building
        }

# 建筑物类（简化版）
class Building:
    def __init__(self, id, name, coordinates):
        self.id = id
        self.name = name
        self.coordinates = coordinates

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "coordinates": self.coordinates
        }

# 用于记录鼠标点击事件获取坐标点，这里假设通过鼠标左键点击地图上建筑物位置来设置坐标点，鼠标右键点击设置路径
def handle_mouse_click(event):
    global building_points, path_list
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        x, y = pygame.mouse.get_pos()
        # 将点击获取的坐标转换为相对于背景图原始尺寸的相对坐标（精确到小数点后2位）
        relative_x = round(x / background_width, 2)
        relative_y = round(y / background_height, 2)
        building_points.append((relative_x, relative_y))
        print(f"添加坐标点: ({relative_x}, {relative_y})")  # 打印出添加的坐标点相对坐标信息
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # 鼠标右键点击来设置路线
        if len(building_points) >= 2:
            start_point = building_points[-2]
            end_point = building_points[-1]
            new_path = Path(len(path_list), start_point, end_point)
            path_list.append(new_path)
            print(new_path.get_info())

# 游戏主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_mouse_click(event)

    # 绘制背景地图，直接按原始尺寸绘制，能完整显示全图（这里可根据屏幕尺寸和图片宽高比例调整绘制位置使其居中，当前简单处理直接左上角对齐绘制）
    screen.blit(background_image, (0, 0))

    # 绘制已设置的建筑物坐标点（以小圆点表示，可调整颜色、大小等外观属性）
    for point in building_points:
        # 根据相对坐标和背景图实际绘制尺寸计算出屏幕上的真实坐标（精确到小数点后2位）
        real_x = round(point[0] * background_width, 2)
        real_y = round(point[1] * background_height, 2)
        pygame.draw.circle(screen, (255, 0, 0), (int(real_x), int(real_y)), 5)

    # 绘制路径（这里简单以直线连接两点表示路线）
    for path in path_list:
        start_x = round(path.start_point[0] * background_width, 2)
        start_y = round(path.start_point[1] * background_height, 2)
        end_x = round(path.end_point[0] * background_width, 2)
        end_y = round(path.end_point[1] * background_height, 2)
        pygame.draw.line(screen, (0, 0, 255), (int(start_x), int(start_y)), (int(end_x), int(end_y)), 2)

    pygame.display.flip()

# 保存所有数据到JSON文件
def save_data_to_json():
    data = {
        "students": [student.to_dict() for student in students],
        "buildings": [Building(i + 1, name, (0, 0)) for i, name in enumerate(["宿舍楼A", "宿舍楼B", "宿舍楼C", "宿舍楼D", "宿舍楼E", "宿舍楼F", "食堂G", "食堂H", "教学楼I", "教学楼J", "教学楼K", "教学楼L"])],
        "paths": [path.to_dict() for path in path_list],
        "subjects": [subject.to_dict() for subject in subjects]
    }
    with open('data.json', 'w') as file:
        json.dump(data, file)

# 加载所有数据从JSON文件
def load_data_from_json():
    global students, path_list, subjects
    try:
        with open('data.json', 'r') as file:
            data = json.load(file)
            students = [Student(**student_dict) for student_dict in data["students"]]
            path_list = [Path(**path_dict) for path_dict in data["paths"]]
            subjects = [Subject(**subject_dict) for subject_dict in data["subjects"]]
    except FileNotFoundError:
        print("没有找到保存的数据文件。")

# 示例：添加学生信息
def add_student(id, name, class_name, dormitory):
    students.append(Student(id, name, class_name, dormitory))

# 示例：添加科目信息
def add_subject(id, name, start_time, end_time, building):
    subjects.append(Subject(id, name, start_time, end_time, building))

# 示例用法（可在游戏循环结束后调用这些函数进行测试等操作）
if __name__ == "__main__":
    # 添加一些示例学生信息
    add_student(1, "张三", "一班", "宿舍楼A")
    add_student(2, "李四", "二班", "宿舍楼B")

    # 添加一些示例科目信息
    add_subject(1, "数学", "08:00", "09:40", "教学楼I")
    add_subject(2, "英语", "10:00", "11:40", "教学楼J")

    print("所有路径信息：")
    print_all_paths()
    # 更新索引为0的路径的难度为5（这里只是示例，可根据实际需求调整索引和难度值）
    update_path_difficulty(0, 5)
    print("更新难度后所有路径信息：")
    print_all_paths()
    # 查找长度小于100的路径（这里的长度单位基于背景图实际坐标计算得出，同样可根据实际调整长度阈值）
    short_paths = find_paths_shorter_than(100)
    print("长度小于100的路径信息：")
    for path in short_paths:
        print(path.get_info())

    # 保存数据到JSON文件
    save_data_to_json()

    # 加载数据示例
    # load_data_from_json()

pygame.quit()