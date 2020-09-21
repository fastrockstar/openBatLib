import model
import view

import tools

class Controller(object):
    """Class to manage the models and view components

    :param object: object
    :type object: object
    """
    _version = '0.1'

    def __init__(self, fmat, fparameter, system, ref_case, dt='1sec'):
        
        # Load system parameters
        parameter = self.load_parameter(fparameter, system)
        
        # Load PV generator input
        ppv = self.load_pv_input(fmat, 'ppv')

        # Load data from reference cases (load and inverter parameters)
        parameter, pl = self.load_ref_case(parameter, fmat, fparameter, ref_case)

        # Resample input data for time steps > 1 sec
        if dt != '1sec':
            t = int(''.join(filter(lambda i: i.isdigit(), dt)))
            unit = ''.join(filter(lambda i: i.isalpha(), dt))
            ppv = model.resample_input(t, unit, ppv)
            pl = model.resample_input(t, unit, pl)

        # Call model for AC coupled systems
        if parameter['Top'] == 'AC':
            Pr, Pbs, Ppv, Ppvs, Pperi = model.max_self_consumption(parameter, ppv, pl, pvmod=True, max=True)
            self.model = model.BatModAC(parameter, ppv, pl, Pr, Pbs, Ppv, Ppvs, Pperi)
        
        # Call model for DC coupled systems
        elif parameter['Top'] == 'DC':
            Pr, Prpv, Ppv, ppv2ac, Ppv2ac_out = model.max_self_consumption(parameter, ppv, pl, pvmod=True, max=True)
            self.model = model.BatModDC(parameter, ppv, pl, Pr, Prpv, Ppv, ppv2ac, Ppv2ac_out)
        
        # Call model for PV-coupled systems
        elif parameter['Top'] == 'PV':
            Pac, Ppv, Pperi = model.max_self_consumption(parameter, ppv, pl,pvmod=True, max=True)
            self.model = model.BatModPV(parameter, ppv, pl, Pac, Ppv, Pperi)

        self.view = view.View()
    
    def load_parameter(self, fparameter, system):
        """Loads system parameter

        :param fparameter: Path to file
        :type fparameter: string
        :param system: Indicator for the system
        :type system: string
        """
        parameter = tools.load_parameter(fparameter, system)
        parameter = tools.eta2abc(parameter)

        return parameter

    def load_pv_input(self, fmat, name):
        """Loads PV input data

        :param fmat: Path to file
        :type fmat: string
        :param name: Name of the input series
        :type name: string
        """
        ppv = tools.load_mat(fmat, name)

        return ppv

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

    def load_inverter(self, fname, inverter):
        """Loads inverter parameter

        :param fname: Path to file
        :type fname: string
        :param inverter: Inverter
        :type load_inverter: string
        """
        pass