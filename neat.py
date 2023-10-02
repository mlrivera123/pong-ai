import pygame
from pong import Paddle
from pong import Ball
from pong import draw
from pong import main
pygame.init()

# Create window for the game
window_width, window_height = 700,  500
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("pong training montage")
score_font = pygame.font.SysFont("ariel", 50)


# Set paddle width, height
paddle_width, paddle_height = 20, 100
left_paddle_starting_x = 10
right_paddle_starting_x = window_width - 10
paddle_starting_y = window_height/2 - paddle_height/2

# Initialize paddle as x coord, y coord, width, height
left_paddle = Paddle(left_paddle_starting_x, paddle_starting_y, paddle_width, paddle_height)
right_paddle = Paddle(right_paddle_starting_x, paddle_starting_y, paddle_width, paddle_height)

# Initializing ball starting point
ball_radius = 7
ball_starting_x = window_width/2
ball_starting_y = window_height/2
ball = Ball(ball_starting_x, ball_starting_y, ball_radius)

# Setting game info
winning_score = 10
left_starting_score = 0
right_starting_score = 0

main()