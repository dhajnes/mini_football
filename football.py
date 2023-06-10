# Example file showing a basic pygame "game loop"
import pygame
import numpy as np
from itertools import combinations, permutations

# pygame setup
pygame.init()
SCREEN = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
PLAYER_RADIUS = 10

WHITE = (255, 255, 255)
BLACK = (0,0,0)
GREEN = (28, 92, 51)
RED = (180,20,20)
BLUE = (11, 150, 230)
YELLOW = (185, 200, 20)
ORANGE = (200, 140, 20)
PINK = (180, 30, 200)

TEAM_COLORS = [RED, BLUE, YELLOW, ORANGE, PINK]


class Player():
    def __init__(self, player_ID, team_ID, mode, pos=np.array([0,0])):
        self.player_ID = player_ID
        self.team_ID = team_ID
        self.pos = pos
        self.theta = 0
        self.prev_pos = pos
        self.prev_theta = self.theta
        self.velocity_vector = np.array([1,1])
        self.speed_const = 2
        self.ball_possesion = False
        self.r = PLAYER_RADIUS
        self.mode = mode
        self.players = None
        self.ball_state = None

    def __str__(self) -> str:
        return "---\nPlayer {} of team {} at pos:\n{}\nWith rotation: {}, velocity_vector: {}, ball: {}\n---".format(self.player_ID, self.team_ID, self.pos, self.theta, self.velocity_vector, self.ball_possesion)

    def __repr__(self) -> str:
        return "===\nPlayer {} of team {} at pos:\n{}\nWith rotation: {}, velocity_vector: {}, ball: {}\n===".format(self.player_ID, self.team_ID, self.pos, self.theta, self.velocity_vector, self.ball_possesion)
    
    def _get_bounding_box(self):
        """ Returns bounding box of itself, left top corner, right bottom corner `x0, y0, x1, y1`.
        """
        x0, y0 = self.pos[0] - self.r, self.pos[1] + self.r
        x1, y1 = self.pos[0] + self.r, self.pos[1] - self.r
        return (x0, y0, x1, y1)
    
    def update_game_state(self, players, ball_state):
        self.players = players
        self.ball_state = ball_state

    def control(self):

        if self.mode == "pursuit":
            # find closest opponent
            closest_opponent = None
            closest_distance = np.inf
            for player in self.players:
                if player.player_ID == self.player_ID:
                    continue
                if player.team_ID != self.team_ID:
                    dist = np.linalg.norm(self.pos - player.pos)
                    if dist < closest_distance:
                        closest_distance = dist
                        closest_opponent = player
            
            if self.team_ID % 2 == 0:
                # if im even I am pursuer
                velocity_vector = closest_opponent.pos - self.pos
            else:
                # else evader
                velocity_vector = -(closest_opponent.pos - self.pos)

            self.velocity_vector = velocity_vector / np.linalg.norm(velocity_vector)



