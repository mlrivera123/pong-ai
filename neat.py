import pygame
from pong import Paddle
from pong import Ball
from pong import draw
from pong import handle_paddle_movement
import neat
import os
pygame.init()

# Create window for the game
window_width, window_height = 700,  500
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("pong training montage")
score_font = pygame.font.SysFont("ariel", 50)

# Set paddle width, height
paddle_width, paddle_height = 20, 100
left_paddle_starting_x = 10
right_paddle_starting_x = window_width - paddle_width - 10
paddle_starting_y = window_height/2 - paddle_height/2

# Initialize paddle as x coord, y coord, width, height
left_paddle = Paddle(left_paddle_starting_x, paddle_starting_y, paddle_width, paddle_height)
right_paddle = Paddle(right_paddle_starting_x, paddle_starting_y, paddle_width, paddle_height)

# Initializing ball starting point
ball_radius = 7
ball_max_veolcity = 5
ball_starting_x = window_width/2
ball_starting_y = window_height/2
ball = Ball(ball_starting_x, ball_starting_y, ball_radius)

# Setting game info
winning_score = 10

# We create a game stats object that will be returned by a single game loop
class game_stats:
    def __init__(self, left_hits, right_hits, left_score, right_score):
        self.left_hits = left_hits        
        self.right_hits = right_hits
        self.left_score = left_score
        self.right_score = right_score

