import model
import view

import tools

class Controller(object):
    """Class to manage the models and view components

    :param object: object
    :type object: object
    """
    _version = '0.1'

    def __init__(self, fmat, fparameter, system, ref_case):
        # Load system parameters
        parameter = tools.load_parameter(fparameter, system)
        parameter = tools.eta2abc(parameter)
        
        # Load PV generator input
        ppv = tools.load_mat(fmat, 'ppv')

        # Load data from reference cases
        parameter, pl = self.load_ref_case(parameter, fmat, fparameter, ref_case)

        # Call model for AC coupled systems
        if parameter['Top'] == 'AC':
            Pr, Pbs, Ppv, Ppvs, Pperi = model.max_self_consumption(parameter, ppv, pl, pvmod=True)
            self.model = model.BatModAC(parameter, ppv, pl, Pr, Pbs, Ppv, Ppvs, Pperi)
        
        self.view = view.View()
    
    def load_ref_case(self, parameter, fmat, fparameter, ref_case):
            
        if ref_case == '1':
            # Load parameters of first inverter
            if parameter['Top'] == 'AC' or parameter['Top'] == 'PV':
                inverter_parameter = tools.load_parameter(fparameter, 'L')            
            parameter['P_PV'] = 5
            pl = tools.load_mat(fmat, 'Pl1')
                                        
        elif ref_case == '2':
            # Load paramertes of second inverter
            if parameter['Top'] == 'AC' or parameter['Top'] == 'PV':
                inverter_parameter = tools.load_parameter(fparameter, 'M')            
            parameter['P_PV'] = 10
            pl = tools.load_mat(fmat, 'Pl2')

        # Load inverter parameters for AC or PV coupled systems
        if parameter['Top'] == 'AC' or parameter['Top'] == 'PV':

            inverter_parameter = tools.eta2abc(inverter_parameter)

            parameter['P_PV2AC_in'] = inverter_parameter['P_PV2AC_in']
            parameter['P_PV2AC_out']= inverter_parameter['P_PV2AC_out']
            parameter['P_PVINV_AC'] = inverter_parameter['P_PVINV_AC']

            parameter['PV2AC_a_in'] = inverter_parameter['PV2AC_a_in']
            parameter['PV2AC_b_in'] = inverter_parameter['PV2AC_b_in']
            parameter['PV2AC_c_in'] = inverter_parameter['PV2AC_c_in']
            parameter['PV2AC_a_out'] = inverter_parameter['PV2AC_a_out']
            parameter['PV2AC_b_out'] = inverter_parameter['PV2AC_b_out']
            parameter['PV2AC_c_out'] = inverter_parameter['PV2AC_c_out']

            if parameter['Top'] == 'PV':
                parameter['P_SYS_SOC0_AC'] = inverter_parameter['P_PVINV_AC']

        return parameter, pl

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