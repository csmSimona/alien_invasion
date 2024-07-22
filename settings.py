class Settings:
    """存储游戏《外星人入侵》中所有设置的类"""

    def __init__(self):
        """初始化游戏的设置"""
        # 屏幕设置
        self.title = "Alien Invasion"
        self.screen_width = 1200
        self.screen_height = 600
        self.bg_color = (230, 230, 230)
        # 飞船设置
        self.ship_limit = 3
        # 子弹设置
        self.bullet_width = 5
        self.bullet_height = 5
        self.bullet_color = (60, 60, 60)
        self.bullet_allowed = 5
        # 外星人设置
        self.fleet_drop_speed = 10  # 外星人向下移动速度
        self.speedup_scale = 1.1 # 更新移动速度
        self.score_scale = 1.5 # 分数提高速度
        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """初始化随游戏进行而变化的设置"""
        self.ship_speed = 1.5 # 飞船速度
        self.bullet_speed = 2.5 # 子弹速度
        self.alien_speed = 1.0 # 外星人速度
        self.fleet_direction = 1 # 外星人移动方向：1 表示向右移动，-1 表示向左移动
        self.alien_points = 50 # 击落一个外星人的分数

    def increase_speed(self):
        """提高速度设置的值"""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)