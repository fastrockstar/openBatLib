import tools
import numpy as np
import numba as nb
import time

class BatModDC(object):
    """Performance Simulation Model for DC-coupled PV-Battery systems

    :param object: object
    :type object: object
    """
    _version = 0.1

    def __init__(self, fparameter, fmat, system, ref_case):
        self.load_sys_parameter(fparameter, system)
        self.ppv = self.load_input(fmat, 'ppv')
        
        if ref_case == '1' and self.parameter['ref_1'] or ref_case == '2' and self.parameter['ref_2']:
            self.load_ref_case(fparameter, ref_case, fmat)

        self.simulation_loss()
        
        self.bat_mod_res()

    def load_input(self, fname, name):
        """Loads power time series

        :param fname: Path to file
        :type fname: string
        :param name: Name of series
        :type name: string
        """
        return tools.load_mat(fname, name)

    def load_ref_case(self, fparameter, ref_case, fmat):
        
        if ref_case == '1':
            self.parameter['P_PV'] = 5
            self.pl = self.load_input(fmat, 'Pl1')
        
        elif ref_case == '2':
            self.parameter['P_PV'] = 10
            self.pl = self.load_input(fmat, 'Pl2')

    def load_sys_parameter(self, fparameter, system):
        self.parameter = tools.load_parameter(fparameter, system)
        self.parameter = tools.eta2abc(self.parameter)
    
    def simulation_ideal(self, pvmod=True):
        # Preallocation
        self.Pbat = np.zeros_like(self.ppv) # DC power of the battery in W
        self.soc = np.zeros_like(self.ppv) # State of charge of the battery
        self.Ppv2bat_in = np.zeros_like(self.ppv) # Input power of the PV2BAT conversion pathway in W
        self.Pbat2ac_out = np.zeros_like(self.ppv) # Output power of the BAT2AC conversion pathway in W
        self.Ppvbs = np.zeros_like(self.ppv) # AC power of the PV-battery system in W
        self.Ppv = np.empty_like(self.ppv) # DC power output of the PV generator
        self.Pr = np.empty_like(self.ppv) # Residual power
        self.Pperi = np.zeros_like(self.ppv) # Additional power consumption of other system components

        self.dt = 1 # Time increment in s
        self.th = 0 # Start threshold for the recharging of the battery
        self.soc0 = 0 # State of charge of the battery in the first time step
        
        # DC power output of the PV generator
        if pvmod:
            # ppv: Normalized DC power output of the PV generator in kW/kWp
            self.Ppv = np.maximum(0, self.ppv) * self.parameter['P_PV'] * 1000
        else:
            # ppv: DC power output of the PV generator in W
            self.Ppv = np.maximum(0, self.ppv) * self.parameter['P_PV']
        
        # Residual power
        self.Pr = self.Ppv - self.pl 

        # Start of the time step simulation
        self.soc0, self.Pbat, self.soc = tools.run_ideal_DC(int(self.ppv.size), self.soc0, self.parameter['E_BAT'], self.Pr, self.dt, self.Pbat, self.soc)
        
        print(np.mean(self.soc))
        print(np.mean(self.Pbat))

        self.Ppvbs = self.Ppv - np.maximum(0, self.Pbat) - (np.minimum(0, self.Pbat)) # Realized AC power of the PV-battery system
        self.Ppv2ac = self.Ppv - np.maximum(0, self.Pbat) # AC output power of the PV2AC conversion pathway
        self.Ppv2bat = np.maximum(0, self.Pbat) # DC input power of the PV2BAT conversion pathway

    def simulation_loss(self, pvmod=True):
        '''
        TODO: 1 Warum ppv2ac doppelt
              2 Pr/Prpv anpassen
        '''
        # Initialization and preallocation
        self.Pbat = np.zeros_like(self.ppv) # DC power of the battery in W
        self.soc = np.zeros_like(self.ppv) # State of charge of the battery
        self.Ppv2bat_in = np.zeros_like(self.ppv) # Input power of the PV2BAT conversion pathway in W
        self.Pbat2ac_out = np.zeros_like(self.ppv) # Output power of the BAT2AC conversion pathway in W
        self.Ppv2ac_in_ac = np.zeros_like(self.ppv)
        self.Ppvbs = np.zeros_like(self.ppv) # AC power of the PV-battery system in W
        self.Ppv = np.empty_like(self.ppv) # DC power output of the PV generator

        self.dt = 1 # Time increment in s
        self.th = 0 # Start threshold for the recharging of the battery
        self.soc0 = 0 # State of charge of the battery in the first time step

        if pvmod: # ppv: Normalized DC power output of the PV generator in kW/kWp
            self.Ppv = self.ppv * self.parameter['P_PV'] * 1000
        else: 
            self.Ppv = self.ppv
        
        # DC power output of the PV generator taking into account the maximum 
        # DC input power of the PV2AC conversion pathway
        self.Ppv = np.minimum(self.Ppv, self.parameter['P_PV2AC_in'] * 1000)

        # Residual power

        # Additional power consumption of other system components (e.g. AC power meter) in W
        self.Pperi = np.ones(self.ppv.size) * self.parameter['P_PERI_AC']

        # Power demand on the AC side
        self.Pac = self.pl + self.parameter['P_PERI_AC']

        # Normalized AC output power of the PV2AC conversion pathway to cover the AC
        # power demand
        self.ppv2ac = np.minimum(self.Pac, self.parameter['P_PV2AC_out'] * 1000) / self.parameter['P_PV2AC_out'] / 1000

        # Target DC input power of the PV2AC conversion pathway
        self.Ppv2ac_in_ac = np.minimum(self.Pac, self.parameter['P_PV2AC_out'] * 1000) + (self.parameter['PV2AC_a_out'] * self.ppv2ac ** 2 + self.parameter['PV2AC_b_out'] * self.ppv2ac + self.parameter['PV2AC_c_out'])

        # Normalized DC input power of the PV2AC conversion pathway TODO 1
        self.ppv2ac = self.Ppv / self.parameter['P_PV2AC_in'] / 1000
        
        # Target AC output power of the PV2AC conversion pathway
        self.Ppv2ac_out = np.maximum(0, self.Ppv - (self.parameter['PV2AC_a_in'] * self.ppv2ac ** 2 + self.parameter['PV2AC_b_in'] * self.ppv2ac + self.parameter['PV2AC_c_in'])) 
        
        # Residual power for battery charging
        self.Prpv = self.Ppv - self.Ppv2ac_in_ac
        
        # Residual power for battery discharging
        self.Pr = self.Ppv2ac_out - self.Pac

        # Simulation of the PV-battery system
        # Initialization of particular variables        
        
        self.Ppv2ac_out, self.Ppv2bat_in, self.Pbat2ac_out, self.Ppvbs, self.Pbat, self.soc, self.soc0 = tools.run_loss_DC(self.parameter['E_BAT'], self.parameter['P_PV2AC_in'], self.parameter['P_PV2AC_out'], self.parameter['P_PV2BAT_in'], self.parameter['P_BAT2AC_out'], self.parameter['PV2AC_a_in'], self.parameter['PV2AC_b_in'], self.parameter['PV2AC_c_in'], self.parameter['PV2BAT_a_in'], self.parameter['PV2BAT_b_in'], self.parameter['BAT2AC_a_out'], self.parameter['BAT2AC_b_out'], self.parameter['BAT2AC_c_out'], self.parameter['eta_BAT'], self.parameter['SOC_h'], self.parameter['P_PV2BAT_DEV'], self.parameter['P_BAT2AC_DEV'], round(self.parameter['t_DEAD']), self.parameter['t_CONSTANT'], self.parameter['P_SYS_SOC1_DC'], self.parameter['P_SYS_SOC0_AC'], self.parameter['P_SYS_SOC0_DC'], self.parameter['PV2AC_c_in'], int(self.ppv.size), self.soc0, self.Prpv, self.Pr, self.Ppv, self.Ppv2bat_in, self.ppv2ac, self.Ppv2ac_out, self.Pbat2ac_out, self.Ppvbs, self.Pbat, self.soc, self.dt, self.th)
        
        print('Ppv2ac_out = ', np.mean(self.Ppv2ac_out))
        print('Ppv2bat_in = ', np.mean(self.Ppv2bat_in))
        print('Pbat2ac_out = ', np.mean(self.Pbat2ac_out))
        print('Ppvbs = ', np.mean(self.Ppvbs))
        print('Pbat = ', np.mean(self.Pbat))
        print('soc = ', np.mean(self.soc))

        # Define missing parameters
        self.Ppv2ac = self.Ppv2ac_out # AC output power of the PV2AC conversion pathway
        self.Ppv2bat = self.Ppv2bat_in # DC input power of the PV2BAT conversion pathway
               
    def bat_mod_res(self):
       self.E = tools.bat_res_mod(self.parameter, self.pl, self.Ppv, self.Pbat, self.Ppv2ac, self.Ppv2bat, self.Ppvbs, self.Pperi)

