import os
import controller


#mat = r"C:\Users\kroes\Nextcloud\Shares\09_Studierende\Persönliche Ordner\Kai\Bachelorarbeit\PerMod 2.1\PerModInput.mat"
#mat = r'/home/kai/Dokumente/Bachelorarbeit/PerMod 2.1/PerModInput.mat'
mat = r'/Users/kairosken/Documents/Bachelorarbeit/PerMod 2.1/PerModInput.mat'
#parameter = r"C:\Users\kroes\Nextcloud\Shares\09_Studierende\Persönliche Ordner\Kai\Bachelorarbeit\PerMod 2.1\PerModPAR.xlsx"
#parameter = r'/home/kai/Dokumente/Bachelorarbeit/PerMod 2.1/PerModPAR.xlsx'
parameter = r'/Users/kairosken/Documents/Bachelorarbeit/PerMod 2.1/PerModPAR.xlsx'
system = 'H'
ref_case = '1'

SERVER_HOST = "192.168.208.106"
SERVER_PORT = 1502
UNIT_ID = 71

input_val = 'Moin'

#sim = controller.Controller()

mod = controller.Controller()

#sim.sim(fmat=mat, fparameter=parameter, system=system, ref_case=ref_case, dt='1sec',)

mod.modbus(host=SERVER_HOST, port=SERVER_PORT, unit_id=UNIT_ID, input_val=input_val)

#sim.print_E()

#sim.plot()