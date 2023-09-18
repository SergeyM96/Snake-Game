# Snake Game - Version 1
# Developed by Sergey Morozov

"""
Play with arrow keys or 'a''w''s'd', to pause the game press P.
"""
import pygame
import random
import pickle
import os

# Import Button class
from Button import button

# Initialize Pygame
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'  # Center pygame on the user's screen.

# Define colors
WHITE = (255, 255, 255)
NAVI_BLUE = (36, 62, 114)
RED = (255, 0, 0)
LIGHT_RED = (249, 52, 52)
GREEN = (0, 155, 0)
LIGHT_GREEN = (74, 196, 74)

# Game property constants
BLOCK_SIZE = 20                # Size of each block (square) in pixels
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 600
CENTER_DISPLAY_WIDTH = DISPLAY_WIDTH // 2  # Center X-coordinate of the display
CENTER_DISPLAY_HEIGHT = DISPLAY_HEIGHT // 2  # Center Y-coordinate of the display
BOUND_X = DISPLAY_WIDTH - (BLOCK_SIZE * 2)  # X-coordinate boundary
BOUND_Y = DISPLAY_HEIGHT - (BLOCK_SIZE * 2)  # Y-coordinate boundary
SCORE_OFFSET_X = 140           # X-coordinate offset for displaying scores
SCORE_OFFSET_Y = 27            # Y-coordinate offset for displaying scores
SCORE_BOUND_WIDTH = DISPLAY_WIDTH - 180      # Width of the score display area
SCORE_BOUND_HEIGHT = 100 - BLOCK_SIZE        # Height of the score display area

FPS = 9  # controls the speed of the snake.

# Game variables
DEGREES = 270                   # Initial direction of the snake (270 degrees = up)
RAND_APPLE_X, RAND_APPLE_Y = (0, 0)           # Initial apple coordinates
GOLDEN_APPLE = random.randint(1, 10) == 10   # Indicates if a golden apple is present
LEAD_X = CENTER_DISPLAY_WIDTH   # Initial X-coordinate of the snake's head
LEAD_Y = CENTER_DISPLAY_HEIGHT  # Initial Y-coordinate of the snake's head
LEAD_X_CHANGE = BLOCK_SIZE      # Initial change in X-coordinate (movement)
LEAD_Y_CHANGE = 0               # Initial change in Y-coordinate (movement)
APPLE_COUNTER = 0               # Current score
HIGH_SCORE = 0                  # Highest score
BUTTON_WIDTH = 150              # Width of buttons
BUTTON_HEIGHT = 50              # Height of buttons
SNAKE_LIST = []                 # List to store snake coordinates

# Import fonts
BODY_FONT = pygame.font.SysFont("comicsansms", 50)    # Font for the game body
BUTTON_FONT = pygame.font.SysFont("comicsansms", 25)  # Font for buttons

# Import images
SNAKE_HEAD_IMAGE = pygame.image.load("images/SnakeHead.png")      # Snake head image
SNAKE_BODY_IMAGE = pygame.image.load("images/SnakeBody.png")      # Snake body image
APPLE_IMAGE = pygame.image.load("images/Apple.png")               # Apple image
GOLDEN_APPLE_IMAGE = pygame.image.load("images/GoldenApple.png")  # Golden apple image
ICON = pygame.image.load("images/Icon.png")                       # Game icon

# Configure display
GAME_DISPLAY = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption("Snake")
pygame.display.set_icon(ICON)
CLOCK = pygame.time.Clock()

