from pathlib import Path
class GameStats:
    """跟踪游戏的统计信息"""

    def __init__(self, ai_game):
        """初始化统计信息"""
        self.settings = ai_game.settings
        self._get_high_score()
    
    def _get_high_score(self):
        """从文件中获取最高分"""
        path = Path('high_score.txt')
        contents = path.read_text()
        self.high_score = int(contents)
        self.reset_stats() # 最高分

    def reset_stats(self):
        """初始化在游戏运行期间可能变化的统计信息"""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1