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
        return len(self.buffer)

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
        Customer.count += 1

    def run(self):
        if self.current >= len(self.einkaufsliste):
            Customer.duration += self.stepTime
            Customer.complete += 1
            print(self.stepTime, self.name, "done")
            return  # wir können nichts mehr machen

        evQ.push(Ev(self.stepTime, self.beginn_einkauf, prio=3))
        return

    def beginn_einkauf(self):
        arrivalDelay, _, _, _ = self.einkaufsliste[self.current]
        print(self.stepTime, self.name, "beginn")

        self.stepTime += arrivalDelay
        evQ.push(Ev(self.stepTime, self.ankunft_station, prio=4))
        return

    def ankunft_station(self):
        _, station, timeMultiplier, capacity = self.einkaufsliste[self.current]
        print(self.stepTime, self.name, "ankuft", station.name)

        # die station ist voll
        print(station.current_customer_count())
        if station.current_customer_count() >= capacity:
            print(self.stepTime, self.name, "ankuft voll", station.name)
            Customer.dropped[station.name] += 1
            self.current += 1
            self.run()
            return

        self.stepTime += station.delay_per_item * timeMultiplier
        station.add_customer(self)
        return

    def finanlize_station(self):
        _, station, timeMultiplier, _ = self.einkaufsliste[self.current]
        Customer.served[station.name] += 1
        evQ.push(Ev(self.stepTime, self.verlassen_station, prio=2))
        return self.stepTime

    def verlassen_station(self):
        _, station, _, _ = self.einkaufsliste[self.current]
        print(self.stepTime, self.name, "verlassen", station.name)
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


evQ = EvQueue()
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
# arrivalDelay, station, timeMultiplier, capacity
einkaufsliste1 = [(10, baecker, 10, 10), (30, metzger, 5, 10),
                  (45, kaese, 3, 5), (60, kasse, 30, 20)]
einkaufsliste2 = [(30, metzger, 2, 5), (30, kasse, 3, 20),
                  (20, baecker, 3, 20)]
startCustomers(einkaufsliste1, 'A', 0, 200, 30 * 60 + 1)
startCustomers(einkaufsliste2, 'B', 1, 60, 30 * 60 + 1)
evQ.start()
my_print('Simulationsende: %is' % EvQueue.time)
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
