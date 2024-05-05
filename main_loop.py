from network import Network
from base_station import BaseStation
from event import *
import calc
import json
import logging
logger = logging.getLogger(__name__)

try:
    with open ("config.json") as config_f:
        config = json.load(config_f)
        N = config["N"]
        T_MAX = config["T_MAX"]
        T_START = config["T_START"]
        LOGGER = config["LOGGER"]
        if LOGGER == "ERR":
            logging.basicConfig(filename='simulation.log', level=logging.ERROR)
        elif LOGGER == "WAR":
            logging.basicConfig(filename='simulation.log', level=logging.WARNING)
        else: 
            logging.basicConfig(filename='simulation.log', level=logging.INFO)    
except FileNotFoundError:
    print("Brak pliku konfiguracyjnego.")
    
def clock(time : int,  execution_time : int):
    time = execution_time
    logger.info(f"[AKTUALNY CZAS] {time}")
    return time

def execute_event_on_base_station(station_id : int, event_type : EventType, base_station : BaseStation, network: Network): # TODO nwm czy zmiana lambdy ma sens tu, raczej nie bo jest tylko 4 razy na dobe a z każdym eventem cały obiekt network leci do tej funkcji
    if event_type == EventType.UE_ARRIVAL:
        base_station.add_ue()
    elif event_type == EventType.UE_END_OF_LIFE:
         network.lambda_change()
    elif event_type == EventType.BS_WAKE_UP:
        base_station.wake_up()
    elif event_type == EventType.BS_SLEEP:
        base_station.put_to_sleep()
    else: 
        logging.error("COŚ SIĘ ZEPUSŁO I NIE BYŁO MNIE SŁYCHAĆ")
    
def change_lambda_in_network(network : Network, base_lambda : float, time : int): #TODO tutaj taki if jak wyżej tylko do zmiany lambdy w zależności od czasu
    if time == 0:
        network.actual_lambda = base_lambda/2
    elif time == calc.hour_to_milis(8):
        network.actual_lambda = (3*base_lambda)/4
    elif time == calc.hour_to_milis(14):
        network.actual_lambda = base_lambda
    elif time == calc.hour_to_milis(18):
        network.actual_lambda = (3*base_lambda)/4
    logging.warning(f"Time : {time} ms, lambda changed to : {network.actual_lambda}")

if __name__ == '__main__':
    base_lambda = 1.0
    time = T_START
    network = Network(N, base_lambda)
    eventCalendar = []
    eventCalendar.append(Event(0,-1, EventType.LAMBDA_CHANGE))
    eventCalendar.append(Event(calc.hour_to_milis(8), -1, EventType.LAMBDA_CHANGE))
    eventCalendar.append(Event(calc.hour_to_milis(14), -1, EventType.LAMBDA_CHANGE))
    eventCalendar.append(Event(calc.hour_to_milis(18), -1, EventType.LAMBDA_CHANGE))
    # Mamy 2 listy obiektów - listę stacji bazowych w sieci oraz listę zdarzeń
    # Przykład użycia listy stacji bazowych tworzonej w klasie Network.
    for baseStation in network.stations:
       logger.info(f"ID:{baseStation.id}")
    # Główna pętla symulacji - działamy tak długo aż będą obiekty w kalendarzu lub do końca czasu.
    while len(eventCalendar) > 0 and time <= T_MAX:
        event = eventCalendar.pop(0)
        logger.info(f"Typ zdarzenia:{event.event_type}")
        if event.event_type != EventType.LAMBDA_CHANGE:
            execute_event_on_base_station(event.station_id, event.event_type, network.stations[event.station_id])
        elif event.event_type == EventType.LAMBDA_CHANGE:
            change_lambda_in_network(network, base_lambda, event.execution_time)
        else: 
            logging.info("Błędne zdarzenie")
        time = clock(time, event.execution_time) 
    print("Koniec jest bliski.")
    exit()
       
        

    
        
    