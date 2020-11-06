import random
import logging
import threading
import time

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d [%(threadName)s] - %(message)s', datefmt='%H:%M:%S', level=logging.INFO)


cantidadMaximaLatas = 5
cantidadMaximaBotellas = 5
# CUANDO SE ENTREGA LA MERCADERIA POR EL PROVEEDOR SE GUARDA EN LA DESPENSA
latasEnDespensa = []
botellasEnDespensa = []
cantHeladeras = 5
cantProveedores = 20
cantBebedores = 3
listaHeladeras = []
# SEMAFORO PARA CARGA DE HELADERA
semaforocargaHeladera = threading.Semaphore(1)
semaforoProveedor = threading.Semaphore(1)
# VARIABLE PARA SABER CUAL ES LA HELADERA MAS VACIA
HeladeraMasVacia = 25
HeladerasLlenadas = False


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
        # AGREGO LA CANTIDAD DE FALTANTES QUE TIENE LA HELADERA
        self.Faltantes = cantidadMaximaBotellas + cantidadMaximaLatas
        self.primeraCarga = False

    def agregarBotella(self):
        # AGREGO LA BOTELLA A LA HELADERA Y SACO UNA DE LA DESPENSA
        self.Botellas.append(botellasEnDespensa.pop())

    def agregarLata(self):
        # AGREGO LA BOTELLA A LA HELADERA Y SACO UNA DE LA DESPENSA
        self.Latas.append(latasEnDespensa.pop())

    def run(self):
        logging.info(
            f'Enchufo la heladera {self.numeroHeladera} y comienzo a llenarla')
        while True:

            # CONSULTO SI ES LA MAS VACIA
            if (self.numeroHeladera == HeladeraMasVacia or self.primeraCarga == False):

                # CONSULTO SI FALTA LLENAR BOTELLAS Y SI TENGO DISPONIBLE
                if len(self.Botellas) < cantidadMaximaBotellas and len(botellasEnDespensa) > 0:
                    self.agregarBotella()
                if len(self.Latas) < cantidadMaximaLatas and len(latasEnDespensa) > 0:
                    self.agregarLata()
                # UNA VEZ ESTA LLENA LA HELADERA SUELTO EL SEMAFORO PARA QUE LO PUEDA TOMAR LA SIGUIENTE
                if len(self.Botellas) == cantidadMaximaBotellas and len(self.Latas) == cantidadMaximaLatas:
                    if(self.primeraCarga == False):
                        logging.info(
                            f'Termine de llenar la Heladera {self.numeroHeladera} y presiono el botón de enfriado rápido')
                        self.primeraCarga = True
                    else:
                        logging.info(
                            f'Se relleno la Heladera {self.numeroHeladera}')
                    semaforocargaHeladera.release()
                    time.sleep(10)


class Despensa(threading.Thread):
    def __init__(self, cantHeladeras):
        super().__init__()
        self.cantidadHeladeras = cantHeladeras

    def comprarHeladeras(self):
        for i in range(self.cantidadHeladeras):
            listaHeladeras.append(Heladera(i))

    def llenarHeladera(self):
        for i in range(self.cantidadHeladeras):
            semaforocargaHeladera.acquire()
            listaHeladeras[i].start()
        HeladerasLlenadas = True

    def rellenarHeladera(self):
        semaforocargaHeladera.acquire()
        cantidadFaltante = 0
        global HeladeraMasVacia
        masVaciaAnterior = HeladeraMasVacia
        while HeladeraMasVacia == masVaciaAnterior:

            for i in range(self.cantidadHeladeras):
                if ((cantidadMaximaLatas + cantidadMaximaBotellas) - (len(listaHeladeras[i].Botellas) + len(listaHeladeras[i].Latas))) > cantidadFaltante:
                    HeladeraMasVacia = i
        logging.info(
            f'La Heladera {HeladeraMasVacia} es la que mas faltantes tiene')
        semaforocargaHeladera.release()

    def run(self):
        self.comprarHeladeras()
        self.llenarHeladera()
        while True:
            self.rellenarHeladera()


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
        semaforoProveedor.acquire()
        self.decargarLatas()
        self.descargarBotellas()
        semaforoProveedor.release()

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
        semaforoProveedor.acquire()
        while self.cantMaximaBotellas > 0 or self.cantMaximaLatas > 0:

            if len(listaHeladeras[self.heladeraElegida].Latas) > 0 and self.cantMaximaLatas > 0:
                self.tomarLata()
            if len(listaHeladeras[self.heladeraElegida].Botellas) > 0 and self.cantMaximaBotellas > 0:
                self.tomarBotella()
        logging.info(
            f'Bebedor {self.numero}: Me tome todo, creo que me voy a desmayar!!!')
        semaforoProveedor.release()

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

    # SOLO SE PUEDE PINCHAR CUANDO TODAS LAS HELADERAS ESTEN LLENAS
    if HeladerasLlenadas == True:

        # SIMULAR EL PINCHADO DE LATAS
        heladeraAleatoria = random.randint(0, cantHeladeras - 1)
        lataAleatoria = random.randint(0, cantidadMaximaLatas - 1)
        listaHeladeras[heladeraAleatoria].Latas[lataAleatoria].estado = "Pinchada"
        logging.info(
            f' Se ha pinchado la lata {lataAleatoria} en la Heladera {heladeraAleatoria}!!!')
        time.sleep(15)
