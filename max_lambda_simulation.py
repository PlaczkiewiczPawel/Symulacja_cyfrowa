
from network import Network
from base_station import BaseStation
from event import *
from generator import *
from exepctions import *
from datetime import datetime
import calc
from sortedcontainers import SortedList
import json
import logging
import numpy as np
import copy
import matplotlib.pyplot as plt
import os
import itertools
import csv

logger = logging.getLogger(__name__)

class SimulationState(Enum):
        LAMBDA_SIMULATION = 0
        L_SIMULATION = 1
        ENERGY_SIMULATION = 2

try:
    with open ("config.json") as config_f:
        config = json.load(config_f)
        H = config["H"]
        R = config["R"]
        N = config["N"]
        MIN_T_ZERO = config["NUMBER_OF_USERS_T_ZERO_RAND_MIN"]
        MAX_T_ZERO = config["NUMBER_OF_USERS_T_ZERO_RAND_MAX"]
        MIN_T_PAST  = config["NUMBER_OF_USERS_FROM_PAST_RAND_MIN"]
        MAX_T_PAST = config["NUMBER_OF_USERS_FROM_PAST_RAND_MAX"]  
        T_MAX = config["T_MAX"]
        T_START = config["T_START"]
        LOGGER_MODE = config["LOGGER_MODE"]
        NUMBER_OF_SIMULATIONS = config["NUMBER_OF_SIMULATIONS"]
        BETA_MAX = 1/config["LAMBDA_MIN"] 
        BETA_MIN = 1/config["LAMBDA_MAX"]
        BETA_STEP =  (1/config["LAMBDA_STEP"]) / 10
        SEED_FILE_NUMBER = config["SEED_FILE_NUMBER"]
        SEED_NUMBER = config["SEED_NUMBER"]
        GENERATOR_MODE = config["GENERATOR_MODE"]
        SIMULATION_STATE = SimulationState.LAMBDA_SIMULATION
except FileNotFoundError:
    print("Brak pliku konfiguracyjnego.")
    exit()
    
def create_folder_structure_for_saving_data():
    try:
        count = (len(next(os.walk('wyniki_lambda_max'))[1])) # sprawdza ile folder ma podfolderów
    except StopIteration:
        count = 0
    os.makedirs(f'wyniki_lambda_max/wyniki_{count}')
    with open(f'wyniki_lambda_max/wyniki_{count}/max_lambda_finder.csv', 'a+', newline='') as file:
            file.write("NUMER_SYMULACJI;MAX_LAMBDA_PRAWIDLOWA;LAMBDA_NIEPRAWIDLOWA;RZECZYWISTA_LAMBDA_NIEPRAWIDLOWA\n")
    return count

def init_number_of_users(station : BaseStation, generator : Generator):
        no_users_in_station = generator.generate_no_users_in_system() # ilość userów już w systemie
        no_users_to_init = generator.generate_init_no_users() # ilość userów którzy pojawiają się w chwili 0
        station.used_resources = no_users_in_station
        return no_users_in_station, no_users_to_init
    
def T_START_users_handle(station : BaseStation, no_users_to_init : int, event_calendar_init : SortedList, generator : Generator) -> SortedList:
    logger.warning(f"[USERS TO INIT IN t=0 ON STAION {station.id}] - {no_users_to_init}")
    for user in range(no_users_to_init):
        generator.generate_next_user()
        generator.generator_UE_time_of_life()
        event_calendar_init.add(Event(T_START, station.id , EventType.UE_ARRIVAL)) # Ci userzy pojawia się w chwili 0, będą generować kolejnych tau = 0
        event_calendar_init.add(Event(T_START + generator.mi, station.id , EventType.UE_END_OF_LIFE)) # skończą życie po czasie mi
    return event_calendar_init

