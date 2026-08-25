# Monarch v1.1, completed 7/3/26

# This rudimentary Python chess engine is very weak. I'd estimate it to be around 800



from settings import WIDTH, HEIGHT
from board import board
from moves import legal_moves
from evaluation import evaluate
from search import SearchEngine
from utils import is_checkmate, is_stalemate, convert_SAN
import pygame
import time
from game_loop import *
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_DIR = os.path.join(BASE_DIR, "Chess_Engine")

sys.path.append(ENGINE_DIR)

from uci import StockfishEngine
engine = StockfishEngine()
monarch_engine = SearchEngine()

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Monarch")
font = pygame.font.SysFont("Calibri", 24)

game = GameLoop(screen, font)
game.is_player = True
game.run()


pygame.quit()