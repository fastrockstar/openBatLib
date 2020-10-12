import tools
import numpy as np
import scipy.io as sio
import numba as nb
from numba import types
from numba.typed import Dict
from numba import njit
import pandas as pd
import time
import datetime
import csv
from pyModbusTCP.client import ModbusClient
from pyModbusTCP  import utils

class BatModDC(object):
    """Performance Simulation Model for DC-coupled PV-Battery systems

    :param object: object
    :type object: object
    """
    _version = 0.1

    def __init__(self, parameter, d, ppv, pl, Pr, Prpv, Ppv, ppv2ac, Ppv2ac_out, dt):
        self.parameter = parameter
        self.d = d
        self.ppv = ppv
        self.pl = pl
        self.Pr = Pr
        self.Prpv = Prpv
        self.Ppv = Ppv
        self.ppv2ac = ppv2ac
        self.Ppv2ac_out = Ppv2ac_out
        self.Ppv2ac_out0 = 0
        self.Ppv2bat_in0 = 0
        
        self.dt = dt
        # Initialization and preallocation
        self.Pbat = np.zeros_like(self.ppv) # DC power of the battery in W
        self.soc = np.zeros_like(self.ppv) # State of charge of the battery
        self.Ppv2bat_in = np.zeros_like(self.ppv) # Input power of the PV2BAT conversion pathway in W
        self.Pbat2ac_out = np.zeros_like(self.ppv) # Output power of the BAT2AC conversion pathway in W
        self.Pbat2ac_out0 = 0
        self.Ppvbs = np.zeros_like(self.ppv) # AC power of the PV-battery system in W

        self.th = 0 # Start threshold for the recharging of the battery
        self.soc0 = 0 # State of charge of the battery in the first time step

        # Additional power consumption of other system components (e.g. AC power meter) in W
        self.Pperi = np.ones(self.ppv.size) * self.parameter['P_PERI_AC']

        self.simulation()
        
        self.bat_mod_res()

    def simulation(self, pvmod=True):
        '''
        TODO: 1 Warum ppv2ac doppelt
              2 Pr/Prpv anpassen 
        '''

        self.Ppv2ac_out, self.Ppv2bat_in, self.Ppv2bat_in0, self.Pbat2ac_out, self.Pbat2ac_out0, self.Ppvbs, self.Pbat, self.soc, self.soc0 = run_loss_DC_test(self.d, self.dt, self.soc0, self.soc, self.Pr, self.Prpv,  self.Ppv, self.Ppv2bat_in0, self.Ppv2bat_in, self.Pbat2ac_out0, self.Pbat2ac_out, self.Ppv2ac_out0, self.Ppv2ac_out, self.Ppvbs, self.Pbat)
        
        # self.efine missing parameters
        self.Ppv2ac = self.Ppv2ac_out # AC output power of the PV2AC conversion pathway
        self.Ppv2bat = self.Ppv2bat_in # DC input power of the PV2BAT conversion pathway
               
    def bat_mod_res(self):
        self.E = tools.bat_res_mod(self.parameter, self.pl, self.Ppv, self.Pbat, self.dt, self.Ppv2ac, self.Ppv2bat, self.Ppvbs, self.Pperi)

    def get_E(self):
        return self.E

    def get_soc(self):
        '''
        idx = pd.date_range(start='00:00:00', periods=len(self.soc), freq='S')
        _soc = pd.Series(self.soc, index=idx)
        soc_1h = _soc.resample('1h').sum()
        soc_1h = soc_1h.to_numpy()
        '''
        return self.soc

    def get_Pbat(self):
        return self.Pbat

class BatModAC(object):
    """Performance Simulation Model for AC-coupled PV-Battery systems

    :param object: object
    :type object: object
    """
    _version = '0.1'

    def __init__(self, parameter, d, ppv, pl, Pr, Ppv, Ppvs, Pperi, dt):
        self.parameter = parameter
        self.d = d
        self.ppv = ppv
        self.pl = pl
        self.Pr = Pr
        self.Pbs = np.zeros_like(ppv)
        self.Ppv = Ppv
        self.Ppvs = Ppvs
        self.Pperi = Pperi
        self.dt = dt

        # # Initialization and preallocation
        self.Pbat = np.zeros_like(self.ppv) # DC power of the battery in W
        self.soc = np.zeros_like(self.ppv) # State of charge of the battery
        self.th = 0 # Start threshold for the recharging of the battery
        self.soc0 = 0 # State of charge of the battery in the first time step
        self.Pbs0 = 0

        self.simulation()

        mdic = {"Pbat_py": self.Pbat,
                "Pbs_py": self.Pbs,
                "Pr_py": self.Pr,
                "Ppvs_py": self.Ppvs,
                "Pperi_py": self.Pperi,
                'pl_py': self.pl,
                "ppv_py": self.ppv,
                "soc_py": self.soc,
                "Ppv_py": self.Ppv}
        
        sio.savemat("python_export.mat", mdic, oned_as='column')


        
        self.bat_mod_res()

        sio.savemat("python_export_E.mat", self.E, oned_as='column')

    def simulation(self, pvmod=True):
        ## PerModAC: Performance Simulation Model for AC-coupled PV-Battery Systems
        '''
        TODO: Preallocation verschieben
              Pr anpassen
        '''
        
        ## 3.3 Simulation of the battery system
        #self.Pbat, self.Pbs, self.soc, self.soc0 = run_loss_AC(self.parameter['E_BAT'], self.parameter['eta_BAT'], self.parameter['t_CONSTANT'], self.parameter['P_SYS_SOC0_DC'], self.parameter['P_SYS_SOC0_AC'], self.parameter['P_SYS_SOC1_DC'], self.parameter['P_SYS_SOC1_AC'], self.parameter['AC2BAT_a_in'], self.parameter['AC2BAT_b_in'], self.parameter['AC2BAT_c_in'], self.parameter['BAT2AC_a_out'], self.parameter['BAT2AC_b_out'], self.parameter['BAT2AC_c_out'], self.parameter['P_AC2BAT_DEV'], self.parameter['P_BAT2AC_DEV'], self.parameter['P_BAT2AC_out'], self.parameter['P_AC2BAT_in'], round(self.parameter['t_DEAD']) , self.parameter['SOC_h'], self.dt, self.th, self.soc0, int(self.ppv.size), self.soc, self.Pr, self.Pbs, self.Pbat)
        self.Pbat, self.Pbs, self.soc, self.soc0, self.Pbs0 = run_loss_AC_test(self.d, self.dt, self.soc0, self.soc, self.Pr, self.Pbs0, self.Pbs, self.Pbat)

    def bat_mod_res(self):
        self.E = tools.bat_res_mod(self.parameter, self.pl, self.Ppv, self.Pbat, self.dt, self.Ppvs, self.Pbs, self.Pperi) 

    def get_E(self):
        return self.E

    def get_soc(self):
        '''
        idx = pd.date_range(start='00:00:00', periods=len(self.soc), freq='S')
        _soc = pd.Series(self.soc, index=idx)
        soc_1h = _soc.resample('1h').sum()
        soc_1h = soc_1h.to_numpy()
        '''
        return self.soc

    def get_Pbat(self):
        return self.Pbat
    
    def get_Pbs(self):
        return self.Pbs