def PAST_users_handle(station : BaseStation, no_users_in_station : int, event_calendar_init : SortedList,  generator : Generator) -> SortedList:
    logger.warning(f"[USERS IN STATION {station.id} BEFORE t=0] - {no_users_in_station}")
    for user in range(no_users_in_station):
            generator.generate_next_user()
            generator.generator_UE_time_of_life()
            event_calendar_init.add(Event(T_START + generator.mi - 1, station.id , EventType.UE_END_OF_LIFE)) # zakładamy kwant czasu 1s, zatem user musiał co najmniej tyle być w systemie wcześniej
            logger.warning(f"USER {user} to {generator.mi - 1}")
    return event_calendar_init

def init_calendar(network_init : Network, generator : Generator) -> SortedList:
    # Inicjalizacja kalendarza oraz sieci na której potem zaczynamy symulację dla każdej bety
    event_calendar_init = [Event(0,-1, EventType.LAMBDA_CHANGE), Event(calc.hour_to_s(8), -1, EventType.LAMBDA_CHANGE), Event(calc.hour_to_s(14), -1, EventType.LAMBDA_CHANGE),Event(calc.hour_to_s(18), -1, EventType.LAMBDA_CHANGE)]
    event_calendar_init = SortedList(event_calendar_init, key=lambda x: x.execution_time)
    for station in network_init.stations:
        no_users_on_station, no_users_to_init = init_number_of_users(station, generator)
        event_calendar_init = T_START_users_handle(station, no_users_to_init, event_calendar_init, generator)
        event_calendar_init = PAST_users_handle(station, no_users_on_station, event_calendar_init, generator)
    return event_calendar_init

def init_logger_for_simulation(count : int, simulation_counter : int):
    logger_path = f'wyniki_lambda_max/wyniki_{count}/symulacja_{simulation_counter}/simulation_{simulation_counter}.log'
    if LOGGER_MODE == "ERR":
        logging.basicConfig(filename=logger_path, level=logging.ERROR, force=True, encoding="utf-8")
    elif LOGGER_MODE == "WAR":
        logging.basicConfig(filename=logger_path, level=logging.WARNING, force=True, encoding="utf-8")
    else: 
        logging.basicConfig(filename=logger_path, level=logging.INFO, force=True, encoding="utf-8")    
    logger.warning([f"DATE_TIME_START_BETA - {datetime.now()}"])


def init_generator(simulation_counter : int):
    try:
        if GENERATOR_MODE == 0:
            logger.warning("[TRYB_GENERATORA] - PSEUDOLOSOWY")
            generator = Generator(0, MIN_T_ZERO, MAX_T_ZERO, MIN_T_PAST, MAX_T_PAST)
        elif GENERATOR_MODE == 1: 
            logger.warning("[TRYB_GENERATORA] - DETERMINISTYCZNY 1")
            if not (0<=SEED_FILE_NUMBER<=29 or 0<=SEED_NUMBER<=999):
                logger.error("[TRYB GENERATORA] - PARAMETRY GENERATORA NIEPRAWIDŁOWE")
                exit()
            with open(f'seeds/seed_{SEED_FILE_NUMBER}.csv', 'r', newline='') as file:
                seed = int(next(itertools.islice(csv.reader(file), SEED_NUMBER, None))[0])
                print(seed)
            generator = Generator_seeded(seed, 0, MIN_T_ZERO, MAX_T_ZERO, MIN_T_PAST, MAX_T_PAST)
        elif GENERATOR_MODE == 2:
            logger.warning("[TRYB_GENERATORA] - DETERMINISTYCZNY 2")
            if not (0<=SEED_FILE_NUMBER<=29 or 0<=SEED_NUMBER<=999):
                logger.error("[TRYB GENERATORA] - PARAMETRY GENERATORA NIEPRAWIDŁOWE")
                exit()
            with open(f'seeds/seed_{SEED_FILE_NUMBER}.csv', 'r', newline='') as file:
                seed = int(next(itertools.islice(csv.reader(file), simulation_counter, None))[0])
            generator = Generator_seeded(seed, 0, MIN_T_ZERO, MAX_T_ZERO, MIN_T_PAST, MAX_T_PAST)
        else:
            logger.error("[TRYB_GENERATORA] - BLAD PRZY WYBORZE GENERATORA, SPRAWDZ PARAMTERY")
            exit()
        return generator
    except FileNotFoundError:
        logger.error("[BRAK KATALOGU SEEDS] - Uruchom skrypt create_rng.py z katalogu glownego")
        exit()

