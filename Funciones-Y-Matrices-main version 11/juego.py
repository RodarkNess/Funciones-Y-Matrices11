# Clase Juego (lógica principal y bucle)
import pygame
import sys
import math
import random
from pathlib import Path

from config import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, VISIBLE_RADIUS, FPS
from config import BLACK, WHITE, GRAY, DARK_GRAY, GREEN, BROWN, RED, BLUE, YELLOW, PURPLE

# Minimap (defaults si faltan)
try:
    from config import MINIMAP_MAX_W, MINIMAP_MAX_H, MINIMAP_MARGIN
except Exception:
    MINIMAP_MAX_W = 220
    MINIMAP_MAX_H = 180
    MINIMAP_MARGIN = 10

# Puntajes
try:
    from config import SCORE_ITEM, SCORE_ENEMY, SCORE_LEVEL, SCORE_LEVEL_BONUS_PER_LEVEL
except Exception:
    SCORE_ITEM = 50
    SCORE_ENEMY = 100
    SCORE_LEVEL = 500
    SCORE_LEVEL_BONUS_PER_LEVEL = 50

# Texturas & sonidos & HUD & título/gameover
try:
    from config import IMG_PLAYER, IMG_ENEMY, IMG_CHEST, IMG_PORTAL, IMG_FLOOR, IMG_WALL, RENDER_SCALE
    from config import SND_CHEST, SND_SWORD, SND_HURT, SND_PORTAL
    from config import SND_MUSIC_TITLE, SND_MUSIC_GAMEOVER, MUSIC_VOLUME, FX_VOLUME
    from config import HUD_HEART_FULL, HUD_HEART_EMPTY, HUD_ARMOR_ON, HUD_ARMOR_OFF, HUD_SWORD_ON, HUD_SWORD_OFF
    from config import TITLE_IMAGE, GAMEOVER_IMAGE, GAMEOVER_SCORE_Y_FACTOR, GAMEOVER_SCORE_OFFSET
except Exception:
    IMG_PLAYER = 'assets/images/player.png'
    IMG_ENEMY  = 'assets/images/enemy.png'
    IMG_CHEST  = 'assets/images/chest.png'
    IMG_PORTAL = 'assets/images/portal.png'
    IMG_FLOOR  = 'assets/images/floor.png'
    IMG_WALL   = 'assets/images/wall.png'
    RENDER_SCALE = 1.0
    SND_CHEST  = 'assets/sounds/chest.wav'
    SND_SWORD  = 'assets/sounds/sword.wav'
    SND_HURT   = 'assets/sounds/hurt.wav'
    SND_PORTAL = 'assets/sounds/portal.wav'
    SND_MUSIC_TITLE    = 'assets/sounds/music.wav'
    SND_MUSIC_GAMEOVER = 'assets/sounds/gameover.wav'
    MUSIC_VOLUME = 0.5
    FX_VOLUME    = 0.8
    HUD_HEART_FULL  = 'assets/images/heart_full.png'
    HUD_HEART_EMPTY = 'assets/images/heart_empty.png'
    HUD_ARMOR_ON    = 'assets/images/armor_on.png'
    HUD_ARMOR_OFF   = 'assets/images/armor_off.png'
    HUD_SWORD_ON    = 'assets/images/sword_on.png'
    HUD_SWORD_OFF   = 'assets/images/sword_off.png'
    TITLE_IMAGE = 'assets/images/title.png'
    GAMEOVER_IMAGE = 'assets/images/gameover.png'
    GAMEOVER_SCORE_Y_FACTOR = 0.35
    GAMEOVER_SCORE_OFFSET = 10

from mapa import Mapa

