from openbatlib import controller
from openbatlib import model
import numpy as np

c = controller.Controller()

rt = controller.Controller()

# Use this method to start the simulation
c.sim(system="H", ref_case="1", dt=1)
"""
#system = "H"

#ref_case = "1"

dt = 1

fparameter = '/Users/kairosken/Documents/openBatLib/parameter/PerModPAR.xlsx'

freference = '/Users/kairosken/Documents/openBatLib/reference_case/ref_case_data.npz'

parameter = rt.get_parameter(fparameter, system)

ppv = rt._load_pv_input(freference, 'ppv')

parameter, pl = rt._load_ref_case(parameter, freference, fparameter, ref_case)

Pr, Ppv, Ppvs, Pperi = model.max_self_consumption(parameter, ppv, pl, pvmod=True)
# Initialization and preallocation
Pbat = np.zeros_like(ppv)  # DC power of the battery in W
Pbs = np.zeros_like(ppv) # AC power of the battery system in W
soc = np.zeros_like(ppv)  # State of charge of the battery
th = 0  # Start threshold for the recharging of the battery
soc0 = 0  # State of charge of the battery in the first time step
Pbs0 = 0 # AC power of the battery system of the previous time step in W



results = rt.real_time(parameter, _dt=dt, _soc0=soc0, _soc=soc, _Pr=Pr, _Pbs0=Pbs0, _Pbs=Pbs, _Pbat=Pbat)
"""

c.print_SPI()

#c.print_E()
