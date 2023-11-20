from collections import deque
import heapq

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
def my_print1(k, s, msg):
    t = EvQueue.time
    print(str(round(t, 4)) + ':' + k + ' ' + msg + ' at ' + s)
    fc.write(str(round(t, 4)) + ':' + k + ' ' + msg + ' at ' + s + '\n')


# print on console and into station log
# s: station name
# name: customer name
def my_print2(s, msg, name):
    t = EvQueue.time
    # print(str(round(t,4))+':'+s+' '+msg)
    fs.write(str(round(t, 4)) + ':' + s + ' ' + msg + ' ' + name + '\n')


# class consists of instance variables:
# t: time stamp
# work: job to be done
# args: list of arguments for job to be done
# prio: used to give leaving, being served, and arrival different priorities
class Ev:
    counter = 0

    def __init__(self, t, work, args=(), prio=255):
        self.t = t
        self.n = Ev.counter
        self.work = work
        self.args = args
        self.prio = prio
        Ev.counter += 1


# class consists of
# q: event queue
# time: current time
# evCount: counter of all popped events
# methods push, pop, and start as described in the problem description

class EvQueue:
    time = 0
    events = []
    evCount = 0

    def event(self):
        self.evCount += 1
        return heapq.heappop(self.events)

    def push(self, event: Ev):
        heapq.heappush(self.events, (event.t, event.prio, event.n, event))

    def start(self):
        while self.events:
            tuple: (int, int, int, Ev) = self.event()
            event: Ev = tuple[3]
            event.work()


# class consists of
# name: station name
# buffer: customer queue
# delay_per_item: service time
# CustomerWaiting, busy: possible states of this station
class Station():
    def __init__(self, serviceTime, name):
        self.delay_per_item = serviceTime
        self.name = name
        self.buffer = deque()
        self.state = 0  # 0 customer waiting, 1 busy

    def current_customer_count(self):
        return len(self.buffer) - self.state
    
    def get_buffer_names(self):
        out = ""
        s = len(self.buffer)
        for i in range(self.state, s):
            out = out + self.buffer[i].name
            if (i < s - 1):
                out = out + ","

        return out

    def get_current(self):
        if self.state == 1:
            return self.buffer[0].name
        else:
            return ""


    def add_customer(self, customer):
        self.buffer.append(customer)
        if self.state == 0:
            self.state = 1
            evQ.push(Ev(customer.stepTime, self.finish_customer, prio=1))
        return

    def finish_customer(self):
        customer: Customer = self.buffer.popleft()
        leaveTime = customer.stepTime

        if len(self.buffer) > 0:
            newCustomer: Customer = self.buffer[0]
            newCustomer.stepTime = leaveTime + (self.delay_per_item * newCustomer.einkaufsliste[newCustomer.current][2])
            evQ.push(Ev(newCustomer.stepTime, self.finish_customer, prio=1))
        else:
            self.state = 0

        customer.finanlize_station()
        return

