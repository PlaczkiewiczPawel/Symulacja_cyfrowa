import json
from base_station import BaseStation
from sortedcontainers import SortedList
from operator import itemgetter

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
    
    def add_ue_lambda(self, station_id):
        self.sum_of_all_connections += 1
        if self.stations[station_id].used_resources < self.R: # sprawdzenie naszej stacji
            self.stations[station_id].used_resources += 1
            return station_id
        else:
            min_res=self.R
            min_id = None
            for station in self.stations:
                if station.used_resources<min_res:
                    min_res=station.used_resources
                    min_id=station.id
            if min_id != None:
                self.stations[min_id].used_resources += 1
                return min_id
            else:
                self.sum_of_lost_connections += 1
                return -1
                 
    def add_ue_L(self, station_id):
        self.sum_of_all_connections += 1
        if self.stations[station_id].used_resources < self.R and self.stations[station_id].is_sleeping == False: # sprawdzenie naszej stacji
            self.stations[station_id].used_resources += 1
            if (self.stations[station_id].used_resources / self.R) >= self.H:
                return station_id, True
            else:
                return station_id, False
        else:
            min_res=self.R
            min_id = None
            for station in self.stations:
                if station.used_resources<min_res and station.is_sleeping == False:
                    min_res=station.used_resources
                    min_id=station.id
            if min_id != None:
                self.stations[min_id].used_resources += 1
                if (self.stations[min_id].used_resources / self.R) >= self.H:
                    return min_id, True
                else:
                    return min_id, False
            else:
                self.sum_of_lost_connections += 1
                return -1, None
                    
    def choose_for_wake_up(self):
        for station in self.stations:
            if station.is_sleeping == True:
                return station.id
        return -1
    def save_to_file(self): 
        pass
    
    

       