from threading import Thread, Condition
from time import sleep
import random
from random import randint
import sys
import argparse
import string
import logging

# ---- #

logging.basicConfig(level=logging.DEBUG,
                    format='> %(threadName)-9s: %(message)s',)

# ---- #

parser = argparse.ArgumentParser(
    description="Modelagem do problema Produtor-Consumidor em Python")

parser.add_argument('-bs', dest="buffersize", metavar="Buffer Size", type=int, default=10,
                    help="Número inteiro que define tamanho do buffer. O tamanho padrão é 10.")

parser.add_argument('-pn', dest="producersnumber", metavar="Producer Number", type=int, default=1,
                    help="Número inteiro que define a quantidade de threads produtoras. O número padrão é 1.")
parser.add_argument('-cn', dest="consumersnumber", metavar="Consumer Number", type=int, default=1,
                    help="Número inteiro que define a quantidade de threads consumidoras. O número padrão é 1.")

parser.add_argument('-pr', dest="producingrate", metavar="Producing Rate", type=int, default=0,
                    help="Taxa de produção de recurso das threads produtoras. Ou seja, quanto de recurso as threads produtoras produzirão de cada vez. O número padrão é aleatório.")

parser.add_argument('-pt', dest="producertime", metavar="Producer Time", type=int, default=1,
                    help="Número inteiro que define o tempo (em segundos) entre as produções de recursos das threads produtoras. O tempo padrão é 1s.")
parser.add_argument('-ct', dest="consumertime", metavar="Consumer Time", type=int, default=2,
                    help="Número inteiro que define o tempo (em segundos) entre os consumos de recursos das threads consumidoras. O tempo padrão é 2s.")

parser.add_argument('-v', '--verbose', action="count",
                    help="Aumenta verbosidade de saída.")
args = parser.parse_args()

# ---- #

buffer_size = args.buffersize
producer_number = args.producersnumber
consumer_number = args.consumersnumber
producing_rate = args.producingrate
producer_time = args.producertime
consumer_time = args.consumertime
verbosity = args.verbose

# ---- #


class Buffer:
    def __init__(self, capacidade):
        self.buffer = []
        self.capacidade = capacidade

    def estoque(self):
        cont = 0
        for x in range(len(self.buffer)):
            cont += 1
        return cont

    def produz(self, itens):
        if verbosity > 1:
            logging.debug(f'Adicionando {len(itens)} item(ns) ao buffer...')
        for i in range(len(itens)):
            self.buffer.append(itens[i])
        sleep(producer_time)
        if verbosity:
            logging.debug(
                f'{len(itens)} item(ns) adicionado(s)! | {itens} | Estoque do buffer: {self.estoque()}/{self.capacidade}')
        else:
            logging.debug(
                f'{len(itens)} item(ns) adicionado(s)! | Estoque do buffer: {self.estoque()}/{self.capacidade}')
        sleep(producer_time)

    def consome(self, item):
        if verbosity > 1:
            logging.debug('Consumindo item do buffer...')
        self.buffer.remove(item)
        sleep(consumer_time)
        logging.debug(
            f'Item {item} consumido! | Estoque do buffer: {self.estoque()}/{self.capacidade}')
        sleep(consumer_time)

# ---- #


def produtor(bufr, mutx, itens_lst):
    logging.debug('Thread produtora iniciada...')
    sleep(3)
    while True:
        mutx.acquire()

        if bufr.estoque() < bufr.capacidade:
            if verbosity > 1:
                logging.debug(
                    'Produzindo e tornando item(ns) disponível(is)...')

            itens = []
            quant = producing_rate
            if quant == 0:
                while True:
                    quant = randint(1, bufr.capacidade)
                    if bufr.estoque() + quant < bufr.capacidade:
                        break
            if not bufr.estoque() + quant > bufr.capacidade:
                for x in range(quant):
                    itens.append(random.choice(itens_lst))
                bufr.produz(itens)
        else:
            logging.debug('Estoque cheio! Thread produtora dormindo...')
            mutx.wait()

        if verbosity > 1:
            logging.debug('Notificando todos os consumidores')

        mutx.notifyAll()
        mutx.release()
        sleep(producer_time)


def consumidor(bufr, mutx):
    logging.debug('Thread consumidora iniciada...')
    sleep(3)
    while True:
        mutx.acquire()

        if bufr.estoque() == 0:
            logging.debug(
                'Estoque vazio! Thread produtora dormindo / aguardando recursos...')
            mutx.wait()
        else:
            bufr.consome(random.choice(bufr.buffer))

        if verbosity > 1:
            logging.debug('Notificando todos os produtores')

        mutx.notifyAll()
        mutx.release()
        sleep(consumer_time)


# ---- #
if __name__ == "__main__":
    print(".::Programa em Python que modela o problema Produtor-Consumidor::.")
    if len(sys.argv) < 2:
        print("- Este programa possui argumentos!")
        print("- Para mais informações, execute: produtor_consumidor.py --help")
    print()
    print("Valores iniciais:")
    print(f"\t> Número de Threads Produtoras: {producer_number}")
    print(f"\t> Número de Threads Consumidoras: {consumer_number}")
    print(
        f"\t> Taxa de Produção: {producing_rate if producing_rate > 0 else 'Aleatório (entre 1 e a capacidade do buffer)'}")
    print(f"\t> Delay das Threads Produtoras: {producer_time}")
    print(f"\t> Delay das Threads Consumidoras: {consumer_time}")
    print(f"\t> Nível verborrágico: {verbosity}")
    print()
    continuar = input('Continuar? [S/n]: ')
    if continuar not in 'sS':
        sys.exit()
    print()

    itens = list(string.ascii_uppercase)
    buff = Buffer(buffer_size)
    mutex = Condition()

    producer_threads = []
    consumer_threads = []

    for prodn in range(producer_number):
        thrdName = 'Produtor {}  '.format(prodn+1)
        producer_threads.append(
            Thread(target=produtor, name=thrdName, args=(buff, mutex, itens)))
        producer_threads[prodn].start()
        sleep(2)

    for consn in range(consumer_number):
        thrdName = 'Consumidor {}'.format(consn+1)
        consumer_threads.append(
            Thread(target=consumidor, name=thrdName, args=(buff, mutex)))
        consumer_threads[consn].start()
        sleep(2)

    # Opcional:

    # for p in range(producer_number):
    #     producer_threads[p].join()

    # for c in range(consumer_threads):
    #     consumer_threads[c].join()
