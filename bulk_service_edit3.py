import random
import math
import heapq
import queue
from matplotlib import pyplot as plt

#Parameters
N = 500000  # keep this the same
mu = 1/600  # 1 transaction per 600 seconds (10 minutes) -- keep this fixed
s = 600 #change to minutes or keep seconds

average_transaction_size = 0.000250 #MB (250 bytes to MB)
event_queue = []
queue_length = 0

# Global lists of event times
service_times = []
departure_times = []
arrival_times = []
server_busy = False


def inverse_cdf(lam):

    r = random.random()
    x = (-1*math.log(1-r)) / lam
    return x

def create_interarrival_array(N, lam):
    interarrival_times = []
    for each in range(N):
        interarrival_times.append(inverse_cdf(lam))

    return interarrival_times

def generate_arrival_time(interarrival_times):
    int_times = interarrival_times.copy()
    arrival_times.append(0)

    for each in range(1,N):
        arrival_times.append(int_times.pop(0) + arrival_times[each-1])
    return arrival_times

def create_service_times(N, mu):
    for each in range(N*2):
        service_times.append(inverse_cdf(mu))

    return service_times

def insert_arrival_times(event_queue, arrival_times):

    for each in range(N):
        e = {}
        e['time'] = arrival_times[each]
        e['type'] = 'arrival'
        heapq.heappush(event_queue, (arrival_times[each], e))

    return event_queue


def create_departure_event(event_queue, depart_time, bulk_number, server_busy, immediate):
    server_busy = True
    e = {}
    e['time'] = depart_time
    e['type'] = 'departure'
    e['size'] = bulk_number
    e['immediate'] = immediate

    heapq.heappush(event_queue, (depart_time, e))

    return server_busy, event_queue


def process_arrival(current_time, event_queue, service_time, queue_length, server_busy):
    if not server_busy:
        immediate = True
        depart_time = current_time + service_time
        server_busy, event_queue = create_departure_event(event_queue, depart_time, 1, server_busy, immediate)
    else:
        queue_length = queue_length + 1


    return server_busy, event_queue, queue_length

def process_departure(event, event_queue, server_busy, queue_length):
    server_busy = False
    if queue_length != 0:
        queue_length = queue_length - event['size']

def bulk_service(event_queue, service_times, b, N, queue_length,server_busy, num_full_blocks, services):
    serv_times = service_times.copy()

    while event_queue:
        services = services + 1
        current_time, event = heapq.heappop(event_queue)
        # If the arrival that is departing was  immediately serviced, queue_length should remain unchanged
        # print ("Current Time: ", current_time, "Event: ", event)
        if event['type'] == 'arrival':
            if queue_length == 0:
                serv_time = serv_times.pop(0)

            server_busy, event_queue, queue_length = process_arrival(current_time, event_queue, serv_time, queue_length, server_busy)
        else: # process departure
            # Push the event['time'] on to the list of departure times
            server_busy = False
            for i in range(event['size']):
                departure_times.append(event['time'])

            # Reduce the queue length by the number of customers that just departed
            if queue_length != 0 and not event['immediate']:
                queue_length = queue_length - event['size']
            # print("Queue length: ", queue_length)

            # If there are more customers waiting, put a new bulk into service
            # and generate its departure event
            if queue_length > 0:
                if queue_length >= b:
                    departure_bulk_size = b
                    num_full_blocks = num_full_blocks + 1
                else:
                    departure_bulk_size = queue_length
                # print("Departure bulk size: ", departure_bulk_size)
                # Put a new group of customers into service
                immediate=False
                serv_time = serv_times.pop(0)
                server_busy, event_queue = create_departure_event(event_queue, current_time + serv_time, departure_bulk_size, server_busy, immediate );

    return departure_times, num_full_blocks, services

def calc_res_time(N, arrival_times, departure_times):
    res_times = []
    for i in range(N):
        res_times.append(departure_times[i] - arrival_times[i])

    avg_res_time = sum(res_times)/ len(res_times)
    return avg_res_time


analytic_times = []
sim_times = []

# # Change this loop to be over block sizes instead of over utlizations
# block_sizes = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8]
mus = [240, 360, 480, 600, 720, 840, 960]

for mu in mus:
    b = round(1/ average_transaction_size)
    event_queue = []
    event_time = 0
    queue_length = 0

    util = 0.5 ## NOT SURE
    # lam = util/s
    lam = 3.3

    num_full_blocks = 0
    services = 0

    service_times = []
    departure_times = []
    arrival_times = []
    server_busy = False

    interarrival_times = create_interarrival_array(N, lam)
    arrival_times = generate_arrival_time(interarrival_times)
    service_times = create_service_times(N, mu)
    event_queue = insert_arrival_times(event_queue, arrival_times)
    departure_times, num_full_blocks, services = bulk_service(event_queue, service_times, b, N, queue_length, server_busy, num_full_blocks, services)
    sim_res_time = calc_res_time(N, arrival_times, departure_times)
    analytic_res_time = s / (1 - (util))

    print  (analytic_res_time,  sim_res_time)
    print(num_full_blocks, services)
    sim_times.append(sim_res_time)

# Plot
plt.figure()    # Makes a new figure window to plot in
plt.plot(mus, sim_times, 'or')
plt.ylim([0,2000])
# Add another plot line for simulated bulk service values
plt.legend(['Simulated', 'Simulation'])
plt.xlabel('Block Intervals (seconds)')
plt.ylabel('Average residence time (seconds)')
plt.show()    # Make the plot appear
