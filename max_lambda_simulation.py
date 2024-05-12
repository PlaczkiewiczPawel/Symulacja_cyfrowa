from network import Network
from base_station import BaseStation
from event import *
from generator import Generator
import calc
import json
import logging
import numpy as np
import copy
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
    

def init_number_of_users(station : BaseStation, generator : Generator):
        no_users_in_station = generator.generate_no_users_in_system() # ilość userów już w systemie
        no_users_to_init = generator.generate_init_no_users() # ilość userów którzy pojawiają się w chwili 0
        station.used_resources = no_users_in_station
        return no_users_in_station, no_users_to_init
    
def T_START_users_handle(station : BaseStation, no_users_to_init : int, event_calendar_init : list, generator : Generator) -> list:
    logger.warning(f"USERS TO INIT in t=0 {no_users_to_init}")
    for user in range(no_users_to_init):
        generator.generate_next_user()
        event_calendar_init.append(Event(T_START, station.id , EventType.UE_ARRIVAL)) # Ci userzy pojawia się w chwili 0, będą generować kolejnych tau = 0
        event_calendar_init.append(Event(T_START + generator.mi, station.id , EventType.UE_END_OF_LIFE)) # skończą życie po czasie mi
    return event_calendar_init

def PAST_users_handle(station : BaseStation, no_users_in_station : int, event_calendar_init : list,  generator : Generator):
    logger.warning(f"USERS IN STATION BEFORE t=0 {no_users_in_station}")
    for user in range(no_users_in_station):
            generator.generate_next_user()
            event_calendar_init.append(Event(T_START + generator.mi - 1, station.id , EventType.UE_END_OF_LIFE)) # zakładamy kwant czasu 1s, zatem user musiał co najmniej tyle być w systemie wcześniej
            logger.warning(f"USER {user} to {generator.mi - 1}")
    return event_calendar_init

def init_calendar(network_init : Network, generator : Generator) -> list:
    # Inicjalizacja kalendarza oraz sieci na której potem zaczynamy symulację dla każdej bety
    event_calendar_init = [Event(0,-1, EventType.LAMBDA_CHANGE), Event(calc.hour_to_s(8), -1, EventType.LAMBDA_CHANGE), Event(calc.hour_to_s(14), -1, EventType.LAMBDA_CHANGE),Event(calc.hour_to_s(18), -1, EventType.LAMBDA_CHANGE)]
    for station in network_init.stations:
        no_users_on_station, no_users_to_init = init_number_of_users(station, generator)
        event_calendar_init = T_START_users_handle(station, no_users_to_init, event_calendar_init, generator)
        event_calendar_init = PAST_users_handle(station, no_users_on_station, event_calendar_init, generator)
    return event_calendar_init

def init_simulation():
    beta_list = np.arange(0.01, 0.101, 0.01) # Tablica do szukania maks lambda
    beta_list = np.flip(beta_list)
    print(beta_list)
    network_init = Network(N, 0)
    generator = Generator() # Inicjalizacja generatora -> raz na symulacje
    event_calendar_init = init_calendar(network_init, generator)
    return beta_list, network_init, generator, event_calendar_init

def init_next_beta(base_beta : float, network_init : Network, event_calendar_init : list):
    base_beta = round(base_beta, 5)
    logger.warning(f"Bazowa lambda to teraz {base_beta}")
    time = T_START
    network_beta = copy.copy(network_init)
    network_beta.actual_beta = base_beta
    generator.beta = base_beta
    event_calendar_beta = event_calendar_init.copy() # dla każdej bety startowy kalendarz powinien być taki sam
    return time, network_beta, event_calendar_beta

def clock(time : int,  execution_time : int):
    time = execution_time
    logger.info(f"[AKTUALNY CZAS] {time}")
    return time

def execute_event_on_base_station(event_type : EventType, base_station : BaseStation):
    if event_type == EventType.UE_END_OF_LIFE:
         base_station.remove_ue()
    elif event_type == EventType.BS_WAKE_UP:
        base_station.wake_up()
    elif event_type == EventType.BS_SLEEP:
        base_station.put_to_sleep()
    else: 
        logging.error("COŚ SIĘ ZEPUSŁO I NIE BYŁO MNIE SŁYCHAĆ")
    
def change_lambda_in_network(network_init : Network, base_beta : float, time : int):
    if time == 0:
        network_init.actual_beta = round(base_beta/2, 10)
    elif time == calc.hour_to_s(8):
        network_init.actual_beta = round((3*base_beta)/4, 10)
    elif time == calc.hour_to_s(14):
        network_init.actual_beta = round(base_beta, 10)
    elif time == calc.hour_to_s(18):
        network_init.actual_beta = round((3*base_beta)/4, 10)
    generator.beta = network_init.actual_beta
    logging.error(f"Time : {time} ms, lambda changed to : {network_init.actual_beta}")

def add_user_to_network(event : EventType):
    user_added_to_station_id = network_init.add_ue(event.station_id)
    if user_added_to_station_id == -1:
        logger.error(f"Stracono użytkownika!!!! przy wartości lambda={network_init.actual_beta}")
        print(f"Znalezniono max beta {base_beta}")
        exit()
    elif user_added_to_station_id != event.station_id:
             logger.info(f"Użytkownik dodany do innej stacji : {user_added_to_station_id}")
    elif user_added_to_station_id == event.station_id:
        logger.info(f"Użytkownik dodany do stacji : {user_added_to_station_id}")
    else:
        logger.error("BŁĄD, użytkownik zaginął!!!")
    generator.generate_next_user()
    event_calendar_beta.append(Event(time + generator.tau, event.station_id, event_type=EventType.UE_ARRIVAL))
    event_calendar_beta.append(Event(time + generator.tau + generator.mi, event.station_id, event_type=EventType.UE_END_OF_LIFE))

def execute_event(event : EventType):
    logger.info(f"Typ zdarzenia:{event.event_type}")
    if event.event_type in [EventType.UE_END_OF_LIFE, EventType.BS_SLEEP, EventType.BS_WAKE_UP]: 
        execute_event_on_base_station(event.event_type, network_init.stations[event.station_id])
    elif event.event_type == EventType.LAMBDA_CHANGE:
        change_lambda_in_network(network_init, base_beta, event.execution_time)
    elif event.event_type == EventType.UE_ARRIVAL:
        add_user_to_network(event)
    else: 
        logging.info("Błędne zdarzenie")     

if __name__ == '__main__':
    beta_list, network_init, generator, event_calendar_init = init_simulation()
    # Szuakmy maks bety w oparciu o ten sam początkowy stan sieci i kalendarza
    for base_beta in beta_list:
        time, network_beta, event_calendar_beta = init_next_beta(base_beta, network_init, event_calendar_init)
        # Główna pętla symulacji - działamy tak długo aż będą obiekty w kalendarzu lub do końca czasu.
        while len(event_calendar_beta) > 0 and time <= T_MAX:
            event_calendar_beta.sort(key=lambda x: x.execution_time) # zdarzenia muszą być wcześniej POSORTOWANE PO CZASIE!!!!!
            event = event_calendar_beta.pop(0)
            time = round(clock(time, event.execution_time), 2)
            execute_event(event)
    print("Koniec jest bliski.")
    exit()
       
        

    
        
    