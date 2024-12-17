import pygame

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

# 用于记录鼠标点击事件获取坐标点，这里假设通过鼠标左键点击地图上建筑物位置来设置坐标点
def handle_mouse_click(event):
    global building_points
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        x, y = pygame.mouse.get_pos()
        # 将点击获取的坐标转换为相对于背景图原始尺寸的相对坐标（精确到小数点后两位）
        relative_x = round(x / background_width, 2)
        relative_y = round(y / background_height, 2)
        building_points.append((relative_x, relative_y))
        print(f"添加坐标点: ({relative_x}, {relative_y})")  # 打印出添加的坐标点相对坐标信息

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
        # 根据相对坐标和背景图实际绘制尺寸计算出屏幕上的真实坐标（精确到小数点后两位）
        real_x = round(point[0] * background_width, 2)
        real_y = round(point[1] * background_height, 2)
        pygame.draw.circle(screen, (255, 0, 0), (int(real_x), int(real_y)), 5)

    pygame.display.flip()

pygame.quit()