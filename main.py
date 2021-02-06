import os
import controller
import numpy as np
import pandas as pd


#mat = r"C:\Users\kroes\Nextcloud\Shares\09_Studierende\Persönliche Ordner\Kai\Bachelorarbeit\PerMod 2.1\PerModInput.mat"
#mat = r'/home/kai/Dokumente/Bachelorarbeit/PerMod 2.1/PerModInput.mat'
# File path for macOS
mat = r'/Users/kairosken/Documents/Bachelorarbeit/PerMod 2.1/PerModInput.mat'
# File path for Linux
#mat = r'/home/kai/Dokumente/openBatLib/Data/PerModInput.mat'
#parameter = r"C:\Users\kroes\Nextcloud\Shares\09_Studierende\Persönliche Ordner\Kai\Bachelorarbeit\PerMod 2.1\PerModPAR.xlsx"
#parameter = r'/home/kai/Dokumente/Bachelorarbeit/PerMod 2.1/PerModPAR.xlsx'
# File path to parameter macOS
parameter = r'/Users/kairosken/Documents/Bachelorarbeit/PerMod 2.1/PerModPAR.xlsx'
# File path for Linux
#parameter = r'/home/kai/Dokumente/openBatLib/Data/PerModPAR.xlsx'
# File path for macOS
#fname_test = r'/Users/kairosken/Documents/Bachelorarbeit/Zeitreihe_Testlauf.csv'
#File path for Linux
#fname_test = r'/home/kai/Dokumente/openBatLib/Data/Zeitreihe_Testlauf.csv'
system = 'H'
ref_case = '1'

#df_test_run = pd.read_csv(fname_test, index_col=0, parse_dates=True)

dt = 1
soc0 = 0.8 
soc = np.array([0.0])
Pr = np.array([100e3])
Pbs = np.array([0.0])
Pbs0 = 76.3
Pbat = np.array([0.0])

# File path for macOS
#csv_file = '/Users/kairosken/Documents/Bachelorarbeit/Python/plenticore_Bl.csv'
# File path for Linux PC
#csv_file = '/home/kai/Dokumente/openBatLib/Data/plenticore_Bl_test_run_1_week.csv'

SERVER_HOST = "192.168.208.106"
SERVER_PORT = 1502
UNIT_ID = 71

c = controller.Controller()

#params = c.get_parameter(fparameter=parameter, system=system)

#Pbat, Pbs, soc, soc0 = c.real_time(params, _dt=dt, _soc0=soc0, _soc=soc, _Pr=Pr, _Pbs0=Pbs0, _Pbs=Pbs, _Pbat=Pbat)

c.sim(fmat=mat, fparameter=parameter, system=system, ref_case=ref_case, dt=dt)

c.print_E()

#c.E_to_csv(r'/Users/kairosken/Documents/Bachelorarbeit/Python/Data Log/Energie/S2_py_neu.csv')

#c.modbus(host=SERVER_HOST, port=SERVER_PORT, unit_id=UNIT_ID, data_frame=df_test_run, ref_case=ref_case, dt=dt, fname=csv_file, fparameter=parameter, fmat=mat, system=system)

#Pr = mod.get_residual_power_AC(parameter=params,ppv=ppv_test, pl=pl_test)

#Pbat, Pbs, soc, soc0 = c.real_time(params, _dt=dt, _soc0=soc0, _soc=soc, _Pr=Pr, _Pbs0=Pbs0, _Pbs=Pbs, _Pbat=Pbat)
#Ppv2ac_out, Ppv2bat_in, Ppv2bat_in0, Pbat2ac_out, Pbat2ac_out0, Ppvbs, Pbat, soc, soc0 = c.real_time(params, _dt=dt, _soc0=soc0, _soc=soc, _Pr=Pr, _Prpv=Prpv,  _Ppv=Ppv, _Ppv2bat_in0=Ppv2bat_in0, _Ppv2bat_in=Ppv2bat_in, _Pbat2ac_out0=Pbat2ac_out0, _Pbat2ac_out=Pbat2ac_out, _Ppv2ac_out0=Ppv2ac_out0, _Ppv2ac_out=Ppv2ac_out, _Ppvbs=Pvbs, _Pbat=Pbat)
#print(soc0)
#Pbat, Pbs, soc, soc0 = c.real_time(params, _dt=900, _soc0=soc0, _soc=soc, _Pr=Pr, _Pbs=Pbs, _Pbat=Pbat)
#print(soc0)


#mod.modbus(host=SERVER_HOST, port=SERVER_PORT, unit_id=UNIT_ID, input_vals=Pr, dt=dt, fname=csv_file)

#print('finished!')



#c.plot()

#c.dict_to_csv('normal_Pbs_AC.csv')

#c.to_pickle('Pbs_ohne_Estimator_AC.npy', name='Pbs')
#c.to_pickle('Pbat_ohne_Estimator_AC', name='Pbat')