class BatModAC(object):
    """Performance Simulation Model for AC-coupled PV-Battery systems

    :param object: object
    :type object: object
    """
    _version = '0.1'

    def __init__(self, fparameter, fmat, system, ref_case, losses=False):
        self.load_sys_parameter(fparameter, system)
        self.ppv = self.load_input(fmat, 'ppv')
        
        if ref_case == '1' and self.parameter['ref_1'] or ref_case == '2' and self.parameter['ref_2']:
            self.load_ref_case(fparameter, ref_case, fmat)
        
        self.simulation_loss()
        
        self.bat_mod_res()

        print(' ')

    def load_input(self, fname, name):
        """Loads power time series

        :param fname: Path to file
        :type fname: string
        :param name: Name of series
        :type name: string
        """
        return tools.load_mat(fname, name)

    def load_ref_case(self, fparameter, ref_case, fmat):
            
        if ref_case == '1':
            self.inverter_parameter = tools.load_parameter(fparameter, 'L')
            self.parameter['P_PV'] = 5
            self.pl = self.load_input(fmat, 'Pl1')
                                        
        elif ref_case == '2':
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
    
    def load_sys_parameter(self, fparameter, system):
        self.parameter = tools.load_parameter(fparameter, system)
        self.parameter = tools.eta2abc(self.parameter)

    def simulation_loss(self, pvmod=True):
        ## PerModAC: Performance Simulation Model for AC-coupled PV-Battery Systems
        '''
        TODO: Preallocation verschieben
              Pr anpassen
        '''
        # Preallocation
        self.Pbs = np.zeros_like(self.ppv) # AC power of the battery system in W
        self.Pbat = np.zeros_like(self.ppv) # DC power of the battery in W
        self.soc = np.zeros_like(self.ppv) # State of charge of the battery
        self.dt = 1 # Time increment in s
        self.th = 0 # Start threshold for the recharging of the battery
        self.soc0 = 0 # State of charge of the battery in the first time step

        # DC power output of the PV generator
        if pvmod: # ppv: Normalized DC power output of the PV generator in kW/kWp
            self.Ppv = np.minimum(self.ppv * self.parameter['P_PV'], self.parameter['P_PV2AC_in']) * 1000
            
        else: # ppv: DC power output of the PV generator in W
            self.Ppv = np.minimum(self.ppv, self.parameter['P_PV2AC_in'] * 1000)

        # Normalized input power of the PV inverter
        self.ppvinvin = self.Ppv / self.parameter['P_PV2AC_in'] / 1000

        # AC power output of the PV inverter taking into account the conversion losses and maximum
        # output power of the PV inverter
        self.Ppvs = np.minimum(np.maximum(0, self.Ppv-(self.parameter['PV2AC_a_in'] * self.ppvinvin * self.ppvinvin + self.parameter['PV2AC_b_in'] * self.ppvinvin + self.parameter['PV2AC_c_in'])), self.parameter['P_PV2AC_out'] * 1000) 

        ## 3.2 Residual power

        # Additional power consumption of other system components (e.g. AC power meter) in W
        self.Pperi = np.ones_like(self.ppv) * self.parameter['P_PERI_AC']

        # Adding the standby consumption of the PV inverter in times without any AC power output of the PV system 
        # to the additional power consumption
        self.Pperi[self.Ppvs == 0] += self.parameter['P_PVINV_AC'] 

        # Residual power
        self.Pr = self.Ppvs - self.pl - self.Pperi

        ## 3.3 Simulation of the battery system
        self.Pbat, self.Pbs, self.soc, self.soc0 = tools.run_loss_AC(self.parameter['E_BAT'], self.parameter['eta_BAT'], self.parameter['t_CONSTANT'], self.parameter['P_SYS_SOC0_DC'], self.parameter['P_SYS_SOC0_AC'], self.parameter['P_SYS_SOC1_DC'], self.parameter['P_SYS_SOC1_AC'], self.parameter['AC2BAT_a_in'], self.parameter['AC2BAT_b_in'], self.parameter['AC2BAT_c_in'], self.parameter['BAT2AC_a_out'], self.parameter['BAT2AC_b_out'], self.parameter['BAT2AC_c_out'], self.parameter['P_AC2BAT_DEV'], self.parameter['P_BAT2AC_DEV'], self.parameter['P_BAT2AC_out'], self.parameter['P_AC2BAT_in'], round(self.parameter['t_DEAD']) , self.parameter['SOC_h'], self.dt, self.th, self.soc0, int(self.ppv.size), self.soc, self.Pr, self.Pbs, self.Pbat)

    def bat_mod_res(self):
        self.E = tools.bat_res_mod(self.parameter, self.pl, self.Ppv, self.Pbat, self.Ppvs, self.Pbs, self.Pperi) 

