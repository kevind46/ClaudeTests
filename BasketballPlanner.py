import pygame
import sys
import math

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Basketball Play Designer")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 50, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
COURT_COLOR = (235, 214, 160)  # Light wood color
LINE_COLOR = (60, 60, 60)

# Court dimensions (relative to screen)
COURT_WIDTH = 800
COURT_HEIGHT = 470
COURT_X = (WIDTH - COURT_WIDTH) // 2
COURT_Y = (HEIGHT - COURT_HEIGHT) // 2 + 50

# Player dimensions
PLAYER_RADIUS = 15
SELECTED_OUTLINE_WIDTH = 3

# Button dimensions
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 40
BUTTON_MARGIN = 10

# Fonts
font = pygame.font.SysFont('Arial', 16)
large_font = pygame.font.SysFont('Arial', 24)

# Classes
class Player:
    def __init__(self, x, y, team, number):
        self.x = x
        self.y = y
        self.team = team  # 'offense' or 'defense'
        self.number = number
        self.color = RED if team == 'offense' else BLUE
        self.path = []
        self.screen_actions = []  # List of (x, y, radius) for screens
        self.selected = False
        self.dragging = False
        
    def draw(self, surface):
        # Draw path
        if len(self.path) > 0:
            for i in range(len(self.path) - 1):
                pygame.draw.line(surface, self.color, self.path[i], self.path[i+1], 2)
            pygame.draw.line(surface, self.color, self.path[-1], (self.x, self.y), 2)
            
            # Draw arrow at the end of the path
            if len(self.path) > 0:
                end_x, end_y = self.x, self.y
                if len(self.path) > 0:
                    start_x, start_y = self.path[-1]
                    angle = math.atan2(end_y - start_y, end_x - start_x)
                    arrow_length = 10
                    pygame.draw.line(surface, self.color, 
                                    (end_x, end_y),
                                    (end_x - arrow_length * math.cos(angle - math.pi/6), 
                                     end_y - arrow_length * math.sin(angle - math.pi/6)), 2)
                    pygame.draw.line(surface, self.color, 
                                    (end_x, end_y),
                                    (end_x - arrow_length * math.cos(angle + math.pi/6), 
                                     end_y - arrow_length * math.sin(angle + math.pi/6)), 2)
        
        # Draw screen actions
        for screen_x, screen_y, radius in self.screen_actions:
            pygame.draw.circle(surface, YELLOW, (screen_x, screen_y), radius, 2)
        
        # Draw player
        pygame.draw.circle(surface, self.color, (self.x, self.y), PLAYER_RADIUS)
        pygame.draw.circle(surface, BLACK, (self.x, self.y), PLAYER_RADIUS, 1)
        
        # Draw selection outline
        if self.selected:
            pygame.draw.circle(surface, GREEN, (self.x, self.y), PLAYER_RADIUS + SELECTED_OUTLINE_WIDTH, SELECTED_OUTLINE_WIDTH)
        
        # Draw player number
        text = font.render(str(self.number), True, WHITE)
        text_rect = text.get_rect(center=(self.x, self.y))
        surface.blit(text, text_rect)
        
    def is_clicked(self, pos):
        x, y = pos
        distance = math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
        return distance <= PLAYER_RADIUS
    
    def add_path_point(self, pos):
        self.path.append(pos)
    
    def add_screen(self, pos, radius=20):
        self.screen_actions.append((pos[0], pos[1], radius))
    
    def clear_path(self):
        self.path = []
        self.screen_actions = []

