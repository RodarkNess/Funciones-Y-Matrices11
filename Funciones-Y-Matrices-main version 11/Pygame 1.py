import pygame
import random
import math
import sys

# Inicializar Pygame
pygame.init()

# Constantes
TILE_SIZE = 40
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

class Personaje:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.simbolo = 'P'
        self.vida = 100
        self.movimientos = 0
    
    def mover(self, dx, dy, matriz):
        nuevo_x = self.x + dx
        nuevo_y = self.y + dy
        
        # Verificar límites del mapa
        if (0 <= nuevo_x < len(matriz)) and (0 <= nuevo_y < len(matriz[0])):
            # Verificar si la celda está vacía o es transitable
            if matriz[nuevo_x][nuevo_y] in [' ', '.', 'C', 'E']:
                self.x = nuevo_x
                self.y = nuevo_y
                self.movimientos += 1
                return True
        return False

class Enemigo:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.simbolo = 'E'
        self.vida = 50
        self.vision = 5
        self.ultimo_movimiento = 0
    
    def mover_hacia_jugador(self, jugador, matriz, movimiento_actual):
        # Solo se mueve cada 2 movimientos del jugador
        if movimiento_actual - self.ultimo_movimiento < 2:
            return False
            
        # Calcular distancia al jugador
        dist_x = jugador.x - self.x
        dist_y = jugador.y - self.y
        
        # Si el jugador está dentro del rango de visión
        if abs(dist_x) <= self.vision and abs(dist_y) <= self.vision:
            # Moverse una casilla hacia el jugador
            dx = 0
            dy = 0
            
            if abs(dist_x) > abs(dist_y):
                dx = 1 if dist_x > 0 else -1
            else:
                dy = 1 if dist_y > 0 else -1
            
            nuevo_x = self.x + dx
            nuevo_y = self.y + dy
            
            if (0 <= nuevo_x < len(matriz)) and (0 <= nuevo_y < len(matriz[0])):
                if matriz[nuevo_x][nuevo_y] in [' ', '.', 'P']:
                    self.x = nuevo_x
                    self.y = nuevo_y
                    self.ultimo_movimiento = movimiento_actual
                    return True
        return False

class Cofre:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.simbolo = 'C'
        self.contenido = random.choice(['vida', 'arma', 'oro'])
        self.abierto = False

class Mapa:
    def __init__(self, filas, columnas):
        self.filas = filas
        self.columnas = columnas
        self.matriz = [[' ' for _ in range(columnas)] for _ in range(filas)]
        self.revelado = [[False for _ in range(columnas)] for _ in range(filas)]
        self.jugador = None
        self.enemigos = []
        self.cofres = []
        self.portal = None
    
    def generar_mapa(self):
        # Crear caminos básicos
        for i in range(self.filas):
            for j in range(self.columnas):
                if random.random() < 0.7:  # 70% de probabilidad de camino
                    self.matriz[i][j] = '.'
        
        # Colocar portal de salida
        portal_x = random.randint(0, self.filas-1)
        portal_y = random.randint(0, self.columnas-1)
        self.matriz[portal_x][portal_y] = 'S'
        self.portal = (portal_x, portal_y)
        
        # Colocar jugador en el centro
        centro_x = self.filas // 2
        centro_y = self.columnas // 2
        self.jugador = Personaje(centro_x, centro_y)
        self.matriz[centro_x][centro_y] = self.jugador.simbolo
        
        # Revelar área inicial alrededor del jugador
        self.revelar_area(centro_x, centro_y, VISIBLE_RADIUS)
        
        # Colocar enemigos
        for _ in range(5):
            x, y = self._posicion_aleatoria_valida()
            enemigo = Enemigo(x, y)
            self.enemigos.append(enemigo)
            self.matriz[x][y] = enemigo.simbolo
        
        # Colocar cofres
        for _ in range(8):
            x, y = self._posicion_aleatoria_valida()
            cofre = Cofre(x, y)
            self.cofres.append(cofre)
            self.matriz[x][y] = cofre.simbolo
    
    def _posicion_aleatoria_valida(self):
        while True:
            x = random.randint(0, self.filas-1)
            y = random.randint(0, self.columnas-1)
            if self.matriz[x][y] == '.':
                return x, y
    
    def revelar_area(self, x, y, radio):
        for i in range(max(0, x - radio), min(self.filas, x + radio + 1)):
            for j in range(max(0, y - radio), min(self.columnas, y + radio + 1)):
                # Usamos distancia euclidiana para un círculo de visión
                distancia = math.sqrt((x - i)**2 + (y - j)**2)
                if distancia <= radio:
                    self.revelado[i][j] = True
    
    def actualizar_matriz(self):
        # Limpiar matriz de personajes y objetos móviles
        for i in range(self.filas):
            for j in range(self.columnas):
                if self.matriz[i][j] in ['P', 'E', 'C']:
                    self.matriz[i][j] = ' '
        
        # Restaurar caminos
        for i in range(self.filas):
            for j in range(self.columnas):
                if self.matriz[i][j] == ' ' and random.random() < 0.7:
                    self.matriz[i][j] = '.'
        
        # Colocar portal
        if self.portal:
            self.matriz[self.portal[0]][self.portal[1]] = 'S'
        
        # Colocar jugador
        self.matriz[self.jugador.x][self.jugador.y] = self.jugador.simbolo
        
        # Colocar enemigos
        for enemigo in self.enemigos:
            self.matriz[enemigo.x][enemigo.y] = enemigo.simbolo
        
        # Colocar cofres
        for cofre in self.cofres:
            if not cofre.abierto:
                self.matriz[cofre.x][cofre.y] = cofre.simbolo

