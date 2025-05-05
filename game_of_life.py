import pygame
import sys
import time
from rich import print
import random

import concurrent.futures
import keyboard
import pyautogui
import tkinter as tk
from tkinter import messagebox

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900
GRID_SIZE_X = 25
GRID_SIZE_Y = 25
CELL_SIZE = min(SCREEN_WIDTH // GRID_SIZE_X, SCREEN_HEIGHT // GRID_SIZE_Y)
WHITE = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("CGoL | Press Right Shift for help")
clock = pygame.time.Clock()

grid = [[WHITE for _ in range(GRID_SIZE_Y)] for _ in range(GRID_SIZE_X)]

generation_count = 0
edit_mode = 0
game_state = "title"


def play_random_death_sound():
    rand_sound = pygame.mixer.Sound(f"death-sound-{random.randint(1, 11)}.wav")
    rand_sound.set_volume(0.1)
    rand_sound.play()

def draw_grid():
    for y in range(GRID_SIZE_Y):
        for x in range(GRID_SIZE_X):
            pygame.draw.rect(screen, grid[x][y], (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.line(screen, (128, 128, 128), (x * CELL_SIZE, 0), (x * CELL_SIZE, y * CELL_SIZE + CELL_SIZE))
    for y in range(GRID_SIZE_Y):
        pygame.draw.line(screen, (128, 128, 128), (0, y * CELL_SIZE), (GRID_SIZE_X * CELL_SIZE, y * CELL_SIZE))
    pygame.draw.line(screen, (128, 128, 128), (0, GRID_SIZE_Y * CELL_SIZE - 1), (GRID_SIZE_X * CELL_SIZE, GRID_SIZE_Y * CELL_SIZE - 1))

def draw_title_screen():
    font_large = pygame.font.SysFont("Arial", 72)
    font_small = pygame.font.SysFont("Arial", 36)

    title_text = font_large.render("Conway's Game of Life", True, (255, 255, 255))
    start_text = font_small.render("Press SPACE to Start", True, (200, 200, 200))

    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

    screen.blit(title_text, title_rect)
    screen.blit(start_text, start_rect)

def get_cell_position(mouse_x, mouse_y):
    return mouse_x // CELL_SIZE, mouse_y // CELL_SIZE

def update_cell_life():
    global grid
    temp_grid = [[WHITE for _ in range(GRID_SIZE_Y)] for _ in range(GRID_SIZE_X)]

    for y in range(GRID_SIZE_Y):
        for x in range(GRID_SIZE_X):
            top_left_value = grid[x-1 if x != 0 else (GRID_SIZE_X-1)][y-1 if y != 0 else (GRID_SIZE_Y-1)]
            top_middle_value = grid[x][y-1 if y != 0 else (GRID_SIZE_Y-1)]
            top_right_value = grid[x+1 if x != (GRID_SIZE_X-1) else 0][y-1 if y != 0 else (GRID_SIZE_Y-1)]
            middle_left_value = grid[x-1 if x != 0 else (GRID_SIZE_X-1)][y]
            middle_right_value = grid[x+1 if x != (GRID_SIZE_X-1) else 0][y]
            bottom_left_value = grid[x-1 if x != 0 else (GRID_SIZE_X-1)][y+1 if y != (GRID_SIZE_Y-1) else 0]
            bottom_middle_value = grid[x][y+1 if y != (GRID_SIZE_Y-1) else 0]
            bottom_right_value = grid[x+1 if x != (GRID_SIZE_X-1) else 0][y+1 if y != (GRID_SIZE_Y-1) else 0]
            red_living_cells = 0
            red_living_cells += (top_left_value == RED)
            red_living_cells += (top_middle_value == RED)
            red_living_cells += (top_right_value == RED)
            red_living_cells += (middle_left_value == RED)
            red_living_cells += (middle_right_value == RED)
            red_living_cells += (bottom_left_value == RED)
            red_living_cells += (bottom_middle_value == RED)
            red_living_cells += (bottom_right_value == RED)
            blue_living_cells = 0
            blue_living_cells += (top_left_value == BLUE)
            blue_living_cells += (top_middle_value == BLUE)
            blue_living_cells += (top_right_value == BLUE)
            blue_living_cells += (middle_left_value == BLUE)
            blue_living_cells += (middle_right_value == BLUE)
            blue_living_cells += (bottom_left_value == BLUE)
            blue_living_cells += (bottom_middle_value == BLUE)
            blue_living_cells += (bottom_right_value == BLUE)

            if grid[x][y] == RED or grid[x][y] == BLUE:
                if red_living_cells > blue_living_cells:
                    if red_living_cells == 2 or red_living_cells == 3:
                        temp_grid[x][y] = RED
                    else:
                        temp_grid[x][y] = WHITE
                elif red_living_cells == blue_living_cells and red_living_cells != 0:
                    temp_grid[x][y] = grid[x][y] 
                    play_random_death_sound()
                else:
                    if blue_living_cells == 2 or blue_living_cells == 3:
                        temp_grid[x][y] = BLUE
                    else:
                        temp_grid[x][y] = WHITE

            elif grid[x][y] == WHITE:
                if red_living_cells > blue_living_cells:
                    if red_living_cells == 3:
                        temp_grid[x][y] = RED
                elif blue_living_cells > red_living_cells:
                    if blue_living_cells == 3:
                        temp_grid[x][y] = BLUE

    grid = temp_grid

def print_color_count():
    white_count = 0
    red_count = 0
    blue_count = 0
    for x in range(GRID_SIZE_X):
        for y in range(GRID_SIZE_Y):
            white_count += (grid[x][y] == WHITE)
            red_count += (grid[x][y] == RED)
            blue_count += (grid[x][y] == BLUE) 
    print("[green]\nCURRENT COLOR COUNT:")
    print(f"WHITE: {white_count}")
    print(f"[red]RED: {red_count}\n")
    pygame.display.set_caption(f"GENERATIONS: {generation_count}   RED: {red_count}  BLUE: {blue_count}")

def get_current_color_count_from_grid_right_now():
    white_count = 0
    red_count = 0
    blue_count = 0
    for x in range(GRID_SIZE_X):
        for y in range(GRID_SIZE_Y):
            white_count += (grid[x][y] == WHITE)
            red_count += (grid[x][y] == RED)
            blue_count += (grid[x][y] == BLUE) 
    print("RED: " + str(red_count) + ", " +  "BLUE: " + str(blue_count))

    zoop = tk.Tk()
    zoop.withdraw()
    messagebox.showinfo("ALERT", "P1 ARMY SIZE: " + str(red_count) + ", " "P2 ARMY SIZE: " + str(blue_count))
    zoop.destroy()

edit_message = ""
message_time = 0 


edit_message = ""  
game_message = "" 
message_time = 0 

def main():
    global active_tasks, message_queue, generation_count, edit_mode, game_state
    global edit_message, message_time, game_message

    running_state = False
    last_print_time = 0

    game_state = "title"

    while True:
        current_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if game_state == "title":  
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_state = "game" 
                    continue 

            elif game_state == "game":  
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = get_cell_position(event.pos[0], event.pos[1])
                    if 0 <= x < GRID_SIZE_X and 0 <= y < GRID_SIZE_Y:
                        if edit_mode == 0:
                            if event.button == 1:
                                grid[x][y] = RED if grid[x][y] == WHITE else WHITE
                            elif event.button == 3:
                                grid[x][y] = BLUE if grid[x][y] == WHITE else WHITE
                        elif edit_mode == 1:
                            if event.button == 1:
                                grid[x][y] = RED if grid[x][y] == WHITE else WHITE
                        elif edit_mode == 2:
                            if event.button == 1:
                                grid[x][y] = BLUE if grid[x][y] == WHITE else WHITE

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        running_state = not running_state
                        if running_state:
                            game_message = "Game Running"
                        else:
                            game_message = "Game Paused"
                        message_time = current_time  

                    elif event.key == pygame.K_TAB:
                        root = tk.Tk()
                        root.withdraw()
                        messagebox.showinfo("ALERT", "ELAPSED GENERATIONS: " + str(generation_count))
                        root.destroy()
                        print(generation_count)

                    elif event.key == pygame.K_LSHIFT:
                        get_current_color_count_from_grid_right_now()
                    
                    elif event.key == pygame.K_RSHIFT:
                        root = tk.Tk()
                        root.withdraw()
                        messagebox.showinfo("HELP", "Number keys for editing modes\nEsc = Exit\nLeft Shift = Unit count\nTab = Generation count\nSpace = Play/Pause")
                        root.destroy()

                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                    elif event.key == pygame.K_1:
                        edit_mode = 1
                        edit_message = "P1 editing mode ON"
                        message_time = current_time  
                        print("[cyan]Player 1 edit mode ON")
                    elif event.key == pygame.K_2:
                        edit_mode = 2
                        edit_message = "P2 editing mode ON"
                        message_time = current_time  
                        print("[cyan]Player 2 edit mode ON")
                    elif event.key == pygame.K_0:
                        edit_mode = 0
                        edit_message = "Both-player edit mode ON (default)"
                        message_time = current_time  
                        print("[cyan]Both-player edit mode ON (default)")

        if current_time - message_time > 2.5:
            edit_message = ""  
            game_message = ""

        if game_state == "game" and running_state and current_time - last_print_time >= 0.1:
            update_cell_life()
            generation_count += 1
            last_print_time = current_time

        if game_state == "title":
            screen.fill((0, 0, 0))
            draw_title_screen()

        elif game_state == "game":
            screen.fill(WHITE)
            draw_grid()

            if edit_message != "":
                font = pygame.font.SysFont("Consolas", 36)
                message_text = font.render(edit_message, True, (255, 255, 255))
                screen.blit(message_text, (10, SCREEN_HEIGHT - 50))

            if game_message != "":
                font = pygame.font.SysFont("Consolas", 36)
                message_text = font.render(game_message, True, (255, 255, 255))
                screen.blit(message_text, (10, SCREEN_HEIGHT - 100))

        pygame.display.flip()
        clock.tick(600)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

if __name__ == "__main__":
    main()