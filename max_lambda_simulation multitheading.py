from network import Network
from base_station import BaseStation
from event import *
from generator import *
from exepctions import *
from datetime import datetime
from simulation_state import SimulationState
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
import time as t
import concurrent.futures

COUNT = 0
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
logger.addHandler(console)

try:
    with open ("config.json") as config_f:
        config = json.load(config_f)
        H = config["H"]
        R = config["R"]
        N = config["N"]
        DAYS = config["DAYS"]
        MIN_T_ZERO = config["NUMBER_OF_USERS_T_ZERO_RAND_MIN"]
        MAX_T_ZERO = config["NUMBER_OF_USERS_T_ZERO_RAND_MAX"]
        MIN_T_PAST  = config["NUMBER_OF_USERS_FROM_PAST_RAND_MIN"]
        MAX_T_PAST = config["NUMBER_OF_USERS_FROM_PAST_RAND_MAX"]  
        T_START = config["T_START"]
        LOGGER_MODE = config["LOGGER_MODE"]
        NUMBER_OF_SIMULATIONS = config["NUMBER_OF_SIMULATIONS"]
        BETA_MAX = config["BETA_MAX"] 
        BETA_MIN = config["BETA_MIN"]
        BETA_STEP = config["BETA_STEP"]
        L_MAX = config["L_MAX"] 
        L_MIN = config["L_MIN"]
        L_STEP = config["L_STEP"]
        SEED_FILE_NUMBER = config["SEED_FILE_NUMBER"]
        SEED_NUMBER = config["SEED_NUMBER"]
        GENERATOR_MODE = config["GENERATOR_MODE"]
        SIMULATION_STATE = SimulationState.LAMBDA_SIMULATION
except FileNotFoundError:
    print("Brak pliku konfiguracyjnego.")
    exit()

def create_folder_structure_for_saving_data():
    try:
        COUNT = (len(next(os.walk('wyniki_lambda_max'))[1])) # sprawdza ile folder ma podfolderów
    except StopIteration:
        COUNT = 0
    os.makedirs(f'wyniki_lambda_max/wyniki_{COUNT}')
    # with open(f'wyniki_lambda_max/wyniki_{COUNT}/symulacja_{simulation_counter}/max_lambda_finder.csv', 'a+', newline='') as file:
    #         file.write("NUMER_SYMULACJI;MAX_LAMBDA_PRAWIDLOWA;LAMBDA_NIEPRAWIDLOWA;RZECZYWISTA_LAMBDA_NIEPRAWIDLOWA\n")
    return COUNT

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
    event_calendar_init = [Event(0,-1, EventType.LAMBDA_CHANGE), Event(calc.hour_to_s(8), -1, EventType.LAMBDA_CHANGE), Event(calc.hour_to_s(14), -1, EventType.LAMBDA_CHANGE), Event(calc.hour_to_s(18), -1, EventType.LAMBDA_CHANGE), Event(calc.hour_to_s(24), -1, EventType.DAILY_RESET)]
    event_calendar_init = SortedList(event_calendar_init, key=lambda x: x.execution_time)
    for station in network_init.stations:
        no_users_on_station, no_users_to_init = init_number_of_users(station, generator)
        event_calendar_init = T_START_users_handle(station, no_users_to_init, event_calendar_init, generator)
        event_calendar_init = PAST_users_handle(station, no_users_on_station, event_calendar_init, generator)
    return event_calendar_init

def init_logger_for_simulation(simulation_counter : int):
    logger_path = f'wyniki_lambda_max/wyniki_{COUNT}/symulacja_{simulation_counter}/simulation_{simulation_counter}.log'
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
            logger.warning(F"[TRYB_GENERATORA] - DETERMINISTYCZNY 1 dla seedu numer {SEED_NUMBER} z pliku {SEED_FILE_NUMBER}")
            if not (0<=SEED_FILE_NUMBER<=29 or 0<=SEED_NUMBER<=999):
                logger.warning("[TRYB GENERATORA] - PARAMETRY GENERATORA NIEPRAWIDŁOWE")
                exit()
            with open(f'seeds/seed_{SEED_FILE_NUMBER}.csv', 'r', newline='') as file:
                seed = int(next(itertools.islice(csv.reader(file), SEED_NUMBER, None))[0])
                print(seed)
            generator = Generator_seeded(seed, 0, MIN_T_ZERO, MAX_T_ZERO, MIN_T_PAST, MAX_T_PAST)
        elif GENERATOR_MODE == 2:
            logger.warning(f"[TRYB_GENERATORA] - DETERMINISTYCZNY 2 dla pliku seed {SEED_FILE_NUMBER}")
            if not (0<=SEED_FILE_NUMBER<=29 or 0<=SEED_NUMBER<=999):
                logger.warning("[TRYB GENERATORA] - PARAMETRY GENERATORA NIEPRAWIDŁOWE")
                exit()
            with open(f'seeds/seed_{SEED_FILE_NUMBER}.csv', 'r', newline='') as file:
                seed = int(next(itertools.islice(csv.reader(file), simulation_counter, None))[0])
            generator = Generator_seeded(seed, 0, MIN_T_ZERO, MAX_T_ZERO, MIN_T_PAST, MAX_T_PAST)
        else:
            logger.warning("[TRYB_GENERATORA] - BLAD PRZY WYBORZE GENERATORA, SPRAWDZ PARAMTERY")
            exit()
        return generator
    except FileNotFoundError:
        logger.warning("[BRAK KATALOGU SEEDS] - Uruchom skrypt create_rng.py z katalogu glownego")
        exit()

