class View(object):
    """View class to present the simulation results

    :param object: object
    :type object: object
    """
    _version = '0.1'

    @staticmethod
    def print_E(dict):
        print ("{:<10} {:<10}".format('Name','Wh'))
        for name, value in dict.items():
            print('{:<10} {:<10}'.format(name, round(value, 3)))
