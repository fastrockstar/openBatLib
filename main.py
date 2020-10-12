import os
import controller
import numpy as np


#mat = r"C:\Users\kroes\Nextcloud\Shares\09_Studierende\Persönliche Ordner\Kai\Bachelorarbeit\PerMod 2.1\PerModInput.mat"
#mat = r'/home/kai/Dokumente/Bachelorarbeit/PerMod 2.1/PerModInput.mat'
mat = r'/Users/kairosken/Documents/Bachelorarbeit/PerMod 2.1/PerModInput.mat'
#parameter = r"C:\Users\kroes\Nextcloud\Shares\09_Studierende\Persönliche Ordner\Kai\Bachelorarbeit\PerMod 2.1\PerModPAR.xlsx"
#parameter = r'/home/kai/Dokumente/Bachelorarbeit/PerMod 2.1/PerModPAR.xlsx'
parameter = r'/Users/kairosken/Documents/Bachelorarbeit/PerMod 2.1/PerModPAR.xlsx'
system = 'I'
ref_case = '1'

dt = 1
soc0 = 0.8 
soc = np.array([0.0])
Pr = np.array([1000])
Pbs = np.array([0.0])
Pbs0 = 76.3
Pbat = np.array([0.0])

input_vals = np.array([1500.0, 2000.0, -500.0, -300.0, -1500.0, -2000.0, -2500.0, -3500.0, -4000.0, -1500.0,
                       500.0, 300.0, -500.0, -300.0, 200.0, 300.0, -100.0, -1000.0, -1500.0, 500.0,
                       300.0, 430.0, -2000.0, -3500.0, 100.0, 500.0, 700.0, 800.0, 900.0, 1000.0])

#csv_file = '/Users/kairosken/Documents/Bachelorarbeit/Python/plenticore_Bl.csv'
csv_file = '/home/kai/Dokumente/openBatLib/Data/plenticore_Bl.csv'

SERVER_HOST = "192.168.208.106"
SERVER_PORT = 1502
UNIT_ID = 71

input_val = 'Moin'

#c = controller.Controller()

mod = controller.Controller()
#params = c.get_parameter(parameter, system)
#Pbat, Pbs, soc, soc0 = c.real_time(params, _dt=dt, _soc0=soc0, _soc=soc, _Pr=Pr, _Pbs0=Pbs0, _Pbs=Pbs, _Pbat=Pbat)
#Ppv2ac_out, Ppv2bat_in, Ppv2bat_in0, Pbat2ac_out, Pbat2ac_out0, Ppvbs, Pbat, soc, soc0 = c.real_time(params, _dt=dt, _soc0=soc0, _soc=soc, _Pr=Pr, _Prpv=Prpv,  _Ppv=Ppv, _Ppv2bat_in0=Ppv2bat_in0, _Ppv2bat_in=Ppv2bat_in, _Pbat2ac_out0=Pbat2ac_out0, _Pbat2ac_out=Pbat2ac_out, _Ppv2ac_out0=Ppv2ac_out0, _Ppv2ac_out=Ppv2ac_out, _Ppvbs=Pvbs, _Pbat=Pbat)
#print(soc0)
#Pbat, Pbs, soc, soc0 = c.real_time(params, _dt=900, _soc0=soc0, _soc=soc, _Pr=Pr, _Pbs=Pbs, _Pbat=Pbat)
#print(soc0)
#c.sim(fmat=mat, fparameter=parameter, system=system, ref_case=ref_case, dt=dt)

mod.modbus(host=SERVER_HOST, port=SERVER_PORT, unit_id=UNIT_ID, input_vals=input_vals, dt=dt, fname=csv_file)

print('finished!')

#c.print_E()

#c.E_to_csv('S3_py_est.csv')

#c.plot()

#c.dict_to_csv('normal_Pbs_AC.csv')

#c.to_pickle('Pbs_ohne_Estimator_AC.npy', name='Pbs')
#c.to_pickle('Pbat_ohne_Estimator_AC', name='Pbat')