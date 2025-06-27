import pygame 
import random
import csv 
import time #lo importe por el timer q puse

from graficos import *
pilas_tablero = []
pilas_recoleccion = []
mazo_reserva = []
pila_descarte = []

tiempo_inicio_juego = 0
movimientos_realizados = 0
                                                #####acordar del error ese
#variable que guarda el ranking
ranking_cache = [] 

#estas son las de arrastre de las cartass
carta_en_mano = None 
posicion_carta_en_mano = (0, 0) 
offset_x = 0 
offset_y = 0 
origen_arrastre = None 

CARPETA_IMAGENES_CARTAS = 'cartas/'
IMAGEN_DORSO_CARTA = None 
IMAGENES_CARTAS_CACHE = {} 
sonido_activado = True 
ARCHIVO_RANKING = 'ranking.csv' 

ancho_carta = 90
alto_carta = 120
espacio_horizontal_entre_pilas = 11.6
espacio_vertical_dentro_pila = 30
inicio_x_pilas = 20
inicio_y_pilas = 160
mazo_reserva_x = inicio_x_pilas 
mazo_reserva_y = 20
pila_descarte_x = mazo_reserva_x + ancho_carta + espacio_horizontal_entre_pilas
pila_descarte_y = 20
fundacion_final_x = ANCHO - 20
fundacion_x_base = fundacion_final_x - (4 * ancho_carta + 3 * espacio_horizontal_entre_pilas) 
fundacion_y = 20

#Esta guarda el nombre del usuari o
nombre_jugador_para_ranking = ""

MENU = 0
JUGANDO = 1
RANKING = 2
PEDIR_NOMBRE_RANKING = 3 

def inicializar_recursos_graficos(): #carga dorso de la carta y preparo el cache de las imagenes
    global IMAGEN_DORSO_CARTA, IMAGENES_CARTAS_CACHE
    
    try:
        IMAGEN_DORSO_CARTA = pygame.image.load(CARPETA_IMAGENES_CARTAS + "dorso carta.jpg").convert_alpha()
        IMAGEN_DORSO_CARTA = pygame.transform.scale(IMAGEN_DORSO_CARTA, (90, 120))
    except pygame.error as e:
        print(f"Error al cargar la imagen del dorso de la carta: {e}")
        IMAGEN_DORSO_CARTA = pygame.Surface((90, 120))
        IMAGEN_DORSO_CARTA.fill((100, 100, 100))

    IMAGENES_CARTAS_CACHE = {}


def cargar_imagen_carta(valor, palo):
    
    clave_carta = f"{valor}_{palo}"
    
    if clave_carta in IMAGENES_CARTAS_CACHE:
        return IMAGENES_CARTAS_CACHE[clave_carta]

    nombre_archivo = f"{valor} de {palo}.jpg"
    ruta_completa = CARPETA_IMAGENES_CARTAS + nombre_archivo
    
    try:
        imagen = pygame.image.load(ruta_completa).convert_alpha()
        imagen_escalada = pygame.transform.scale(imagen, (90, 120))
        IMAGENES_CARTAS_CACHE[clave_carta] = imagen_escalada
        return imagen_escalada
    except pygame.error as e:
        print(f"Error al cargar la imagen {ruta_completa}: {e}")
        fallback_imagen = pygame.Surface((90, 120))
        fallback_imagen.fill((255, 0, 255))
        IMAGENES_CARTAS_CACHE[clave_carta] = fallback_imagen
        return fallback_imagen


def mostrar_imagen_carta(pantalla_a_dibujar, carta_tupla, x, y): #Muestra la imagen de una carta en la pantalla, boca arriba o boca abajo.
    valor, palo, boca_arriba = carta_tupla 
    
    if boca_arriba:
        imagen_a_mostrar = cargar_imagen_carta(valor, palo)
    else:
        imagen_a_mostrar = IMAGEN_DORSO_CARTA
        
    pantalla_a_dibujar.blit(imagen_a_mostrar, (x, y))

def generar_mazo(): 

    palos = ["espada", "basto", "copa", "oro"]
    valores = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12] 

    mazo = []
    for palo in palos:
        for valor in valores:
            mazo.append((valor, palo, False)) 
    random.shuffle(mazo)
    return mazo

