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
cantProveedores = 40
listaHeladeras = []
# SEMAFORO PARA CARGA DE HELADERA
semaforocargaHeladera = threading.Semaphore(1)


class Heladera(threading.Thread):
    def __init__(self, numeroHeladera):
        super().__init__()
        self.numeroHeladera = numeroHeladera
        self.cantBotellas = 0
        self.cantLatas = 0

    def agregarBotella(self):
        # AGREGO LA BOTELLA A LA HELADERA Y SACO UNA DE LA DESPENSA
        self.cantBotellas += 1
        botellasEnDespensa.pop()

    def agregarLata(self):
        # AGREGO LA BOTELLA A LA HELADERA Y SACO UNA DE LA DESPENSA
        self.cantLatas += 1
        latasEnDespensa.pop()

    def run(self):
        # TOMO EL SEMAFORO PARA QUE SOLO SE EJECUTE UN HILO A LA
        semaforocargaHeladera.acquire()
        logging.info(
            f'Enchufo la heladera {self.numeroHeladera} y comienzo a llenarla')
        while self.cantBotellas < cantidadMaximaBotellas or self.cantLatas < cantidadMaximaLatas:
            # CONSULTO SI FALTA LLENAR BOTELLAS Y SI TENGO DISPONIBLE
            if self.cantBotellas < cantidadMaximaBotellas and len(botellasEnDespensa) > 0:
                self.agregarBotella()
            if self.cantLatas < cantidadMaximaLatas and len(latasEnDespensa) > 0:
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
            latasEnDespensa.append(1)

    def descargarBotellas(self):
        logging.info(
            f'Proveeror {self.numero}: Le entrego {self.botellasAEntregar} botellas')
        for i in range(self.latasAEntregar):
            botellasEnDespensa.append(1)

    def run(self):
        self.decargarLatas()
        self.descargarBotellas()


Despensa(cantHeladeras).start()

for i in range(cantProveedores):
    Proveedor(i).start()
