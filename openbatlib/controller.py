import os
import pandas as pd

from openbatlib import model
from openbatlib import view


class Error(Exception):
    pass


class InputError(Error):
    def __init__(self, expression):
        self.expression = expression


class Controller:
    """Class to manage the models and view components
    """
    _version = '0.1'

    def __init__(self):
        self.view = view.View()
        self.cwd = os.getcwd()

    def sim(self, fparameter=None, freference=None, system=None, ref_case=None, dt=1, spi=False):
        """Method for managing the simulation

        :param fparameter: File path to the system parameters
        :type fparameter: string

        :param system: Identifier for the system under simulation in the file
        :type system: string

        :param ref_case: Identifier for to chose one of the two reference cases
        :type ref_case: string

        :param dt: time step width in seconds
        :type dt: integer
        """

        if fparameter is None:
            # set path to the reference case file
            fparameter = os.path.join(self.cwd, 'parameter/PerModPAR.xlsx')

        if freference is None:   
            # set path to the reference case file
            freference = os.path.join(self.cwd, 'reference_case/ref_case_data.npz')

        try:
            # Load system parameters
            parameter = self._load_parameter(fparameter, system)
            if not parameter['ref_1'] and ref_case == '1':
                raise InputError('System not suitable with selected reference case 1!')
            if not parameter['ref_2'] and ref_case == '2':
                raise InputError('System not suitable with selected reference case 2!')

        except InputError as err:
            raise
        # Load PV generator input
        ppv = self._load_pv_input(freference, 'ppv')

        # Load data from reference cases (load and inverter parameters)
        parameter, pl = self._load_ref_case(parameter, freference, fparameter, ref_case)

        # Call model for AC coupled systems
        if parameter['Top'] == 'AC':
            d = model.transform_dict_to_array(parameter)
            self.model = model.BatModAC(parameter, d, ppv, pl, dt)
            self.model.simulation()
            self.model.bat_mod_res()
            self.model.calculate_spi()
        
        # Call model for DC coupled systems
        elif parameter['Top'] == 'DC':
            d = model.transform_dict_to_array(parameter)
            self.model = model.BatModDC(parameter, d, ppv, pl, dt)
            self.model.simulation()
            self.model.bat_mod_res()
            self.model.calculate_spi()
        
        # Call model for PV-coupled systems
        elif parameter['Top'] == 'PV':
            Pac, Ppv, Pperi = model.max_self_consumption(parameter, ppv, pl, pvmod=True)
            d = model.transform_dict_to_array(parameter)
            self.model = model.BatModPV(parameter, d, ppv, pl, Pac, Ppv, Pperi, dt)

        # Load the view class
        self.view = view.View()
    
    def modbus(self, host, port, unit_id, data_frame, ref_case, dt, fname, fparameter, fref, system):
        """Function to establish a connection to a battery system via ModBus protocol

        :param host: IP-Address of the host
        :type host: string
        :param port: Port of the host
        :type port: integer
        :param unit_id: Unit-ID of the host
        :type unit_id: integer
        :param data_frame: Data Frame holding the values
        :type data_frame: pandas data frame
        :param ref_case: Identifier for one of the two reference cases
        :type ref_case: string
        :param dt: Time step width in seconds
        :type dt: integer
        :param fname: File path to the system under simulation
        :type fname: string
        :param fparameter: File path to the system parameters
        :type fparameter: string
        :param fref: File to the refence cases
        :type fref: string
        :param system: Indentifier for the system under simulation
        :type system: string
        """
        parameter = self._load_parameter(fparameter, system)
        #df_resample = model.resample_data_frame(df=data_frame)

        ppv = data_frame['ppv'].to_numpy()
        pl = data_frame['L'].to_numpy()
        parameter, pl_not_used = self._load_ref_case(parameter, fref, fparameter, ref_case)

        Pr, Ppv_not_used, Ppvs_not_used, Pperi_not_used = model.max_self_consumption(parameter, ppv, pl, pvmod=True)

        Pr = Pr * -1 # negative values for charging, positive values for discharging

        self.model = model.ModBus(host, port, unit_id, Pr, dt, fname)

    def real_time(self, parameter, **kwargs):
        """Function for direct access to the battery models

        :param parameter: PV battery system parameters
        :type parameter: dict
        
        :return r: Dictionary of the simulation results
        :rtype r: dict
        """
        r = dict() # Dictionary storing the results
        if parameter['Top'] == 'AC':
            d = self._dict_to_array(parameter)
            r['Pbat'], r['Pbs'], r['soc'], r['soc0'], r['Pbs0'] = model.BatMod_AC(d, **kwargs)
             
            return r
        
        elif type == 'DC':
            d = self._dict_to_array(parameter)
            r['Ppv2ac_out'], r['Ppv2bat_in'], r['Ppv2bat_in0'], r['Pbat2ac_out'], r['Pbat2ac_out0'],
            r['Ppvbs'], r['Pbat'], r['soc'], r['soc0'] = model.BatMod_DC(d, **kwargs)
            
            return r
        
        elif type == 'PV':
            d = self._dict_to_array(parameter)
            r['_soc'], r['_soc0'], r['_Ppv'], r['_Ppvbs'], r['_Pbat'], r['_Ppv2ac_out'], r['_Pbat2pv_out'],
            r['_Ppv2bat_in'] = model.BatMod_PV(d, **kwargs)

            return r

    def _load_parameter(self, fparameter, system):
        """Loads system parameter

        :param fparameter: Path to file
        :type fparameter: string
        :param system: Indicator for the system
        :type system: string
        """
        parameter = model.load_parameter(fparameter, system)
        parameter = model.eta2abc(parameter)

        return parameter

    def get_residual_power_AC(self, parameter, ppv, pl):
        Pr, Ppv, Ppvs, Pperi = model.max_self_consumption(parameter, ppv, pl, pvmod=True)
        return Pr

    def _dict_to_array(self, parameter):
        return model.transform_dict_to_array(parameter)

    def get_parameter(self, fparameter, system):
        return self._load_parameter(fparameter, system)

    def _load_pv_input(self, fname, name):
        """Loads PV input data

        :param fref: Path to file
        :type fref: string
        :param name: Name of the input series
        :type name: string
        """
        return model.load_ref_case(fname, name)

    def _load_set_values(self, fname):
        return fname

    def _load_ref_case(self, parameter, fname, fparameter, ref_case):
            
        if ref_case == '1':
            # Load parameters of first inverter
            if parameter['Top'] == 'AC' or parameter['Top'] == 'PV':
                inverter_parameter = model.load_parameter(fparameter, 'L')            
            parameter['P_PV'] = 5.0
            pl = model.load_ref_case(fname, 'pl1')
                                        
        elif ref_case == '2':
            # Load paramertes of second inverter
            if parameter['Top'] == 'AC' or parameter['Top'] == 'PV':
                inverter_parameter = model.load_parameter(fparameter, 'M')            
            parameter['P_PV'] = 10
            pl = model.load_ref_case(fname, 'pl2')

        # Load inverter parameters for AC or PV coupled systems
        if parameter['Top'] == 'AC' or parameter['Top'] == 'PV':

            inverter_parameter = model.eta2abc(inverter_parameter)

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
        E_real, E_ideal = self.model.get_E()
        E_real_df = pd.DataFrame.from_dict(E_real, orient='index', columns=['real / MWh'])
        E_ideal_df = pd.DataFrame.from_dict(E_ideal, orient='index', columns=['ideal / MWh'])
        E_df = pd.concat([E_ideal_df, E_real_df], axis=1)
        print(E_df.round(4))
        
        #self.view.print_E(E_real)
        
        #self.view.print_E(E_ideal)

    def print_SPI(self):
        spi = self.model.get_SPI()
        self.view.print_SPI(spi)


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