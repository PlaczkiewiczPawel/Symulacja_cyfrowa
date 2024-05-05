import json
from base_station import BaseStation

try:
    with open ("config.json") as config_f:
       config = json.load(config_f)
       H = config["H"]
except FileNotFoundError:
    print("Brak pliku konfiguracyjnego.")

# Klasa główna zawiera parametry potrzebne do późniejszego rysowania wykresów itp.
class Network:
    def __init__(self, number_of_stations : int):
        self.max_lambda = 0
        self.sum_of_used_energy = 0
        self.sum_of_used_resources = 0
        self.sum_of_lost_connections = 0
        self.actual_lambda = 0
        self.L = 0
        self.H = H
        self.station_id = 0
        self.stations = []
        # Tu powstaje lista obiektów Stacja bazowa, z róznymi id
        for i in range(number_of_stations):
            self.stations.append(BaseStation(self.station_id))
            self.station_id += 1
    def save_to_file(self):
        pass
    def lambda_change(self):
        pass
    
    
    

       