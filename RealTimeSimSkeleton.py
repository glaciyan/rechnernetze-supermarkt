from collections import deque
import threading
from threading import Thread
import time

f = open("supermarkt.txt", "w")
fc = open("supermarkt_customer.txt", "w")
fs = open("supermarkt_station.txt", "w")


# print on console and into supermarket log
def my_print(msg):
    print(msg)
    f.write(msg + '\n')


# print on console and into customer log
# k: customer name
# s: station name
def my_print1(k, s, msg, t):
    # t = EvQueue.time
    print(str(round(t, 4)) + ':' + k + ' ' + msg + ' at ' + s)
    fc.write(str(round(t, 4)) + ':' + k + ' ' + msg + ' at ' + s + '\n')


# print on console and into station log
# s: station name
# name: customer name
def my_print2(s, msg, name, t):
    # t = EvQueue.time
    # print(str(round(t,4))+':'+s+' '+msg)
    fs.write(str(round(t, 4)) + ':' + s + ' ' + msg + ' ' + name + '\n')

# class consists of
# name: station name
# buffer: customer queue
# delay_per_item: service time
# CustomerWaiting, busy: possible states of this station
class Station(Thread):
    finished = False

    def __init__(self, delay_per_item, name):
        Thread.__init__(self)
        self.delay_per_item = delay_per_item
        self.name = name
        self.CustomerWaitEv = threading.Event()
        self.buffer = deque()
        self.buffer_lock = threading.Lock()

    def run(self):
        while not Station.finished:
            self.CustomerWaitEv.wait()
            while len(self.buffer) > 0:
                self.serve()


    def serve(self):
        self.buffer_lock.acquire()
        customer: Customer = self.buffer.popleft()
        self.buffer_lock.release()

        waitTime = self.delay_per_item * customer.einkaufsliste[customer.current][2]
        time.sleep(waitTime)
        customer.servEv.set()


# class consists of
# statistics variables
# and methods as described in the problem description
class Customer(Thread):
    served = dict()
    dropped = dict()
    complete = 0
    duration = 0
    duration_cond_complete = 0
    count = 0

    def __init__(self):
        Thread.__init__(self)
        self.servEv = threading.Event()

    def run(self):
        pass


# please implement here



def startCustomers(einkaufsliste, name, startTime, newCustomerTime, mT):
    i = 1
    t = startTime
    while t < mT:
        kunde = Customer(list(einkaufsliste), name + str(i), t)
        # ev = Ev(t, kunde.run, prio=1)
        # evQ.push(ev)
        i += 1
        t += newCustomerTime


baecker = Station(10, 'Bäcker')
metzger = Station(30, 'Metzger')
kaese = Station(60, 'Käse')
kasse = Station(5, 'Kasse')
Customer.served['Bäcker'] = 0
Customer.served['Metzger'] = 0
Customer.served['Käse'] = 0
Customer.served['Kasse'] = 0
Customer.dropped['Bäcker'] = 0
Customer.dropped['Metzger'] = 0
Customer.dropped['Käse'] = 0
Customer.dropped['Kasse'] = 0
einkaufsliste1 = [(10, baecker, 10, 10), (30, metzger, 5, 10), (45, kaese, 3, 5), (60, kasse, 30, 20)]
einkaufsliste2 = [(30, metzger, 2, 5), (30, kasse, 3, 20), (20, baecker, 3, 20)]
startCustomers(einkaufsliste1, 'A', 0, 200, 30 * 60 + 1)
startCustomers(einkaufsliste2, 'B', 1, 60, 30 * 60 + 1)
# my_print('Simulationsende: %is' % EvQueue.time)
my_print('Anzahl Kunden: %i' % (Customer.count
                                ))
my_print('Anzahl vollständige Einkäufe %i' % Customer.complete)
x = Customer.duration / Customer.count
my_print(str('Mittlere Einkaufsdauer %.2fs' % x))
x = Customer.duration_cond_complete / Customer.complete
my_print('Mittlere Einkaufsdauer (vollständig): %.2fs' % x)
S = ('Bäcker', 'Metzger', 'Käse', 'Kasse')
for s in S:
    x = Customer.dropped[s] / (Customer.served[s] + Customer.dropped[s]) * 100
    my_print('Drop percentage at %s: %.2f' % (s, x))

f.close()
fc.close()
fs.close()