class Button:
    def __init__(self, x, y, width, height, text, color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.action = action
        self.active = False
        
    def draw(self, surface):
        # Draw button
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        # Draw text
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        # Draw active indicator
        if self.active:
            indicator_rect = pygame.Rect(self.rect.x - 5, self.rect.y, 5, self.rect.height)
            pygame.draw.rect(surface, GREEN, indicator_rect)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class PlayDesigner:
    def __init__(self):
        self.players = []
        self.selected_player = None
        self.mode = "move"  # 'move', 'path', 'screen'
        self.create_players()
        self.setup_ui()
        
    def create_players(self):
        # Create offense players (5)
        offense_positions = [
            (COURT_X + COURT_WIDTH // 2, COURT_Y + COURT_HEIGHT - 50),
            (COURT_X + COURT_WIDTH // 2 - 100, COURT_Y + COURT_HEIGHT - 150),
            (COURT_X + COURT_WIDTH // 2 + 100, COURT_Y + COURT_HEIGHT - 150),
            (COURT_X + COURT_WIDTH // 2 - 150, COURT_Y + COURT_HEIGHT // 2),
            (COURT_X + COURT_WIDTH // 2 + 150, COURT_Y + COURT_HEIGHT // 2)
        ]
        
        for i, pos in enumerate(offense_positions):
            self.players.append(Player(pos[0], pos[1], 'offense', i+1))
        
        # Create defense players (5)
        defense_positions = [
            (COURT_X + COURT_WIDTH // 2, COURT_Y + COURT_HEIGHT - 80),
            (COURT_X + COURT_WIDTH // 2 - 80, COURT_Y + COURT_HEIGHT - 180),
            (COURT_X + COURT_WIDTH // 2 + 80, COURT_Y + COURT_HEIGHT - 180),
            (COURT_X + COURT_WIDTH // 2 - 120, COURT_Y + COURT_HEIGHT // 2 - 30),
            (COURT_X + COURT_WIDTH // 2 + 120, COURT_Y + COURT_HEIGHT // 2 - 30)
        ]
        
        for i, pos in enumerate(defense_positions):
            self.players.append(Player(pos[0], pos[1], 'defense', i+1))
    
    def setup_ui(self):
        self.buttons = []
        button_y = 10
        
        # Mode buttons
        self.buttons.append(Button(10, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Move Players", GRAY, "move"))
        self.buttons.append(Button(10 + BUTTON_WIDTH + BUTTON_MARGIN, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Set Path", GRAY, "path"))
        self.buttons.append(Button(10 + (BUTTON_WIDTH + BUTTON_MARGIN) * 2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Add Screen", GRAY, "screen"))
        
        # Action buttons
        self.buttons.append(Button(10 + (BUTTON_WIDTH + BUTTON_MARGIN) * 3, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Clear All Paths", GRAY, "clear_all"))
        self.buttons.append(Button(10 + (BUTTON_WIDTH + BUTTON_MARGIN) * 4, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Reset Players", GRAY, "reset"))
        
        # Set the first button as active
        self.buttons[0].active = True
    
    def draw_court(self, surface):
        # Draw court
        pygame.draw.rect(surface, COURT_COLOR, (COURT_X, COURT_Y, COURT_WIDTH, COURT_HEIGHT))
        pygame.draw.rect(surface, LINE_COLOR, (COURT_X, COURT_Y, COURT_WIDTH, COURT_HEIGHT), 2)
        
        # Draw half court line
        pygame.draw.line(surface, LINE_COLOR, (COURT_X, COURT_Y), (COURT_X + COURT_WIDTH, COURT_Y), 2)
        
        # Draw baseline
        pygame.draw.line(surface, LINE_COLOR, (COURT_X, COURT_Y + COURT_HEIGHT), (COURT_X + COURT_WIDTH, COURT_Y + COURT_HEIGHT), 2)
        
        # Draw center circle
        pygame.draw.circle(surface, LINE_COLOR, (COURT_X + COURT_WIDTH // 2, COURT_Y), 60, 2)
        
        # Draw paint area
        paint_width = 160
        paint_height = 190
        paint_x = COURT_X + (COURT_WIDTH - paint_width) // 2
        paint_y = COURT_Y + COURT_HEIGHT - paint_height
        pygame.draw.rect(surface, LINE_COLOR, (paint_x, paint_y, paint_width, paint_height), 2)
        
        # Draw free throw line
        pygame.draw.line(surface, LINE_COLOR, (paint_x, paint_y), (paint_x + paint_width, paint_y), 2)
        
        # Draw free throw circle
        pygame.draw.circle(surface, LINE_COLOR, (paint_x + paint_width // 2, paint_y), 60, 2)
        
        # Draw backboard and rim
        backboard_width = 80
        backboard_x = COURT_X + (COURT_WIDTH - backboard_width) // 2
        backboard_y = COURT_Y + COURT_HEIGHT
        pygame.draw.line(surface, BLACK, (backboard_x, backboard_y), (backboard_x + backboard_width, backboard_y), 4)
        
        # Draw hoop
        hoop_radius = 10
        hoop_x = COURT_X + COURT_WIDTH // 2
        hoop_y = COURT_Y + COURT_HEIGHT - 15
        pygame.draw.circle(surface, ORANGE, (hoop_x, hoop_y), hoop_radius, 2)
        
        # Draw three-point line
        three_pt_radius = 235
        three_pt_center_x = COURT_X + COURT_WIDTH // 2
        three_pt_center_y = COURT_Y + COURT_HEIGHT
        
        # Draw the arc portion
        pygame.draw.arc(surface, LINE_COLOR, 
                       (three_pt_center_x - three_pt_radius, 
                        three_pt_center_y - three_pt_radius,
                        three_pt_radius * 2, three_pt_radius * 2),
                       math.pi, 0, 2)
    
    def handle_click(self, pos):
        # Check if any button is clicked
        for button in self.buttons:
            if button.is_clicked(pos):
                self.handle_button_action(button)
                return
        
        # If in move mode, check if any player is clicked
        if self.mode == "move":
            for player in self.players:
                if player.is_clicked(pos):
                    if self.selected_player:
                        self.selected_player.selected = False
                    player.selected = True
                    player.dragging = True
                    self.selected_player = player
                    return
            
            # If no player is clicked, deselect current player
            if self.selected_player:
                self.selected_player.selected = False
                self.selected_player = None
        
        # If in path mode and a player is selected, add a path point
        elif self.mode == "path" and self.selected_player and self.is_point_on_court(pos):
            self.selected_player.add_path_point(pos)
        
        # If in screen mode and a player is selected, add a screen at that position
        elif self.mode == "screen" and self.selected_player and self.is_point_on_court(pos):
            self.selected_player.add_screen(pos)
    
    def handle_button_action(self, button):
        if button.action in ["move", "path", "screen"]:
            self.mode = button.action
            for btn in self.buttons:
                btn.active = (btn == button)
        
        elif button.action == "clear_all":
            for player in self.players:
                player.clear_path()
        
        elif button.action == "reset":
            self.players = []
            self.selected_player = None
            self.create_players()
    
    def is_point_on_court(self, pos):
        x, y = pos
        return (COURT_X <= x <= COURT_X + COURT_WIDTH and 
                COURT_Y <= y <= COURT_Y + COURT_HEIGHT)
    
    def handle_mouse_motion(self, pos):
        if self.mode == "move" and self.selected_player and self.selected_player.dragging:
            if self.is_point_on_court(pos):
                self.selected_player.x, self.selected_player.y = pos
    
    def handle_mouse_up(self):
        if self.selected_player:
            self.selected_player.dragging = False
    
    def draw(self, surface):
        # Clear screen
        surface.fill(WHITE)
        
        # Draw court
        self.draw_court(surface)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface)
        
        # Draw mode text
        mode_text = f"Current Mode: {self.mode.capitalize()}"
        text_surf = large_font.render(mode_text, True, BLACK)
        surface.blit(text_surf, (WIDTH - text_surf.get_width() - 10, 20))
        
        # Draw instructions
        instructions = []
        if self.mode == "move":
            instructions = ["Click and drag players to position them on the court"]
        elif self.mode == "path":
            instructions = ["Select a player, then click on the court to set path points"]
        elif self.mode == "screen":
            instructions = ["Select a player, then click on the court to add screen locations"]
        
        for i, text in enumerate(instructions):
            text_surf = font.render(text, True, BLACK)
            surface.blit(text_surf, (WIDTH // 2 - text_surf.get_width() // 2, HEIGHT - 30 - i * 20))
        
        # Draw players
        for player in self.players:
            player.draw(surface)

# Main game loop
def main():
    clock = pygame.time.Clock()
    play_designer = PlayDesigner()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    play_designer.handle_click(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                play_designer.handle_mouse_motion(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    play_designer.handle_mouse_up()
        
        # Draw everything
        play_designer.draw(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()