class BatModPV(object):
    """Performance Simulation Model for PV-coupled PV-Battery systems

    :param object: object
    :type object: object
    """
    _version = '0.1'

    def __init__(self, parameter, ppv, pl, Pac, Ppv, Pperi):
        self.parameter =  parameter
        self.ppv = ppv
        self.pl = pl 
        self.Pac = Pac
        self.Ppv = Ppv
        self.Pperi = Pperi
        '''
        self.load_sys_parameter(fparameter, system)
        self.ppv = self.load_input(fmat, 'ppv')
        
        if ref_case == '1' and self.parameter['ref_1'] or ref_case == '2' and self.parameter['ref_2']:
            self.load_ref_case(fparameter, ref_case, fmat)
        '''  
        self.simulation()
        
        self.bat_mod_res()
    '''
    def load_input(self, fname, name):
        """Loads power time series

        :param fname: Path to file
        :type fname: string
        :param name: Name of series
        :type name: string
        """
        return tools.load_mat(fname, name)
    '''
    '''
    def load_ref_case(self, fparameter, ref_case, fmat):
            
        if ref_case == '1':
            self.inverter_parameter = tools.load_parameter(fparameter, 'L')
            self.parameter['P_PV'] = 5
            self.pl = self.load_input(fmat, 'Pl1')
                                        
        if ref_case == '2':
            self.inverter_parameter = tools.load_parameter(fparameter, 'M')
            self.parameter['P_PV'] = 10
            self.pl = self.load_input(fmat, 'Pl2')
            
        self.inverter_parameter = tools.eta2abc(self.inverter_parameter)

        self.parameter['P_PV2AC_in'] = self.inverter_parameter['P_PV2AC_in']
        self.parameter['P_PV2AC_out']= self.inverter_parameter['P_PV2AC_out']
        self.parameter['P_PVINV_AC'] = self.inverter_parameter['P_PVINV_AC']

        self.parameter['PV2AC_a_in'] = self.inverter_parameter['PV2AC_a_in']
        self.parameter['PV2AC_b_in'] = self.inverter_parameter['PV2AC_b_in']
        self.parameter['PV2AC_c_in'] = self.inverter_parameter['PV2AC_c_in']
        self.parameter['PV2AC_a_out'] = self.inverter_parameter['PV2AC_a_out']
        self.parameter['PV2AC_b_out'] = self.inverter_parameter['PV2AC_b_out']
        self.parameter['PV2AC_c_out'] = self.inverter_parameter['PV2AC_c_out']
    
        self.parameter['P_SYS_SOC0_AC'] = self.inverter_parameter['P_PVINV_AC']
    '''
    '''
    def load_sys_parameter(self, fparameter, system):
        self.parameter = tools.load_parameter(fparameter, system)
        self.parameter = tools.eta2abc(self.parameter)
    '''
    def simulation(self, pvmod=True):
        ## PerModAC: Performance Simulation Model for PV-coupled PV-Battery Systems

        # Preallocation
        self.Pbat = np.zeros_like(self.ppv) # DC power of the battery in W
        self.soc = np.zeros_like(self.ppv) # State of charge of the battery
        self.Ppv2ac_out = np.zeros_like(self.ppv) # Output power of the PV2AC conversion pathway in W
        self.Ppv2bat_in = np.zeros_like(self.ppv) # Input power of the PV2BAT conversion pathway in W
        self.Pbat2pv_out = np.zeros_like(self.ppv) # Output power of the BAT2PV conversion pathway in W
        self.Ppvbs = np.zeros_like(self.ppv) # AC power of the PV-battery system in W
        #self.Pperi = np.ones_like(self.ppv) * self.parameter['P_PERI_AC'] # Additional power consumption of other system components (e.g. AC power meter) in W
        self.dt = 1 # Time increment in s
        self.th = 0 # Start threshold for the recharging of the battery
        self.soc0 = 0 # Initial state of charge of the battery in the first time step
        '''
        # DC power output of the PV generator
        if pvmod: # ppv: Normalized DC power output of the PV generator in kW/kWp
            self.Ppv = self.ppv * self.parameter['P_PV'] * 1000
            
        else: # ppv: DC power output of the PV generator in W
            self.Ppv = self.ppv
        '''
        # Power demand on the AC side
        #self.Pac = self.pl + self.Pperi

        ## Simulation of the battery system
        self.soc, self.soc0, self.Ppv, self.Ppvbs, self.Pbat, self.Ppv2ac_out, self.Pbat2pv_out, self.Ppv2bat_in = tools.run_loss_PV(self.parameter['E_BAT'], self.parameter['P_PV2AC_in'], self.parameter['P_PV2AC_out'], self.parameter['P_PV2BAT_in'], self.parameter['P_BAT2PV_out'], self.parameter['PV2AC_a_in'], self.parameter['PV2AC_b_in'], self.parameter['PV2AC_c_in'], self.parameter['PV2BAT_a_in'], self.parameter['PV2BAT_b_in'], self.parameter['PV2BAT_c_in'], self.parameter['PV2AC_a_out'], self.parameter['PV2AC_b_out'], self.parameter['PV2AC_c_out'], self.parameter['BAT2PV_a_out'], self.parameter['BAT2PV_b_out'], self.parameter['BAT2PV_c_out'], self.parameter['eta_BAT'], self.parameter['SOC_h'], self.parameter['P_PV2BAT_DEV'], self.parameter['P_BAT2AC_DEV'], self.parameter['P_SYS_SOC1_DC'], self.parameter['P_SYS_SOC0_AC'], self.parameter['P_SYS_SOC0_DC'], int(self.ppv.size), self.soc0, self.Pac, self.Ppv, self.Ppv2bat_in, self.Ppv2ac_out, self.Pbat2pv_out, self.Ppvbs, self.Pbat, self.soc, self.dt, self.th, self.parameter['t_DEAD'], self.parameter['t_CONSTANT'])

        # Define missing parameters
        self.Ppv2ac = self.Ppv2ac_out # AC output power of the PV2AC conversion pathway
        self.Ppv2bat = self.Ppv2bat_in # DC input power of the PV2BAT conversion pathway

    def bat_mod_res(self):
       self.E = tools.bat_res_mod(self.parameter, self.pl, self.Ppv, self.Pbat, self.Ppv2ac, self.Ppv2bat, self.Ppvbs, self.Pperi)

    def get_E(self):
        return self.E

    def get_soc(self):
        '''
        idx = pd.date_range(start='00:00:00', periods=len(self.soc), freq='S')
        _soc = pd.Series(self.soc, index=idx)
        soc_1h = _soc.resample('1h').sum()
        soc_1h = soc_1h.to_numpy()
        '''
        return self.soc

    def get_Pbat(self):
        return self.Pbat

