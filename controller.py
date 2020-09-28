import model
import view

import tools

class Controller(object):
    """Class to manage the models and view components

    :param object: object
    :type object: object
    TODO: Die init überarbeiten, so dass zwischen batmod und modbus unterschieden werden kann
    """
    _version = '0.1'

    def sim(self, fmat, fparameter, system, ref_case, dt='1sec'):
        
        # Load system parameters
        parameter = self._load_parameter(fparameter, system)
        
        # Load PV generator input
        ppv = self._load_pv_input(fmat, 'ppv')

        # Load data from reference cases (load and inverter parameters)
        parameter, pl = self._load_ref_case(parameter, fmat, fparameter, ref_case)

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

        # Load the view class
        self.view = view.View()
    
    def modbus(self, host, port, unit_id, input_val):
        set_val = self._load_set_values(input_val)
        self.model = model.ModBus(host, port, unit_id, set_val)

    def _load_parameter(self, fparameter, system):
        """Loads system parameter

        :param fparameter: Path to file
        :type fparameter: string
        :param system: Indicator for the system
        :type system: string
        """
        parameter = tools.load_parameter(fparameter, system)
        parameter = tools.eta2abc(parameter)

        return parameter

    def _load_pv_input(self, fmat, name):
        """Loads PV input data

        :param fmat: Path to file
        :type fmat: string
        :param name: Name of the input series
        :type name: string
        """
        ppv = tools.load_mat(fmat, name)

        return ppv

    def _load_set_values(self, fname):
        return fname

    def _load_ref_case(self, parameter, fmat, fparameter, ref_case):
            
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

    def print_E(self):
        E = self.model.get_E()
        self.view.print_E(E)

    def plot(self):
        soc = self.model.get_soc()
        Pbat = self.model.get_Pbat()
        self.view.plot(soc)
        self.view.plot(Pbat)