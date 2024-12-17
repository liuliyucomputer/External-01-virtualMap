import pygame
import json
import time
from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional
import heapq
import random

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
ORANGE = (190, 0, 200)

# 虚拟时间起始时间
VIRTUAL_START_HOUR = 21  # 学生晚上9:30
VIRTUAL_START_MINUTE = 30
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
    def __init__(self, path_id: int, start: Point, end: Point, length: float, time_cost: float, is_forward: bool = True):
        self.id = path_id
        self.start = start
        self.end = end
        self.length = length
        self.time_cost = time_cost
        self.is_forward = is_forward

    def draw(self, config: GameConfig):
        """绘制路径"""
        start_pos = self.start.to_screen_coords(config.bg_width, config.bg_height)
        end_pos = self.end.to_screen_coords(config.bg_width, config.bg_height)
        pygame.draw.line(config.screen, BLUE, start_pos, end_pos, PATH_WIDTH)


class Student:
    def __init__(self, student_id: int, name: str, class_name: str, dormitory: str, buildings: Dict[str, Point]):
        self.id = student_id
        self.name = name
        self.class_name = class_name
        self.dormitory = dormitory
        self.buildings = buildings
        self.position: Optional[Point] = buildings[dormitory]  # 初始化位置为宿舍
        self.schedule: List[Tuple[int, int, str, int]] = []  # (小时, 分钟, 地点, 花费时间)
        self.current_schedule_index: int = 0
        self.current_path: List[Path] = []  # 当前路径
        self.move_start_time: Optional[float] = None
        self.generate_schedule()  # 生成日程

    def generate_schedule(self):
        # 生成日程安排
        self.schedule = [
            (7, 0, random.choice(["CanteenD5", "CanteenF5", "MD"]), 20),  # 早餐
            (8, 0, random.choice(["F3a", "F3b", "F3c", "F3d"]), 100),  # 第一节课
            (10, 0, random.choice(["F3a", "F3b", "F3c", "F3d"]), 60),  # 第二节课
            (11, 40, random.choice(["CanteenD5", "CanteenF5", "MD"]), 20),  # 午餐
            (12, 0, self.dormitory, 30),  # 回宿舍
            (14, 0, random.choice(["F3a", "F3b", "F3c", "F3d"]), 100),  # 第三节课
            (16, 0, random.choice(["F3a", "F3b", "F3c", "F3d"]), 100),  # 第四节课
            (18, 0, random.choice(["CanteenD5", "CanteenF5", "MD"]), 20),  # 晚餐
            (20, 30, self.dormitory, 30),  # 返回宿舍
        ]

    def find_shortest_path(self, start: Point, end: Point, paths: List[Path]) -> List[Path]:
        graph = {point: [] for path in paths for point in [path.start, path.end]}
        for path in paths:
            graph[path.start].append((path.end, path))
            if not any(p[1].start == path.end and p[1].is_forward for p in graph[path.end]):
                graph[path.end].append((path.start, Path(path.id, path.end, path.start, path.length, path.time_cost, is_forward=False)))

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

    def update_position(self, current_time: float):
        """更新学生位置"""
        if self.current_schedule_index < len(self.schedule):
            scheduled_time = self.schedule[self.current_schedule_index]
            scheduled_hour = scheduled_time[0]
            scheduled_minute = scheduled_time[1]
            scheduled_building = scheduled_time[2]
            duration = scheduled_time[3]

            scheduled_timestamp = scheduled_hour * 3600 + scheduled_minute * 60
            
            if current_time >= scheduled_timestamp:
                # 找到路径并更新
                self.current_path = self.find_shortest_path(self.position, self.buildings[scheduled_building], game.paths)
                self.move_start_time = current_time
                self.position = self.buildings[scheduled_building]  # 到达目标地点
                self.current_schedule_index += 1  # 前往下一个活动

    def draw(self, config: GameConfig):
        """绘制学生"""
        if self.position:
            pos = self.position.to_screen_coords(config.bg_width, config.bg_height)
            pygame.draw.circle(config.screen, ORANGE, pos, STUDENT_RADIUS)  # 使用橙色显示学生
            font = pygame.font.Font(None, 20)
            text = font.render(self.name, True, WHITE)
            text_rect = text.get_rect(center=pos)
            config.screen.blit(text, text_rect)


def smooth_step(t: float) -> float:
    """平滑插值函数"""
    return t * t * (3 - 2 * t)


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
        self.font = pygame.font.Font(None, 36)
        self.virtual_time = (VIRTUAL_START_HOUR * 3600 + VIRTUAL_START_MINUTE * 60 + VIRTUAL_START_SECOND)
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
                    student = Student(
                        student_data['id'],
                        student_data['name'],
                        student_data['class_name'],
                        student_data['dormitory'],
                        self.buildings
                    )
                    self.students.append(student)

        except FileNotFoundError:
            print("数据文件未找到")

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