class ModBus(object):
    """Establishes connection to a battery system via ModBus protocol

    :param object: object
    :type object: object
    """
    def __init__(self, host, port, unit_id, input_vals, dt, fname):
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.dt = dt
        self.input_vals = input_vals
        self.fname = fname
        self.open_connection()
        self.create_csv_file()

        self.start_loop()
    
    def open_connection(self):

        # Open ModBus connection
        try:
            self.c = ModbusClient(host=self.host, port=self.port, unit_id=self.unit_id, auto_open=True, auto_close=True)
        except ValueError:
            print("Error with host: {}, port: {} or unit-ID: {} params".format(self.host, self.port, self.unit_id))
        # Arrray for the setting values

    def start_loop(self):
        # Transform the array to fit the time duration
        self.set_vals = np.repeat(self.input_vals, self.dt * 60)
        
        i = 0
        idx = pd.date_range(start=datetime.datetime.now(), periods=(self.input_vals.size * 60), freq='S')
        print(len(idx))
        while i<len(idx):
            if datetime.datetime.now().second == idx[i].second:
                self.set_val = int(self.set_vals[i])
                if self.set_val < 0:
                    # Write negative value to battery charge power (AC) setpoint register
                    self.c.write_single_register(1024, self.set_val & 0xFFFF)
                    # Log writing time
                    self.set_time = datetime.datetime.now()
                else:
                    # Write positive value to battery charge power (AC) setpoint to register
                    self.c.write_single_register(1024, self.set_val)
                    # Log writing time
                    self.set_time = datetime.datetime.now()
                
                try:
                    # Read total AC power value from register
                    _P_ac = self.c.read_holding_registers(172, 2)
                    self.read_time_P_ac = datetime.datetime.now()
                except:
                    print('Could not read register 172!')

                try:
                    # Read actual battery charge/discharge power value from register
                    _P_bat = self.c.read_holding_registers(582, 1)
                    self.read_time_P_bat = datetime.datetime.now()
                except:
                    print('Could not read register 582!')
                        
                # Load content of two registers into a single float value
                zregs = utils.word_list_to_long(_P_ac, big_endian=False)
                # Decode and store float value of the AC-power
                self.P_ac = utils.decode_ieee(*zregs) 
                # Store the DC charging power 
                self.P_bat = np.int16(*_P_bat)
                # Read actual soc
                self.soc0 = self.read_soc(210)

                try:
                    # Save the values to a csv file
                    self.save_to_csv()
                except:
                    print('Could not save to csv!')                    
                
                i += 1
 
    def read_soc(self, reg):
        # Load the actual state fo charge of the battery
        regs = self.c.read_holding_registers(reg, 2)        
        # Load content of two registers into a single float value
        zregs = utils.word_list_to_long(regs, big_endian=False)

        return utils.decode_ieee(*zregs)

    def create_csv_file(self):
         # Create a new csv-file
         with open(self.fname, 'w') as f:
            writer = csv.writer(f, dialect='excel')
            writer.writerow(['set_time',
                             'read_time_P_ac',
                             'read_time_P_bat',
                             'soc',
                             'set_value',
                             'P_ac',
                             'P_bat']) 

    def save_to_csv(self):
        # Save the read values to a csv file
        with open(self.fname, "a") as f:
            wr = csv.writer(f, dialect='excel')
            wr.writerow([self.set_time, self.read_time_P_ac, self.read_time_P_bat, self.soc0, self.set_val, self.P_ac, self.P_bat])