class Juego:
    def __init__(self):
        self.mapa_actual = None
        self.nivel = 1
        self.screen = None
        self.clock = pygame.time.Clock()
        self.font = None
        self.mensaje = ''
        self.mensaje_tiempo = 0
        self.pista_portal = ''
        self.estado = 'inicio'
        self.score_total = 0
        self.flash_score_text = ''
        self.flash_score_time = 0
        self.flash_score_duration = 1500
        self.tile_px = int(TILE_SIZE * (RENDER_SCALE if isinstance(RENDER_SCALE, (int, float)) else 1.0))
        # texturas
        self.tex_player = None
        self.tex_enemy = None
        self.tex_chest = None
        self.tex_portal = None
        self.tex_floor = None
        self.tex_wall = None
        # HUD icons
        self.hud_heart_full = None
        self.hud_heart_empty = None
        self.hud_armor_on = None
        self.hud_armor_off = None
        self.hud_sword_on = None
        self.hud_sword_off = None
        # sonidos
        self.snd_chest = None
        self.snd_sword = None
        self.snd_hurt = None
        self.snd_portal = None
        # imágenes título y gameover
        self.title_scaled = None
        self.gameover_scaled = None

    def iniciar_pygame(self):
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Aventura optimizada (corazones y puntuación)')
        self.font = pygame.font.SysFont(None, 32)
        self.cargar_texturas()
        self.cargar_sonidos()
        self.cargar_imagen_titulo()
        self.cargar_imagen_gameover()
        # Música: título (loop) desde el inicio
        self.play_title_music()

    def cargar_texturas(self):
        def load_scaled(path, use_alpha=True):
            try:
                img = pygame.image.load(path)
                img = img.convert_alpha() if use_alpha else img.convert()
                return pygame.transform.smoothscale(img, (self.tile_px, self.tile_px))
            except Exception:
                surf = pygame.Surface((self.tile_px, self.tile_px), pygame.SRCALPHA if use_alpha else 0)
                surf.fill((200, 0, 200, 180) if use_alpha else (200, 0, 200))
                return surf.convert_alpha() if use_alpha else surf.convert()
        self.tex_player = load_scaled(IMG_PLAYER, True)
        self.tex_enemy  = load_scaled(IMG_ENEMY, True)
        self.tex_chest  = load_scaled(IMG_CHEST, True)
        self.tex_portal = load_scaled(IMG_PORTAL, True)
        self.tex_floor  = load_scaled(IMG_FLOOR, False)
        self.tex_wall   = load_scaled(IMG_WALL, False)
        # HUD icons (24 px)
        def load_hud(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.smoothscale(img, (24, 24))
            except Exception:
                surf = pygame.Surface((24,24), pygame.SRCALPHA)
                surf.fill((255,0,255,150))
                return surf
        self.hud_heart_full  = load_hud(HUD_HEART_FULL)
        self.hud_heart_empty = load_hud(HUD_HEART_EMPTY)
        self.hud_armor_on    = load_hud(HUD_ARMOR_ON)
        self.hud_armor_off   = load_hud(HUD_ARMOR_OFF)
        self.hud_sword_on    = load_hud(HUD_SWORD_ON)
        self.hud_sword_off   = load_hud(HUD_SWORD_OFF)

    def cargar_sonidos(self):
        try:
            pygame.mixer.init()
            # FX
            def load_fx(path, vol=FX_VOLUME):
                try:
                    s = pygame.mixer.Sound(path)
                    s.set_volume(vol)
                    return s
                except Exception:
                    return None
            self.snd_chest  = load_fx(SND_CHEST)
            self.snd_sword  = load_fx(SND_SWORD)
            self.snd_hurt   = load_fx(SND_HURT)
            self.snd_portal = load_fx(SND_PORTAL)
        except Exception:
            pass

    def play_title_music(self):
        try:
            pygame.mixer.music.load(SND_MUSIC_TITLE)
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    def play_gameover_music(self):
        try:
            pygame.mixer.music.load(SND_MUSIC_GAMEOVER)
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    def cargar_imagen_titulo(self):
        try:
            bg = pygame.image.load(TITLE_IMAGE).convert()
            img_w, img_h = bg.get_width(), bg.get_height()
            win_w, win_h = SCREEN_WIDTH, SCREEN_HEIGHT
            scale = min(win_w / img_w, win_h / img_h)
            new_w = int(img_w * scale)
            new_h = int(img_h * scale)
            self.title_scaled = pygame.transform.smoothscale(bg, (new_w, new_h))
        except Exception:
            self.title_scaled = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.title_scaled.fill(BLACK)

    def cargar_imagen_gameover(self):
        try:
            bg = pygame.image.load(GAMEOVER_IMAGE).convert()
            img_w, img_h = bg.get_width(), bg.get_height()
            win_w, win_h = SCREEN_WIDTH, SCREEN_HEIGHT
            scale = min(win_w / img_w, win_h / img_h)
            new_w = int(img_w * scale)
            new_h = int(img_h * scale)
            self.gameover_scaled = pygame.transform.smoothscale(bg, (new_w, new_h))
        except Exception:
            self.gameover_scaled = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.gameover_scaled.fill(BLACK)

    def cambiar_mapa(self, filas, columnas):
        if self.mapa_actual is None:
            self.mapa_actual = Mapa(filas, columnas)
            self.mapa_actual.generar_mapa()
        else:
            j_prev = self.mapa_actual.jugador
            self.mapa_actual = Mapa(filas, columnas)
            self.mapa_actual.generar_mapa()
            j = self.mapa_actual.jugador
            j.corazones_totales = j_prev.corazones_totales
            j.corazones_llenos = j_prev.corazones_llenos
            j.armaduras = j_prev.armaduras
            j.espadas = j_prev.espadas
            j.puntuacion = j_prev.puntuacion
        self.mostrar_mensaje(f'--- Nivel {self.nivel} ---')
        px, py = self.mapa_actual.portal
        self.pista_portal = f'({px}, ?)' if random.choice([True, False]) else f'(?, {py})'

    def iniciar(self):
        self.iniciar_pygame()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    if self.estado == 'inicio':
                        if event.key == pygame.K_RETURN:
                            self.estado = 'jugando'
                            self.nivel = 1
                            self.mapa_actual = None
                            self.score_total = 0
                            self.flash_score_text = ''
                            self.cambiar_mapa(15, 15)
                    elif self.estado == 'gameover':
                        if event.key == pygame.K_RETURN:
                            self.estado = 'inicio'
                            self.mapa_actual = None
                            self.nivel = 1
                            self.mensaje = ''
                            self.pista_portal = ''
                            self.flash_score_text = ''
                            try:
                                pygame.mixer.music.fadeout(200)
                            except Exception:
                                pass
                            self.play_title_music()
                    elif self.estado == 'jugando':
                        dx, dy = 0, 0
                        if event.key == pygame.K_w: dx = -1
                        elif event.key == pygame.K_s: dx = 1
                        elif event.key == pygame.K_a: dy = -1
                        elif event.key == pygame.K_d: dy = 1
                        if dx != 0 or dy != 0:
                            if self.mapa_actual.jugador.mover(dx, dy, self.mapa_actual.base_matriz):
                                self.mapa_actual.revelar_area(self.mapa_actual.jugador.x, self.mapa_actual.jugador.y, VISIBLE_RADIUS)
                                for enemigo in self.mapa_actual.enemigos:
                                    enemigo.mover_hacia_jugador(self.mapa_actual.jugador, self.mapa_actual.base_matriz, self.mapa_actual.jugador.movimientos)
                                self.verificar_cofre()
                                if self.resolver_colisiones_enemigos():
                                    pass
                                if self.estado == 'jugando' and self.verificar_portal():
                                    level_bonus = SCORE_LEVEL + (self.nivel * SCORE_LEVEL_BONUS_PER_LEVEL)
                                    self.score_total += level_bonus
                                    if self.snd_portal: self.snd_portal.play()
                                    self.mostrar_flash_score(f'+{level_bonus}')
                                    self.mostrar_mensaje(f'¡Portal encontrado! Bonus nivel {self.nivel}: +{level_bonus} puntos. Pasando al siguiente nivel...')
                                    self.nivel += 1
                                    j = self.mapa_actual.jugador
                                    j.corazones_totales += 1
                                    self.recargar_corazones(j)
                                    self.cambiar_mapa(15 + self.nivel, 15 + self.nivel)
            if self.estado == 'jugando':
                if pygame.time.get_ticks() - self.mensaje_tiempo > 3000:
                    self.mensaje = ''
            if self.flash_score_text and (pygame.time.get_ticks() - self.flash_score_time > self.flash_score_duration):
                self.flash_score_text = ''
            if self.estado == 'inicio':
                self.dibujar_pantalla_inicio()
            elif self.estado == 'jugando':
                self.dibujar()
            elif self.estado == 'gameover':
                self.dibujar_pantalla_gameover()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

    # Pantallas
    def dibujar_pantalla_inicio(self):
        # Letterbox: centrado sin deformar la imagen
        self.screen.fill(BLACK)
        if self.title_scaled:
            win_w, win_h = SCREEN_WIDTH, SCREEN_HEIGHT
            new_w, new_h = self.title_scaled.get_width(), self.title_scaled.get_height()
            x = (win_w - new_w) // 2
            y = (win_h - new_h) // 2
            self.screen.blit(self.title_scaled, (x, y))
        pygame.display.flip()

    def dibujar_pantalla_gameover(self):
        self.screen.fill(BLACK)
        if self.gameover_scaled:
            win_w, win_h = SCREEN_WIDTH, SCREEN_HEIGHT
            go_w, go_h = self.gameover_scaled.get_width(), self.gameover_scaled.get_height()
            go_x = (win_w - go_w) // 2
            go_y = (win_h - go_h) // 2
            # Fondo
            self.screen.blit(self.gameover_scaled, (go_x, go_y))
            # Puntaje encima del monito (aprox. a factor de altura)
            try:
                y_factor = GAMEOVER_SCORE_Y_FACTOR
            except Exception:
                y_factor = 0.35
            try:
                y_off = GAMEOVER_SCORE_OFFSET
            except Exception:
                y_off = 10
            anchor_y = go_y + int(go_h * y_factor)
            puntaje_surface = self.font.render(f"Puntaje: {self.score_total}", True, WHITE)
            px = go_x + (go_w - puntaje_surface.get_width()) // 2
            py = max(10, anchor_y - y_off - puntaje_surface.get_height())
            # Caja semitransparente opcional para contraste
            box = pygame.Surface((puntaje_surface.get_width()+16, puntaje_surface.get_height()+8), pygame.SRCALPHA)
            box.fill((0, 0, 0, 120))
            self.screen.blit(box, (px-8, py-4))
            self.screen.blit(puntaje_surface, (px, py))
        else:
            # Fallback: solo texto
            puntaje_surface = self.font.render(f"Puntaje: {self.score_total}", True, WHITE)
            px = (SCREEN_WIDTH - puntaje_surface.get_width()) // 2
            py = 20
            self.screen.blit(puntaje_surface, (px, py))
        
        pygame.display.flip()

    # Lógica
    def mostrar_mensaje(self, texto):
        self.mensaje = texto
        self.mensaje_tiempo = pygame.time.get_ticks()
    def mostrar_flash_score(self, texto):
        self.flash_score_text = texto
        self.flash_score_time = pygame.time.get_ticks()

    def resolver_colisiones_enemigos(self):
        j = self.mapa_actual.jugador
        colisionados = [e for e in self.mapa_actual.enemigos if j.x == e.x and j.y == e.y]
        if not colisionados:
            return False
        for e in colisionados:
            if j.espadas > 0:
                j.espadas -= 1
                self.mapa_actual.enemigos.remove(e)
                self.score_total += SCORE_ENEMY
                if self.snd_sword: self.snd_sword.play()
                self.mostrar_flash_score(f'+{SCORE_ENEMY}')
                self.mostrar_mensaje('Usaste una ESPADA: enemigo eliminado!')
                continue
            if j.armaduras > 0:
                j.armaduras -= 1
                if self.empujar_enemigo(e, pasos=2):
                    self.mostrar_mensaje('Usaste ARMADURA: enemigo empujado!')
                else:
                    j.perder_corazon()
                    if self.snd_hurt: self.snd_hurt.play()
                    self.mostrar_mensaje(f'No se pudo empujar: perdiste un corazón ({j.corazones_llenos}/{j.corazones_totales})')
                if j.corazones_llenos == 0:
                    self.mostrar_mensaje('¡Has sido derrotado!')
                    self.estado = 'gameover'
                    try:
                        pygame.mixer.music.fadeout(400)
                    except Exception:
                        pass
                    self.play_gameover_music()
                    return True
                continue
            j.perder_corazon()
            if self.snd_hurt: self.snd_hurt.play()
            self.mostrar_mensaje(f'¡Perdiste un corazón! ({j.corazones_llenos}/{j.corazones_totales})')
            if j.corazones_llenos == 0:
                self.mostrar_mensaje('¡Has sido derrotado!')
                self.estado = 'gameover'
                try:
                    pygame.mixer.music.fadeout(400)
                except Exception:
                    pass
                self.play_gameover_music()
                return True
        return False

    def empujar_enemigo(self, enemigo, pasos=2):
        dx = enemigo.ultimo_dx
        dy = enemigo.ultimo_dy
        if dx == 0 and dy == 0:
            j = self.mapa_actual.jugador
            dx = 1 if enemigo.x > j.x else -1 if enemigo.x < j.x else 0
            dy = 1 if enemigo.y > j.y else -1 if enemigo.y < j.y else 0
            dx *= -1
            dy *= -1
        final_x, final_y = enemigo.x, enemigo.y
        for step in range(1, pasos + 1):
            nx = enemigo.x + dx * step
            ny = enemigo.y + dy * step
            if 0 <= nx < self.mapa_actual.filas and 0 <= ny < self.mapa_actual.columnas:
                if self.mapa_actual.base_matriz[nx][ny] in ('.', 'S'):
                    final_x, final_y = nx, ny
                else:
                    break
            else:
                break
        if (final_x, final_y) != (enemigo.x, enemigo.y):
            enemigo.x, enemigo.y = final_x, final_y
            return True
        return False

    def verificar_cofre(self):
        j = self.mapa_actual.jugador
        for c in self.mapa_actual.cofres:
            if not c.abierto and j.x == c.x and j.y == c.y:
                c.abierto = True
                if self.snd_chest: self.snd_chest.play()
                if c.contenido == 'armadura':
                    j.armaduras += 1
                    self.mostrar_mensaje('¡Cofre abierto! ARMADURA obtenida.')
                elif c.contenido == 'espada':
                    j.espadas += 1
                    self.mostrar_mensaje('¡Cofre abierto! ESPADA obtenida.')
                elif c.contenido == 'dinero':
                    j.puntuacion += c.valor
                    self.mostrar_mensaje(f'¡Cofre abierto! Dinero +{c.valor}. Puntos: {j.puntuacion}')
                self.score_total += SCORE_ITEM
                self.mostrar_flash_score(f'+{SCORE_ITEM}')
                return True
        return False

    def verificar_portal(self):
        j = self.mapa_actual.jugador
        px, py = self.mapa_actual.portal
        return j.x == px and j.y == py

    def recargar_corazones(self, jugador, costo_por_corazon=100):
        while jugador.corazones_llenos < jugador.corazones_totales and jugador.puntuacion >= costo_por_corazon:
            jugador.puntuacion -= costo_por_corazon
            jugador.corazones_llenos += 1

    # Render
    def dibujar(self):
        self.screen.fill(BLACK)
        offset_x = (SCREEN_WIDTH // 2) - (self.mapa_actual.jugador.y * self.tile_px)
        offset_y = (SCREEN_HEIGHT // 2) - (self.mapa_actual.jugador.x * self.tile_px)

        start_i = max(0, math.floor((-offset_y) / self.tile_px))
        end_i = min(self.mapa_actual.filas, math.ceil((SCREEN_HEIGHT - offset_y) / self.tile_px))
        start_j = max(0, math.floor((-offset_x) / self.tile_px))
        end_j = min(self.mapa_actual.columnas, math.ceil((SCREEN_WIDTH - offset_x) / self.tile_px))

        for i in range(start_i, end_i):
            for j in range(start_j, end_j):
                if not self.mapa_actual.revelado[i][j]:
                    continue
                x = j * self.tile_px + offset_x
                y = i * self.tile_px + offset_y
                celda = self.mapa_actual.base_matriz[i][j]
                if celda == '.':
                    self.screen.blit(self.tex_floor, (x, y))
                elif celda == 'S':
                    self.screen.blit(self.tex_floor, (x, y))
                    self.screen.blit(self.tex_portal, (x, y))
                else:
                    self.screen.blit(self.tex_wall, (x, y))

        def dentro_view(i, j):
            return start_i <= i < end_i and start_j <= j < end_j

        for c in self.mapa_actual.cofres:
            if not c.abierto and self.mapa_actual.revelado[c.x][c.y] and dentro_view(c.x, c.y):
                cx = c.y * self.tile_px + offset_x
                cy = c.x * self.tile_px + offset_y
                self.screen.blit(self.tex_chest, (cx, cy))

        for e in self.mapa_actual.enemigos:
            if self.mapa_actual.revelado[e.x][e.y] and dentro_view(e.x, e.y):
                ex = e.y * self.tile_px + offset_x
                ey = e.x * self.tile_px + offset_y
                self.screen.blit(self.tex_enemy, (ex, ey))

        px = self.mapa_actual.jugador.y * self.tile_px + offset_x
        py = self.mapa_actual.jugador.x * self.tile_px + offset_y
        self.screen.blit(self.tex_player, (px, py))

        self.dibujar_minimapa()
        self.dibujar_hud()
        pygame.display.flip()

    def dibujar_minimapa(self):
        max_w = MINIMAP_MAX_W if isinstance(MINIMAP_MAX_W, (int, float)) else 220
        max_h = MINIMAP_MAX_H if isinstance(MINIMAP_MAX_H, (int, float)) else 180
        margin = MINIMAP_MARGIN if isinstance(MINIMAP_MARGIN, (int, float)) else 10
        filas = self.mapa_actual.filas
        columnas = self.mapa_actual.columnas
        tile_w = max_w / max(1, columnas)
        tile_h = max_h / max(1, filas)
        tile = int(max(3, min(tile_w, tile_h)))
        width = tile * columnas
        height = tile * filas
        screen_h = self.screen.get_height()
        x0 = margin
        y0 = screen_h - margin - height
        if y0 < margin:
            y0 = margin
        pygame.draw.rect(self.screen, (20, 20, 20), (x0, y0, width, height))
        pygame.draw.rect(self.screen, YELLOW, (x0, y0, width, height), 3)
        for i in range(filas):
            for j in range(columnas):
                cx = x0 + j * tile
                cy = y0 + i * tile
                if not self.mapa_actual.revelado[i][j]:
                    pygame.draw.rect(self.screen, BLACK, (cx, cy, tile, tile))
                else:
                    celda = self.mapa_actual.base_matriz[i][j]
                    if celda == '.':
                        pygame.draw.rect(self.screen, (0, 140, 0), (cx, cy, tile, tile))
                    elif celda == 'S':
                        pygame.draw.rect(self.screen, PURPLE, (cx, cy, tile, tile))
                    elif celda == ' ':
                        pygame.draw.rect(self.screen, (60, 60, 60), (cx, cy, tile, tile))
        for c in self.mapa_actual.cofres:
            if not c.abierto and self.mapa_actual.revelado[c.x][c.y]:
                cx = x0 + c.y * tile
                cy = y0 + c.x * tile
                pygame.draw.rect(self.screen, BROWN, (cx, cy, tile, tile))
        for e in self.mapa_actual.enemigos:
            if self.mapa_actual.revelado[e.x][e.y]:
                ex = x0 + e.y * tile
                ey = y0 + e.x * tile
                pygame.draw.rect(self.screen, RED, (ex, ey, tile, tile))
        px = x0 + self.mapa_actual.jugador.y * tile
        py = y0 + self.mapa_actual.jugador.x * tile
        pygame.draw.rect(self.screen, BLUE, (px, py, tile, tile))

    def dibujar_hud(self):
        j = self.mapa_actual.jugador
        # Íconos arriba-izquierda
        base_x, base_y = 10, 10
        spacing = 30
        heart1 = self.hud_heart_full if j.corazones_llenos >= 1 else self.hud_heart_empty
        heart2 = self.hud_heart_full if j.corazones_llenos >= 2 else self.hud_heart_empty
        self.screen.blit(heart1, (base_x, base_y))
        self.screen.blit(heart2, (base_x + spacing, base_y))
        armor_icon = self.hud_armor_on if j.armaduras > 0 else self.hud_armor_off
        self.screen.blit(armor_icon, (base_x + spacing*2, base_y))
        sword_icon = self.hud_sword_on if j.espadas > 0 else self.hud_sword_off
        self.screen.blit(sword_icon, (base_x + spacing*3, base_y))
        # Textos (debajo)
        tx, ty = 10, base_y + 35
        movs_texto = self.font.render(f'Movimientos: {j.movimientos}', True, WHITE)
        self.screen.blit(movs_texto, (tx, ty))
        pos_texto = self.font.render(f'Posición: ({j.x}, {j.y})', True, WHITE)
        self.screen.blit(pos_texto, (tx, ty + 28))
        mapa_texto = self.font.render(f'Mapa: {self.mapa_actual.filas}x{self.mapa_actual.columnas}', True, WHITE)
        self.screen.blit(mapa_texto, (tx, ty + 56))
        pista_texto = self.font.render(f'Pista portal: {self.pista_portal}', True, YELLOW)
        self.screen.blit(pista_texto, (tx, ty + 84))
        # Puntaje arriba-derecha
        puntaje_total_surface = self.font.render(f'Puntaje: {self.score_total}', True, WHITE)
        right_x = SCREEN_WIDTH - puntaje_total_surface.get_width() - 10
        self.screen.blit(puntaje_total_surface, (right_x, 10))
        # Mensaje temporal & flash
        if self.mensaje:
            msg_surface = self.font.render(self.mensaje, True, YELLOW)
            msg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH // 2, 30))
            self.screen.blit(msg_surface, msg_rect)
        if self.flash_score_text:
            flash_surface = self.font.render(self.flash_score_text, True, WHITE)
            flash_rect = flash_surface.get_rect(center=(SCREEN_WIDTH // 2, 60))
            pygame.draw.rect(self.screen, (0, 0, 0), (flash_rect.x - 6, flash_rect.y - 2, flash_rect.width + 12, flash_rect.height + 4))
            self.screen.blit(flash_surface, flash_rect)
