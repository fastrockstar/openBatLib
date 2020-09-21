import tools
import numpy as np
import numba as nb
import pandas as pd
import time
from pyModbusTCP.client import ModbusClient
from pyModbusTCP  import utils

class BatModDC(object):
    """Performance Simulation Model for DC-coupled PV-Battery systems

    :param object: object
    :type object: object
    """
    _version = 0.1

    def __init__(self, parameter, ppv, pl, Pr, Prpv, Ppv, ppv2ac, Ppv2ac_out):
        self.parameter = parameter
        self.ppv = ppv
        self.pl = pl
        self.Pr = Pr
        self.Prpv = Prpv
        self.Ppv = Ppv
        self.ppv2ac = ppv2ac
        self.Ppv2ac_out = Ppv2ac_out

        self.simulation()
        
        self.bat_mod_res()

    def simulation(self, pvmod=True):
        '''
        TODO: 1 Warum ppv2ac doppelt
              2 Pr/Prpv anpassen
        '''
        # Initialization and preallocation
        self.Pbat = np.zeros_like(self.ppv) # DC power of the battery in W
        self.soc = np.zeros_like(self.ppv) # State of charge of the battery
        self.Ppv2bat_in = np.zeros_like(self.ppv) # Input power of the PV2BAT conversion pathway in W
        self.Pbat2ac_out = np.zeros_like(self.ppv) # Output power of the BAT2AC conversion pathway in W
        self.Ppvbs = np.zeros_like(self.ppv) # AC power of the PV-battery system in W

        self.dt = 1 # Time increment in s
        self.th = 0 # Start threshold for the recharging of the battery
        self.soc0 = 0 # State of charge of the battery in the first time step

        # Additional power consumption of other system components (e.g. AC power meter) in W
        self.Pperi = np.ones(self.ppv.size) * self.parameter['P_PERI_AC']
        
        self.Ppv2ac_out, self.Ppv2bat_in, self.Pbat2ac_out, self.Ppvbs, self.Pbat, self.soc, self.soc0 = tools.run_loss_DC(self.parameter['E_BAT'], self.parameter['P_PV2AC_in'], self.parameter['P_PV2AC_out'], self.parameter['P_PV2BAT_in'], self.parameter['P_BAT2AC_out'], self.parameter['PV2AC_a_in'], self.parameter['PV2AC_b_in'], self.parameter['PV2AC_c_in'], self.parameter['PV2BAT_a_in'], self.parameter['PV2BAT_b_in'], self.parameter['BAT2AC_a_out'], self.parameter['BAT2AC_b_out'], self.parameter['BAT2AC_c_out'], self.parameter['eta_BAT'], self.parameter['SOC_h'], self.parameter['P_PV2BAT_DEV'], self.parameter['P_BAT2AC_DEV'], round(self.parameter['t_DEAD']), self.parameter['t_CONSTANT'], self.parameter['P_SYS_SOC1_DC'], self.parameter['P_SYS_SOC0_AC'], self.parameter['P_SYS_SOC0_DC'], self.parameter['PV2AC_c_in'], int(self.ppv.size), self.soc0, self.Prpv, self.Pr, self.Ppv, self.Ppv2bat_in, self.ppv2ac, self.Ppv2ac_out, self.Pbat2ac_out, self.Ppvbs, self.Pbat, self.soc, self.dt, self.th)
        
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

class BatModAC(object):
    """Performance Simulation Model for AC-coupled PV-Battery systems

    :param object: object
    :type object: object
    """
    _version = '0.1'

    def __init__(self, parameter, ppv, pl, Pr, Pbs, Ppv, Ppvs, Pperi):
        self.parameter = parameter
        self.ppv = ppv
        self.pl = pl
        self.Pr = Pr
        self.Pbs = Pbs
        self.Ppv = Ppv
        self.Ppvs = Ppvs
        self.Pperi = Pperi

        self.simulation()
        
        self.bat_mod_res()

    def simulation(self, pvmod=True):
        ## PerModAC: Performance Simulation Model for AC-coupled PV-Battery Systems
        '''
        TODO: Preallocation verschieben
              Pr anpassen
        '''
        # # Initialization and preallocation
        self.Pbat = np.zeros_like(self.ppv) # DC power of the battery in W
        self.soc = np.zeros_like(self.ppv) # State of charge of the battery
        self.dt = 1 # Time increment in s
        self.th = 0 # Start threshold for the recharging of the battery
        self.soc0 = 0 # State of charge of the battery in the first time step

        ## 3.3 Simulation of the battery system
        self.Pbat, self.Pbs, self.soc, self.soc0 = tools.run_loss_AC(self.parameter['E_BAT'], self.parameter['eta_BAT'], self.parameter['t_CONSTANT'], self.parameter['P_SYS_SOC0_DC'], self.parameter['P_SYS_SOC0_AC'], self.parameter['P_SYS_SOC1_DC'], self.parameter['P_SYS_SOC1_AC'], self.parameter['AC2BAT_a_in'], self.parameter['AC2BAT_b_in'], self.parameter['AC2BAT_c_in'], self.parameter['BAT2AC_a_out'], self.parameter['BAT2AC_b_out'], self.parameter['BAT2AC_c_out'], self.parameter['P_AC2BAT_DEV'], self.parameter['P_BAT2AC_DEV'], self.parameter['P_BAT2AC_out'], self.parameter['P_AC2BAT_in'], round(self.parameter['t_DEAD']) , self.parameter['SOC_h'], self.dt, self.th, self.soc0, int(self.ppv.size), self.soc, self.Pr, self.Pbs, self.Pbat)

    def bat_mod_res(self):
        self.E = tools.bat_res_mod(self.parameter, self.pl, self.Ppv, self.Pbat, self.Ppvs, self.Pbs, self.Pperi) 

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
    SERVER_HOST = "192.168.208.106"
    SERVER_PORT = 1502

    c = ModbusClient()
    # uncomment this line to see debug message
    #c.debug(True)
    # define modbus server host, port
    c.host(SERVER_HOST)
    c.port(SERVER_PORT)
    c.unit_id(71)

    wert = 0

    if not c.is_open():
        if not c.open():
            print("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))

    # Read the SOC of the battery zweite nummer ist der time out in sek
    regs = c.read_holding_registers(210, 2)

    regs[1], regs[0] = regs[0], regs[1]

    if regs:
    #zwei register in ein float 
        zregs = utils.word_list_to_long(regs) 
        
        #float dekodieren
    # for i in range(0,len(zregs)):
        wert = utils.decode_ieee(*zregs)
        print(wert)
            
    #close session
    print(wert)
    c.close()



def max_self_consumption(parameter, ppv, pl, pvmod=True, max=True):

    # Maximize self consumption for AC-coupled systems
    if parameter['Top'] == 'AC':
        # Preallocation
        Pbs = np.zeros_like(ppv) # AC power of the battery system in W

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

        return Pr, Pbs, Ppv, Ppvs, Pperi
    
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

def resample_input(t, unit, input):
    if unit == 'sec':
        output = np.repeat(input, t)    
        output /= t
    
    if unit == 'min':
        output = np.repeat(input, 60*t)    
        output /= 60*t

    return output


