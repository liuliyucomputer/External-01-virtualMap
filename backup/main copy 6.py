import pygame
import json
import time
from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional
import heapq

# 常量配置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
BUILDING_POINT_RADIUS = 5
STUDENT_RADIUS = 5
PATH_WIDTH = 2

# 颜色常量
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
ORANGE  = (190, 00, 200) 
# ORANGE = (255, 165, 0)  # 学生颜色
# BROWN = (165, 42, 42) 
# 虚拟时间起始时间
VIRTUAL_START_HOUR = 7
VIRTUAL_START_MINUTE = 0
VIRTUAL_START_SECOND = 0

@dataclass(frozen=True, order=True)
class Point:
    """坐标点类"""
    x: float
    y: float

    def to_screen_coords(self, bg_width: int, bg_height: int) -> Tuple[int, int]:
        """转换为屏幕坐标"""
        return (int(self.x * bg_width), int(self.y * bg_height))

@dataclass
class GameConfig:
    """游戏配置类"""
    screen: pygame.Surface
    background: pygame.Surface
    bg_width: int
    bg_height: int

class Path:
    def __init__(self, path_id: int, start: Point, end: Point, length: float, time_cost: float):
        self.id = path_id
        self.start = start
        self.end = end
        self.length = length
        self.time_cost = time_cost

    def draw(self, config: GameConfig):
        """绘制路径"""
        start_pos = self.start.to_screen_coords(config.bg_width, config.bg_height)
        end_pos = self.end.to_screen_coords(config.bg_width, config.bg_height)
        pygame.draw.line(config.screen, BLUE, start_pos, end_pos, PATH_WIDTH)