def init_simulation(simulation_counter : int):
    print(BETA_MIN, BETA_MAX)
    beta_list = np.arange(BETA_MIN, BETA_MAX, BETA_STEP)  # Wektory tetstowe  [0.1, 0.8, 0.9] [0.010, 0.011, 0.012]
    beta_list = np.flip(beta_list)
    print(beta_list)
    os.makedirs(f'wyniki_lambda_max/wyniki_{COUNT}/symulacja_{simulation_counter}/hist/tau')
    os.makedirs(f'wyniki_lambda_max/wyniki_{COUNT}/symulacja_{simulation_counter}/hist/mi')
    with open(f'wyniki_lambda_max/wyniki_{COUNT}/symulacja_{simulation_counter}/max_lambda_finder.csv', 'a+', newline='') as file:
            file.write("NUMER_SYMULACJI;MAX_LAMBDA_PRAWIDLOWA;LAMBDA_NIEPRAWIDLOWA;RZECZYWISTA_LAMBDA_NIEPRAWIDLOWA\n")
    init_logger_for_simulation(simulation_counter)
    generator = init_generator(simulation_counter)
    network_init = Network(N, R, H)
    event_calendar_init = init_calendar(network_init, generator)                                                                                                                                                                                                                                                                                                       
    return beta_list, network_init, generator, event_calendar_init
   
def init_next_beta(base_beta : float, network_init : Network, event_calendar_init : SortedList, generator : Generator):
    base_beta = round(base_beta, 5)
    print(base_beta)
    logger.warning(f"[BETA BAZOWA] -  {base_beta}")
    time = T_START
    network_beta = copy.deepcopy(network_init)
    event_calendar_beta = copy.deepcopy(event_calendar_init) # dla każdej bety startowy kalendarz powinien być taki sam
    network_beta.actual_beta = base_beta
    generator.beta = base_beta
    generator.mi_hist = []
    generator.tau_hist = []
    return time, network_beta, event_calendar_beta, base_beta

def init_next_L(min_beta : float, L : float,  network_init : Network, event_calendar_init : SortedList, generator : Generator):
    min_beta = round(min_beta, 3)
    logger.warning(f"[MAX BETA] -  {min_beta}")
    time = T_START
    network_beta = copy.deepcopy(network_init)
    network_beta.L = L
    event_calendar_beta = copy.deepcopy(event_calendar_init) # dla każdej bety startowy kalendarz powinien być taki sam
    network_beta.actual_beta = min_beta
    min_no_of_users_for_no_sleep = np.ceil(network_beta.R * network_beta.L)
    generator.beta = min_beta
    generator.mi_hist = []
    generator.tau_hist = []
    lost_all_daily = []
    logger.warning(f"[MINIMALNA LICZBA USEROW] - dla progu {network_beta.L} ZEBY STACJE NIE SPALY {min_no_of_users_for_no_sleep}")
    return time, network_beta, event_calendar_beta, lost_all_daily
    

def clock(time : float,  execution_time : float):
    time = execution_time
    logger.info(f"[AKTUALNY CZAS] {time}")
    return time

