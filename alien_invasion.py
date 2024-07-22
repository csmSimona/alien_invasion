import sys
from time import sleep
import pygame
from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien
from pathlib import Path

class AlienInvasion:
    """管理游戏资源和行为的类"""

    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init() # 初始化背景
        self.clock = pygame.time.Clock() # 定义时钟
        self.settings = Settings() # 定义设置
        self.game_active = False

        # 设置显示窗口
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))

        # 全屏显示
        # self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        # self.settings.screen_width = self.screen.get_rect().width
        # self.settings.screen_height = self.screen.get_rect().height

        pygame.display.set_caption(self.settings.title) # 设置窗口标题
        
        self.stats = GameStats(self) # 创建一个用于存储游戏统计信息的实例
        self.sb = Scoreboard(self) # 创建计分板
        self.play_button = Button(self, 'Play') # 定义开始按钮
        self.ship = Ship(self) # 定义飞船
        self.bullets = pygame.sprite.Group() # 定义子弹编组
        self.aliens = pygame.sprite.Group() # 定义外星人编组
        self._create_fleet()


    def run_game(self):
        """开始游戏的主循环"""
        while True:
            self._check_events()
            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()
            self.clock.tick(60) # 设置帧率
    

    def _check_events(self):
        """响应按键和鼠标事件"""
        pygame.key.stop_text_input() # 解决按键盘字母键没反应的问题
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._update_high_score()
                sys.exit()  # 退出游戏
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
    

    def _check_keydown_events(self, event):
        """响应按下"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_q:
            self._update_high_score()
            sys.exit()  # 退出游戏
        elif event.key == pygame.K_p:
            self._start_game() # 开始游戏
    
    
    def _check_keyup_events(self, event):
        """响应释放"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False


    def _check_play_button(self, mouse_pos):
        """在玩家单击 Play 按钮时开始新游戏"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self._start_game()
            self.settings.initialize_dynamic_settings() # 初始化游戏设置
            

    def _start_game(self):
        # 重置游戏的统计信息
        self.stats.reset_stats()
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()
        self.game_active = True
        # 清空外星人列表和子弹列表
        self.bullets.empty()
        self.aliens.empty()
        # 创建一个新的外星舰队，并将飞船放在屏幕底部的中央
        self._create_fleet()
        self.ship.center_ship()
        # 隐藏光标
        pygame.mouse.set_visible(False)



    def _fire_bullet(self):
        """创建一颗子弹，并将其加入编组bullets"""
        # 限制子弹数量
        if len(self.bullets) < self.settings.bullet_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)


    def _update_bullets(self):
        """更新子弹的位置并删除已消失的子弹"""
        # 更新子弹的位置
        self.bullets.update()
        # 删除已消失的子弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()


    def _check_bullet_alien_collisions(self):
        """响应子弹和外星人的碰撞"""
        # 删除发生碰撞的子弹和外星人
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
        # 一个外星舰队被击落后删除现有的子弹并创建一个新的外星舰队
        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            # 提高等级
            self.stats.level += 1
            self.sb.prep_level()
    

    def _create_fleet(self):
        """创建一个外星舰队"""
        # 创建一个外星人，再不断添加，直到没有空间添加外星人为止
        # 外星人的间距为外星人的宽度
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width
            # 添加一行外星人后，重置 x 值并递增 y 值
            current_x = alien_width
            current_y += 2 * alien_height


    def _create_alien(self, x_position, y_position):
        """创建一个外星人，并将其加入外星舰队"""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.y = y_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)


    def _check_fleet_edges(self):
        """在有外星人到达边缘时采取相应的措施"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break


    def _change_fleet_direction(self):
        """将整个外星舰队向下移动，并改变它们的方向"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1


    def _update_aliens(self):
        """检查是否有外星人位于屏幕边缘，并更新整个外星舰队的位置"""
        self._check_fleet_edges()
        self.aliens.update()
        # 检测外星人和飞船之间的碰撞
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()


    def _ship_hit(self):
        """响应飞船和外星人的碰撞"""
        """当有外星人撞到飞船时，将余下的飞船数减 1，创建一个新的外星舰队，并将飞船重新放在屏幕底部的中央。
        另外，让游戏暂停一会儿，让玩家意识到发生了碰撞，并在创建新的外星舰队前重整旗鼓。"""
        if self.stats.ships_left > 0:
            # 将 ships_left 减 1
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            # 清空外星人列表和子弹列表
            self.bullets.empty()
            self.aliens.empty()
            # 创建一个新的外星舰队，并将飞船放在屏幕底部的中央
            self._create_fleet()
            self.ship.center_ship()
            # 暂停
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)  # 显示光标


    def _check_aliens_bottom(self):
        """检查是否有外星人到达了屏幕的下边缘"""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # 像飞船被撞到一样进行处理
                self._ship_hit()
                break
    

    def _update_screen(self):
        """更新屏幕上的图像，并切换到新屏幕"""
        self.screen.fill(self.settings.bg_color) # 每次循环时都重绘屏幕
        # 重绘每一颗子弹
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme() # 绘制飞船
        self.aliens.draw(self.screen) # 绘制外星人
        self.sb.show_score()
        if not self.game_active:
            self.play_button.draw_button()
        pygame.display.flip()  # 让最近绘制的屏幕可见
    
    def _update_high_score(self):
        """存储最高分到文件中"""
        path = Path('high_score.txt')
        path.write_text(str(self.stats.high_score))




if __name__ == '__main__':
    # 创建游戏实例并运行游戏
    ai = AlienInvasion()
    ai.run_game()