def max_self_consumption(parameter, ppv, pl, pvmod=True, max=True):

    # Maximize self consumption for AC-coupled systems
    if parameter['Top'] == 'AC':
       
        # DC power output of the PV generator
        if pvmod: # ppv: Normalized DC power output of the PV generator in kW/kWp
            Ppv = np.minimum(ppv * parameter['P_PV'], parameter['P_PV2AC_in']) * 1000
        else: # ppv: DC power output of the PV generator in W
            Ppv = np.minimum(ppv, parameter['P_PV2AC_in'] * 1000)

        # Normalized input power of the PV inverter
        ppvinvin = Ppv / parameter['P_PV2AC_in'] / 1000

        # AC power output of the PV inverter taking into account the conversion losses and maximum
        # output power of the PV inverter
        Ppvs = np.minimum(np.maximum(0, Ppv-(parameter['PV2AC_a_in'] * ppvinvin * ppvinvin + parameter['PV2AC_b_in'] * ppvinvin + parameter['PV2AC_c_in'])), parameter['P_PV2AC_out'] * 1000) 
        
        ## 3.2 Residual power

        # Additional power consumption of other system components (e.g. AC power meter) in W
        Pperi = np.ones_like(ppv) * parameter['P_PERI_AC']

        # Adding the standby consumption of the PV inverter in times without any AC power output of the PV system 
        # to the additional power consumption
        Pperi[Ppvs == 0] += parameter['P_PVINV_AC'] 

        # Residual power
        Pr = Ppvs - pl - Pperi

        return Pr, Ppv, Ppvs, Pperi
    
    # Maximize self consumption for DC-coupled systems
    elif parameter['Top'] == 'DC':
        # Initialization and preallocation
        Ppv2ac_in_ac = np.zeros_like(ppv)
        Ppv = np.empty_like(ppv) # DC power output of the PV generator

        if pvmod: # ppv: Normalized DC power output of the PV generator in kW/kWp
            Ppv = ppv * parameter['P_PV'] * 1000
        else: 
            Ppv = ppv

        # DC power output of the PV generator taking into account the maximum 
        # DC input power of the PV2AC conversion pathway
        Ppv = np.minimum(Ppv, parameter['P_PV2AC_in'] * 1000)

        # Residual power

        # Power demand on the AC side
        Pac = pl + parameter['P_PERI_AC']

        # Normalized AC output power of the PV2AC conversion pathway to cover the AC
        # power demand
        ppv2ac = np.minimum(Pac, parameter['P_PV2AC_out'] * 1000) / parameter['P_PV2AC_out'] / 1000

        # Target DC input power of the PV2AC conversion pathway
        Ppv2ac_in_ac = np.minimum(Pac, parameter['P_PV2AC_out'] * 1000) + (parameter['PV2AC_a_out'] * ppv2ac**2 + parameter['PV2AC_b_out'] * ppv2ac + parameter['PV2AC_c_out'])

        # Normalized DC input power of the PV2AC conversion pathway TODO 1
        ppv2ac = Ppv / parameter['P_PV2AC_in'] / 1000
        
        # Target AC output power of the PV2AC conversion pathway
        Ppv2ac_out = np.maximum(0, Ppv - (parameter['PV2AC_a_in'] * ppv2ac**2 + parameter['PV2AC_b_in'] * ppv2ac + parameter['PV2AC_c_in'])) 
        
        # Residual power for battery charging
        Prpv = Ppv - Ppv2ac_in_ac
    
        # Residual power for battery discharging
        Pr = Ppv2ac_out - Pac

        return Pr, Prpv, Ppv, ppv2ac, Ppv2ac_out

    # Meximize self consumption for PV-coupled systems
    elif parameter['Top'] == 'PV':
        # Preallocation
        #Pbat = np.zeros_like(ppv) # DC power of the battery in W
        #soc = np.zeros_like(ppv) # State of charge of the battery
        #Ppv2ac_out = np.zeros_like(ppv) # Output power of the PV2AC conversion pathway in W
        #Ppv2bat_in = np.zeros_like(ppv) # Input power of the PV2BAT conversion pathway in W
        #Pbat2pv_out = np.zeros_like(ppv) # Output power of the BAT2PV conversion pathway in W
        #Ppvbs = np.zeros_like(ppv) # AC power of the PV-battery system in W
        Ppv = np.empty_like(ppv) # DC power output of the PV generator
        Pperi = np.ones_like(ppv) * parameter['P_PERI_AC'] # Additional power consumption of other system components (e.g. AC power meter) in W
        #dt = 1 # Time increment in s
        #th = 0 # Start threshold for the recharging of the battery
        #soc0 = 0 # State of charge of the battery in the first time step

        # DC power output of the PV generator
        if pvmod: # ppv: Normalized DC power output of the PV generator in kW/kWp
            Ppv = ppv * parameter['P_PV'] * 1000
            
        else: # ppv: DC power output of the PV generator in W
            Ppv = ppv

        # Power demand on the AC side
        Pac = pl + Pperi

        return Pac, Ppv, Pperi

