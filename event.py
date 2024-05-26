from enum import Enum

# Typy zdarzeń zapisujemy przy pomocy typu wyliczeniowego - Enum, dla użytkownika czytelny, dla maszyny szybki bo to zwykłe liczby całkowite.
class EventType(Enum):
        UE_ARRIVAL = 0
        UE_END_OF_LIFE = 1
        BS_SLEEP = 2
        BS_WAKE_UP = 3
        LAMBDA_CHANGE = 4
        DAILY_RESET = 5

# Prosta klasa, która nie zawiera metod i służy jako zawartość kalendarza
class Event():
    def __init__(self, execution_time : int, station_id : int, event_type : EventType):
        self.execution_time = execution_time
        self.event_type = event_type
        self.station_id = station_id
    