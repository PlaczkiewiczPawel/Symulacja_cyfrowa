import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st


import csv

def read_csv(path : str):
    data = []
    with open(path, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in spamreader:
            if row[1] != 'MAX_LAMBDA_PRAWIDLOWA':
                data.append(float(row[1]))
    csvfile.close()
    return data

if __name__ == '__main__':
    path = r'Wyniki\seed_12\Lambda_seed_12.csv'
    n = np.arange(0, 10, 1)
    print(n)
    data = read_csv(path)
    print(data)
    mean = round(np.mean(data),3)
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
    plt.plot(n, data, 'o', label="λ_max")
    plt.axhline(y=mean, color='red', label="Średnia wartość λ_max ")
    plt.xticks(n)
    plt.yticks(np.arange(min(data), max(data), 0.05))
    plt.title("Maksymalna wartość λ dla, której nie były tracone żadne zgłoszenia.")
    plt.ylabel("λ_max [1/min]")
    plt.xlabel("Numer symulacji")
    plt.legend(loc = 'upper right')
    plt.savefig(r'Wyniki\seed_12\lambda_seed_12.png')
    plt.show()
    