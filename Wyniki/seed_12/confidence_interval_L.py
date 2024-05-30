import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st


import csv

def csv_no_of_cols(path : str):
    with open(path, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
           number_of_cols = len(row) - 1
           return number_of_cols
    csvfile.close()
    
def read_col(path : str):
    title = True
    L = 0
    data = []
    with open(path, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            if title == True:
                title = False
                L = round(float(row[col]), 3)
            else:
                data.append(float(row[col]))
    csvfile.close()
    return L, data

if __name__ == '__main__':
    path = r'Wyniki\seed_12\L_seed_12.csv'      
    number_of_cols = csv_no_of_cols(path)
    col = 1
    for i in range(number_of_cols):
        L, data = read_col(r'Wyniki\seed_12\L_seed_12.csv')
        col+=1
        n = np.arange(0, 10, 1)
        mean = round(np.mean(data), 3)
        confidence_interval = 0.1
        confidence_interval_values = st.t.interval(confidence_interval, len(data)-1, loc=mean, scale=st.sem(data))
        confidence_interval_values = (mean - confidence_interval_values[0], confidence_interval_values[1] - mean)
        print(confidence_interval_values)
        data_L, data_H = [], []
        for value in data:
            data_L.append(value-confidence_interval_values[0])
            data_H.append(value+confidence_interval_values[1])
        plt.rc('figure', figsize=(10, 7))
        plt.figure()
        plt.plot(n, data_L, 'o', label="Dolny przedział ufności")
        plt.plot(n, data_H, 'o', label="Górny przedział ufności")
        plt.plot(n, data, 'o', label="Średnia dobowa ilość traconych zgłoszeń")
        plt.axhline(y=mean, color='red', label="Średnia ze średniej dobowej liczby traconych zgłoszeń")
        plt.xticks(n)
        plt.yticks(np.arange(min(data), max(data), 0.01))
        plt.title(f"Średnia dobowa ilość traconych zgłoszeń dla progu {L}")
        plt.ylabel("Średnia dobowa liczba traconych zgłoszeń ")
        plt.xlabel("Numer symulacji")
        plt.legend(loc = 'upper right')
        plt.savefig(r'Wyniki\seed_12\lambda_seed_12.png')
        plt.show()
        
   