def iniciar_juego():

    global pilas_tablero, pilas_recoleccion, mazo_reserva, pila_descarte
    global tiempo_inicio_juego, movimientos_realizados 
    global carta_en_mano, posicion_carta_en_mano, offset_x, offset_y, origen_arrastre 
    
    mazo_completo_barajado = generar_mazo()

    pilas_tablero_nuevas, fundaciones_nuevas, mazo_reserva_nuevo, pila_descarte_nueva = repartir_cartas(mazo_completo_barajado)
    pilas_tablero = pilas_tablero_nuevas
    pilas_recoleccion = fundaciones_nuevas 
    mazo_reserva = mazo_reserva_nuevo
    pila_descarte = pila_descarte_nueva

    tiempo_inicio_juego = time.time() 
    movimientos_realizados = 0

    carta_en_mano = None 
    origen_arrastre = None


def repartir_cartas(mazo_completo): #Reparte las cartas para iniciar el juego de Solitario, esto ttrabaja con tuplas de 3 elementos.
 
    pilas_tablero_local = [[] for _ in range(7)]
    fundaciones_local = [[] for _ in range(4)]
    mazo_reserva_temp_local = list(mazo_completo) 
    pila_descarte_local = []

    for i in range(7):
        for j in range(i + 1):
            if len(mazo_reserva_temp_local) > 0:
                carta_base = mazo_reserva_temp_local.pop(0) 
                pilas_tablero_local[i].append((carta_base[0], carta_base[1], j == i)) 
    
    mazo_reserva_local = mazo_reserva_temp_local 

    return pilas_tablero_local, fundaciones_local, mazo_reserva_local, pila_descarte_local

def voltear_carta_superior_pila_tablero(pila): #da vuelta la carta

    if pila and not pila[-1][2]: 
        ultima_carta = pila.pop()
        pila.append((ultima_carta[0], ultima_carta[1], True))
        return True 
    return False 


def obtener_color_palo(palo): #defini el "color" de un palo, oro y copa son rojo y espada y basto son negro
    if palo in ["oro", "copa"]:
        return "rojo"
    elif palo in ["espada", "basto"]:
        return "negro"
    return None 


def es_movimiento_valido_tablero(carta_a_mover, pila_destino): 

    valor_mover = carta_a_mover[0]
    palo_mover = carta_a_mover[1]
    color_mover = obtener_color_palo(palo_mover)

    if not pila_destino: 
        return valor_mover == 12 #solo un Rey (12) puede ir a una pila vacía
    else: 
        carta_superior_destino = pila_destino[-1]
        valor_destino = carta_superior_destino[0]
        palo_destino = carta_superior_destino[1]
        color_destino = obtener_color_palo(palo_destino)

    #la carta a mover debe ser de valor uno menor que la carta superior de destino
        condicion_valor = valor_mover == valor_destino - 1
        
        #la carta a mover debe ser de "color" diferente a la carta superior de destino
        condicion_color = color_mover != color_destino

        return condicion_valor and condicion_color


def es_movimiento_valido_fundacion(carta_a_mover, pila_destino):  #Verifica si un movimiento de UNA carta es válido a una pila de recolección, la carta que se intenta mover y la pila de recolección donde se intenta soltar.
    valor_mover = carta_a_mover[0]
    palo_mover = carta_a_mover[1]

    if not pila_destino:
        return valor_mover == 1
    else: 
        carta_superior_destino = pila_destino[-1]
        valor_destino = carta_superior_destino[0]
        palo_destino = carta_superior_destino[1]

        #la carta a mover debe ser de valor uno mayor que la carta superior de destino
        condicion_valor = valor_mover == valor_destino + 1
        
        #la carta a mover debe ser del mismo palo que la carta superior de destino
        condicion_palo = palo_mover == palo_destino

        return condicion_valor and condicion_palo


#estas manejan el ranking y lo guardan en un csv
def guardar_ranking(nombre_jugador, tiempo_juego, movimientos):

    nueva_entrada = [nombre_jugador, tiempo_juego, movimientos]
    
    try:
        with open(ARCHIVO_RANKING, 'a', newline='') as file:
            writer = csv.writer(file)
            
            if file.tell() == 0: 
                writer.writerow(['Nombre', 'Tiempo (segundos)', 'Movimientos']) 
            
            writer.writerow(nueva_entrada)
        print(f"Ranking guardado: {nombre_jugador}, {tiempo_juego}, {movimientos}")
    except IOError as e:
        print(f"Error al guardar el ranking en {ARCHIVO_RANKING}: {e}")

