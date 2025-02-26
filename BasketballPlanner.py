import pygame
import sys
import math
from enum import Enum

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Basketball Play Designer")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (240, 240, 240)
COURT_COLOR = (242, 224, 173)
LINE_COLOR = (140, 120, 100)

# Court dimensions
COURT_WIDTH = 800
COURT_HEIGHT = 450
COURT_X = (WIDTH - COURT_WIDTH) // 2
COURT_Y = 50
THREE_POINT_RADIUS = 180
FREE_THROW_RADIUS = 60
FREE_THROW_LINE_Y = COURT_Y + 150
RIM_X = COURT_X + COURT_WIDTH // 2
RIM_Y = COURT_Y + 40
BACKBOARD_WIDTH = 60
BACKBOARD_Y = COURT_Y + 20

# Player settings
PLAYER_RADIUS = 15
SCREEN_RADIUS = 20

# Buttons
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 40
BUTTON_MARGIN = 10
BUTTON_Y = COURT_Y + COURT_HEIGHT + 20

# States
class State(Enum):
    IDLE = 0
    PLACING_PLAYER = 1
    SELECTING_PLAYER = 2
    DRAWING_PATH = 3
    ADDING_SCREEN = 4
    PLAYING = 5
    ASSIGN_DEFENDER = 6

# Player types
class PlayerType(Enum):
    OFFENSE = 0
    DEFENSE = 1

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, 0, 5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, 5)
        
        font = pygame.font.SysFont("Arial", 16, bold=True)
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def is_hovered(self, pos):
        if self.rect.collidepoint(pos):
            self.current_color = self.hover_color
            return True
        else:
            self.current_color = self.color
            return False
            
    def is_clicked(self, pos, event):
        if self.rect.collidepoint(pos) and event.type == pygame.MOUSEBUTTONDOWN:
            return True
        return False

# Player class
class Player:
    def __init__(self, x, y, player_type, color, number):
        self.x = x
        self.y = y
        self.type = player_type
        self.color = color
        self.number = number
        self.path = []
        self.screen_points = []
        self.current_path_index = 0
        self.speed = 2
        self.original_x = x
        self.original_y = y
        self.marked_player = None  # For defense, who they're guarding
        self.is_screened = False
        self.screen_timer = 0
        
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), PLAYER_RADIUS)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), PLAYER_RADIUS, 2)
        
        font = pygame.font.SysFont("Arial", 12, bold=True)
        text_surf = font.render(str(self.number), True, BLACK)
        text_rect = text_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(text_surf, text_rect)
        
        # Draw line to marked player if defense
        if self.marked_player and self.type == PlayerType.DEFENSE:
            pygame.draw.line(surface, GRAY, (int(self.x), int(self.y)), 
                            (int(self.marked_player.x), int(self.marked_player.y)), 1)
        
    def draw_path(self, surface):
        if len(self.path) < 2:
            return
            
        for i in range(len(self.path) - 1):
            pygame.draw.line(surface, BLACK, self.path[i], self.path[i + 1], 2)
            
        # Draw screen points
        for screen_point in self.screen_points:
            pygame.draw.circle(surface, YELLOW, screen_point, SCREEN_RADIUS, 2)
            
    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.current_path_index = 0
        self.is_screened = False
        self.screen_timer = 0
        
    def move_along_path(self):
        # If defensive player and assigned to guard someone
        if self.type == PlayerType.DEFENSE and self.marked_player:
            # If screened, move slower and try to get around screen
            if self.is_screened:
                self.screen_timer += 1
                # Only screened for a certain time
                if self.screen_timer > 60:  # 1 second at 60fps
                    self.is_screened = False
                    self.screen_timer = 0
                    self.speed = 2
                else:
                    self.speed = 0.5
                    
            # If offensive player has a path, follow them
            if len(self.path) > 0:
                # Continue on own path
                if self.current_path_index < len(self.path) - 1:
                    target_x, target_y = self.path[self.current_path_index + 1]
                    
                    dx = target_x - self.x
                    dy = target_y - self.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    if distance < self.speed:
                        self.x = target_x
                        self.y = target_y
                        self.current_path_index += 1
                    else:
                        self.x += (dx / distance) * self.speed
                        self.y += (dy / distance) * self.speed
                    
                    return True
                else:
                    # Follow offensive player if reached end of path
                    dx = self.marked_player.x - self.x
                    dy = self.marked_player.y - self.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    if distance > PLAYER_RADIUS * 2:
                        self.x += (dx / distance) * self.speed
                        self.y += (dy / distance) * self.speed
                    
                    return True
            else:
                # No path, just follow offensive player
                dx = self.marked_player.x - self.x
                dy = self.marked_player.y - self.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance > PLAYER_RADIUS * 2:
                    self.x += (dx / distance) * self.speed
                    self.y += (dy / distance) * self.speed
                
                return True
        
        # For offensive players or unassigned defense, follow their path
        if not self.path or self.current_path_index >= len(self.path) - 1:
            return False
            
        target_x, target_y = self.path[self.current_path_index + 1]
        
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < self.speed:
            self.x = target_x
            self.y = target_y
            self.current_path_index += 1
        else:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            
        return True
        
    def is_at_screen_point(self):
        if not self.path or self.current_path_index >= len(self.path):
            return False
            
        current_pos = (int(self.x), int(self.y))
        for screen_point in self.screen_points:
            distance = math.sqrt((current_pos[0] - screen_point[0])**2 + (current_pos[1] - screen_point[1])**2)
            if distance < 5:
                return screen_point
        return False

    def is_colliding_with_screen(self, screen_pos, screen_player):
        distance = math.sqrt((self.x - screen_pos[0])**2 + (self.y - screen_pos[1])**2)
        return distance < SCREEN_RADIUS + PLAYER_RADIUS