class Customer():
    served = dict()
    dropped = dict()
    complete = 0
    duration = 0  # TODO vielleicht verwende ich den falsch
    duration_cond_complete = 0  # TODO herausfinden wie man den zählt
    count = 0

    def __init__(self, einkaufsliste, name, startTime):
        self.einkaufsliste = einkaufsliste
        self.name = name
        self.startTime = startTime
        self.stepTime = self.startTime
        self.current = 0
        self.dropped = False
        Customer.count += 1

    def run(self):
        if self.current >= len(self.einkaufsliste):
            Customer.duration += self.stepTime - self.startTime
            if not self.dropped:
                Customer.duration_cond_complete += self.stepTime - self.startTime
                Customer.complete += 1
            # print(self.stepTime, self.name, "done")
            # print(self.name, self.stepTime - self.startTime, " start time ", self.startTime)
            EvQueue.time = self.stepTime
            return  # wir können nichts mehr machen

        evQ.push(Ev(self.stepTime, self.beginn_einkauf, prio=3))
        return

    def beginn_einkauf(self):
        arrivalDelay, _, _, _ = self.einkaufsliste[self.current]
        # print(self.stepTime, self.name, "beginn")

        self.stepTime += arrivalDelay
        evQ.push(Ev(self.stepTime, self.ankunft_station, prio=4))
        return

    def ankunft_station(self):
        _, station, timeMultiplier, capacity = self.einkaufsliste[self.current]

        # die station ist voll
        # print(station.current_customer_count())
        if station.current_customer_count() >= capacity:
            # print(round(self.stepTime, 4), self.name, "ankuft voll dropped at", station.name)
            my_print(station.name + '\t' + str(round(self.stepTime, 4))+ "\t"+ "dropped " + self.name+ "\t"+ station.get_buffer_names() + "\t" + str(capacity - station.current_customer_count()) + "\t" + station.get_current())
            Customer.dropped[station.name] += 1
            # self.current += 1
            # self.run()
            self.dropped = True
            return

        # print(round(self.stepTime, 4), self.name, "ankuft", station.name)
        time = self.stepTime
        self.stepTime += station.delay_per_item * timeMultiplier
        station.add_customer(self)
        my_print(station.name + '\t' + str(round(time, 4))+ "\t"+ "a " + self.name+ "\t"+ station.get_buffer_names() + "\t" + str(capacity - station.current_customer_count()) + "\t" + station.get_current())
        return

    def finanlize_station(self):
        _, station, timeMultiplier, _ = self.einkaufsliste[self.current]
        Customer.served[station.name] += 1
        evQ.push(Ev(self.stepTime, self.verlassen_station, prio=2))
        return self.stepTime

    def verlassen_station(self):
        _, station, _, capacity = self.einkaufsliste[self.current]
        # print(round(self.stepTime, 4), self.name, "verlassen", station.name)
        my_print(station.name + '\t' + str(round(self.stepTime, 4))+ "\t"+ "d " + self.name+ "\t"+ station.get_buffer_names() + "\t" + str(capacity - station.current_customer_count()) + "\t" + station.get_current())
        self.current += 1
        self.run()
        return



def startCustomers(einkaufsliste, name, startTime, newCustomerTime, maxTime):
    i = 1
    t = startTime
    while t < maxTime:
        kunde = Customer(list(einkaufsliste), name + str(i), t)
        ev = Ev(t, kunde.run, prio=1)
        evQ.push(ev)
        i += 1
        t += newCustomerTime


import locale

locale.setlocale(locale.LC_ALL, "de_DE")

evQ = EvQueue()
r1 = Station(0.5, 'R1')
r2 = Station(2.5, 'R2')
r3 = Station(0.025, 'R3')
Customer.served['R1'] = 0
Customer.served['R2'] = 0
Customer.served['R3'] = 0
Customer.dropped['R1'] = 0
Customer.dropped['R2'] = 0
Customer.dropped['R3'] = 0
# arrivalDelay, station, timeMultiplier, capacity
einkaufsliste1 = [(10, r1, 1, 4), (10, r2, 1, 4),
                  (1, r3, 1, 2)]
startCustomers(einkaufsliste1, 'p', 0.1, 0.1, 3.51)
# startCustomers(einkaufsliste2, 'B', 1, 60, 30 * 60 + 1)
evQ.start()
print('Simulationsende: %is' % EvQueue.time)
print('Anzahl Kunden: %i' % (Customer.count))
print('Anzahl vollständige Einkäufe %i' % Customer.complete)
x = Customer.duration / Customer.count
print(str('Mittlere Einkaufsdauer %.2fs' % x))
x = Customer.duration_cond_complete / Customer.complete
print('Mittlere Einkaufsdauer (vollständig): %.2fs' % x)
S = ('R1', 'R2', 'R3')
for s in S:
    x = Customer.dropped[s] / (Customer.served[s] + Customer.dropped[s]) * 100
    print('Drop percentage at %s: %.2f' % (s, x))

f.close()
fc.close()
fs.close()
