from collections import deque
import threading
from threading import Thread
import time

f = open("supermarkt.txt", "w")
fc = open("supermarkt_customer.txt", "w")
fs = open("supermarkt_station.txt", "w")
timeFactor = 0.01

temp_m = threading.Lock()


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
            self.CustomerWaitEv.clear()

    def serve(self):
        self.buffer_lock.acquire()
        customer: Customer = self.buffer.popleft()
        self.buffer_lock.release()

        waitTime = self.delay_per_item * customer.einkaufsliste[customer.current][2]
        time.sleep(waitTime * timeFactor)
        print(customer.current_time_step(), customer.name, "served", self.name)
        Customer.served[self.name] += 1
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

    def current_time_step(self):
        return (time.time_ns() - start_time_ns) / timeFactor * 1e-9

    def __init__(self, einkaufsliste, name, startTime):
        Thread.__init__(self)
        self.einkaufsliste = einkaufsliste
        self.name = name
        self.startTime = startTime
        self.servEv = threading.Event()
        self.current = 0
        self.finished = False
        self.has_skipped = False
        self.timeStep = self.startTime
        Customer.count += 1

    def run(self):
        # temp_m.acquire()
        # print("TEST", self.name, self.startTime)
        # temp_m.release()

        time.sleep(self.startTime * timeFactor)
        # print(self.startTime * timeFactor)

        self.start_time_ns = time.time_ns()
        print((self.start_time_ns - start_time_ns) / timeFactor * 1e-9, self.name, "beginn")

        while not self.finished:
            if self.current >= len(self.einkaufsliste):
                self.finished = True
                print(self.current_time_step(), self.name, "done")
                Customer.complete += not self.has_skipped
                time_taken = time.time_ns() - self.start_time_ns
                Customer.duration += time_taken
                if not self.has_skipped:
                    Customer.duration_cond_complete += time_taken

                break

            time.sleep(self.einkaufsliste[self.current][0] * timeFactor)

            station: Station = self.einkaufsliste[self.current][1]

            capacity = self.einkaufsliste[self.current][3]
            if len(station.buffer) >= capacity:
                self.current += 1
                self.has_skipped = True
                Customer.dropped[station.name] += 1
                continue

            station.buffer_lock.acquire()
            station.buffer.append(self)
            station.buffer_lock.release()

            station.CustomerWaitEv.set()
            print(self.current_time_step(), self.name, "ankuft", station.name)

            self.servEv.wait()
            self.servEv.clear()

            self.current += 1


# please implement here

customer_threads = []

def startCustomers(einkaufsliste, name, startTime, newCustomerTime, mT):
    i = 1
    t = startTime
    while t < mT:
        kunde = Customer(list(einkaufsliste), name + str(i), t)
        customer_threads.append(kunde)
        kunde.start()
        # ev = Ev(t, kunde.run, prio=1)
        # evQ.push(ev)
        i += 1
        t += newCustomerTime


baecker = Station(10, 'Bäcker')
baecker.start()
metzger = Station(30, 'Metzger')
metzger.start()
kaese = Station(60, 'Käse')
kaese.start()
kasse = Station(5, 'Kasse')
kasse.start()
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

start_time_ns = time.time_ns()

startCustomers(einkaufsliste1, 'A', 0, 200, 30 * 60 + 1)
startCustomers(einkaufsliste2, 'B', 1, 60, 30 * 60 + 1)

for k in customer_threads:
    k.join()



my_print('Simulationsende: %is' % ((time.time_ns() - start_time_ns) / timeFactor * 1e-9))
my_print('Anzahl Kunden: %i' % (Customer.count
                                ))
my_print('Anzahl vollständige Einkäufe %i' % Customer.complete)
x = (Customer.duration / timeFactor * 1e-9) / Customer.count
my_print(str('Mittlere Einkaufsdauer %.2fs' % x))
x = (Customer.duration_cond_complete / timeFactor * 1e-9) / Customer.complete
my_print('Mittlere Einkaufsdauer (vollständig): %.2fs' % x)
S = ('Bäcker', 'Metzger', 'Käse', 'Kasse')
for s in S:
    x = Customer.dropped[s] / (Customer.served[s] + Customer.dropped[s]) * 100
    my_print('Drop percentage at %s: %.2f' % (s, x))

f.close()
fc.close()
fs.close()