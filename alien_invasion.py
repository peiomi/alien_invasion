import sys
from time import sleep
from pygame import (
    sprite, init, display, event as e, QUIT, time, mouse,
    KEYDOWN, K_d, KEYUP, K_a, K_q, K_SPACE, MOUSEBUTTONDOWN)
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard

class AlienInvasion:

    def __init__(self):
        init()
        self.clock = time.Clock()
        self.settings = Settings()
        self.screen = display.set_mode((self.settings.screen_width, self.settings.screen_height))
        display.set_caption("Alien Invasion")

        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = sprite.Group()
        self.aliens = sprite.Group()

        self._create_fleet()

        self.game_active = False 
        self.play_button = Button(self, "PLAY")

    def run_game(self):
        while True:
            self._check_events()

            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                
            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        for event in e.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == KEYUP:
                self._check_keyup_events(event)
            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_keydown_events(self, event):
        if event.key == K_d:
            self.ship.moving_right = True
        elif event.key == K_a:
            self.ship.moving_left = True
        elif event.key == K_q:
            sys.exit()
        elif event.key == K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        if event.key == K_d:
            self.ship.moving_right = False
        elif event.key == K_a:
            self.ship.moving_left = False

    def _check_play_button(self, mouse_pos):
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.game_active = True
            mouse.set_visible(False)

            self.bullets.empty()
            self.aliens.empty()

            self._create_fleet()
            self.ship.center_ship()

    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        collisions = sprite.groupcollide(self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            self.stats.level += 1 
            self.sb.prep_level()

    def _create_alien(self, x_position, y_position):
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _create_fleet(self):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        # staggered rows
        current_y = alien_height
        row = 0
        while current_y < (self.settings.screen_height - 5 * alien_height):
            if row % 2 == 0:
                current_x = alien_width
            else:
                current_x = alien_width + alien_width
            
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width

            current_y += 2 * alien_height / 1.5
            row += 1

        # congruent rows
        """ current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 4 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width

            current_x = alien_width
            current_y += 2 * alien_height """

    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()

        if sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        self._check_aliens_bottom()

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien._check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _check_aliens_bottom(self):
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                self._ship_hit()
                break

    def _ship_hit(self):
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            self.bullets.empty()
            self.aliens.empty()

            self._create_fleet()
            self.ship.center_ship()
            sleep(0.5)
        else:
            self.game_active = False
            mouse.set_visible(True)

    def _update_screen(self):
        self.screen.blit(self.settings.bg, (0, 0))
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.blitme()
        self.aliens.draw(self.screen)

        self.sb.show_score()

        if not self.game_active:
            self.play_button.draw_button()

        display.flip()

if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()