def execute_event_on_base_station(type_of_event: EventType, base_station : BaseStation, time : float, network_beta : Network, event_calendar_beta : SortedList):
    if type_of_event == EventType.UE_END_OF_LIFE:
        base_station.remove_ue()
        if SIMULATION_STATE == SimulationState.L_SIMULATION and base_station.used_resources / network_beta.R <= network_beta.L and base_station.is_sleeping == False and base_station.sleep_process == False :
            event_calendar_beta.add(Event(time+0.05, base_station.id, EventType.BS_SLEEP))
            base_station.sleep_process = True
        logging.info(f"[USUNIETO ZE STACJI] - {base_station.id} ")
    elif type_of_event == EventType.BS_WAKE_UP:
        wake_up_id = network_beta.choose_for_wake_up()
        no_of_users_to_move = int(base_station.used_resources / 2)
        logger.warning(f"[{time} BUDZENIE PO PRZEPEŁNIENIU {base_station.id} - LICZBA UE DO PRZENIESIENIA {no_of_users_to_move}]")
        if wake_up_id == -1:
            logger.warning(f"[BUDZENIE PO PRZEPEŁNIENIU {base_station.id} - BRAK STACJI DO OBUDZENIA)]")
        else:
            logger.warning(f"[BUDZENIE PO PRZEPEŁNIENIU] - {base_station.id}, PRZENOSZENIE UE DO {wake_up_id} ")
            network_beta.stations[base_station.id].overflow_H(no_of_users_to_move)
            network_beta.stations[wake_up_id].wake_up(no_of_users_to_move)
            for event in event_calendar_beta:
                if event.station_id == base_station.id and event.event_type == EventType.UE_END_OF_LIFE and no_of_users_to_move > 0:
                    event.station_id = wake_up_id
                    no_of_users_to_move-=1
            logging.warning(f"[OBUDZONO STACJE] - {wake_up_id} i przeniesiono do niej  UE ze stacji {base_station.id}. Aktualna liczba UE na stacji to {base_station.used_resources}] ")
    elif type_of_event == EventType.BS_SLEEP:
        for station in network_beta.stations:
            if station.is_sleeping == False and station.id != base_station.id:
                base_station.sleep_process = False
                break
            else:
                return
        logger.warning(f"[{time} USYPIANIE STACJI {base_station.id} - LICZBA UE DO PRZENIESIENIA {base_station.used_resources}]")
        event_to_add = []
        base_station.put_to_sleep()
        for event in event_calendar_beta:
            if base_station.id == event.station_id and event.event_type == EventType.UE_END_OF_LIFE:
                user_added_to_station_id, overflow_start = network_beta.add_ue_L(event.station_id)
                if overflow_start == True and network_beta.stations[user_added_to_station_id].overflow_process == False:
                        event_to_add.append(Event(time+0.05, user_added_to_station_id, EventType.BS_WAKE_UP))
                        network_beta.stations[user_added_to_station_id].overflow_process = True
                if user_added_to_station_id != -1:
                    logger.warning(f"[USYPIANIE STACJI {base_station.id} UE przeniesiony do {user_added_to_station_id}]")
                    event.station_id = user_added_to_station_id
                else:
                    logger.warning(f"[USYPIANIE STACJI - UE STRACONY]")
        base_station.sleep_process = False
        for event in event_to_add:
            event_calendar_beta.add(event)
        logging.warning(f"[USPIONO STACJE] - {base_station.id} ")
    else: 
        logging.warning("COŚ SIĘ ZEPUSŁO I NIE BYŁO MNIE SŁYCHAĆ")
    
def change_beta_in_network(network_beta : Network, base_beta : float, time : int):
    if time % 86400 == 0:
        network_beta.actual_beta = round(base_beta * 2, 5)
    elif time % 86400 == calc.hour_to_s(8):
        network_beta.actual_beta = round((base_beta * (4/3)), 5)
    elif time % 86400 == calc.hour_to_s(14):
        network_beta.actual_beta = round(base_beta, 5)
    elif time % 86400 == calc.hour_to_s(18):
        network_beta.actual_beta = round((base_beta * (4/3)), 5)
    generator.beta = network_beta.actual_beta
    logging.warning(f"[ZMIANA BETY] - t={time} beta = {network_beta.actual_beta}")

def create_next_user(time, event, event_calendar_beta):
    generator.generate_next_user()
    event_calendar_beta.add(Event(time + generator.tau, event.station_id, event_type=EventType.UE_ARRIVAL))
    
def add_user_to_network(event : Event, network_beta : Network, time : float, event_calendar_beta : SortedList) -> int:
    create_next_user(time, event, event_calendar_beta)
    if SIMULATION_STATE == SimulationState.LAMBDA_SIMULATION:
        user_added_to_station_id = network_beta.add_ue_lambda(event.station_id)
    else:
        user_added_to_station_id, overflow_start = network_beta.add_ue_L(event.station_id)
        if overflow_start == True and network_beta.stations[user_added_to_station_id].overflow_process == False:
            event_calendar_beta.add(Event(time+0.05, user_added_to_station_id, EventType.BS_WAKE_UP))
            network_beta.stations[user_added_to_station_id].overflow_process = True
    if user_added_to_station_id == -1:
        if SIMULATION_STATE==SimulationState.LAMBDA_SIMULATION:
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
        logger.info("BŁĄD, użytkownik zaginął!!!")
     

