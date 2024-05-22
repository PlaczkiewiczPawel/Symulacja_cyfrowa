import json
from base_station import BaseStation

# Klasa główna zawiera parametry potrzebne do późniejszego rysowania wykresów itp.
class Network:
    def __init__(self: float, N : int, R : int, H : float):
        self.sum_of_used_energy = 0
        self.sum_of_used_resources = 0
        self.sum_of_lost_connections = 0
        self.sum_of_all_connections = 0
        self.actual_beta = 0
        self.L = 0
        self.H = H
        self.R = R
        self.N = N
        self.station_counter = 0
        self.stations = []
        # Tu powstaje lista obiektów Stacja bazowa, z róznymi id.
        for i in range(self.N):
            self.stations.append(BaseStation(self.station_counter))
            self.station_counter += 1
    def add_ue(self, station_id):
        self.sum_of_all_connections += 1
        if self.stations[station_id].used_resources < self.R and self.stations[station_id].is_sleeping == False: # sprawdzenie naszej stacji
            self.stations[station_id].used_resources += 1
            return station_id
        else:
            for station in self.stations:
                    if station.used_resources < self.R and self.stations[station_id].is_sleeping == False: # sprawdzenie pozostałych + ew. naszej, nie opłaca się jej pozbywać
                        station.used_resources += 1
                        return station.id
        self.sum_of_lost_connections += 1
        return -1
                        
        
    def save_to_file(self):
        pass
    
    

       