def cargar_ranking(): #lo carga, podes verlo despues de correrlo
    ranking_data = []
    try:
        with open(ARCHIVO_RANKING, 'r', newline='') as file:
            reader = csv.reader(file)
            
            header = next(reader, None) 
            if header is None: 
                return []

            for row in reader:
                if len(row) == 3: 
                    ranking_data.append({
                        'Nombre': row[0],
                        'Tiempo (segundos)': int(row[1]),
                        'Movimientos': int(row[2])
                    })
        ranking_data.sort(key=lambda x: (x['Tiempo (segundos)'], x['Movimientos']))
        
    except FileNotFoundError:
        print(f"El archivo de ranking '{ARCHIVO_RANKING}' no existe. Se creará uno nuevo.")
    except ValueError as e:
        print(f"Error al leer datos del ranking (conversión): {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado al cargar el ranking: {e}")
        
    return ranking_data



def dibujar_texto(pantalla, texto, tamaño, color, x, y):
    """
    Dibuja texto centrado en las coordenadas dadas.
    """
    fuente = pygame.font.Font(None, tamaño)
    superficie_texto = fuente.render(texto, True, color)
    rect_texto = superficie_texto.get_rect(center=(x, y))
    pantalla.blit(superficie_texto, rect_texto)


def dibujar_boton_silencio(pantalla, sonido_activado_param):#diibuje el boton de silencio, uso la deteccion de clicks y el sonido de fondo 
    x_btn = ANCHO - 50
    y_btn = 30
    radio = 20
    
    color_btn = ROJO if not sonido_activado_param else BLANCO
    
    pygame.draw.circle(pantalla, color_btn, (x_btn, y_btn), radio, 2)
    
    if sonido_activado_param:
        pygame.draw.polygon(pantalla, color_btn, 
                            [(x_btn - 10, y_btn - 10), (x_btn - 10, y_btn + 10), (x_btn + 5, y_btn)])
        pygame.draw.circle(pantalla, color_btn, (x_btn + 10, y_btn - 5), 5)
    else:
        pygame.draw.line(pantalla, color_btn, (x_btn - 15, y_btn - 15), (x_btn + 15, y_btn + 15), 3)
        pygame.draw.line(pantalla, color_btn, (x_btn + 15, y_btn - 15), (x_btn - 15, y_btn + 15), 3)

    return pygame.Rect(x_btn - radio, y_btn - radio, radio * 2, radio * 2)


def toggle_sonido(): #alterna activado y desac
    global sonido_activado
    sonido_activado = not sonido_activado
    if sonido_activado:
        pygame.mixer.music.set_volume(0.5) 
        print("Sonido activado")
    else:
        pygame.mixer.music.set_volume(0.0) 
        print("Sonido silenciado")


#empece con el tablero
def dibujar_tablero(pantalla, pilas_tablero_param, mazo_reserva_param, pila_descarte_param, pilas_recoleccion_param): 
    pantalla.fill(VERDE) 

#pilas del trablero
    indice_pila = 0
    while indice_pila < len(pilas_tablero_param):
        pila_de_cartas = pilas_tablero_param[indice_pila]
        posicion_x_pila = inicio_x_pilas + indice_pila * (ancho_carta + espacio_horizontal_entre_pilas)
        
        if not pila_de_cartas:
            pygame.draw.rect(pantalla, BLANCO, (posicion_x_pila, inicio_y_pilas, ancho_carta, alto_carta), 1)

        indice_carta = 0
        while indice_carta < len(pila_de_cartas):
            carta_completa = pila_de_cartas[indice_carta]
            posicion_y_carta = inicio_y_pilas + indice_carta * espacio_vertical_dentro_pila
            mostrar_imagen_carta(pantalla, carta_completa, posicion_x_pila, posicion_y_carta)
            indice_carta = indice_carta + 1
        
        indice_pila = indice_pila + 1

    if mazo_reserva_param:
        mostrar_imagen_carta(pantalla, (0, "", False), mazo_reserva_x, mazo_reserva_y)
    else:
        pygame.draw.rect(pantalla, BLANCO, (mazo_reserva_x, mazo_reserva_y, ancho_carta, alto_carta), 1)
    
    if pila_descarte_param: #pila de descarte
        mostrar_imagen_carta(pantalla, pila_descarte_param[-1], pila_descarte_x, pila_descarte_y)
    else:
        pygame.draw.rect(pantalla, BLANCO, (pila_descarte_x, pila_descarte_y, ancho_carta, alto_carta), 1)

    for i in range(4):
        fundacion_x = fundacion_x_base + i * (ancho_carta + espacio_horizontal_entre_pilas)
        if pilas_recoleccion_param[i]:
            mostrar_imagen_carta(pantalla, pilas_recoleccion_param[i][-1], fundacion_x, fundacion_y)
        else:
            pygame.draw.rect(pantalla, BLANCO, (fundacion_x, fundacion_y, ancho_carta, alto_carta), 1)