def execute_event(event : Event, base_beta : float, network_beta : Network, day_no : int, time : float, event_calendar_beta : SortedList, simulation_counter):
    logger.info(f"[TYP ZDARZENIA] - {event.event_type}")
    if event.event_type in [EventType.UE_END_OF_LIFE, EventType.BS_SLEEP, EventType.BS_WAKE_UP]: 
        execute_event_on_base_station(event.event_type, network_beta.stations[event.station_id], time, network_beta, event_calendar_beta)
    elif event.event_type == EventType.LAMBDA_CHANGE:
        change_beta_in_network(network_beta, base_beta, event.execution_time)
    elif event.event_type == EventType.DAILY_RESET:
        day_no += 1
        logger.error([f"ZMIANA DNIA: POCZĄTEK DNIA {day_no}"])
        event_calendar_beta.add(Event(time, -1, EventType.LAMBDA_CHANGE))
        event_calendar_beta.add(Event(time + calc.hour_to_s(8), -1, EventType.LAMBDA_CHANGE))
        event_calendar_beta.add(Event(time + calc.hour_to_s(14), -1, EventType.LAMBDA_CHANGE))
        event_calendar_beta.add(Event(time + calc.hour_to_s(18), -1, EventType.LAMBDA_CHANGE))
        event_calendar_beta.add(Event(time + calc.hour_to_s(24), -1, EventType.DAILY_RESET))
        if SIMULATION_STATE==SimulationState.L_SIMULATION:
            lost_all_ratio_day = network_beta.sum_of_lost_connections / network_beta.sum_of_all_connections
            network_beta.sum_of_lost_connections = 0
            network_beta.sum_of_all_connections = 0
            lost_all_daily.append(lost_all_ratio_day)
            with open(f'wyniki_lambda_max/wyniki_{COUNT}/symulacja_{simulation_counter}/L_finder.csv', 'a+', newline='') as file:
                    file.write(str(lost_all_ratio_day)+'\n')
    elif event.event_type == EventType.UE_ARRIVAL:
        add_user_to_network(event, network_beta, time, event_calendar_beta)
    else: 
        logging.info("Błędne zdarzenie")
    return day_no

def draw_save_plot(simulation_counter,base_beta):
    fig_tau = plt.hist(generator.tau_hist, 1000)
    plt.title(f"Histogram rozkładu czasu między kolejnymi zgłoszeniami dla lambda={round((1/base_beta),2)}", fontsize=9)
    plt.xlabel("Czas pomiędzy kolejnymi zgłoszeniami [s]")
    plt.ylabel("Ilość wystąpień")
    plt.savefig(f'wyniki_lambda_max/wyniki_{count}/symulacja_{simulation_counter}/hist/tau/tau_for_beta_{base_beta}.png')
    #plt.show(block=False)
    #plt.pause(3)
    plt.close()
    fig_mi = plt.hist(generator.mi_hist, 30)
    plt.title(f"Histogram rozkładu czasu obsługi")
    plt.xlabel("Czas obsługi [s]")
    plt.ylabel("Ilość wystąpień")
    plt.savefig(f'wyniki_lambda_max/wyniki_{count}/symulacja_{simulation_counter}/hist/mi/mi_for_beta_{base_beta}.png')    
    #plt.show(block=False)
    #plt.pause(3)
    plt.close()
    
    
def save_data_for_given_beta(base_beta : float, simulation_counter : int):
    draw_save_plot(simulation_counter,base_beta)
    logger.warning(f"[ZAKONCZONO_DLA_BETA] - {base_beta}")
 
def save_data_for_too_small_beta(simulation_counter, min_beta, base_beta, network_beta):
     draw_save_plot(simulation_counter,base_beta)
     with open(f'wyniki_lambda_max/wyniki_{COUNT}/symulacja_{simulation_counter}/max_lambda_finder.csv', 'a+', newline='') as file:
            file.write(str(simulation_counter) + ";" + str(round(1 / min_beta, 2)) + ';' + str(round(1 / base_beta, 2)) + ";" + str(round(1 / network_beta.actual_beta, 2)) + '\n')
            logger.warning([f"DATE_TIME_END_BETA - {datetime.now()}"])
    