def init_simulation(count : int, simulation_counter : int):
    beta_list =  np.arange(BETA_MIN, BETA_MAX, BETA_STEP)  # Wektory tetstowe [0.01, 0.8, 0.9] [0.1, 0.8, 0.9] [0.010, 0.011, 0.012]
    beta_list = np.flip(beta_list)
    print(beta_list)
    os.makedirs(f'wyniki_lambda_max/wyniki_{count}/symulacja_{simulation_counter}/hist/tau')
    os.makedirs(f'wyniki_lambda_max/wyniki_{count}/symulacja_{simulation_counter}/hist/mi')
    init_logger_for_simulation(count, simulation_counter)
    network_init = Network(N, R, H)
    generator = init_generator(simulation_counter)
    event_calendar_init = init_calendar(network_init, generator)                                                                                                                                                                                                                                                                                                       
    return beta_list, network_init, generator, event_calendar_init
   
def init_next_beta(base_beta : float, network_init : Network, event_calendar_init : SortedList):
    base_beta = round(base_beta, 3)
    logger.warning(f"[BETA BAZOWA] -  {base_beta}")
    time = T_START
    network_beta = copy.deepcopy(network_init)
    event_calendar_beta = copy.deepcopy(event_calendar_init) # dla każdej bety startowy kalendarz powinien być taki sam
    network_beta.actual_beta = base_beta
    generator.beta = base_beta
    generator.mi_hist = []
    generator.tau_hist = []
    return time, network_beta, event_calendar_beta, base_beta

def init_next_L(min_beta : float, L : float,  network_init : Network, event_calendar_init : SortedList):
    min_beta = round(min_beta, 3)
    logger.warning(f"[MAX BETA] -  {min_beta}")
    time = T_START
    network_beta = copy.deepcopy(network_init)
    network_beta.L = L
    event_calendar_beta = copy.deepcopy(event_calendar_init) # dla każdej bety startowy kalendarz powinien być taki sam
    network_beta.actual_beta = min_beta
    min_no_of_users_for_no_sleep = int(np.ceil((network_beta.R * network_beta.L)/2)) + 1
    generator.beta = min_beta
    generator.mi_hist = []
    generator.tau_hist = []
    generator.min_t_zero = min_no_of_users_for_no_sleep
    generator.min_t_past = min_no_of_users_for_no_sleep
    generator.max_t_zero = generator.min_t_past + 10
    generator.max_t_past = generator.max_t_past + 10
    logger.warning(f"[MINIMALNA LICZBA USEEROW] - dla progu {network_beta.L} ZEBY STACJE NIE SPALY {generator.min_t_zero}")
    return time, network_beta, event_calendar_beta
    

def clock(time : int,  execution_time : int):
    time = execution_time
    logger.info(f"[AKTUALNY CZAS] {time}")
    return time

