import json
from base_station import BaseStation
import logging

try:
    with open ("config.json") as config_f:
       config = json.load(config_f)
       H = config["H"]
       R = config["R"]
except FileNotFoundError:
    print("Brak pliku konfiguracyjnego.")

# Klasa główna zawiera parametry potrzebne do późniejszego rysowania wykresów itp.
class Network:
    def __init__(self, number_of_stations: int, base_beta : float):
        self.max_lambda = 0
        self.sum_of_used_energy = 0
        self.sum_of_used_resources = 0
        self.sum_of_lost_connections = 0
        self.actual_beta = base_beta
        self.L = 0
        self.H = H
        self.R = R
        self.station_counter = 0
        self.stations = []
        # Tu powstaje lista obiektów Stacja bazowa, z róznymi id.
        for i in range(number_of_stations):
            self.stations.append(BaseStation(self.station_counter))
            self.station_counter += 1
    def add_ue(self, station_id):
        if self.stations[station_id].used_resources < self.R: # sprawdzenie naszej stacji
            self.stations[station_id].used_resources += 1
            return station_id
        else:
            for station in self.stations:
                    if station.used_resources < self.R: # sprawdzenie pozostałych + ew. naszej, nie opłaca się jej pozbywać
                        station.used_resources += 1
                        return station.id
        self.max_lambda = 1/self.actual_beta
        return -1
                        
        
    def save_to_file(self):
        pass
    
    

       