class BatModPV(object):
    """Performance Simulation Model for PV-coupled PV-Battery systems

    :param object: object
    :type object: object
    """
    _version = '0.1'

    def __init__(self, fparameter, fmat, system, ref_case, losses=False):
        self.load_sys_parameter(fparameter, system)
        self.ppv = self.load_input(fmat, 'ppv')
        
        if ref_case == '1' and self.parameter['ref_1'] or ref_case == '2' and self.parameter['ref_2']:
            self.load_ref_case(fparameter, ref_case, fmat)
          
        self.simulation_loss()
        
        self.bat_mod_res()

    def load_input(self, fname, name):
        """Loads power time series

        :param fname: Path to file
        :type fname: string
        :param name: Name of series
        :type name: string
        """
        return tools.load_mat(fname, name)

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

    def load_sys_parameter(self, fparameter, system):
        self.parameter = tools.load_parameter(fparameter, system)
        self.parameter = tools.eta2abc(self.parameter)

    def simulation_loss(self, pvmod=True):
        ## PerModAC: Performance Simulation Model for PV-coupled PV-Battery Systems

        # Preallocation
        self.Pbat = np.zeros_like(self.ppv) # DC power of the battery in W
        self.soc = np.zeros_like(self.ppv) # State of charge of the battery
        self.Ppv2ac_out = np.zeros_like(self.ppv) # Output power of the PV2AC conversion pathway in W
        self.Ppv2bat_in = np.zeros_like(self.ppv) # Input power of the PV2BAT conversion pathway in W
        self.Pbat2pv_out = np.zeros_like(self.ppv) # Output power of the BAT2PV conversion pathway in W
        self.Ppvbs = np.zeros_like(self.ppv) # AC power of the PV-battery system in W
        self.Pperi = np.ones_like(self.ppv) * self.parameter['P_PERI_AC'] # Additional power consumption of other system components (e.g. AC power meter) in W
        self.dt = 1 # Time increment in s
        self.th = 0 # Start threshold for the recharging of the battery
        self.soc0 = 0 # State of charge of the battery in the first time step

        # DC power output of the PV generator
        if pvmod: # ppv: Normalized DC power output of the PV generator in kW/kWp
            self.Ppv = self.ppv * self.parameter['P_PV'] * 1000
            
        else: # ppv: DC power output of the PV generator in W
            self.Ppv = self.ppv

        # Power demand on the AC side
        self.Pac = self.pl + self.Pperi

        ## Simulation of the battery system
        self.soc, self.soc0, self.Ppv, self.Ppvbs, self.Pbat, self.Ppv2ac_out, self.Pbat2pv_out, self.Ppv2bat_in = tools.run_loss_PV(self.parameter['E_BAT'], self.parameter['P_PV2AC_in'], self.parameter['P_PV2AC_out'], self.parameter['P_PV2BAT_in'], self.parameter['P_BAT2PV_out'], self.parameter['PV2AC_a_in'], self.parameter['PV2AC_b_in'], self.parameter['PV2AC_c_in'], self.parameter['PV2BAT_a_in'], self.parameter['PV2BAT_b_in'], self.parameter['PV2BAT_c_in'], self.parameter['PV2AC_a_out'], self.parameter['PV2AC_b_out'], self.parameter['PV2AC_c_out'], self.parameter['BAT2PV_a_out'], self.parameter['BAT2PV_b_out'], self.parameter['BAT2PV_c_out'], self.parameter['eta_BAT'], self.parameter['SOC_h'], self.parameter['P_PV2BAT_DEV'], self.parameter['P_BAT2AC_DEV'], self.parameter['P_SYS_SOC1_DC'], self.parameter['P_SYS_SOC0_AC'], self.parameter['P_SYS_SOC0_DC'], int(self.ppv.size), self.soc0, self.Pac, self.Ppv, self.Ppv2bat_in, self.Ppv2ac_out, self.Pbat2pv_out, self.Ppvbs, self.Pbat, self.soc, self.dt, self.th, self.parameter['t_DEAD'], self.parameter['t_CONSTANT'])

        # Define missing parameters
        self.Ppv2ac = self.Ppv2ac_out # AC output power of the PV2AC conversion pathway
        self.Ppv2bat = self.Ppv2bat_in # DC input power of the PV2BAT conversion pathway

    def bat_mod_res(self):
       self.E = tools.bat_res_mod(self.parameter, self.pl, self.Ppv, self.Pbat, self.Ppv2ac, self.Ppv2bat, self.Ppvbs, self.Pperi)

