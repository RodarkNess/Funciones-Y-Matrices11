# Clase Mapa con progresión de dificultad
import random
from collections import deque
from entidades import Personaje, Enemigo, Cofre
from config import VISIBLE_RADIUS

class Mapa:
    def __init__(self, filas, columnas, seed=None):
        self.filas = filas
        self.columnas = columnas
        self.base_matriz = [[' ' for _ in range(columnas)] for _ in range(filas)]
        self.revelado = [[False for _ in range(columnas)] for _ in range(filas)]
        self.jugador = None
        self.enemigos = []
        self.cofres = []
        self.portal = None
        if seed is not None:
            random.seed(seed)

    def generar_mapa(self):
        nivel_est = max(self.filas, self.columnas) - 15
        if nivel_est < 1: nivel_est = 1
        # Más muros con el nivel: baja probabilidad de suelo
        prob_suelo = max(0.45, 0.72 - 0.03 * (nivel_est - 1))
        intentos_max = 10
        min_dist_portal = min(10 + nivel_est, (self.filas + self.columnas) // 2)
        cx, cy = self.filas // 2, self.columnas // 2
        exito = False
        for _ in range(intentos_max):
            self._generar_terreno(prob_suelo)
            self.base_matriz[cx][cy] = '.'
            self.jugador = Personaje(cx, cy)
            alcanzables, dist = self._alcanzables_desde((cx, cy))
            if not alcanzables:
                continue
            portal = self._elegir_portal(alcanzables, dist, min_dist=min_dist_portal)
            if portal is None:
                portal = max(alcanzables, key=lambda p: dist[p])
            px, py = portal
            self.base_matriz[px][py] = 'S'
            self.portal = (px, py)
            alcanzables, dist = self._alcanzables_desde((cx, cy))
            if (px, py) not in alcanzables:
                continue
            self._colocar_entidades(alcanzables, jugador=(cx, cy), portal=(px, py), nivel=nivel_est)
            self.revelar_area(cx, cy, VISIBLE_RADIUS)
            exito = True
            break
        if not exito:
            self._generar_terreno(prob_suelo)
            self.base_matriz[cx][cy] = '.'
            self.jugador = Personaje(cx, cy)
            esquina = self._esquina_mas_lejana(cx, cy)
            px, py = esquina
            self._carvar_camino((cx, cy), (px, py))
            self.base_matriz[px][py] = 'S'
            self.portal = (px, py)
            alcanzables, _ = self._alcanzables_desde((cx, cy))
            self._colocar_entidades(alcanzables, jugador=(cx, cy), portal=(px, py), nivel=nivel_est)
            self.revelar_area(cx, cy, VISIBLE_RADIUS)

    def revelar_area(self, x, y, radio):
        r2 = radio * radio
        for i in range(max(0, x - radio), min(self.filas, x + radio + 1)):
            for j in range(max(0, y - radio), min(self.columnas, y + radio + 1)):
                dx = x - i
                dy = y - j
                if dx*dx + dy*dy <= r2:
                    self.revelado[i][j] = True

    def _generar_terreno(self, prob_suelo: float):
        for i in range(self.filas):
            fila = self.base_matriz[i]
            for j in range(self.columnas):
                fila[j] = '.' if random.random() < prob_suelo else ' '

    def _alcanzables_desde(self, inicio):
        si, sj = inicio
        if not self._es_transitable(si, sj):
            return set(), {}
        visitados = set()
        dist = {}
        q = deque([(si, sj)])
        visitados.add((si, sj))
        dist[(si, sj)] = 0
        while q:
            x, y = q.popleft()
            for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if self._en_limites(nx, ny) and self._es_transitable(nx, ny) and (nx, ny) not in visitados:
                    visitados.add((nx, ny))
                    dist[(nx, ny)] = dist[(x, y)] + 1
                    q.append((nx, ny))
        return visitados, dist

    def _elegir_portal(self, alcanzables, dist, min_dist=5):
        candidatos = [p for p in alcanzables if dist.get(p, 0) >= min_dist]
        if not candidatos:
            return None
        candidatos.sort(key=lambda p: dist[p], reverse=True)
        top = max(1, len(candidatos)//4)
        return random.choice(candidatos[:top])

    def _colocar_entidades(self, alcanzables, jugador, portal, nivel):
        disponibles = set(alcanzables)
        disponibles.discard(jugador)
        disponibles.discard(portal)
        if not disponibles:
            return
        area = self.filas * self.columnas
        # Enemigos: aumentan con nivel y tamaño
        base_enemigos = 3
        enemigos_nivel = base_enemigos + nivel + max(0, area//220) + (nivel//3)
        enemigos_max = max(5, area//35)
        num_enemigos = min(enemigos_nivel, enemigos_max, len(disponibles))
        # Cofres
        base_cofres = 5
        cofres_nivel = base_cofres + max(0, nivel//3) + max(0, area//280)
        cofres_max = max(4, area//50)
        num_cofres = min(cofres_nivel, cofres_max, max(0, len(disponibles) - num_enemigos))
        # Colocar enemigos
        for _ in range(num_enemigos):
            x, y = random.choice(tuple(disponibles))
            disponibles.remove((x, y))
            e = Enemigo(x, y)
            e.vision = min(10, 4 + nivel//2)
            self.enemigos.append(e)
        # Colocar cofres
        for _ in range(num_cofres):
            x, y = random.choice(tuple(disponibles))
            disponibles.remove((x, y))
            self.cofres.append(Cofre(x, y))

    def _carvar_camino(self, origen, destino):
        ox, oy = origen
        dx, dy = destino
        step_x = 1 if dx > ox else -1
        for x in range(ox, dx + step_x, step_x):
            self.base_matriz[x][oy] = '.'
        step_y = 1 if dy > oy else -1
        for y in range(oy, dy + step_y, step_y):
            self.base_matriz[dx][y] = '.'

    def _esquina_mas_lejana(self, x, y):
        esquinas = [(0,0),(0,self.columnas-1),(self.filas-1,0),(self.filas-1,self.columnas-1)]
        return max(esquinas, key=lambda p: abs(p[0]-x)+abs(p[1]-y))
    def _en_limites(self, x, y):
        return 0 <= x < self.filas and 0 <= y < self.columnas
    def _es_transitable(self, x, y):
        return self.base_matriz[x][y] in ('.','S')
