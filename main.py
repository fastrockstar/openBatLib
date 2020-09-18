import os
import controller


#mat = r"C:\Users\kroes\Nextcloud\Shares\09_Studierende\Persönliche Ordner\Kai\Bachelorarbeit\PerMod 2.1\PerModInput.mat"
mat = r'/home/kai/Dokumente/Bachelorarbeit/PerMod 2.1/PerModInput.mat'
#parameter = r"C:\Users\kroes\Nextcloud\Shares\09_Studierende\Persönliche Ordner\Kai\Bachelorarbeit\PerMod 2.1\PerModPAR.xlsx"
parameter = r'/home/kai/Dokumente/Bachelorarbeit/PerMod 2.1/PerModPAR.xlsx'
system = 'I'
ref_case = '1'

c = controller.Controller(mat, parameter, system, ref_case)

print('')