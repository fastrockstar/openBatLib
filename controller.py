import pandas as pd
from numba import types
from numba.typed import Dict
from numba import njit

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

    def __init__(self):

        self.view = view.View()

    def sim(self, fmat, fparameter, system, ref_case, dt=1):
        
        # Load system parameters
        parameter = self._load_parameter(fparameter, system)
        
        # Load PV generator input
        ppv = self._load_pv_input(fmat, 'ppv')

        # Load data from reference cases (load and inverter parameters)
        parameter, pl = self._load_ref_case(parameter, fmat, fparameter, ref_case)

        # Call model for AC coupled systems
        if parameter['Top'] == 'AC':
            Pr, Ppv, Ppvs, Pperi = model.max_self_consumption(parameter, ppv, pl, pvmod=True)
            d = model.transform_dict_to_array(parameter)
            self.model = model.BatModAC(parameter, d, ppv, pl, Pr, Ppv, Ppvs, Pperi, dt)
        
        # Call model for DC coupled systems
        elif parameter['Top'] == 'DC':
            Pr, Prpv, Ppv, ppv2ac, Ppv2ac_out = model.max_self_consumption(parameter, ppv, pl, pvmod=True)
            d = model.transform_dict_to_array(parameter)
            self.model = model.BatModDC(parameter, d, ppv, pl, Pr, Prpv, Ppv, ppv2ac, Ppv2ac_out, dt)
        
        # Call model for PV-coupled systems
        elif parameter['Top'] == 'PV':
            Pac, Ppv, Pperi = model.max_self_consumption(parameter, ppv, pl, pvmod=True)
            self.model = model.BatModPV(parameter, ppv, pl, Pac, Ppv, Pperi)

        # Load the view class
        self.view = view.View()
    
    def modbus(self, host, port, unit_id, data_frame, ref_case, dt, fname, fparameter, fmat, system):
        parameter = self._load_parameter(fparameter, system)
        #df_resample = model.resample_data_frame(df=data_frame)

        ppv = data_frame['ppv'].to_numpy()
        pl = data_frame['L'].to_numpy()
        parameter, pl_not_used = self._load_ref_case(parameter, fmat, fparameter, ref_case)

        Pr, Ppv_not_used, Ppvs_not_used, Pperi_not_used = model.max_self_consumption(parameter, ppv, pl, pvmod=True)

        Pr = Pr * -1 # negative values for charging, positive values for discharging

        self.model = model.ModBus(host, port, unit_id, Pr, dt, fname)

    def real_time(self, parameter, **kwargs):
        if parameter['Top'] == 'AC':
            d = self._dict_to_array(parameter)
            Pbat, Pbs, soc, soc0 = model.BatMod_AC(d, **kwargs)
            return Pbat, Pbs, soc, soc0
        elif type == 'DC':
            d = self._dict_to_array(parameter)
            Ppv2ac_out, Ppv2bat_in, Ppv2bat_in0, Pbat2ac_out, Pbat2ac_out0, Ppvbs, Pbat, soc, soc0 = model.BatMod_DC(d, **kwargs)
            return Ppv2ac_out, Ppv2bat_in, Ppv2bat_in0, Pbat2ac_out, Pbat2ac_out0, Ppvbs, Pbat, soc, soc0
        elif type == 'PV':
            self.model = model.BatMod_PV(d, **kwargs)
    
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

    def get_residual_power_AC(self, parameter, ppv, pl):
        Pr, Ppv, Ppvs, Pperi = model.max_self_consumption(parameter, ppv, pl, pvmod=True)
        return Pr

    def _dict_to_array(self, parameter):
        d = model.transform_dict_to_array(parameter)
        return d

    def get_parameter(self, fparameter, system):
        return self._load_parameter(fparameter, system)

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
            parameter['P_PV'] = 5.0
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

    def E_to_csv(self, name):
        E = self.model.get_E()
        self.view.E_to_csv(name, E)

    def plot(self):
        soc = self.model.get_soc()
        Pbat = self.model.get_Pbat()
        self.view.plot(soc)
        self.view.plot(Pbat)

    def to_csv(self, name):
        soc = self.model.get_soc()
        E = self.model.get_E()
        self.view.store_to_csv(name=name, data=E)

    def dict_to_csv(self, name):
        E = self.model.get_E()
        self.view.store_dict_to_csv(name=name, data=E)

    def to_pickle(self, fname , name):
        if name == 'soc':
            soc = self.model.get_soc()
            self.view.store_to_pickle(fname=fname, data=soc)
        if name == 'Pbat':
            Pbat = self.model.get_Pbat()
            self.view.store_to_pickle(fname=fname, data=Pbat)
        if name == 'Pbs':
            Pbs = self.model.get_Pbs()
            self.view.store_to_pickle(fname=fname, data=Pbs)