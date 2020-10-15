import os
import controller
import numpy as np
import pandas as pd


#mat = r"C:\Users\kroes\Nextcloud\Shares\09_Studierende\Persönliche Ordner\Kai\Bachelorarbeit\PerMod 2.1\PerModInput.mat"
#mat = r'/home/kai/Dokumente/Bachelorarbeit/PerMod 2.1/PerModInput.mat'
mat = r'/Users/kairosken/Documents/Bachelorarbeit/PerMod 2.1/PerModInput.mat'
#parameter = r"C:\Users\kroes\Nextcloud\Shares\09_Studierende\Persönliche Ordner\Kai\Bachelorarbeit\PerMod 2.1\PerModPAR.xlsx"
#parameter = r'/home/kai/Dokumente/Bachelorarbeit/PerMod 2.1/PerModPAR.xlsx'
# File path to parameter macOS
parameter = r'/Users/kairosken/Documents/Bachelorarbeit/PerMod 2.1/PerModPAR.xlsx'
fname_test = r'/Users/kairosken/Documents/Bachelorarbeit/Zeitreihe_Testlauf.csv'
system = 'G'
ref_case = '1'

df_test_run = pd.read_csv(fname_test, index_col=0)

ppv_test = df_test_run['ppv'].to_numpy()
pl_test = df_test_run['L'].to_numpy()

dt = 1
soc0 = 0.8 
soc = np.array([0.0])
Pr = np.array([1000])
Pbs = np.array([0.0])
Pbs0 = 76.3
Pbat = np.array([0.0])



# File path for macOS
#csv_file = '/Users/kairosken/Documents/Bachelorarbeit/Python/plenticore_Bl.csv'
# File path for Linux PC
csv_file = '/home/kai/Dokumente/openBatLib/Data/plenticore_Bl_test_run.csv'

SERVER_HOST = "192.168.208.106"
SERVER_PORT = 1502
UNIT_ID = 71

c = controller.Controller()

#paramas = c.get_parameter(fparameter=parameter, system=system)

#Pbat, Pbs, soc, soc0 = c.real_time(params, _dt=dt, _soc0=soc0, _soc=soc, _Pr=Pr, _Pbs0=Pbs0, _Pbs=Pbs, _Pbat=Pbat)

c.modbus(host=SERVER_HOST, port=SERVER_PORT, unit_id=UNIT_ID, ppv=ppv_test, pl=pl_test, ref_case=ref_case, dt=dt, fname=csv_file, fparameter=parameter, fmat=mat, system=system)

#Pr = mod.get_residual_power_AC(parameter=params,ppv=ppv_test, pl=pl_test)

#Pbat, Pbs, soc, soc0 = c.real_time(params, _dt=dt, _soc0=soc0, _soc=soc, _Pr=Pr, _Pbs0=Pbs0, _Pbs=Pbs, _Pbat=Pbat)
#Ppv2ac_out, Ppv2bat_in, Ppv2bat_in0, Pbat2ac_out, Pbat2ac_out0, Ppvbs, Pbat, soc, soc0 = c.real_time(params, _dt=dt, _soc0=soc0, _soc=soc, _Pr=Pr, _Prpv=Prpv,  _Ppv=Ppv, _Ppv2bat_in0=Ppv2bat_in0, _Ppv2bat_in=Ppv2bat_in, _Pbat2ac_out0=Pbat2ac_out0, _Pbat2ac_out=Pbat2ac_out, _Ppv2ac_out0=Ppv2ac_out0, _Ppv2ac_out=Ppv2ac_out, _Ppvbs=Pvbs, _Pbat=Pbat)
#print(soc0)
#Pbat, Pbs, soc, soc0 = c.real_time(params, _dt=900, _soc0=soc0, _soc=soc, _Pr=Pr, _Pbs=Pbs, _Pbat=Pbat)
#print(soc0)
#c.sim(fmat=mat, fparameter=parameter, system=system, ref_case=ref_case, dt=dt)

#mod.modbus(host=SERVER_HOST, port=SERVER_PORT, unit_id=UNIT_ID, input_vals=Pr, dt=dt, fname=csv_file)

print('finished!')

#c.print_E()

#c.E_to_csv('S3_py_est.csv')

#c.plot()

#c.dict_to_csv('normal_Pbs_AC.csv')

#c.to_pickle('Pbs_ohne_Estimator_AC.npy', name='Pbs')
#c.to_pickle('Pbat_ohne_Estimator_AC', name='Pbat')