def run_simulation(simulation_counter):
    global generator, event_calendar_beta, lost_all_daily,SIMULATION_STATE
    SIMULATION_STATE = SimulationState.LAMBDA_SIMULATION
    beta_list, network_init, generator, event_calendar_init = init_simulation(simulation_counter)
    logger.warning(f"[SYMULACJA LAMBDY START] - {datetime.now()}")
    min_beta = -1
    # Szuakmy maks bety w oparciu o ten sam początkowy stan sieci i kalendarza
    for base_beta in beta_list:
        time, network_beta, event_calendar_beta, base_beta = init_next_beta(base_beta, network_init, event_calendar_init, generator)
        for i in network_beta.stations:
            logger.info(i.used_resources)
        # Główna pętla symulacji - działamy tak długo aż będą obiekty w kalendarzu lub do końca czasu.
        day_no = 1
        logger.error([f"ZMIANA DNIA: POCZĄTEK DNIA {day_no}"])
        
        try:
            while len(event_calendar_beta) > 0 and time <= DAYS * calc.hour_to_s(24):
                event = event_calendar_beta.pop(0)
                time = round(clock(time, event.execution_time), 3)
                day_no = execute_event(event, base_beta, network_beta, day_no, time, event_calendar_beta,simulation_counter)
            save_data_for_given_beta(base_beta,simulation_counter)
        except Beta_too_small:
            logger.warning(f"[DLA_BETA_NIE_UDALO_SIE_ZAKONCZYC] : Dla beta_bazowej={base_beta}, bład nastpil przy rzeczywistej wartosci beta={network_beta.actual_beta}")
            save_data_for_too_small_beta(simulation_counter, min_beta, base_beta, network_beta)
            break
        min_beta = base_beta
        logger.warning([f"DATE_TIME_END_BETA_{base_beta} - {datetime.now()}"]) 
    if min_beta == -1: 
        logger.warning(f"[BRAK BETY] - W podanym wektorze nie znaleziono wartości lambda do dalszych kroków symulacji. Zmień zakres. Numer symulacji {simulation_counter}. Brak możliwości symulacji L")
        print("Brak odpowiedniej bety w wektorze.")
        return

    logger.warning(f"[SYMULACJA LAMBDY KONIEC] - {datetime.now()}")
    logger.warning([f"SYMULACJA L START dla znalezionej wartosci beta = {min_beta} - {datetime.now()}"])
    SIMULATION_STATE = SimulationState.L_SIMULATION
    L_list = np.arange(L_MIN, L_MAX + L_STEP, L_STEP)
    L_list = np.flip(L_list)
    for L_tmp in L_list:
        with open(f'wyniki_lambda_max/wyniki_{COUNT}/symulacja_{simulation_counter}/L_finder.csv', 'a+', newline='') as file:
            file.write(str(f"DLA L: {L_tmp}\n"))
        logger.warning(f"[SYMULACJA_L={L_tmp}_START] - {datetime.now()}")
        time, network_beta, event_calendar_beta, lost_all_daily = init_next_L(min_beta, L_tmp, network_init, event_calendar_init, generator)
        day_no = 1
        logger.warning([f"ZMIANA DNIA: POCZĄTEK DNIA {day_no}"])
        while len(event_calendar_beta) > 0 and time <= DAYS * calc.hour_to_s(24):
            event = event_calendar_beta.pop(0)
            time = round(clock(time, event.execution_time), 3)
            day_no = execute_event(event, min_beta, network_beta, day_no, time, event_calendar_beta,simulation_counter)
        lost_all_sum = sum(lost_all_daily)
        lost_all_avg = lost_all_sum / DAYS
        with open(f'wyniki_lambda_max/wyniki_{COUNT}/symulacja_{simulation_counter}/L_finder.csv', 'a+', newline='') as file:
            file.write(str(f"SREDNIA: {lost_all_avg}\n"))
        # if lost_all_avg <= 0.05:
        #     logger.warning(f"[ZNALEZIONO SZUKANE L] - {L_tmp}")
        #     break
        logger.warning([f"[SYMULACJA_L={L_tmp}_KONIEC] - {datetime.now()}"])

if __name__ == '__main__':
    create_folder_structure_for_saving_data()
    NUMBER_OF_SIMULATIONS = 10  # Define your number of simulations

    # Use ProcessPoolExecutor with a max of 4 workers
    with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(run_simulation, simulation_counter) for simulation_counter in range(NUMBER_OF_SIMULATIONS)]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # Get the result (if any)
            except Exception as e:
                logger.error(f"Simulation generated an exception: {e}")

    print("Koniec jest bliski.")
