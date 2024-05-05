from network import Network
from base_station import BaseStation
from event import *
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
        if LOGGER == "ERROR":
            logging.basicConfig(filename='simulation.log', level=logging.ERROR)
        elif LOGGER == "WARNING":
            logging.basicConfig(filename='simulation.log', level=logging.WARNING)
        else: 
            logging.basicConfig(filename='simulation.log', level=logging.INFO)    
except FileNotFoundError:
    print("Brak pliku konfiguracyjnego.")
    
def clock(time : int, time_of_last_event : int, execution_time : int):
    if time_of_last_event != event.execution_time:
        time+=event.execution_time
    else:
        time+=0
    logging.info(time)
    time_of_last_event = execution_time
    return time, time_of_last_event

def execute_event(station_id : int, event_type : EventType, base_station : BaseStation, network: Network): # TODO nwm czy zmiana lambdy ma sens tu, raczej nie bo jest tylko 4 razy na dobe a z każdym eventem cały obiekt network leci do tej funkcji
    if event_type == EventType.UE_ARRIVAL:
        base_station.add_ue()
    elif event_type == EventType.UE_END_OF_LIFE:
         network.lambda_change()
    elif event_type == EventType.BS_WAKE_UP:
        base_station.wake_up()
    elif event_type == EventType.BS_SLEEP:
        base_station.put_to_sleep()
    elif event_type == EventType.LAMBDA_CHANGE:
         network.lambda_change()
    else: 
        logging.error("COŚ SIĘ ZEPUSŁO I NIE BYŁO MNIE SŁYCHAĆ")
    
        

if __name__ == '__main__':
    time = T_START
    time_of_last_event = 0
    network = Network(N)
    event_uno = Event(100, 1, EventType.UE_END_OF_LIFE)
    event_dos = Event(100, 2, EventType.BS_SLEEP)
    eventCalendar = []
    eventCalendar.append(event_uno)
    eventCalendar.append(event_dos)
    # Mamy 2 listy obiektów - listę stacji bazowych w sieci oraz listę zdarzeń
    # Przykład użycia listy stacji bazowych tworzonej w klasie Network.
    for baseStation in network.stations:
       logger.info(f"ID:{baseStation.id}")
    # Główna pętla symulacji - działamy tak długo aż będą obiekty w kalendarzu lub do końca czasu.
    logging.info(time)
    while len(eventCalendar) > 0 and time <= T_MAX:
        event = eventCalendar.pop(0)
        logger.info(f"Typ zdarzenia:{event.event_type}")
        execute_event(event.station_id, event.event_type, network.stations[event.station_id], network)
        time, time_of_last_event = clock(time, time_of_last_event, event.execution_time)
    print("Koniec jest bliski.")
    exit()
       
        

    
        
    