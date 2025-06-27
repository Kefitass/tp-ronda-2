import pygame
import time 
from graficos import *
from funciones import *

pygame.init()
pygame.font.init() 
pygame.mixer.init() 

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Solitario")
reloj = pygame.time.Clock()

inicializar_recursos_graficos()

try:
    pygame.mixer.music.load('musica_fondo.mp3') 
    pygame.mixer.music.play(-1) 
    pygame.mixer.music.set_volume(0.5) 
except pygame.error as e:
    print(f"Error al cargar o reproducir la música: {e}")


MENU = 0
JUGANDO = 1
RANKING = 2
PEDIR_NOMBRE_RANKING = 3 

estado_juego = MENU 
estado_anterior = None #esto vendria a ser para detectar cambios de estado y cargar el ranking una vez

ejecutando = True
while ejecutando:
    reloj.tick(FPS)

    if estado_juego == RANKING and estado_anterior != RANKING:
        ranking_cache = cargar_ranking()
    estado_anterior = estado_juego 

    
    if estado_juego == MENU:
        nuevo_estado = manejar_menu_principal(pantalla, estado_juego)
    elif estado_juego == JUGANDO:
        nuevo_estado = manejar_estado_jugando(pantalla, estado_juego)
    elif estado_juego == RANKING:
        nuevo_estado = manejar_pantalla_ranking(pantalla, estado_juego)
    elif estado_juego == PEDIR_NOMBRE_RANKING:
        nuevo_estado = manejar_pedido_nombre(pantalla, estado_juego)

    #verifica si el juego tiene q terminar
    if nuevo_estado is False:
        ejecutando = False
    else:
        estado_juego = nuevo_estado

    pygame.display.flip() 

pygame.quit()