# Main class
class BasketballPlayDesigner:
    def __init__(self):
        self.state = State.IDLE
        self.players = []
        self.selected_player = None
        self.offense_count = 0
        self.defense_count = 0
        self.active_screens = []
        self.pending_defender = None
        
        # Create buttons
        button_x = COURT_X
        self.buttons = [
            Button(button_x, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, "Add Offense", GREEN, LIGHT_GRAY),
            Button(button_x + BUTTON_WIDTH + BUTTON_MARGIN, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, "Add Defense", RED, LIGHT_GRAY),
            Button(button_x + 2 * (BUTTON_WIDTH + BUTTON_MARGIN), BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, "Set Path", BLUE, LIGHT_GRAY),
            Button(button_x + 3 * (BUTTON_WIDTH + BUTTON_MARGIN), BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, "Add Screen", YELLOW, LIGHT_GRAY),
            Button(button_x + 4 * (BUTTON_WIDTH + BUTTON_MARGIN), BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, "Play", ORANGE, LIGHT_GRAY),
            Button(button_x, BUTTON_Y + BUTTON_HEIGHT + BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT, "Reset", GRAY, LIGHT_GRAY),
            Button(button_x + BUTTON_WIDTH + BUTTON_MARGIN, BUTTON_Y + BUTTON_HEIGHT + BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT, "Replay", ORANGE, LIGHT_GRAY),
            Button(button_x + 2 * (BUTTON_WIDTH + BUTTON_MARGIN), BUTTON_Y + BUTTON_HEIGHT + BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT, "Assign Defender", RED, LIGHT_GRAY)
        ]
        
    def draw_court(self, surface):
        # Court background
        pygame.draw.rect(surface, COURT_COLOR, (COURT_X, COURT_Y, COURT_WIDTH, COURT_HEIGHT))
        pygame.draw.rect(surface, LINE_COLOR, (COURT_X, COURT_Y, COURT_WIDTH, COURT_HEIGHT), 2)
        
        # Half court line
        pygame.draw.line(surface, LINE_COLOR, (COURT_X, COURT_Y + COURT_HEIGHT // 2), 
                         (COURT_X + COURT_WIDTH, COURT_Y + COURT_HEIGHT // 2), 2)
        
        # Center circle
        pygame.draw.circle(surface, LINE_COLOR, (COURT_X + COURT_WIDTH // 2, COURT_Y + COURT_HEIGHT // 2), 60, 2)
        
        # Three point arc
        pygame.draw.arc(surface, LINE_COLOR, 
                        (COURT_X + COURT_WIDTH // 2 - THREE_POINT_RADIUS, COURT_Y - THREE_POINT_RADIUS + 40, 
                         THREE_POINT_RADIUS * 2, THREE_POINT_RADIUS * 2),
                        math.pi, 2 * math.pi, 2)
                        
        # Three point lines
        pygame.draw.line(surface, LINE_COLOR, 
                         (COURT_X, COURT_Y + 40), 
                         (COURT_X, COURT_Y + 40 + THREE_POINT_RADIUS), 2)
        pygame.draw.line(surface, LINE_COLOR, 
                         (COURT_X + COURT_WIDTH, COURT_Y + 40), 
                         (COURT_X + COURT_WIDTH, COURT_Y + 40 + THREE_POINT_RADIUS), 2)
        
        # Free throw line and circle
        pygame.draw.line(surface, LINE_COLOR, 
                         (COURT_X + COURT_WIDTH // 2 - 80, FREE_THROW_LINE_Y), 
                         (COURT_X + COURT_WIDTH // 2 + 80, FREE_THROW_LINE_Y), 2)
        pygame.draw.arc(surface, LINE_COLOR, 
                        (COURT_X + COURT_WIDTH // 2 - FREE_THROW_RADIUS, FREE_THROW_LINE_Y - FREE_THROW_RADIUS, 
                         FREE_THROW_RADIUS * 2, FREE_THROW_RADIUS * 2),
                        math.pi, 2 * math.pi, 2)
        
        # Paint area
        pygame.draw.rect(surface, LINE_COLOR, 
                         (COURT_X + COURT_WIDTH // 2 - 80, COURT_Y, 160, FREE_THROW_LINE_Y - COURT_Y), 2)
        
        # Backboard and rim
        pygame.draw.line(surface, BLACK, 
                         (COURT_X + COURT_WIDTH // 2 - BACKBOARD_WIDTH // 2, BACKBOARD_Y), 
                         (COURT_X + COURT_WIDTH // 2 + BACKBOARD_WIDTH // 2, BACKBOARD_Y), 3)
        pygame.draw.circle(surface, ORANGE, (RIM_X, RIM_Y), 10, 2)
        
    def draw_buttons(self, surface):
        for button in self.buttons:
            button.draw(surface)
            
    def draw_players(self, surface):
        for player in self.players:
            if self.state != State.PLAYING:
                player.draw_path(surface)
            player.draw(surface)
            
    def draw_instruction(self, surface):
        font = pygame.font.SysFont("Arial", 18)
        instruction = ""
        
        if self.state == State.IDLE:
            instruction = "Select an action or player"
        elif self.state == State.PLACING_PLAYER:
            player_type = "offensive" if self.selected_player.type == PlayerType.OFFENSE else "defensive"
            instruction = f"Click to place {player_type} player"
        elif self.state == State.SELECTING_PLAYER:
            instruction = "Click on a player to select"
        elif self.state == State.DRAWING_PATH:
            instruction = "Click to add path points, right-click to finish"
        elif self.state == State.ADDING_SCREEN:
            instruction = "Click on the path to add screen point, right-click to finish"
        elif self.state == State.PLAYING:
            instruction = "Playing animation..."
        elif self.state == State.ASSIGN_DEFENDER:
            if not self.pending_defender:
                instruction = "Select a defensive player first"
            else:
                instruction = f"Select offensive player for defender #{self.pending_defender.number} to guard"
            
        text_surf = font.render(instruction, True, BLACK)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, 30))
        surface.blit(text_surf, text_rect)
        
    def handle_button_click(self, pos, event):
        if self.state == State.PLAYING and not event.type == pygame.MOUSEBUTTONDOWN:
            return
            
        for i, button in enumerate(self.buttons):
            if button.is_clicked(pos, event):
                if i == 0:  # Add Offense
                    if self.state != State.PLAYING:
                        self.state = State.PLACING_PLAYER
                        self.offense_count += 1
                        self.selected_player = Player(-100, -100, PlayerType.OFFENSE, BLUE, self.offense_count)
                elif i == 1:  # Add Defense
                    if self.state != State.PLAYING:
                        self.state = State.PLACING_PLAYER
                        self.defense_count += 1
                        self.selected_player = Player(-100, -100, PlayerType.DEFENSE, RED, self.defense_count)
                elif i == 2:  # Set Path
                    if self.state != State.PLAYING:
                        if self.selected_player:
                            self.selected_player.path = []
                            self.selected_player.screen_points = []
                            self.selected_player.path.append((self.selected_player.x, self.selected_player.y))
                            self.state = State.DRAWING_PATH
                        else:
                            self.state = State.SELECTING_PLAYER
                elif i == 3:  # Add Screen
                    if self.state != State.PLAYING and self.selected_player and self.selected_player.type == PlayerType.OFFENSE:
                        if len(self.selected_player.path) > 1:
                            self.state = State.ADDING_SCREEN
                        else:
                            print("Player needs a path first!")
                elif i == 4:  # Play
                    if self.state != State.PLAYING:
                        for player in self.players:
                            player.reset()
                        self.state = State.PLAYING
                        self.active_screens = []
                elif i == 5:  # Reset
                    self.__init__()
                elif i == 6:  # Replay
                    if self.state == State.PLAYING or any(player.path for player in self.players):
                        for player in self.players:
                            player.reset()
                        self.state = State.PLAYING
                        self.active_screens = []
                elif i == 7:  # Assign Defender
                    if self.state != State.PLAYING:
                        self.state = State.ASSIGN_DEFENDER
                        self.pending_defender = None
                break
                
    def handle_mouse_events(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicked inside court
            if (COURT_X <= pos[0] <= COURT_X + COURT_WIDTH and 
                COURT_Y <= pos[1] <= COURT_Y + COURT_HEIGHT):
                
                if event.button == 1:  # Left click
                    if self.state == State.PLACING_PLAYER:
                        self.selected_player.x = pos[0]
                        self.selected_player.y = pos[1]
                        self.selected_player.original_x = pos[0]
                        self.selected_player.original_y = pos[1]
                        self.players.append(self.selected_player)
                        self.state = State.IDLE
                        self.selected_player = None
                        
                    elif self.state == State.SELECTING_PLAYER:
                        for player in self.players:
                            distance = math.sqrt((player.x - pos[0])**2 + (player.y - pos[1])**2)
                            if distance <= PLAYER_RADIUS:
                                self.selected_player = player
                                self.state = State.IDLE
                                break
                                
                    elif self.state == State.DRAWING_PATH:
                        if self.selected_player:
                            self.selected_player.path.append(pos)
                            
                    elif self.state == State.ADDING_SCREEN:
                        if self.selected_player:
                            # Find closest point on the path
                            min_distance = float('inf')
                            closest_point = None
                            
                            for i in range(len(self.selected_player.path) - 1):
                                x1, y1 = self.selected_player.path[i]
                                x2, y2 = self.selected_player.path[i + 1]
                                
                                # Calculate closest point on line segment
                                line_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                                if line_length == 0:
                                    continue
                                    
                                t = max(0, min(1, ((pos[0] - x1) * (x2 - x1) + (pos[1] - y1) * (y2 - y1)) / (line_length * line_length)))
                                closest_x = x1 + t * (x2 - x1)
                                closest_y = y1 + t * (y2 - y1)
                                
                                distance = math.sqrt((closest_x - pos[0])**2 + (closest_y - pos[1])**2)
                                
                                if distance < min_distance and distance < 20:
                                    min_distance = distance
                                    closest_point = (int(closest_x), int(closest_y))
                            
                            if closest_point:
                                self.selected_player.screen_points.append(closest_point)
                    
                    elif self.state == State.ASSIGN_DEFENDER:
                        for player in self.players:
                            distance = math.sqrt((player.x - pos[0])**2 + (player.y - pos[1])**2)
                            if distance <= PLAYER_RADIUS:
                                if player.type == PlayerType.DEFENSE and not self.pending_defender:
                                    self.pending_defender = player
                                    break
                                elif player.type == PlayerType.OFFENSE and self.pending_defender:
                                    self.pending_defender.marked_player = player
                                    # Set same number for easier reference
                                    self.pending_defender.number = player.number
                                    self.pending_defender = None
                                    self.state = State.IDLE
                                    break
                
                elif event.button == 3:  # Right click
                    if self.state == State.DRAWING_PATH or self.state == State.ADDING_SCREEN:
                        self.state = State.IDLE
                    elif self.state == State.ASSIGN_DEFENDER:
                        self.pending_defender = None
                        self.state = State.IDLE
        
    def update_game(self):
        # Handle player movement during play
        if self.state == State.PLAYING:
            all_done = True
            screen_active = False
            
            # First check for screens and update active_screens list
            for player in self.players:
                if player.type == PlayerType.OFFENSE:
                    screen_pos = player.is_at_screen_point()
                    if screen_pos and screen_pos not in self.active_screens:
                        self.active_screens.append(screen_pos)
            
            # Then move players, handling screen collisions
            for player in self.players:
                if player.move_along_path():
                    all_done = False
                    
                    # Handle collision with screens for defensive players
                    if player.type == PlayerType.DEFENSE:
                        for screen_pos in self.active_screens:
                            if player.is_colliding_with_screen(screen_pos, None) and not player.is_screened:
                                # Defensive player gets "stuck" at screen
                                player.is_screened = True
                                player.speed = 0.5  # Slow down when hitting screen
                                screen_active = True
            
            if all_done and not screen_active:
                self.state = State.IDLE
                
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            screen.fill(WHITE)
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                # Handle button hover
                for button in self.buttons:
                    button.is_hovered(mouse_pos)
                    
                # Handle button clicks
                self.handle_button_click(mouse_pos, event)
                
                # Handle mouse events
                self.handle_mouse_events(mouse_pos, event)
            
            # Update game state
            self.update_game()
            
            # Draw everything
            self.draw_court(screen)
            self.draw_players(screen)
            self.draw_buttons(screen)
            self.draw_instruction(screen)
            
            pygame.display.flip()
            clock.tick(60)
            
        pygame.quit()
        sys.exit()

# Start the game
if __name__ == "__main__":
    game = BasketballPlayDesigner()
    game.run()