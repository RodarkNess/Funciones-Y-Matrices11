
# Constantes y configuración global (con rutas absolutas de assets)
import pygame
pygame.init()

from pathlib import Path

# === BASE_DIR absoluto: carpeta que contiene este config.py ===
BASE_DIR = Path(__file__).resolve().parent

def asset_path(*parts) -> str:
    """Construye una ruta absoluta hacia assets, independiente del cwd."""
    return str(BASE_DIR.joinpath(*parts))

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1200
TILE_SIZE = 80
VISIBLE_RADIUS = 3
FPS = 60

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
GREEN = (0, 150, 0)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# --- Gameplay ---
ENEMY_DAMAGE = 25
MONEY_MIN = 10
MONEY_MAX = 50

# --- Minimap ---
MINIMAP_MAX_W = 220
MINIMAP_MAX_H = 180
MINIMAP_MARGIN = 10

# --- Puntajes ---
SCORE_ITEM = 50
SCORE_ENEMY = 100
SCORE_LEVEL = 500
SCORE_LEVEL_BONUS_PER_LEVEL = 50  # bonus adicional por nivel

# --- Texturas (rutas absolutas) ---
IMG_PLAYER = asset_path('assets', 'images', 'player.png')
IMG_ENEMY  = asset_path('assets', 'images', 'enemy.png')
IMG_CHEST  = asset_path('assets', 'images', 'chest.png')
IMG_PORTAL = asset_path('assets', 'images', 'portal.png')
IMG_FLOOR  = asset_path('assets', 'images', 'floor.png')
IMG_WALL   = asset_path('assets', 'images', 'wall.png')

# --- Escala de render ---
RENDER_SCALE = 1.25  # mantener TILE_SIZE=40 y escalar a 1.25

# --- Sonidos (FX) ---
SND_CHEST  = asset_path('assets', 'sounds', 'chest.wav')
SND_SWORD  = asset_path('assets', 'sounds', 'sword.wav')
SND_HURT   = asset_path('assets', 'sounds', 'hurt.wav')
SND_PORTAL = asset_path('assets', 'sounds', 'portal.wav')

# --- Música por estados (rutas absolutas) ---
SND_MUSIC_TITLE    = asset_path('assets', 'sounds', 'music.wav')     # loop en título/juego
SND_MUSIC_GAMEOVER = asset_path('assets', 'sounds', 'gameover.wav')  # loop en Game Over

# Volúmenes
MUSIC_VOLUME = 0.5   # 50 de 100
FX_VOLUME    = 0.8

# --- HUD icons (rutas absolutas) ---
HUD_HEART_FULL  = asset_path('assets', 'images', 'heart_full.png')
HUD_HEART_EMPTY = asset_path('assets', 'images', 'heart_empty.png')
HUD_ARMOR_ON    = asset_path('assets', 'images', 'armor_on.png')
HUD_ARMOR_OFF   = asset_path('assets', 'images', 'armor_off.png')
HUD_SWORD_ON    = asset_path('assets', 'images', 'sword_on.png')
HUD_SWORD_OFF   = asset_path('assets', 'images', 'sword_off.png')
