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

# 虚拟时间初始设定
VIRTUAL_START_HOUR = 7  # 学生晚上9:30
VIRTUAL_START_MINUTE =15
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
    def __init__(self, student_id: int, name: str, class_name: str, dormitory: str, buildings: Dict[str, Point], paths: List[Path], subjects: List[dict], class_content: str):
        self.id = student_id
        self.name = name
        self.class_name = class_name
        self.dormitory = dormitory
        self.buildings = buildings
        self.paths = paths
        self.subjects = subjects
        self.schedule: List[Tuple[int, int, str, int]] = []  # (小时, 分钟, 地点, 花费时间)
        self.position: Optional[Point] = buildings[dormitory]  # 初始化位置为宿舍
        self.current_time: int = VIRTUAL_START_HOUR * 3600 + VIRTUAL_START_MINUTE * 60 + VIRTUAL_START_SECOND  # 初始化虚拟时间
        self.current_schedule_index: int = 0
        self.current_path: List[Path] = []  # 当前路径
        self.move_start_time: Optional[float] = None
        self.class_content = class_content.split('-')  # 解析班级内容为地点列表
        self.generate_schedule()
        
    def generate_schedule(self):
        """生成日常活动安排"""
        for event in self.class_content:
            for subject in self.subjects:
                if event == subject['building']:
                    start_hour, start_minute = map(int, subject['start_time'].split(':'))
                    end_hour, end_minute = map(int, subject['end_time'].split(':'))
                    duration = (end_hour * 3600 + end_minute * 60) - (start_hour * 3600 + start_minute * 60)
                    self.schedule.append((start_hour, start_minute, subject['building'], duration // 60))
        self.schedule.append((20, 30, self.dormitory, 30))  # 返回宿舍

    def find_shortest_path(self, start: Point, end: Point) -> List[Path]:
        if start == end:
            return []
        graph = {point: [] for path in self.paths for point in [path.start, path.end]}
        for path in self.paths:
            graph[path.start].append((path.end, path))
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

            # 检查是否达到了计划时间并找到路径
            if current_time >= scheduled_timestamp:
                if self.position == self.buildings[scheduled_building]:
                    end_hour = scheduled_hour + duration
                    end_timestamp = end_hour * 3600 + scheduled_minute * 60

                    if current_time < end_timestamp:
                        return  # 若还在课程结束前，直接返回

                if not self.current_path:  # 如果没有当前路径，开始寻找新路径
                    self.current_path = self.find_shortest_path(self.position, self.buildings[scheduled_building])
                    if self.current_path:
                        self.move_start_time = current_time  # 记录移动开始时间

                if self.current_path:  # 只在有路径时更新位置
                    path = self.current_path[0]  # 当前路径段
                    progress = min(1.0, (current_time - self.move_start_time) / path.time_cost)

                    self.position = Point(
                        path.start.x + (path.end.x - path.start.x) * smooth_step(progress),
                        path.start.y + (path.end.y - path.start.y) * smooth_step(progress)
                    )
                    print(f"当前虚拟时间: {current_time}, 计划时间: {scheduled_timestamp}, 建筑物: {scheduled_building}")  # 调试信息
                    if progress >= 1.0:  # 如果当前路径段已完成
                        self.current_path.pop(0)  # 移除已完成的路径段
                        if not self.current_path:  # 如果路径段已全部完成
                            self.current_schedule_index += 1  # 进行下一个活动

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
        self.font = pygame.font.Font(None, 36)  # 添加字体
        self.virtual_time = (VIRTUAL_START_HOUR * 3600 + VIRTUAL_START_MINUTE * 60 + VIRTUAL_START_SECOND)  # 转换为秒
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
                    class_content = next((cls['content'] for cls in data["class"] if cls["class_name"] == student_data["class_name"]), "")
                    student = Student(
                        student_data['id'],
                        student_data['name'],
                        student_data['class_name'],
                        student_data['dormitory'],
                        self.buildings,
                        self.paths,
                        data.get('subjects', []),  # 传递科目数据
                        class_content  # 班级内容
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
        hours = (self.virtual_time // 3600) % 24  # 实时计算小时
        minutes = (self.virtual_time % 3600) // 60  # 实时计算分钟
        seconds = self.virtual_time % 60  # 实时计算秒

        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
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