def execute_event_on_base_station(event_type : EventType, base_station : BaseStation):
    if event_type == EventType.UE_END_OF_LIFE:
        base_station.remove_ue()
        if SIMULATION_STATE == SimulationState.L_SIMULATION and base_station.used_resources / network_beta.R <= network_beta.L and base_station.is_sleeping == False:
            event_calendar_beta.add(Event(time+0.05, base_station.id, EventType.BS_SLEEP))
        logging.info(f"[USUNIETO ZE STACJI] - {base_station.id} ")
    elif event_type == EventType.BS_WAKE_UP:
        base_station.wake_up()
        logging.warning(f"[OBUDZONO STACJE] - {base_station.id} ")
    elif event_type == EventType.BS_SLEEP:
        logger.warning(f"[USYPIANIE STACJI {base_station.id} - LICZBA UE DO PRZENIESIENIA {base_station.used_resources}]")
        base_station.put_to_sleep()
        base_station.used_resources = 0
        event_to_remove = []
        for event in event_calendar_beta:
            if event.station_id == base_station.id and event.event_type == EventType.UE_END_OF_LIFE:
                user_added_to_station_id = network_beta.add_ue(event.station_id)
                if user_added_to_station_id != -1:
                    logger.warning(f"[USYPIANIE STACJI {base_station.id} UE przeniesiony do {user_added_to_station_id}]")
                    event_calendar_beta.add(Event(event.execution_time, user_added_to_station_id, EventType.UE_END_OF_LIFE))
                else:
                    logger.warning(f"[USYPIANIE STACJI - UE STRACONY]")
                event_to_remove.append(event)
        for event in event_to_remove:
            event_calendar_beta.remove(event)
        logging.warning(f"[USPIONO STACJE] - {base_station.id} ")
    else: 
        logging.error("COŚ SIĘ ZEPUSŁO I NIE BYŁO MNIE SŁYCHAĆ")
    
def change_beta_in_network(network_beta : Network, base_beta : float, time : int):
    if time == 0:
        network_beta.actual_beta = round(base_beta/2, 5)
    elif time == calc.hour_to_s(8):
        network_beta.actual_beta = round((3*base_beta)/4, 5)
    elif time == calc.hour_to_s(14):
        network_beta.actual_beta = round(base_beta, 10)
    elif time == calc.hour_to_s(18):
        network_beta.actual_beta = round((3*base_beta)/4, 5)
    generator.beta = network_beta.actual_beta
    logging.error(f"[ZMIANA BETY] - t={time} beta = {network_beta.actual_beta}")

def create_next_user():
    generator.generate_next_user()
    event_calendar_beta.add(Event(time + generator.tau, event.station_id, event_type=EventType.UE_ARRIVAL))
    
def add_user_to_network(event : EventType) -> int:
    user_added_to_station_id = network_beta.add_ue(event.station_id)
    create_next_user()
    if network_beta.sum_of_lost_connections > 0 and SIMULATION_STATE==SimulationState.LAMBDA_SIMULATION:
        raise Beta_too_small('This beta doesn\'t do the trick.')
    elif user_added_to_station_id != event.station_id:
             logger.info(f"[DODANO DO INNEJ STACJI] - {user_added_to_station_id}")
             generator.generator_UE_time_of_life()
             event_calendar_beta.add(Event(time + generator.mi, user_added_to_station_id, event_type=EventType.UE_END_OF_LIFE))
    elif user_added_to_station_id == event.station_id:
        logger.info(f"[DODANO DO OCZEKIWANEJ STACJI]  -  {user_added_to_station_id}")
        generator.generator_UE_time_of_life()
        event_calendar_beta.add(Event(time + generator.mi, user_added_to_station_id, event_type=EventType.UE_END_OF_LIFE))
    else:
        logger.error("BŁĄD, użytkownik zaginął!!!")

def execute_event(event : Event, base_beta : float, network_beta : Network):
    logger.info(f"[TYP ZDARZENIA] - {event.event_type}")
    if event.event_type in [EventType.UE_END_OF_LIFE, EventType.BS_SLEEP, EventType.BS_WAKE_UP]: 
        execute_event_on_base_station(event.event_type, network_beta.stations[event.station_id])
    elif event.event_type == EventType.LAMBDA_CHANGE:
        change_beta_in_network(network_beta, base_beta, event.execution_time)
    elif event.event_type == EventType.UE_ARRIVAL:
        add_user_to_network(event)
    else: 
        logging.info("Błędne zdarzenie")