@nb.jit(nopython=True)
def run_loss_AC_test(d, _dt, _soc0, _soc, _Pr, _Pbs0, _Pbs, _Pbat):
    # Loading of particular variables
    _P_AC2BAT_min = d[9] #_AC2BAT_c_in Minimum AC charging power
    _P_BAT2AC_min = d[12]#_BAT2AC_c_out Minimum AC discharging power
    _E_BAT = d[0]
    _eta_BAT = d[1]
    _t_CONSTANT = d[2]
    _P_SYS_SOC0_DC = d[3]
    _P_SYS_SOC0_AC = d[4]
    _P_SYS_SOC1_DC = d[5]
    _P_SYS_SOC1_AC = d[6]
    _AC2BAT_a_in = d[7]
    _AC2BAT_b_in = d[8]
    _AC2BAT_c_in = d[9]
    _BAT2AC_a_out = d[10]
    _BAT2AC_b_out = d[11]
    _BAT2AC_c_out = d[12]
    _P_AC2BAT_DEV = d[13]
    _P_BAT2AC_DEV = d[14]
    _P_BAT2AC_out = d[15]
    _P_AC2BAT_in = d[16]
    _t_DEAD = int(round(d[17]))
    _SOC_h = d[18]

    # Correction factor to avoid over charge and discharge the battery
    corr = 0.1

    # Initialization of particular variables
    #_P_PV2AC_min = _parameter['PV2AC_c_in'] # Minimum input power of the PV2AC conversion pathway
    _tde = _t_CONSTANT > 0 # Binary variable to activate the first-order time delay element
    _ftde = 1 - np.exp(-_dt / _t_CONSTANT) # Factor of the first-order time delay element
    # Kann and dieser Stelle auf einen Verschiebung von tstart um 2 verzichtet werden. Dann fängt t bei 0 an
    # Was ,achen die Funktonen, die auf eine vorherigen STufe zugreifen?
    _tstart = np.maximum(2, 1 + _t_DEAD) # First time step with regard to the dead time of the system control
    _tend = int(_Pr.size)
    _th = 0

    _E_BAT *= 1000 # Capacity of the battery, conversion from kWh to Wh

    _eta_BAT /= 100 # Effiency of the battery
    
    # Check if the dead or settling time can be ignored and set flags accordingly
    if _dt >= (3 * _t_CONSTANT) or _tend == 1:
        _tstart = 1
        T_DEAD = False
    else:
        T_DEAD = True

    if _dt >= _t_DEAD + 3 * _t_CONSTANT:
        SETTLING = False
    else:
        SETTLING = True
    

    for t in range(_tstart - 1, _tend):

        # Energy content of the battery in the previous time step
        E_b0 = _soc0 * _E_BAT
        
        # Calculate the AC power of the battery system from the residual power
        # with regard to the dead time of the system control
        if T_DEAD:
            P_bs = _Pr[t - _t_DEAD]
        else:
            P_bs = _Pr[t]
        
        # Check if the battery holds enough unused capacity for charging or discharging
        # Estimated amount of energy in Wh that is supplied to or discharged from the storage unit.
        E_bs_est = P_bs * _dt / 3600
        
        # Reduce P_bs to avoid over charging of the battery
        if E_bs_est > 0 and E_bs_est > (_E_BAT - E_b0):
            P_bs = (_E_BAT - E_b0) / _dt * 3600
        # When charging take the correction factor into account
        elif E_bs_est < 0 and np.abs(E_bs_est) > (E_b0):
            P_bs = (E_b0) / _dt * 3600 * (1-corr)
        
        # Adjust the AC power of the battery system due to the stationary 
        # deviations taking the minimum charging and discharging power into
        # account
        if P_bs > _P_AC2BAT_min:
            P_bs = np.maximum(_P_AC2BAT_min, P_bs + _P_AC2BAT_DEV)
            
        elif P_bs < -_P_BAT2AC_min:
            P_bs = np.minimum(-_P_BAT2AC_min, P_bs - _P_BAT2AC_DEV)
            
        else:
            P_bs = 0
        
        # Limit the AC power of the battery system to the rated power of the
        # battery converter
        P_bs = np.maximum(-_P_BAT2AC_out * 1000, np.minimum(_P_AC2BAT_in * 1000, P_bs))

        # Adjust the AC power of the battery system due to the settling time
        # (modeled by a first-order time delay element) Hier hat der Schritt vorher eine Null?
        # Muss der vorherige Wert mit übergeben werden?
        if SETTLING:
            if t > 0:
                P_bs = _tde * _Pbs[t-1] + _tde * (P_bs - _Pbs[t-1]) * _ftde + P_bs * (not _tde)
            else:
                P_bs = _tde * _Pbs0 + _tde * (P_bs - _Pbs0) * _ftde + P_bs * (not _tde)
        
        # Decision if the battery should be charged or discharged
        if P_bs > 0 and _soc0 < 1 - _th * (1 - _SOC_h):
            # The last term th*(1-SOC_h) avoids the alternation between
            # charging and standby mode due to the DC power consumption of the
            # battery converter when the battery is fully charged. The battery
            # will not be recharged until the SOC falls below the SOC-threshold
            # (SOC_h) for recharging from PV.
            
            # Normalized AC power of the battery system
            p_bs = P_bs / _P_AC2BAT_in / 1000
            
            # DC power of the battery affected by the AC2BAT conversion losses
            # of the battery converter
            P_bat = np.maximum(0, P_bs - (_AC2BAT_a_in * p_bs * p_bs + _AC2BAT_b_in * p_bs + _AC2BAT_c_in))
            
        elif P_bs < 0 and _soc0 > 0:
            
            # Normalized AC power of the battery system
            p_bs = np.abs(P_bs / _P_BAT2AC_out / 1000)
            
            # DC power of the battery affected by the BAT2AC conversion losses
            # of the battery converter
            P_bat = P_bs - (_BAT2AC_a_out * p_bs * p_bs + _BAT2AC_b_out * p_bs + _BAT2AC_c_out)

        else: # Neither charging nor discharging of the battery
            
            # Set the DC power of the battery to zero
            P_bat = 0
        
        # Decision if the standby mode is active
        if P_bat == 0 and _soc0 <= 0: # Standby mode in discharged state
            
            # DC and AC power consumption of the battery converter
            P_bat = -np.maximum(0, _P_SYS_SOC0_DC)
            P_bs = _P_SYS_SOC0_AC
                
        elif P_bat == 0 and _soc0 > 0: # Standby mode in fully charged state
            
            # DC and AC power consumption of the battery converter
            P_bat = -np.maximum(0, _P_SYS_SOC1_DC)
            P_bs = _P_SYS_SOC1_AC
    
        # Transfer the realized AC power of the battery system and 
        # the DC power of the battery
        _Pbs[t] = P_bs
        _Pbs0 = P_bs
        _Pbat[t] = P_bat
        
        # Change the energy content of the battery from Ws to Wh conversion
        if P_bat > 0:
            E_b = E_b0 + P_bat * np.sqrt(_eta_BAT) * _dt / 3600
        
        elif P_bat < 0:
            E_b = E_b0 + P_bat / np.sqrt(_eta_BAT) * _dt / 3600
        
        else:
            E_b = E_b0
        
        # Calculate the state of charge of the battery
        _soc0 = E_b / (_E_BAT)
        _soc[t] = _soc0
        
        # Adjust the hysteresis threshold to avoid alternation
        # between charging and standby mode due to the DC power
        # consumption of the battery converter.
        if _th and _soc[t] > _SOC_h or _soc[t] > 1:
            _th = True
        else:
            _th = False 

    return _Pbat, _Pbs, _soc, _soc0, _Pbs0

