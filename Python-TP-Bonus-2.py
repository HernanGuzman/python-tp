import random
import logging
import threading
import time

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d [%(threadName)s] - %(message)s', datefmt='%H:%M:%S', level=logging.INFO)

cantidadMaximaLatas = 10
cantidadMaximaBotellas = 15
# CUANDO SE ENTREGA LA MERCADERIA POR EL PROVEEDOR SE GUARDA EN LA DESPENSA
latasEnDespensa = []
botellasEnDespensa = []
cantHeladeras = 5
cantProveedores = 20
cantBebedores = 3
listaHeladeras = []
# SEMAFORO PARA CARGA DE HELADERA
semaforocargaHeladera = threading.Semaphore(1)


class Lata():
    def __init__(self, estado="Bien"):
        super().__init__()
        self.estado = estado


class Botella():
    def __init__(self, estado="Bien"):
        super().__init__()
        self.estado = estado


class Heladera(threading.Thread):
    def __init__(self, numeroHeladera):
        super().__init__()
        self.numeroHeladera = numeroHeladera
        self.Botellas = []
        self.Latas = []

    def agregarBotella(self):
        # AGREGO LA BOTELLA A LA HELADERA Y SACO UNA DE LA DESPENSA
        self.Botellas.append(botellasEnDespensa.pop())

    def agregarLata(self):
        # AGREGO LA BOTELLA A LA HELADERA Y SACO UNA DE LA DESPENSA
        self.Latas.append(latasEnDespensa.pop())

    def run(self):
        # TOMO EL SEMAFORO PARA QUE SOLO SE EJECUTE UN HILO A LA
        semaforocargaHeladera.acquire()
        logging.info(
            f'Enchufo la heladera {self.numeroHeladera} y comienzo a llenarla')
        while len(self.Botellas) < cantidadMaximaBotellas or len(self.Latas) < cantidadMaximaLatas:
            # CONSULTO SI FALTA LLENAR BOTELLAS Y SI TENGO DISPONIBLE
            if len(self.Botellas) < cantidadMaximaBotellas and len(botellasEnDespensa) > 0:
                self.agregarBotella()
            if len(self.Latas) < cantidadMaximaLatas and len(latasEnDespensa) > 0:
                self.agregarLata()
        # UNA VEZ ESTA LLENA LA HELADERA SUELTO EL SEMAFORO PARA QUE LO PUEDA TOMAR LA SIGUIENTE
        logging.info(
            f'Termine de llenar la Heladera {self.numeroHeladera} y presiono el botón de enfriado rápido')
        semaforocargaHeladera.release()


class Despensa(threading.Thread):
    def __init__(self, cantHeladeras):
        super().__init__()
        self.cantidadHeladeras = cantHeladeras

    def comprarHeladeras(self):
        for i in range(self.cantidadHeladeras):
            listaHeladeras.append(Heladera(i))

    def llenarHeladera(self):
        for i in range(self.cantidadHeladeras):
            listaHeladeras[i].start()

    def run(self):
        self.comprarHeladeras()
        self.llenarHeladera()


class Proveedor(threading.Thread):
    def __init__(self, numero):
        super().__init__()
        self.numero = numero
        self.latasAEntregar = random.randint(1, 5)
        self.botellasAEntregar = random.randint(1, 5)

    def decargarLatas(self):
        logging.info(
            f'Proveeror {self.numero}: Le entrego {self.latasAEntregar} latas')
        for i in range(self.latasAEntregar):
            latasEnDespensa.append(Lata())

    def descargarBotellas(self):
        logging.info(
            f'Proveeror {self.numero}: Le entrego {self.botellasAEntregar} botellas')
        for i in range(self.latasAEntregar):
            botellasEnDespensa.append(Botella())

    def run(self):
        self.decargarLatas()
        self.descargarBotellas()

# MODIFICACION PARA BONUS