# Define Start and Quit buttons
START_BUTTON = button(GREEN, LIGHT_GREEN, GAME_DISPLAY, "START", CENTER_DISPLAY_WIDTH - (BUTTON_WIDTH // 2),
                      CENTER_DISPLAY_HEIGHT - 30, BUTTON_WIDTH, BUTTON_HEIGHT, WHITE, -30, CENTER_DISPLAY_WIDTH,
                      CENTER_DISPLAY_HEIGHT, BUTTON_FONT)

QUIT_BUTTON = button(RED, LIGHT_RED, GAME_DISPLAY, "QUIT", CENTER_DISPLAY_WIDTH - (BUTTON_WIDTH // 2),
                     CENTER_DISPLAY_HEIGHT + 50, BUTTON_WIDTH, BUTTON_HEIGHT, WHITE, 50, CENTER_DISPLAY_WIDTH,
                     CENTER_DISPLAY_HEIGHT, BUTTON_FONT)

# Load high score from a file
try:
    with open('score.dat', 'rb') as file:
        HIGH_SCORE = pickle.load(file)
except FileNotFoundError:
    HIGH_SCORE = 0
    with open('score.dat', 'wb') as file:
        pickle.dump(HIGH_SCORE, file)


def startScreen():
    """
    Display the game start screen and handle user interactions.
    """
    while True:
        fillBackground(True)
        put_message_custom("Welcome to Snake!", GREEN, -80)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                quitProgram()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                reset()
                return

        START_BUTTON.showButton()
        QUIT_BUTTON.showButton()

        if START_BUTTON.isHovered(getCursorPos()):
            pygame.mouse.set_cursor(*pygame.cursors.tri_left)
            if isLeftMouseClicked() or isEnterKeyPressed():
                reset()
                return
        elif QUIT_BUTTON.isHovered(getCursorPos()):
            pygame.mouse.set_cursor(*pygame.cursors.tri_left)
            if isLeftMouseClicked():
                quitProgram()
        else:
            pygame.mouse.set_cursor(*pygame.cursors.arrow)

        pygame.display.update()


def isEnterKeyPressed():
    keys = pygame.key.get_pressed()
    return keys[pygame.K_RETURN]


def showScores(score, new):
    """
    Display the current score and high score on the screen.
    param score: The current score.
    param new: True if it's a new high score, False otherwise.
    """
    screen_text = pygame.font.SysFont("comicsansms", 15).render("Score: " + str(score), True, NAVI_BLUE)
    GAME_DISPLAY.blit(screen_text, (DISPLAY_WIDTH - SCORE_OFFSET_X, SCORE_OFFSET_Y + 20))

    high_score = pygame.font.SysFont("comicsansms", 15).render("High Score: " + str(HIGH_SCORE), True, NAVI_BLUE)

    if new:
        high_score = pygame.font.SysFont("comicsansms", 13).render("New High Score!", True, RED)

    GAME_DISPLAY.blit(high_score, (DISPLAY_WIDTH - SCORE_OFFSET_X, SCORE_OFFSET_Y))


def pause():
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                quitProgram()
            if event.type == pygame.MOUSEBUTTONDOWN:
                return

        put_message_center("Game Paused", NAVI_BLUE)
        put_message_custom("Click to resume..", NAVI_BLUE, fontSize=30, offsetY=50)
        pygame.display.update()


def randomApple():
    """
    Generate a random apple location.
    """
    global RAND_APPLE_X
    global RAND_APPLE_Y
    global GOLDEN_APPLE

    lastAppleX = RAND_APPLE_X
    lastAppleY = RAND_APPLE_Y

    GOLDEN_APPLE = generateGoldenApple()

    RAND_APPLE_X = round(random.randint(BLOCK_SIZE * 2, BOUND_X - (BLOCK_SIZE * 4)) / BLOCK_SIZE) * BLOCK_SIZE
    RAND_APPLE_Y = round(random.randint(BLOCK_SIZE * 2, BOUND_Y - (BLOCK_SIZE * 4)) / BLOCK_SIZE) * BLOCK_SIZE

    while [RAND_APPLE_X, RAND_APPLE_Y] in SNAKE_LIST or RAND_APPLE_X == lastAppleX or RAND_APPLE_Y == lastAppleY or \
            (RAND_APPLE_X >= SCORE_BOUND_WIDTH and RAND_APPLE_Y <= SCORE_BOUND_HEIGHT):
        RAND_APPLE_X = round(random.randint(BLOCK_SIZE * 2, BOUND_X - SCORE_BOUND_WIDTH - (BLOCK_SIZE * 4)) / BLOCK_SIZE) * \
                     BLOCK_SIZE
        RAND_APPLE_Y = round(random.randint(BLOCK_SIZE * 2, BOUND_Y - SCORE_BOUND_HEIGHT - (BLOCK_SIZE * 4)) / BLOCK_SIZE) * \
                     BLOCK_SIZE


def generateGoldenApple():
    return random.randint(1, 15) == 1


def snake(snakeCoors):
    rotatedHead = pygame.transform.rotate(SNAKE_HEAD_IMAGE, DEGREES)

    GAME_DISPLAY.blit(rotatedHead, (snakeCoors[-1][0], snakeCoors[-1][1]))

    for coor in snakeCoors[:-1]:
        GAME_DISPLAY.blit(SNAKE_BODY_IMAGE, [coor[0], coor[1]])


def put_message_center(message, color):
    screen_text = BODY_FONT.render(message, True, color)
    GAME_DISPLAY.blit(screen_text, [CENTER_DISPLAY_WIDTH - (screen_text.get_rect().width // 2), CENTER_DISPLAY_HEIGHT -
                                   (screen_text.get_rect().height // 2)])


def put_message_custom(message, color, offsetY, fontSize=50):
    screen_text = pygame.font.SysFont("comicsansms", fontSize).render(message, True, color)
    GAME_DISPLAY.blit(screen_text, [CENTER_DISPLAY_WIDTH - (screen_text.get_rect().width // 2),
                                   (CENTER_DISPLAY_HEIGHT - (screen_text.get_rect().height // 2) + offsetY)])


def quitProgram():
    pygame.quit()
    exit()


def fillBackground(isStartScreen):
    GAME_DISPLAY.fill(NAVI_BLUE)
    GAME_DISPLAY.fill(WHITE, [BLOCK_SIZE, BLOCK_SIZE, BOUND_X, BOUND_Y])

    if not isStartScreen:
        GAME_DISPLAY.fill(NAVI_BLUE, [SCORE_BOUND_WIDTH, BLOCK_SIZE, DISPLAY_WIDTH - 150, SCORE_BOUND_HEIGHT])
        GAME_DISPLAY.fill(WHITE, [(SCORE_BOUND_WIDTH + BLOCK_SIZE, BLOCK_SIZE), (BLOCK_SIZE * 7, 100 - (BLOCK_SIZE * 2))])


def reset():
    """
    Reset the game state to start a new game.
    """
    global APPLE_COUNTER
    global DEGREES
    global HIGH_SCORE
    global LEAD_X
    global LEAD_Y
    global LEAD_X_CHANGE
    global LEAD_Y_CHANGE
    global RAND_APPLE_X
    global RAND_APPLE_Y
    global SNAKE_LIST
    global GOLDEN_APPLE

    DEGREES = 270
    LEAD_X = CENTER_DISPLAY_WIDTH
    LEAD_Y = CENTER_DISPLAY_HEIGHT
    LEAD_X_CHANGE = BLOCK_SIZE
    LEAD_Y_CHANGE = 0
    RAND_APPLE_X, RAND_APPLE_Y, APPLE_COUNTER = (0, 0, 0)
    SNAKE_LIST = []
    GOLDEN_APPLE = generateGoldenApple()


def gameLoop():
    """
    This is the main game loop, called by startScreen() earlier.
    :return:
    """
    global APPLE_COUNTER
    global DEGREES
    global HIGH_SCORE
    global LEAD_X
    global LEAD_Y
    global LEAD_X_CHANGE
    global LEAD_Y_CHANGE
    global SNAKE_LIST
    global GOLDEN_APPLE
    global FPS
    LEAD_X_CHANGE = BLOCK_SIZE
    LEAD_Y_CHANGE = 0
    game_over = False
    GOLDEN_APPLE = generateGoldenApple()

    randomApple()

    while True:
        events = pygame.event.get()
        fillBackground(False)

        while game_over:  # the user lost
            if HIGH_SCORE < APPLE_COUNTER:
                # set a new high score if applicable
                with open('score.dat', 'wb') as file:
                    pickle.dump(APPLE_COUNTER, file)
                with open('score.dat', 'rb') as file:
                    HIGH_SCORE = pickle.load(file)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    quitProgram()
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    reset()
                    gameLoop()
            fillBackground(False)
            showScores(APPLE_COUNTER, HIGH_SCORE < APPLE_COUNTER)
            put_message_center("Game Over!", RED)
            put_message_custom("Click to play again.", NAVI_BLUE, fontSize=30, offsetY=50)
            pygame.display.update()

        for event in events:
            if event.type == pygame.QUIT:
                quitProgram()
            if event.type == pygame.KEYDOWN:  # key presses
                if (len(SNAKE_LIST) < 2 or DEGREES != 270) and (event.key == pygame.K_LEFT or event.key == pygame.K_a):
                    LEAD_X_CHANGE = -BLOCK_SIZE
                    LEAD_Y_CHANGE = 0
                    DEGREES = 90
                elif (len(SNAKE_LIST) < 2 or DEGREES != 90) and (event.key == pygame.K_RIGHT or event.key == pygame.K_d):
                    LEAD_X_CHANGE = BLOCK_SIZE
                    LEAD_Y_CHANGE = 0
                    DEGREES = 270
                elif (len(SNAKE_LIST) < 2 or DEGREES != 180) and (event.key == pygame.K_UP or event.key == pygame.K_w):
                    LEAD_Y_CHANGE = -BLOCK_SIZE
                    LEAD_X_CHANGE = 0
                    DEGREES = 0
                elif (len(SNAKE_LIST) < 2 or DEGREES != 0) and (event.key == pygame.K_DOWN or event.key == pygame.K_s):
                    LEAD_Y_CHANGE = BLOCK_SIZE
                    LEAD_X_CHANGE = 0
                    DEGREES = 180
                elif event.key == pygame.K_p:
                    pause()

        LEAD_X += LEAD_X_CHANGE
        LEAD_Y += LEAD_Y_CHANGE

        if LEAD_X == RAND_APPLE_X and LEAD_Y == RAND_APPLE_Y:  # if the snake has eaten the apple
            if GOLDEN_APPLE:
                APPLE_COUNTER += 3
            else:
                APPLE_COUNTER += 1
            randomApple()

        snakeHead = [LEAD_X, LEAD_Y]  # updates the snake's head location

        # checks if a golden apple should be generated
        if GOLDEN_APPLE:
            GAME_DISPLAY.blit(GOLDEN_APPLE_IMAGE, (RAND_APPLE_X, RAND_APPLE_Y))
        else:
            GAME_DISPLAY.blit(APPLE_IMAGE, (RAND_APPLE_X, RAND_APPLE_Y))

        # condition checking if the snake has run into itself or gone out of bounds
        if snakeHead in SNAKE_LIST[:-1] or \
                (LEAD_X > BOUND_X or LEAD_X < BLOCK_SIZE or LEAD_Y > BOUND_Y or LEAD_Y < BLOCK_SIZE) \
                or (LEAD_X >= SCORE_BOUND_WIDTH and LEAD_Y <= SCORE_BOUND_HEIGHT):
            game_over = True

        SNAKE_LIST.append(snakeHead)  # add the snakeHead
        snake(SNAKE_LIST)  # generate the snake

        if len(SNAKE_LIST) > APPLE_COUNTER:  # delete the first element of the snakeList.
            del SNAKE_LIST[0]

        showScores(APPLE_COUNTER, HIGH_SCORE < APPLE_COUNTER)
        pygame.display.update()
        CLOCK.tick(FPS + (APPLE_COUNTER / 50))  # set FPS, scales with how many apples the user has


def getCursorPos():
    return pygame.mouse.get_pos()


def isLeftMouseClicked():
    return pygame.mouse.get_pressed()[0]


# Main game loop
while True:
    startScreen()
    gameLoop()