def draw_save_plot():
    fig_tau = plt.hist(generator.tau_hist, 30)
    plt.savefig(f'wyniki_lambda_max/wyniki_{count}/symulacja_{simulation_counter}/hist/tau/tau_for_beta_{base_beta}.png')
    #plt.show(block=False)
    #plt.pause(3)
    plt.close()
    fig_mi = plt.hist(generator.mi_hist, 30)
    plt.savefig(f'wyniki_lambda_max/wyniki_{count}/symulacja_{simulation_counter}/hist/mi/mi_for_beta_{base_beta}.png')    
    #plt.show(block=False)
    #plt.pause(3)
    plt.close()
    
def save_data_for_given_beta(base_beta : float, count : int, simulation_counter : int):
    draw_save_plot()
    logger.warning(f"[ZAKONCZONO_DLA_BETA] - {base_beta}")
 
def save_data_for_too_small_beta():
     draw_save_plot()
     with open(f'wyniki_lambda_max/wyniki_{count}/max_lambda_finder.csv', 'a+', newline='') as file:
            file.write(str(simulation_counter)+";"+str(round(1/min_beta, 2))+';'+str(round(1/base_beta, 2))+";"+str(round(1/network_beta.actual_beta, 2))+'\n')
            logger.warning([f"DATE_TIME_END_BETA - {datetime.now()}"])
      
   
if __name__ == '__main__':
    count = create_folder_structure_for_saving_data()
    for simulation_counter in range(NUMBER_OF_SIMULATIONS):
        SIMULATION_STATE = SimulationState.LAMBDA_SIMULATION
        beta_list, network_init, generator, event_calendar_init = init_simulation(count, simulation_counter)

        min_beta = -1
        # Szuakmy maks bety w oparciu o ten sam początkowy stan sieci i kalendarza
        for base_beta in beta_list:
            time, network_beta, event_calendar_beta, base_beta = init_next_beta(base_beta, network_init, event_calendar_init)
            for i in network_beta.stations:
                logger.info(i.used_resources)
            # Główna pętla symulacji - działamy tak długo aż będą obiekty w kalendarzu lub do końca czasu.
            try:
                while len(event_calendar_beta) > 0 and time <= T_MAX:
                    event = event_calendar_beta.pop(0)
                    time = round(clock(time, event.execution_time), 2)
                    execute_event(event, base_beta, network_beta)
                save_data_for_given_beta(base_beta, count, simulation_counter)
            except Beta_too_small:
                logger.error(f"[DLA_BETA_NIE_UDALO_SIE_ZAKONCZYC] : Dla beta_bazowej={base_beta}, bład nastpil przy rzeczywistej wartosci beta={network_beta.actual_beta}")
                save_data_for_too_small_beta()
                break
            min_beta = base_beta
            logger.warning([f"DATE_TIME_END_BETA_{base_beta} - {datetime.now()}"]) 
        if min_beta == -1: 
            logger.error("[BRAK BETY] - W podanym wektorze nie znaleziono wartości lambda do dalszych kroków symulacji. Zmień zakres.")
            print("Brak odpowiedniej bety w wektorze")
            exit()
   
        # SYMULACJA PROGU L
        logger.warning([f"DATE_TIME_START_L - {datetime.now()}"])
        SIMULATION_STATE = SimulationState.L_SIMULATION
        L_list = np.arange(0.05, 0.2, 0.05)
        min_beta = 0.06
        for L_tmp in L_list:
            time, network_beta, event_calendar_beta = init_next_L(min_beta, L_tmp, network_init, event_calendar_init)
            '''
            event_calendar_beta.add(Event(0, 0, EventType.BS_SLEEP))
            event_calendar_beta.add(Event(0, 1, EventType.BS_SLEEP))
            event_calendar_beta.add(Event(0, 2, EventType.BS_SLEEP))
            '''
            # TODO zrobic ze stacje nie usypialy na starcie i przelaczanie polowy z H do uspionej
            while len(event_calendar_beta) > 0 and time <= T_MAX:
                event = event_calendar_beta.pop(0)
                time = round(clock(time, event.execution_time), 2)
                execute_event(event, min_beta, network_beta)
    print("Koniec jest bliski.")
    logger.warning([f"DATE_TIME_END - {datetime.now()}"])
    exit()