@nb.jit(nopython=True)
def run_loss_DC_test(d, _dt, _soc0, _soc, _Pr, _Prpv,  _Ppv, _Ppv2bat_in0, _Ppv2bat_in, _Pbat2ac_out0, _Pbat2ac_out, _Ppv2ac_out0, _Ppv2ac_out, _Ppvbs, _Pbat):
    '''
    TODO 1 t_start auf das 2. Element?
    '''

    _E_BAT = d[0]
    _P_PV2AC_in = d[1]
    _P_PV2AC_out = d[2]
    _P_PV2BAT_in = d[3]
    _P_BAT2AC_out = d[4]
    _PV2AC_a_in = d[5]
    _PV2AC_b_in = d[6]
    _PV2AC_c_in = d[7]
    _PV2BAT_a_in = d[8]
    _PV2BAT_b_in = d[9]
    _BAT2AC_a_out = d[10]
    _BAT2AC_b_out = d[11]
    _BAT2AC_c_out = d[12]
    _eta_BAT = d[13]
    _SOC_h = d[14]
    _P_PV2BAT_DEV = d[15]
    _P_BAT2AC_DEV = d[16]
    _t_DEAD = int(round(d[17]))
    _t_CONSTANT = d[18]
    _P_SYS_SOC1_DC = d[19]
    _P_SYS_SOC0_AC = d[20]
    _P_SYS_SOC0_DC = d[21]
    _P_PV2AC_min = _PV2AC_c_in

    _E_BAT *= 1000
    _P_PV2AC_out *= 1000
    _eta_BAT /= 100

    # Initialization of particular variables
    #_P_PV2AC_min = _parameter['PV2AC_c_in'] # Minimum input power of the PV2AC conversion pathway
    _tde = _t_CONSTANT > 0 # Binary variable to activate the first-order time delay element
    _ftde = 1 - np.exp(-_dt / _t_CONSTANT) # Factor of the first-order time delay element
    _tstart = np.maximum(2, 1 + _t_DEAD) # First time step with regard to the dead time of the system control
    _tend = int(_Pr.size)
    _th = 0
    corr = 0.1

    # Check if the dead or settling time can be ignored and set flags accordingly
    if _dt >= (3 * _t_CONSTANT) or _tend == 1:
        _tstart = 1
        T_DEAD = False
    else:
        T_DEAD = True

    if _dt >= _t_DEAD + 3 * _t_CONSTANT:
        SETTLING = False
    else:
        SETTLING = True


    for t in range(_tstart -1, _tend):
        # Energy content of the battery in the previous time step
        E_b0 = _soc0 * _E_BAT

        # Residual power with regard to the dead time of the system control
        
        if T_DEAD:
            P_rpv = _Prpv[t - _t_DEAD] 
            P_r = _Pr[t - _t_DEAD]

        else:
            P_rpv = _Prpv[t] 
            P_r = _Pr[t]

        # Check if the battery holds enough unused capacity for charging or discharging
        # Estimated amount of energy that is supplied to or discharged from the storage unit.
        E_bs_rpv = P_rpv * _dt / 3600
        E_bs_r = P_r * _dt / 3600
        
        if E_bs_rpv > 0 and E_bs_rpv > (_E_BAT - E_b0):
            P_rpv = (_E_BAT - E_b0) / _dt * 3600
        # wenn Laden, dann neue Ladeleistung inkl. Korrekturfaktor
        elif E_bs_r < 0 and np.abs(E_bs_r) > (E_b0):
            P_r = (E_b0) / _dt * 3600 * (1-corr)
        
        # Decision if the battery should be charged or discharged
        if P_rpv > 0 and _soc0 < 1 - _th * (1 - _SOC_h):
            '''
            The last term th*(1-SOC_h) avoids the alternation between
            charging and standby mode due to the DC power consumption of the
            battery converter when the battery is fully charged. The battery
            will not be recharged until the SOC falls below the SOC-threshold
            (SOC_h) for recharging from PV.
            '''
            # Charging power
            P_pv2bat_in = P_rpv
            
            # Adjust the charging power due to the stationary deviations
            P_pv2bat_in = np.maximum(0, P_pv2bat_in + _P_PV2BAT_DEV)
            
            # Limit the charging power to the maximum charging power
            P_pv2bat_in = np.minimum(P_pv2bat_in, _P_PV2BAT_in * 1000)
            
            # Adjust the charging power due to the settling time
            # (modeled by a first-order time delay element)
            if SETTLING:
                if t > 0:
                    P_pv2bat_in = _tde * _Ppv2bat_in[(t-1)] + _tde * (P_pv2bat_in - _Ppv2bat_in[(t-1)]) * _ftde + P_pv2bat_in * (not _tde)
                else:
                    P_pv2bat_in = _tde * _Ppv2bat_in0 + _tde * (P_pv2bat_in - _Ppv2bat_in0) * _ftde + P_pv2bat_in * (not _tde)
            # Limit the charging power to the current power output of the PV generator
            P_pv2bat_in = np.minimum(P_pv2bat_in, _Ppv[t])
            
            # Normalized charging power
            ppv2bat = P_pv2bat_in / _P_PV2BAT_in / 1000
            
            # DC power of the battery affected by the PV2BAT conversion losses
            # (the idle losses of the PV2BAT conversion pathway are not taken
            # into account)
            P_bat = np.maximum(0, P_pv2bat_in - (_PV2BAT_a_in * ppv2bat**2 + _PV2BAT_b_in * ppv2bat))
            
            # Realized DC input power of the PV2AC conversion pathway
            P_pv2ac_in = _Ppv[t] - P_pv2bat_in
            
            # Normalized DC input power of the PV2AC conversion pathway
            _ppv2ac = P_pv2ac_in / _P_PV2AC_in / 1000
            
            # Realized AC power of the PV-battery system
            P_pv2ac_out = np.maximum(0, P_pv2ac_in - (_PV2AC_a_in * _ppv2ac**2 + _PV2AC_b_in * _ppv2ac + _PV2AC_c_in))
            P_pvbs = P_pv2ac_out
            
            # Transfer the final values
            _Ppv2ac_out[t] = P_pv2ac_out
            _Ppv2bat_in0 = P_pv2bat_in
            _Ppv2bat_in[t] = P_pv2bat_in

        elif P_rpv < 0 and _soc0 > 0: 

            # Discharging power
            P_bat2ac_out = P_r * -1
            
            # Adjust the discharging power due to the stationary deviations
            P_bat2ac_out = np.maximum(0, P_bat2ac_out + _P_BAT2AC_DEV)
            
            # Adjust the discharging power to the maximum discharging power
            P_bat2ac_out = np.minimum(P_bat2ac_out, _P_BAT2AC_out * 1000)
            
            # Adjust the discharging power due to the settling time
            # (modeled by a first-order time delay element)
            if SETTLING:
                if t > 0:
                    P_bat2ac_out = _tde * _Pbat2ac_out[t-1] + _tde * (P_bat2ac_out - _Pbat2ac_out[t-1]) * _ftde + P_bat2ac_out * (not _tde)
                else:
                    P_bat2ac_out = _tde * _Pbat2ac_out0 + _tde * (P_bat2ac_out - _Pbat2ac_out0) * _ftde + P_bat2ac_out * (not _tde)
            # Limit the discharging power to the maximum AC power output of the PV-battery system
            P_bat2ac_out = np.minimum(_P_PV2AC_out - _Ppv2ac_out[t], P_bat2ac_out)
            
            # Normalized discharging power
            ppv2bat = P_bat2ac_out / _P_BAT2AC_out / 1000
            
            # DC power of the battery affected by the BAT2AC conversion losses
            # (if the idle losses of the PV2AC conversion pathway are covered by
            # the PV generator, the idle losses of the BAT2AC conversion pathway
            # are not taken into account)
            if _Ppv[t] > _P_PV2AC_min:
                P_bat= -1 * (P_bat2ac_out + (_BAT2AC_a_out * ppv2bat**2 + _BAT2AC_b_out * ppv2bat))
            else:
                P_bat = -1 * (P_bat2ac_out + (_BAT2AC_a_out * ppv2bat**2 + _BAT2AC_b_out * ppv2bat + _BAT2AC_c_out)) + _Ppv[t]
            
                    
            # Realized AC power of the PV-battery system
            P_pvbs = _Ppv2ac_out[t] + P_bat2ac_out
            
            # Transfer the final values
            _Pbat2ac_out0 = P_bat2ac_out
            _Pbat2ac_out[t] = P_bat2ac_out

        else: # Neither charging nor discharging of the battery

            # Set the DC power of the battery to zero
            P_bat = 0
        
            # Realized AC power of the PV-battery system
            P_pvbs = _Ppv2ac_out[t]

        
        # Decision if the standby mode is active
        if P_bat == 0 and P_pvbs == 0 and _soc0 <= 0: # Standby mode in discharged state

            # DC and AC power consumption of the PV-battery inverter
            P_bat = -np.maximum(0, _P_SYS_SOC0_DC)
            P_pvbs = -_P_SYS_SOC0_AC

        elif P_bat == 0 and P_pvbs > 0 and _soc0 > 0: # Standby mode in fully charged state

            # DC power consumption of the PV-battery inverter
            P_bat = -np.maximum(0, _P_SYS_SOC1_DC)

        
        # Transfer the realized AC power of the PV-battery system and the DC power of the battery
        _Ppvbs[t] = P_pvbs
        _Pbat[t] = P_bat
        
        # Change the energy content of the battery Wx to Wh conversion
        if P_bat > 0:
            E_b = E_b0 + P_bat * np.sqrt(_eta_BAT) * _dt / 3600
        elif P_bat < 0:
            E_b = E_b0 + P_bat / np.sqrt(_eta_BAT) * _dt / 3600
        else:
            E_b = E_b0
                    
        # Calculate the state of charge of the battery
        _soc0 = E_b / _E_BAT
        _soc[t] = _soc0

        # Adjust the hysteresis threshold to avoid alternation between charging
        # and standby mode due to the DC power consumption of the
        # PV-battery inverter
        if _th and _soc[t] > _SOC_h or _soc[t] > 1:
            _th = True
        else:
            _th = False 

    return _Ppv2ac_out, _Ppv2bat_in, _Ppv2bat_in0, _Pbat2ac_out, _Pbat2ac_out0, _Ppvbs, _Pbat, _soc, _soc0

