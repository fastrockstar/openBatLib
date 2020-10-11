import numpy as np
import matplotlib.pyplot as plt
import csv
class View(object):
    """View class to present the simulation results

    :param object: object
    :type object: object
    """
    _version = '0.1'

    @staticmethod
    def print_E(dict):
        print ("{:<10} {:<10}".format('Name','MWh'))
        for name, value in dict.items():
            print('{:<10} {:<10}'.format(name, round(value, 15)))

    @staticmethod
    def plot(input):
        #y_pos = np.arange(len(input))

        plt.plot(input)
        plt.grid()
        plt.show()

    @staticmethod
    def store_to_csv(name, data):
        with open(name, 'w') as f:
            writer = csv.writer(f)
            for val in data:
                writer.writerow([val])

    @staticmethod
    def E_to_csv(name, E):
        with open(name, 'w') as csv_file:  
            writer = csv.writer(csv_file)
            for key, value in E.items():
                writer.writerow([key, value])

    @staticmethod
    def store_dict_to_csv(name, data):
        with open(name, 'w') as f:  
            writer = csv.writer(f)
            for key, value in data.items():
                writer.writerow([key, value])

    @staticmethod
    def store_to_pickle(fname, data):
        with open(fname, 'wb') as f:
            np.save(f, data)
