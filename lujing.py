import pygame
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


# Path类，用于管理每条路径的相关属性和操作
class Path:
    def __init__(self, start_point, end_point, capacity=100, difficulty=0):
        self.start_point = start_point
        self.end_point = end_point
        self.capacity = capacity
        self.difficulty = difficulty
        self.length = self.calculate_length()

    def calculate_length(self):
        # 使用欧几里得距离公式计算两点间的长度（基于背景图实际坐标）
        start_x = self.start_point[0] * background_width
        start_y = self.start_point[1] * background_height
        end_x = self.end_point[0] * background_width
        end_y = self.end_point[1] * background_height
        return math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)

    def get_info(self):
        return f"起点: {self.start_point}, 终点: {self.end_point}, 长度: {self.length:.2f}, 容量: {self.capacity}, 难度: {self.difficulty}"


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
            new_path = Path(start_point, end_point)
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

# 以下是一些简单的路径管理操作函数示例

# 打印所有路径信息
def print_all_paths():
    for path in path_list:
        print(path.get_info())


# 更新路径难度
def update_path_difficulty(index, new_difficulty):
    if 0 <= index < len(path_list):
        path_list[index].difficulty = new_difficulty
        print(f"更新路径 {index} 的难度为 {new_difficulty}")


# 根据长度筛选路径
def find_paths_shorter_than(max_length):
    short_paths = []
    for path in path_list:
        if path.length < max_length:
            short_paths.append(path)
    return short_paths


# 示例用法（可在游戏循环结束后调用这些函数进行测试等操作）
if __name__ == "__main__":
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


pygame.quit()