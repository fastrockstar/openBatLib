from view import View
import tools

class Controller(object):
    """Class to manage the models

    :param object: object
    :type object: object
    """
    _version = '0.1'

    def __init__(self, model, view):
        self.model = model
        self.view = view
    
    def load_input(self, fname, name):
        """Loads time series

        :param fname: Path to file
        :type fname: string
        :param name: Name of series
        :type name: string
        """
        if name == 'ppv':
            self.model.load_pv_input(fname)
        if 'Pl' in name:
            self.model.load_pl_input(fname, name)

    def load_parameter(self, fname, system):
        """Loads parameter

        :param fname: Path to file
        :type fname: string
        :param col_name: Coloumn of system
        :type col_name: string
        """
        pass

    def load_inverter(self, fname, inverter):
        """Loads inverter parameter

        :param fname: Path to file
        :type fname: string
        :param inverter: Inverter
        :type load_inverter: string
        """
        pass