def transform_dict_to_array(parameter):
    # 
    if parameter['Top'] == 'AC':
        d = np.array(parameter['E_BAT'])                # 0
        d = np.append(d, parameter['eta_BAT'])          # 1        
        d = np.append(d, parameter['t_CONSTANT'])       #  2       
        d = np.append(d, parameter['P_SYS_SOC0_DC'])    #   3          
        d = np.append(d, parameter['P_SYS_SOC0_AC'])    #    4         
        d = np.append(d, parameter['P_SYS_SOC1_DC'])    #     5        
        d = np.append(d, parameter['P_SYS_SOC1_AC'])    #      6       
        d = np.append(d, parameter['AC2BAT_a_in'])      #       7  
        d = np.append(d, parameter['AC2BAT_b_in'])      #        8 
        d = np.append(d, parameter['AC2BAT_c_in'])      #         9
        d = np.append(d, parameter['BAT2AC_a_out'])     #          10   
        d = np.append(d, parameter['BAT2AC_b_out'])     #            11 
        d = np.append(d, parameter['BAT2AC_c_out'])     #             12
        d = np.append(d, parameter['P_AC2BAT_DEV'])     #             13
        d = np.append(d, parameter['P_BAT2AC_DEV'])     #             14
        d = np.append(d, parameter['P_BAT2AC_out'])     #             15
        d = np.append(d, parameter['P_AC2BAT_in'])      #         16
        d = np.append(d, parameter['t_DEAD'])           #     17
        d = np.append(d, parameter['SOC_h'])            #     18
    
    if parameter['Top'] == 'DC':
        d = np.array(parameter['E_BAT'])             #1
        d = np.append(d, parameter['P_PV2AC_in'])      #2       
        d = np.append(d, parameter['P_PV2AC_out'])      #3       
        d = np.append(d, parameter['P_PV2BAT_in'])       # 4     
        d = np.append(d, parameter['P_BAT2AC_out'])       # 5     
        d = np.append(d, parameter['PV2AC_a_in'])          # 6  
        d = np.append(d, parameter['PV2AC_b_in'])           # 7 
        d = np.append(d, parameter['PV2AC_c_in'])            # 8
        d = np.append(d, parameter['PV2BAT_a_in'])            # 9
        d = np.append(d, parameter['PV2BAT_b_in'])             #10
        d = np.append(d, parameter['BAT2AC_a_out'])             #11
        d = np.append(d, parameter['BAT2AC_b_out'])             #12
        d = np.append(d, parameter['BAT2AC_c_out'])             #13
        d = np.append(d, parameter['eta_BAT'])             #14
        d = np.append(d, parameter['SOC_h'])             #15
        d = np.append(d, parameter['P_PV2BAT_DEV'])       # 16     
        d = np.append(d, parameter['P_BAT2AC_DEV'])        #  17   
        d = np.append(d, parameter['t_DEAD'])             #18
        d = np.append(d, parameter['t_CONSTANT'])          # 19  
        d = np.append(d, parameter['P_SYS_SOC1_DC'])        #  20   
        d = np.append(d, parameter['P_SYS_SOC0_AC'])         #   21 
        d = np.append(d, parameter['P_SYS_SOC0_DC'])          #   22
           
    return d