class Juego:
    def __init__(self):
        self.mapa_actual = None
        self.nivel = 1
        self.screen = None
        self.clock = pygame.time.Clock()
        self.font = None
        self.mensaje = ""
        self.mensaje_tiempo = 0
    
    def iniciar_pygame(self):
        # Crear ventana
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Aventura en el Mapa")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
    
    def iniciar(self):
        self.iniciar_pygame()
        self.cambiar_mapa(15, 15)
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    
                    # Mover jugador
                    dx, dy = 0, 0
                    if event.key == pygame.K_w: dx = -1
                    elif event.key == pygame.K_s: dx = 1
                    elif event.key == pygame.K_a: dy = -1
                    elif event.key == pygame.K_d: dy = 1
                    
                    if dx != 0 or dy != 0:
                        if self.mapa_actual.jugador.mover(dx, dy, self.mapa_actual.matriz):
                            # Revelar área alrededor del jugador
                            self.mapa_actual.revelar_area(
                                self.mapa_actual.jugador.x, 
                                self.mapa_actual.jugador.y, 
                                VISIBLE_RADIUS
                            )
                            
                            # Mover enemigos (cada 2 movimientos del jugador)
                            for enemigo in self.mapa_actual.enemigos:
                                enemigo.mover_hacia_jugador(
                                    self.mapa_actual.jugador, 
                                    self.mapa_actual.matriz,
                                    self.mapa_actual.jugador.movimientos
                                )
                            
                            # Actualizar matriz después de movimientos
                            self.mapa_actual.actualizar_matriz()
                            
                            # Verificar condiciones
                            if self.verificar_colision_enemigo():
                                self.mostrar_mensaje("¡Has sido atrapado por un enemigo!")
                                running = False
                            
                            if self.verificar_cofre():
                                self.mostrar_mensaje("¡Encontraste un cofre!")
                            
                            if self.verificar_portal():
                                self.mostrar_mensaje("¡Portal encontrado! Pasando al siguiente nivel...")
                                self.nivel += 1
                                self.cambiar_mapa(15 + self.nivel, 15 + self.nivel)
            
            # Actualizar mensajes
            if pygame.time.get_ticks() - self.mensaje_tiempo > 3000:  # 3 segundos
                self.mensaje = ""
            
            # Dibujar
            self.dibujar()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def cambiar_mapa(self, filas, columnas):
        self.mapa_actual = Mapa(filas, columnas)
        self.mapa_actual.generar_mapa()
        self.mostrar_mensaje(f"--- Nivel {self.nivel} ---")
    
    def verificar_colision_enemigo(self):
        jugador = self.mapa_actual.jugador
        for enemigo in self.mapa_actual.enemigos:
            if jugador.x == enemigo.x and jugador.y == enemigo.y:
                return True
        return False
    
    def verificar_cofre(self):
        jugador = self.mapa_actual.jugador
        for cofre in self.mapa_actual.cofres[:]:
            if not cofre.abierto and jugador.x == cofre.x and jugador.y == cofre.y:
                cofre.abierto = True
                self.mostrar_mensaje(f"¡Cofre abierto! Contenía: {cofre.contenido}")
                return True
        return False
    
    def verificar_portal(self):
        jugador = self.mapa_actual.jugador
        portal = self.mapa_actual.portal
        return jugador.x == portal[0] and jugador.y == portal[1]
    
    def mostrar_mensaje(self, texto):
        self.mensaje = texto
        self.mensaje_tiempo = pygame.time.get_ticks()
    
    def dibujar(self):
        self.screen.fill(BLACK)
        
        # Calcular desplazamiento para centrar al jugador
        offset_x = (self.screen.get_width() // 2) - (self.mapa_actual.jugador.x * TILE_SIZE)
        offset_y = (self.screen.get_height() // 2) - (self.mapa_actual.jugador.y * TILE_SIZE)
        
        # Dibujar mapa
        for i in range(self.mapa_actual.filas):
            for j in range(self.mapa_actual.columnas):
                x = j * TILE_SIZE + offset_x
                y = i * TILE_SIZE + offset_y
                
                # Solo dibujar celdas reveladas
                if self.mapa_actual.revelado[i][j]:
                    # Dibujar fondo
                    if self.mapa_actual.matriz[i][j] == '.':
                        pygame.draw.rect(self.screen, GREEN, (x, y, TILE_SIZE, TILE_SIZE))
                    else:
                        pygame.draw.rect(self.screen, DARK_GRAY, (x, y, TILE_SIZE, TILE_SIZE))
                    
                    # Dibujar elementos
                    if self.mapa_actual.matriz[i][j] == 'P':
                        pygame.draw.rect(self.screen, BLUE, (x, y, TILE_SIZE, TILE_SIZE))
                        pygame.draw.circle(self.screen, WHITE, (x + TILE_SIZE//2, y + TILE_SIZE//2), TILE_SIZE//3)
                    elif self.mapa_actual.matriz[i][j] == 'E':
                        pygame.draw.rect(self.screen, RED, (x, y, TILE_SIZE, TILE_SIZE))
                        pygame.draw.polygon(self.screen, BLACK, [
                            (x + TILE_SIZE//2, y + 5),
                            (x + 5, y + TILE_SIZE - 5),
                            (x + TILE_SIZE - 5, y + TILE_SIZE - 5)
                        ])
                    elif self.mapa_actual.matriz[i][j] == 'C':
                        pygame.draw.rect(self.screen, BROWN, (x, y, TILE_SIZE, TILE_SIZE))
                        pygame.draw.rect(self.screen, YELLOW, (x + 10, y + 10, TILE_SIZE - 20, TILE_SIZE - 20))
                    elif self.mapa_actual.matriz[i][j] == 'S':
                        pygame.draw.rect(self.screen, PURPLE, (x, y, TILE_SIZE, TILE_SIZE))
                        pygame.draw.circle(self.screen, WHITE, (x + TILE_SIZE//2, y + TILE_SIZE//2), TILE_SIZE//4)
                    
                    # Dibujar grid
                    pygame.draw.rect(self.screen, GRAY, (x, y, TILE_SIZE, TILE_SIZE), 1)
                else:
                    # Área no revelada
                    pygame.draw.rect(self.screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE))
        
        # Dibujar HUD
        self.dibujar_hud()
        
        pygame.display.flip()
    
    def dibujar_hud(self):
        # Información del nivel y vida
        nivel_texto = self.font.render(f"Nivel: {self.nivel}", True, WHITE)
        vida_texto = self.font.render(f"Vida: {self.mapa_actual.jugador.vida}", True, WHITE)
        movimientos_texto = self.font.render(f"Movimientos: {self.mapa_actual.jugador.movimientos}", True, WHITE)
        
        self.screen.blit(nivel_texto, (10, 10))
        self.screen.blit(vida_texto, (10, 40))
        self.screen.blit(movimientos_texto, (10, 70))
        
        # Leyenda
        leyenda = [
            "Leyenda:",
            "Azul: Jugador",
            "Rojo: Enemigo",
            "Marrón: Cofre",
            "Morado: Portal",
            "Verde: Camino",
            "Gris oscuro: Pared"
        ]
        
        for i, texto in enumerate(leyenda):
            texto_surface = self.font.render(texto, True, WHITE)
            self.screen.blit(texto_surface, (self.screen.get_width() - 200, 10 + i * 25))
        
        # Controles
        controles = [
            "Controles:",
            "W: Arriba",
            "S: Abajo",
            "A: Izquierda",
            "D: Derecha",
            "Q: Salir"
        ]
        
        for i, texto in enumerate(controles):
            texto_surface = self.font.render(texto, True, WHITE)
            self.screen.blit(texto_surface, (10, self.screen.get_height() - 150 + i * 25))
        
        # Mensaje
        if self.mensaje:
            mensaje_surface = self.font.render(self.mensaje, True, YELLOW)
            mensaje_rect = mensaje_surface.get_rect(center=(self.screen.get_width() // 2, 30))
            self.screen.blit(mensaje_surface, mensaje_rect)

# Iniciar el juego
if __name__ == "__main__":
    juego = Juego()
    juego.iniciar()