class Student:
    def __init__(self, student_id: int, name: str, class_name: str, dormitory: str, schedule: List[str]):
        self.id = student_id
        self.name = name
        self.class_name = class_name
        self.dormitory = dormitory
        self.schedule = schedule
        self.position: Optional[Point] = None
        self.destination: Optional[Point] = None
        self.current_path: Optional[List[Path]] = None
        self.move_start_time: Optional[float] = None

    def update_position(self, current_time: float):
        """更新学生位置"""
        if not (self.current_path and self.move_start_time):
            return

        if not self.current_path:
            return

        path = self.current_path[0]  # 获取当前路径
        progress = min(1.0, (current_time - self.move_start_time) / path.time_cost)
        
        self.position = Point(
            path.start.x + (path.end.x - path.start.x) * progress,
            path.start.y + (path.end.y - path.start.y) * progress
        )
        
        if progress >= 1.0:
            self.current_path.pop(0)  # 移除已完成的路径
            if self.current_path:
                self.move_start_time = current_time  # 重置开始时间

    def draw(self, config: GameConfig):
        """绘制学生"""
        if self.position:
            pos = self.position.to_screen_coords(config.bg_width, config.bg_height)
            pygame.draw.circle(config.screen, ORANGE, pos, STUDENT_RADIUS)  # 使用橙色显示学生
            font = pygame.font.Font(None, 20)
            text = font.render(self.name, True,WHITE  )
            text_rect = text.get_rect(center=pos)
            config.screen.blit(text, text_rect)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background = pygame.image.load("1.png").convert()
        self.config = GameConfig(
            self.screen,
            self.background,
            *self.background.get_size()
        )
        self.paths: List[Path] = []
        self.students: List[Student] = []
        self.buildings: Dict[str, Point] = {}
        self.font = pygame.font.Font(None, 36)  # 添加字体
        self.virtual_time = time.mktime((2023, 10, 1, VIRTUAL_START_HOUR, VIRTUAL_START_MINUTE, VIRTUAL_START_SECOND, 0, 0, 0))
        self.load_data()

    def load_data(self):
        """从JSON加载数据"""
        try:
            with open('data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                for building_data in data.get('buildings', []):
                    coordinates = Point(building_data['coordinates'][0], building_data['coordinates'][1])
                    self.buildings[building_data['name']] = coordinates
                for path_data in data.get('paths', []):
                    start = Point(path_data['start_point'][0], path_data['start_point'][1])
                    end = Point(path_data['end_point'][0], path_data['end_point'][1])
                    self.paths.append(Path(
                        path_data['id'], start, end,
                        path_data['length'], path_data['time_cost']
                    ))
                for student_data in data.get('students', []):
                    schedule = self.get_schedule_for_class(student_data['class_name'], data['class'], data['subjects'])
                    student = Student(
                        student_data['id'],
                        student_data['name'],
                        student_data['class_name'],
                        student_data['dormitory'],
                        schedule
                    )
                    student.position = self.buildings.get(student.dormitory)
                    if student.schedule:
                        student.destination = self.buildings.get(student.schedule[0])  # 设置第一个目的地
                        student.current_path = self.find_shortest_path(student.position, student.destination)
                    student.move_start_time = self.virtual_time
                    self.students.append(student)
        except FileNotFoundError:
            print("数据文件未找到")

    def get_schedule_for_class(self, class_name: str, class_data: List[Dict], subjects_data: List[Dict]) -> List[str]:
        """获取班级的课程安排"""
        for cls in class_data:
            if cls['class_name'] == class_name:
                subjects = cls['content'].split('-')
                schedule = []
                for subject in subjects:
                    for sub in subjects_data:
                        if sub['name'] == subject:
                            schedule.append(sub['building'])
                return schedule
        return []

    def find_shortest_path(self, start: Point, end: Point) -> List[Path]:
        """使用Dijkstra算法找到最短路径"""
        if start == end:
            return []
        
        graph = {point: [] for path in self.paths for point in [path.start, path.end]}
        for path in self.paths:
            graph[path.start].append((path.end, path))
            graph[path.end].append((path.start, path))

        distances = {start: 0}
        queue = [(0, id(start), start, [])]  # 使用id()来区分相同坐标的点
        visited = set()

        while queue:
            current_distance, _, current_node, path = heapq.heappop(queue)
            
            if current_node in visited:
                continue
                
            visited.add(current_node)
            
            if current_node == end:
                return path
                
            for neighbor, edge in graph[current_node]:
                if neighbor not in visited:
                    distance = current_distance + edge.length
                    if neighbor not in distances or distance < distances[neighbor]:
                        distances[neighbor] = distance
                        heapq.heappush(queue, (distance, id(neighbor), neighbor, path + [edge]))

        return []

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def update(self):
        """更新游戏状态"""
        self.virtual_time += 1  # 每次更新加一秒
        for student in self.students:
            student.update_position(self.virtual_time)

    def draw_buildings(self):
        """绘制建筑物及其名称"""
        for building_name, point in self.buildings.items():
            screen_coords = point.to_screen_coords(self.config.bg_width, self.config.bg_height)
            pygame.draw.rect(self.screen, BLACK, (screen_coords[0] - BUILDING_POINT_RADIUS, screen_coords[1] - BUILDING_POINT_RADIUS, BUILDING_POINT_RADIUS * 2, BUILDING_POINT_RADIUS * 2))
            font = pygame.font.Font(None, 24)
            text = font.render(building_name, True, WHITE)  # 使用白色显示建筑名称
            text_rect = text.get_rect(center=(screen_coords[0], screen_coords[1] - 15))  # 名称在建筑物上方
            self.screen.blit(text, text_rect)

    def draw_time(self):
        """显示当前虚拟时间"""
        time_str = time.strftime("%H:%M:%S", time.localtime(self.virtual_time))
        text = self.font.render(time_str, True, YELLOW)
        text_rect = text.get_rect(topleft=(SCREEN_WIDTH - 150, 20))
        pygame.draw.rect(self.screen, BLACK, text_rect)  # 黑色背景框
        self.screen.blit(text, text_rect)

    def draw(self):
        """绘制游戏画面"""
        self.screen.blit(self.background, (0, 0))
        self.draw_buildings()  # 绘制建筑物
        for path in self.paths:
            path.draw(self.config)
        for student in self.students:
            student.draw(self.config)
        self.draw_time()  # 显示时间
        pygame.display.flip()

    def run(self):
        """游戏主循环"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            pygame.time.delay(1000)  # 控制更新速度
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()