# Hier eine Kopie der Schleifen aus tools anlegen als eigene Klassen mit bestimmten Übergabe Paramtern? Was braucht die Schleife unbedingt für Werte
# Dies sind Pr, Pbs, soc0, und parameter aus der Excel Datei. Geht dies mit numba? Ist numba noch nötig, da nur ein Durchlauf passiert? Dann kan auch ohne Probleme ein Dict
# übergeben werden. Dies wird dann in der Schleife ausgelesen.
# Eigene KLasse anlegen real_time die auf tools zugreift, so wie die Simulationen? Wie mit den Parametern umgehen?
# Der Weg Aufruf durch die Main -> Conrol -> Aufruf des Models -> zurück an die Control -> Aufrufen der View -> sichern als Data Frame return. Welcher Inhalt. soc Pbat Pbs usw.
# soc0 ist ein eigener Wert. auslesen aus dem letzten soc?
# Danach ein erneuter Aufruf mit dem gleichen Data Frame, die neuen Werte werden angehängt
# Oder doch nur Pbs übergeben, so dass das Modul si durchlaufen kann? Also auf Pr etc. verzichten. Im ersten Durchlauf ist auch Pbs noch 0.
# Für das Dc MOdell müssen andere Parameter übergeben werden, hier gibt es eine eigene Leistung zum Laden Pr und Prpv und Entladen der Batterie.
# Hier werden auch Pbat und Pbs zurück gegeben