# Creating a pong game class object
class pong_game():
    # Creating a game initializer
    def __init__(self, window, left_paddle, right_paddle, ball):
        self.window = window
        self.window_height = 500
        self.window_width = 700 
        self.left_paddle = left_paddle
        self.right_paddle = right_paddle
        self.ball = ball
        self.left_score = 0
        self.right_score = 0
        # Set variables for fitness function
        self.left_hits = 0
        self.right_hits = 0

    # Put objects back into starting positions
    def reset(self):
        self.ball.reset()
        self.left_paddle.reset()
        self.right_paddle.reset()
        self.left_score = 0
        self.right_score = 0
        self.left_hits = 0
        self.right_hits = 0

    # Handle collision, we have to rewrite this function to update values as internal values
    def handle_collision(self):
        # hits bottom floor, change direction
        if self.ball.y + self.ball.radius >= self.window_height:
            self.ball.y_vel *= -1
        # hits ceiling, change direction
        elif self.ball.y - self.ball.radius <= 0:
            self.ball.y_vel *= -1
        # left paddle
        if self.ball.x_vel < 0:
            if self.ball.y >= self.left_paddle.y and self.ball.y <= self.left_paddle.y + paddle_height:
                if self.ball.x - self.ball.radius <= self.left_paddle.x + self.left_paddle.width:
                    self.ball.x_vel *= -1
                    # Handling collisions
                    middle_y = left_paddle.y + left_paddle.height / 2
                    difference_in_y = middle_y - ball.y
                    reduction_factor = (left_paddle.height / 2) / ball_max_veolcity
                    y_vel = difference_in_y / reduction_factor
                    self.ball.y_vel = y_vel * -1
                    self.left_hits += 1
        # right paddles
        else:
            if ball.y >= right_paddle.y and ball.y <= right_paddle.y + paddle_height:
                if ball.x + ball.radius >= right_paddle.x:
                    ball.x_vel *= -1

                    middle_y = self.right_paddle.y + right_paddle.height / 2
                    difference_in_y = middle_y - ball.y
                    reduction_factor = (right_paddle.height / 2) / ball_max_veolcity
                    y_vel = difference_in_y / reduction_factor
                    self.ball.y_vel = y_vel * -1
                    self.right_hits += 1

    # Function in charge of user inputs
    def game_handle_paddle_movement(self, keys):
        handle_paddle_movement(keys, left_paddle, right_paddle)

    def move_paddle(self, left, up):
        # Left = True
        # Up = True
        if left:
            # Handles left paddle movement
            if up:
                handle_paddle_movement(pygame.K_w, self.left_paddle, self.right_paddle)
            else:
                handle_paddle_movement(pygame.K_s, self.left_paddle, self.right_paddle)
        else:
            # Handles right paddle movement
            if up:
                handle_paddle_movement(pygame.K_UP, self.left_paddle, self.right_paddle)
            else:
                handle_paddle_movement(pygame.K_DOWN, self.left_paddle, self.right_paddle)
        


    # Run a single game loop to test fitness
    def execute_single_loop(self):
        self.ball.move()
        self.handle_collision()

        if self.ball.x < 0:
            self.ball.reset()
            self.right_score += 1
        elif self.ball.x > window_width:
            self.ball.reset()
            self.left_score += 1

        game_statistics = game_stats(self.left_hits, self.right_hits, self.left_score, self.right_score)
        #print(self.left_hits, self.right_hits, self.left_score, self.right_score)
        return game_statistics
    
    def draw_game(self):
        draw(self.window, [self.left_paddle, self.right_paddle], self.ball, self.left_score, self.right_score)

    """
    NEAT AI IMPLEMENTATION
    Create a neat.population.Population object using the Config object created above.
    Call the run method on the Population object, giving it your fitness function and (optionally) the maximum number of generations you want NEAT to run.
    """

    def train_ai(self, genome1, genome2, config):
    # This function takes two genomes and a config file of meta data as an input
    # Each genome contains two sets of genes: Node genes which specify a single neuron
    # And connection genes which specifies a single connection between neurons

    # First we create two forward feedback neural networks
    # These networks will be trained against eachother
        neural_network1 = neat.nn.FeedForwardNetwork.create(genome1, genome2)
        neural_network2 = neat.nn.FeedForwardNetwork.create(genome1, genome2)

    # Next we want to define decisions based off of game variables
    # We will build connections between the y position of the ball and the y position of the paddles
    # We will also include the distance between the ball and the paddle
    # The neural network should coorelate the right paddle height with the height of the ball


        # Left paddle decision
        neural_network1_output = neural_network1.activate(self.left_paddle.y, self.ball.y, (abs(self.left_paddle.x - self.ball.x)))
        neural_network1_direction = neural_network1_output.index(max(neural_network1_output))

        # Neural network direction should return
        # 0 Stay still
        # 1 Move paddle up
        # 2 move paddle down
        if neural_network1_direction == 1:
            self.move_paddle(left = True, up = True)
        elif neural_network1_direction == 2:
            self.move_paddle(left = True, up = False)

        # Right paddle decision
        neural_network2_output = neural_network2.activate(self.right_paddle.y, self.ball.y, (abs(self.right_paddle.x - self.ball.x)))
        neural_network2_direction = neural_network2_output.index(max(neural_network2_output))

        if neural_network2_direction == 1:
            self.move_paddle(left = False, up = True)
        elif neural_network2_direction == 2:
            self.move_paddle(left = False, up = False)

        print(neural_network1_output, neural_network2_output)
        game_output_statistics = self.execute_single_loop()

        self.draw_game()

        # Once a game is finished we will update fitness scores by however many hits a paddle got
        if game_output_statistics.left_score >= 1 or game_output_statistics.right_score >= 1 or game_output_statistics.left_hits >= 50:
            genome1.fitness += game_output_statistics.left_hits
            genome2.fitness += game_output_statistics.right_hits




def run_neat(config):
    p = neat.Population(config)
    # how to restore from previous checkpoint
    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-19')
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # saves checkpoint after generation, allows us to save process
    p.add_reporter(neat.Checkpointer(1))

    # change how many generations you want to make
    winner = p.run(eval_genomes, 1)
    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)


    
clock = pygame.time.Clock()
game = pong_game(window, left_paddle, right_paddle, ball)

run = True
while run:
    clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False


    game.execute_single_loop()
    game.game_handle_paddle_movement(keys)
    game.draw_game()

pygame.quit()