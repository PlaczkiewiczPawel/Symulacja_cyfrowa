import json
import numpy as np
import csv
try:
    with open ("config.json") as config_f:
        config = json.load(config_f)
        L_MAX = config["L_MAX"] 
        L_MIN = config["L_MIN"]
        L_STEP = config["L_STEP"]
       
except FileNotFoundError:
    print("Brak pliku konfiguracyjnego.")
    exit()

L_list = np.arange(L_MIN, L_MAX + L_STEP, L_STEP)
L_list = np.flip(L_list)

output_file = r'C:\Users\Marcel\Symulacja_cyfrowa\L_avg.csv'
for L in L_list:
    with open(output_file, mode='w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        writer.writerow(str(L)+";")
        for i in range(10):
            input_file = rf'C:\Users\Marcel\Symulacja_cyfrowa\Wyniki\seed_12\symulacja_{i}\L_finder.csv'
            counter = -1
            with open(input_file, mode='r', encoding='utf-8') as infile:
                    reader = csv.reader(infile)
                    for row in reader:
                        if row[0].startswith("DLA L:"):
                            try:
                                L_file = row[0][7]+row[0][8]+row[0][9]+row[0][10]+row[0][11]
                            except IndexError:
                                L_file = 0.1
                            if L_file == str(round(L, 3)): counter = 8
                        if counter == 0: 
                            with open(output_file, mode='w', newline='') as outfile:
                                writer = csv.writer(outfile, delimiter=';')
                                writer.writerow(str(row)+";")
                        counter-=1
                    
       