def manejar_menu_principal(pantalla, estado_juego_param): #vemos el menu principal con estio
    global sonido_activado 
    
    pantalla.fill(VERDE)
    dibujar_texto(pantalla, "SOLITARIO", 80, BLANCO, ANCHO // 2, ALTO // 4)
    
    rect_jugar = pygame.Rect(ANCHO // 2 - 100, ALTO // 2 - 30, 200, 60)
    pygame.draw.rect(pantalla, ROJO, rect_jugar)
    dibujar_texto(pantalla, "JUGAR", 40, BLANCO, ANCHO // 2, ALTO // 2)

    rect_ranking = pygame.Rect(ANCHO // 2 - 100, ALTO // 2 + 50, 200, 60)
    pygame.draw.rect(pantalla, ROJO, rect_ranking)
    dibujar_texto(pantalla, "VER RANKING", 40, BLANCO, ANCHO // 2, ALTO // 2 + 80)

    rect_mute_btn = dibujar_boton_silencio(pantalla, sonido_activado)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            return False 
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if rect_jugar.collidepoint(evento.pos):
                iniciar_juego() 
                return JUGANDO #estado nuevo seria
            elif rect_ranking.collidepoint(evento.pos):
                return RANKING #lo mismo
            elif rect_mute_btn.collidepoint(evento.pos): 
                toggle_sonido() 
    return estado_juego_param 


def manejar_estado_jugando(pantalla, estado_juego_param):

    global movimientos_realizados, carta_en_mano, posicion_carta_en_mano, offset_x, offset_y, origen_arrastre
    global pilas_tablero, pilas_recoleccion, mazo_reserva, pila_descarte

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            return False 
        
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1: # Clic izquierdo
                #este detecta el click en mute
                rect_mute_btn = dibujar_boton_silencio(pantalla, sonido_activado)
                if rect_mute_btn.collidepoint(evento.pos):
                    toggle_sonido()
                    continue 
                
                mouse_x, mouse_y = evento.pos
                
                if mazo_reserva: #aca compruebo el click en el maso de reserva
                    rect_mazo_reserva = pygame.Rect(mazo_reserva_x, mazo_reserva_y, ancho_carta, alto_carta)
                    if rect_mazo_reserva.collidepoint(mouse_x, mouse_y):
                        if mazo_reserva:
                            carta_descarte = mazo_reserva.pop() 
                            pila_descarte.append((carta_descarte[0], carta_descarte[1], True)) 
                            movimientos_realizados += 1 
                        continue 
                
                #conpruebno el click en la pila de descarte
                if pila_descarte:
                    rect_pila_descarte = pygame.Rect(pila_descarte_x, pila_descarte_y, ancho_carta, alto_carta)
                    if rect_pila_descarte.collidepoint(mouse_x, mouse_y):
                        carta_selec = pila_descarte[-1]
                        if carta_selec[2]:
                            carta_en_mano = [pila_descarte.pop()] 
                            origen_arrastre = ("descarte", -1, -1) 
                            offset_x = mouse_x - pila_descarte_x
                            offset_y = mouse_y - pila_descarte_y
                        continue

                #este es para las del tablero por si clickeo, lo comprueba
                indice_pila = 0
                while indice_pila < len(pilas_tablero):
                    pila_de_cartas = pilas_tablero[indice_pila]
                    posicion_x_pila = inicio_x_pilas + indice_pila * (ancho_carta + espacio_horizontal_entre_pilas)
                    
                    indice_carta = len(pila_de_cartas) - 1 
                    while indice_carta >= 0:
                        carta_actual = pila_de_cartas[indice_carta]
                        posicion_y_carta = inicio_y_pilas + indice_carta * espacio_vertical_dentro_pila
                        
                        rect_carta = pygame.Rect(posicion_x_pila, posicion_y_carta, ancho_carta, 
                                                 espacio_vertical_dentro_pila if indice_carta < len(pila_de_cartas) -1 else alto_carta)
                        
                        if rect_carta.collidepoint(mouse_x, mouse_y) and carta_actual[2]: 
                            carta_en_mano = pila_de_cartas[indice_carta:]
                            pilas_tablero[indice_pila] = pilas_tablero[indice_pila][:indice_carta]
                            
                            origen_arrastre = ("tablero", indice_pila, indice_carta)
                            offset_x = mouse_x - posicion_x_pila
                            offset_y = mouse_y - posicion_y_carta
                            
                            break 
                        indice_carta -= 1
                    if carta_en_mano: break 
                    indice_pila += 1
        
        elif evento.type == pygame.MOUSEMOTION:
            if carta_en_mano: 
                mouse_x, mouse_y = evento.pos
                posicion_carta_en_mano = (mouse_x - offset_x, mouse_y - offset_y)

        elif evento.type == pygame.MOUSEBUTTONUP:
            if carta_en_mano: 
                mouse_x, mouse_y = evento.pos
                
                soltada_correctamente = False
                
                carta_top_mover = carta_en_mano[0] 

                target_pila_idx = 0
                while target_pila_idx < len(pilas_tablero):
                    target_x_pila = inicio_x_pilas + target_pila_idx * (ancho_carta + espacio_horizontal_entre_pilas)
                    
                    if pilas_tablero[target_pila_idx]:
                        ultima_carta_y = inicio_y_pilas + (len(pilas_tablero[target_pila_idx]) - 1) * espacio_vertical_dentro_pila
                        rect_destino = pygame.Rect(target_x_pila, ultima_carta_y, ancho_carta, alto_carta)
                    else:
                        rect_destino = pygame.Rect(target_x_pila, inicio_y_pilas, ancho_carta, alto_carta)
                    
                    if rect_destino.collidepoint(mouse_x, mouse_y):
                        if origen_arrastre[0] == "tablero" and origen_arrastre[1] == target_pila_idx:
                            for c in reversed(carta_en_mano):
                                pilas_tablero[origen_arrastre[1]].insert(origen_arrastre[2], c)
                            soltada_correctamente = True
                        else:
                            #aca empece con las reglas basicas del solitario
                            if es_movimiento_valido_tablero(carta_top_mover, pilas_tablero[target_pila_idx]):
                                pilas_tablero[target_pila_idx].extend(carta_en_mano)
                                soltada_correctamente = True
                                movimientos_realizados += 1 
                            else:
                                print("Movimiento inválido en tablero")
                        break 
                    target_pila_idx += 1

                if not soltada_correctamente: 
                    for i in range(4):
                        fundacion_x = fundacion_x_base + i * (ancho_carta + espacio_horizontal_entre_pilas)
                        rect_fundacion = pygame.Rect(fundacion_x, fundacion_y, ancho_carta, alto_carta)
                        if rect_fundacion.collidepoint(mouse_x, mouse_y):
                            if len(carta_en_mano) == 1: 
                                carta_unica_mover = carta_en_mano[0] 
                                if origen_arrastre[0] == "fundacion" and origen_arrastre[1] == i:
                                    pilas_recoleccion[i].extend(carta_en_mano) 
                                    soltada_correctamente = True
                                else:

                                    if es_movimiento_valido_fundacion(carta_unica_mover, pilas_recoleccion[i]):
                                        pilas_recoleccion[i].extend(carta_en_mano) 
                                        soltada_correctamente = True
                                        movimientos_realizados += 1 
                                    else:
                                        print("Movimiento inválido en fundación")
                            else:
                                print("Movimiento inválido, solo se puede mover una carta.")
                            break
                
                #si no solte en un lugar que se pueda me devuelve la carta en el lugar q estaba
                if not soltada_correctamente:
                    if origen_arrastre[0] == "tablero":
                        for c in reversed(carta_en_mano):
                            pilas_tablero[origen_arrastre[1]].insert(origen_arrastre[2], c)
                    elif origen_arrastre[0] == "descarte":
                        pila_descarte.extend(carta_en_mano) 
                    print("Movimiento inválido o no reconocido, la carta vuelve a su origen.")
                
                if soltada_correctamente and origen_arrastre[0] == "tablero": #con esto se da vuelta la carta que esta dada vuelta si el movimiento fue valido
                    voltear_carta_superior_pila_tablero(pilas_tablero[origen_arrastre[1]])


                carta_en_mano = None 
                origen_arrastre = None

        #para probar el ranking si toco la g me pide nombre de usser
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_g:
            return PEDIR_NOMBRE_RANKING
    
    dibujar_tablero(pantalla, pilas_tablero, mazo_reserva, pila_descarte, pilas_recoleccion)
    dibujar_boton_silencio(pantalla, sonido_activado)
    
    tiempo_actual = int(time.time() - tiempo_inicio_juego)
    dibujar_texto(pantalla, f"Tiempo: {tiempo_actual}s", 25, BLANCO, 100, ALTO - 30)
    dibujar_texto(pantalla, f"Movimientos: {movimientos_realizados}", 25, BLANCO, 300, ALTO - 30)

    #dibuja la carta que se esta arrastrando
    if carta_en_mano:
        for i, carta_a_dibujar in enumerate(carta_en_mano):
            mostrar_imagen_carta(pantalla, carta_a_dibujar, 
                                 posicion_carta_en_mano[0], 
                                 posicion_carta_en_mano[1] + i * espacio_vertical_dentro_pila)
    return estado_juego_param#retorna el estado actual si no hubo cambio


def manejar_pantalla_ranking(pantalla, estado_juego_param):
    """
    Muestra la pantalla de ranking y maneja las interacciones del usuario.
    Retorna el nuevo estado del juego o False si se debe salir.
    """
    global ranking_cache 
    global sonido_activado

    pantalla.fill(NEGRO) 
    dibujar_texto(pantalla, "RANKING DE SOLITARIO", 60, BLANCO, ANCHO // 2, 50)
    
    y_offset = 120
    if not ranking_cache:
        dibujar_texto(pantalla, "No hay partidas registradas aún.", 30, BLANCO, ANCHO // 2, y_offset)
    else:
        dibujar_texto(pantalla, "Nombre", 30, BLANCO, ANCHO // 2 - 150, y_offset)
        dibujar_texto(pantalla, "Tiempo", 30, BLANCO, ANCHO // 2 + 0, y_offset)
        dibujar_texto(pantalla, "Movimientos", 30, BLANCO, ANCHO // 2 + 150, y_offset)
        
        y_offset += 40
        for i, entrada in enumerate(ranking_cache):
            if i >= 10: break 
            texto_linea = (f"{entrada['Nombre']:<15}   " 
                           f"{entrada['Tiempo (segundos)']:<5}s   "
                           f"{entrada['Movimientos']:<5}") 

            dibujar_texto(pantalla, texto_linea, 25, BLANCO, ANCHO // 2, y_offset)
            y_offset += 30

    rect_volver_menu = pygame.Rect(ANCHO // 2 - 100, ALTO - 60, 200, 50)
    pygame.draw.rect(pantalla, ROJO, rect_volver_menu)
    dibujar_texto(pantalla, "VOLVER AL MENÚ", 30, BLANCO, ANCHO // 2, ALTO - 35)

    rect_mute_btn = dibujar_boton_silencio(pantalla, sonido_activado)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            return False
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if rect_volver_menu.collidepoint(evento.pos):
                return MENU 
            elif rect_mute_btn.collidepoint(evento.pos): 
                toggle_sonido() 

    return estado_juego_param 
def manejar_pedido_nombre(pantalla, estado_juego_param): #pide el nombre del usuario despues de ganar y guarda el ranking

    global nombre_jugador_para_ranking, ranking_cache
    global tiempo_inicio_juego, movimientos_realizados
    
    nombre_actual_local = ""
    input_activo = True
    
    while input_activo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN: 
                    input_activo = False

                    tiempo_transcurrido = int(time.time() - tiempo_inicio_juego)
                    guardar_ranking(nombre_actual_local, tiempo_transcurrido, movimientos_realizados) 
                    
                    ranking_cache = cargar_ranking()
                    return RANKING 
                    
                elif evento.key == pygame.K_BACKSPACE: 
                    nombre_actual_local = nombre_actual_local[:-1]
                else: 
                    if len(nombre_actual_local) < 15: 
                        nombre_actual_local += evento.unicode
        
        pantalla.fill(NEGRO)
        dibujar_texto(pantalla, "¡Felicidades! Ingresa tu nombre:", 40, BLANCO, ANCHO // 2, ALTO // 3)
        
        rect_input = pygame.Rect(ANCHO // 2 - 150, ALTO // 2 - 20, 300, 40)
        pygame.draw.rect(pantalla, BLANCO, rect_input, 2) 
        dibujar_texto(pantalla, nombre_actual_local, 30, BLANCO, ANCHO // 2, ALTO // 2) 
        
        dibujar_texto(pantalla, "(Presiona ENTER para guardar)", 20, BLANCO, ANCHO // 2, ALTO // 2 + 50)
        
        pygame.display.flip()
    
    return estado_juego_param