class Match():
    def __init__(self, mode):
        self.field_dims = np.array([680,520])  # width, height
        self.ball_pos = np.array([])
        self.ball_velocity_vector = np.array([])
        self.field_top_left = np.array([300,100])
        self.field = pygame.Rect(self.field_top_left[0], self.field_top_left[1], self.field_dims[0], self.field_dims[1])
        self.players = []
        self.teams = []
        self.mode = mode
    

    def is_goal(self):
        pass
        # if ball center smaller than left goal or
        # bigger than right goal return true


    def draw_field(self):
        #     assert(type(player) == Player)
        
        # draws the field, green square, white lines, goals etc
        pygame.draw.rect(SCREEN, GREEN, self.field)
        pygame.draw.rect(SCREEN, WHITE, (self.field_top_left[0], self.field_top_left[1], self.field_dims[0], self.field_dims[1]), 3)


    def draw_players(self):
        assert (len(self.players) > 0)
        # print("Number of players: {}".format(len(self.players)))
        for player in self.players:
            # print(player.velocity_vector * player.speed_const)
            new_player_pos = player.pos + (player.velocity_vector * player.speed_const)
            player.pos[0], player.pos[1] = int(np.ceil(new_player_pos[0])), int(np.ceil(new_player_pos[1]))
            

        self.check_for_collisions()

        for player in self.players:
            # draw the player body
            print("[DEBUG] player.pos: ", player.pos)
            pygame.draw.circle(SCREEN, TEAM_COLORS[player.team_ID], player.pos, player.r)

            unit_speed = player.velocity_vector / np.linalg.norm(player.velocity_vector)
            direction_marker_x, direction_marker_y = int(player.pos[0] + unit_speed[0]*player.r), int(player.pos[1] + unit_speed[1]*player.r)
            # draw the direction marker
            pygame.draw.circle(SCREEN, BLACK, (direction_marker_x, direction_marker_y), 3)

    def _check_for_boundary_collisions(self):
        for player in self.players:
            if player.pos[0] < self.field.left:
                overdraw = self.field.left - player.pos[0]
                player.pos[0] += overdraw
            if player.pos[0] > self.field.right:
                overdraw = self.field.right - player.pos[0]
                player.pos[0] += overdraw

            # print("self.field.bottom: ", self.field.bottom)
            # print("self.field.top: ", self.field.top)
            if player.pos[1] > self.field.bottom:
                overdraw = self.field.bottom - player.pos[1]
                player.pos[1] += overdraw
            if player.pos[1] < self.field.top:
                overdraw = self.field.top - player.pos[1]
                player.pos[1] += overdraw

    def _check_for_player_collisions(self):
        
        collision_pairs = list(permutations(self.players, 2))
        for pair in collision_pairs:
            player1, player2 = pair[0], pair[1]
            assert(type(player1) == Player)
            assert(type(player2) == Player)

            # bbox1, bbox2 = player1._get_bounding_box(), player2._get_bounding_box()
            players_dist = np.linalg.norm(player1.pos - player2.pos)
            allowed_dist = player1.r + player2.r
            if players_dist < allowed_dist:
                # collision happening, move player2 away by the collision
                new_player2_pos = player2.pos - allowed_dist - (player1.pos - player2.pos)
                # new_player1_pos = player1.pos - allowed_dist - (player2.pos - player1.pos)
                player2.pos[0], player2.pos[1] = int(np.ceil(new_player2_pos[0])), int(np.ceil(new_player2_pos[1]))
                # player1.pos[0], player1.pos[1] = int(np.ceil(new_player1_pos[0])), int(np.ceil(new_player1_pos[1]))


    def check_for_collisions(self):
        # self._check_for_boundary_collisions()
        self._check_for_player_collisions()
        self._check_for_boundary_collisions()


    def step(self):
        for player in self.players:
            self.ball_pos = np.array([])
            self.ball_velocity_vector = np.array([])
            player.update_game_state(self.players, np.array([self.ball_pos, self.ball_velocity_vector]).ravel())
            player.control()


def spawn_players(match, n_per_team = 2, n_teams = 2):
    for team_id in range(n_teams):
        team = []
        for player_id in range(n_per_team):
            if team_id % 2 == 0:
                x = int(np.ceil(np.random.uniform(match.field.left + PLAYER_RADIUS, match.field.centerx - PLAYER_RADIUS)))
                y = int(np.ceil(np.random.uniform(match.field.top - PLAYER_RADIUS, match.field.bottom + PLAYER_RADIUS)))
            else:
                x = int(np.ceil(np.random.uniform(match.field.centerx + PLAYER_RADIUS, match.field.right - PLAYER_RADIUS)))
                y = int(np.ceil(np.random.uniform(match.field.top - PLAYER_RADIUS, match.field.bottom + PLAYER_RADIUS)))
            print("[DEBUG] spawn coords: {}, {} n team_id: {} player_id: {}".format(x, y, team_id, player_id))
            player = Player(player_ID=player_id + (n_per_team * team_id), team_ID=team_id, pos=np.array([x, y]), mode=match.mode)
            print(player)
            team.append(player)
            
            match.players.append(player)
        match.teams.append(team)



match = Match(mode="pursuit")
spawn_players(match=match, n_per_team=2, n_teams=2)




while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    SCREEN.fill((128,  128, 128))
    match.draw_field()

    match.step()
    match.draw_players()

    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