class Bebedor(threading.Thread):
    def __init__(self, numero, cantMaxLatas, cantMaxBotellas):
        super().__init__()
        self.numero = numero
        self.cantMaximaLatas = cantMaxLatas
        self.cantMaximaBotellas = cantMaxBotellas
        # MEDIANTE RAMDOM LE ASIGNO UNA HELADERA DONDE BEBERÁ
        self.heladeraElegida = random.randint(0, cantHeladeras - 1)
        logging.info(
            f'Bebedor {self.numero}: Hola, me voy a tomar {self.cantMaximaLatas} latas y {self.cantMaximaBotellas} botellas de la heladera {self.heladeraElegida}')

    def tomarLata(self):
        logging.info(
            f'Bebedor {self.numero}: Me tomo una lata de cerveza')
        listaHeladeras[self.heladeraElegida].Latas.pop()
        self.cantMaximaLatas -= 1
        time.sleep(3)

    def tomarBotella(self):
        logging.info(
            f'Bebedor {self.numero}: Me tomo una botella de cerveza')
        listaHeladeras[self.heladeraElegida].Botellas.pop()
        self.cantMaximaBotellas -= 1
        time.sleep(3)

    def run(self):

        while self.cantMaximaBotellas > 0 or self.cantMaximaLatas > 0:
            if len(listaHeladeras[self.heladeraElegida].Latas) > 0 and self.cantMaximaLatas > 0:
                self.tomarLata()
            if len(listaHeladeras[self.heladeraElegida].Botellas) > 0 and self.cantMaximaBotellas > 0:
                self.tomarBotella()
        logging.info(
            f'Bebedor {self.numero}: Me tome todo, creo que me voy a desmayar!!!')


# CLASE CONTROLADOR DE HELADERAS: CADA TANTO TIEMPO EL INSPECTOR REVISA LAS HELADERAS PARA VER SINO HAY LATAS PINCHADAS
class Inspector(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        # REVISO TODAS LAS HELADERAS PARA VER SI EXISTE ALGUNA LATA PINCHADA
        while True:
            for i in range(cantHeladeras-1):

                for j in range(len(listaHeladeras[i].Latas) - 1):
                    if listaHeladeras[i].Latas[j].estado != "Bien":
                        listaHeladeras[i].Latas.pop(j)
                        logging.info(
                            f'Inspector: Encontre la lata {j}  pinchada en la Heladera {i}!!!')
            time.sleep(10)


def revisarHeladeras():
    for i in range(self.cantidadHeladeras):
        listaHeladeras[i].start()


def pincharBotellas():
    for i in range(self.cantidadHeladeras):
        listaHeladeras[i].start()


Despensa(cantHeladeras).start()

for i in range(cantProveedores):
    Proveedor(i).start()

for i in range(cantBebedores):
    # RANDOM PARA VER QUE TIPO DE BEBEDOR ES
    # SI ES 1 SOLO BEBE LATAS, 2 SOLO BOTELLAS Y 3 AMBAS
    tipo = random.randint(1, 3)
    if tipo == 1:
        cantbotellas = 0
        cantidadLatas = random.randint(1, 5)
        Bebedor(i, cantbotellas, cantidadLatas).start()
    elif tipo == 2:
        cantbotellas = random.randint(1, 3)
        cantidadLatas = 0
        Bebedor(i, cantbotellas, cantidadLatas).start()
    else:
        cantbotellas = random.randint(1, 3)
        cantidadLatas = random.randint(1, 5)
        Bebedor(i, cantbotellas, cantidadLatas).start()


Inspector().start()

while True:
    # SIMULAR EL PINCHADO DE LATAS
    heladeraAleatoria = random.randint(0, cantHeladeras - 1)
    lataAleatoria = random.randint(0, cantidadMaximaLatas - 1)
    listaHeladeras[heladeraAleatoria].Latas[lataAleatoria].estado = "Pinchada"
    logging.info(
        f' Se ha pinchado la lata {lataAleatoria} en la Heladera {heladeraAleatoria}!!!')
    time.sleep(15)
