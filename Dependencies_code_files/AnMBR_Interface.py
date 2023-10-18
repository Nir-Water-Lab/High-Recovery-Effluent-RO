import os
import math
import numpy as np
from AnMBR import AnMBR_Analysis

import time

start_time = time.time()

"""Enter major ions concentrations in mol/l"""
mw_Na = 22989.77; mw_Mg = 24305; mw_Ca = 40078 ; mw_Cl = 35453
mw_P = 30974; mw_Si = 28086; mw_K = 39098; mw_S04 = 96062.6

#Feed 1  @ 0% recovery pH 8.27
# Ca = 36.4/mw_Ca  ; K = 8.9/mw_K
# Mg = 8.82/mw_Mg; Na =278/mw_Na ; SO4 = 6.39/mw_S04; Cl = 127/mw_Cl
# P = 26.1/mw_P; Si = 2.19/mw_Si

#Feed 2  @ 0% recovery pH at 6.5
Ca =43/mw_Ca ;		K = 12.4/mw_K;	
Mg = 9.39/mw_Mg; Na = 303/mw_Na;	SO4 = 10.3/mw_S04; 
P = 27.1/mw_P; Si = 2.6/mw_Si
Cl = 127/mw_Cl
# #Feed 3 at 50% recovery ph 8.45
# Ca = 30.6/mw_Ca;		K = 29.2/mw_K ;	
# Mg = 12.3/mw_Mg; Na =440/mw_Na ;	SO4 = 18.2/mw_S04; Cl = 291/mw_Cl
# P = 0.47/mw_P ; Si = 0.4/mw_Si

 
#Feed 4  @ 50% recovery pH at 6.5
# Ca = 0.00119;		K = 0.0006189;	
# Mg = 0.0005669; Na = 0.01957;	SO4 = 0.0001932; Cl = 0.011959
# P = 1.61426e-5; Si = 1.56662e-5
Ct_feed = 98   #mg/l
# S0 = (Cl * 35.453 + Na * 22.98977 + Mg * 24.305 + Ca * 40.078 
    #   + K * 39.098 + SO4 * 96.0626 + P *30.974 + Si * 28.086)




"""Enter acid-base parameters"""
"""
---------------------------------
feed_pH : pH, feed (float)
Alk_feed : Feed alkalinity (float)
""" 
feed_pH = 6.5 # Enter pH 
# at 6.5 , Alk 1 = 0.0056641 , Alk 2 = 0.0050125
# at 8.3, Alk 1 = 0.0097557, Alk 2 = 0.0082483
# at 7.9, Alk 1 = 0.0094378 , Alk 2 = 0.008035

#Nt_feed = 5.0 

Alk_feed = 0.0056641  #feed 1
Alk_feed = 0.0050125  #feed 2

"""Enter process operational conditions"""
"""
---------------------------------------
P_feed : Pressure (float)
t : Temperature (float)
u0 : cross-flow velocity (float)
recovery : recovery (float)
pressure_drop : total pressure drop (float)
"""

J_permeate = 8.3333e-6 #(m/s)   30 LMH Constant Permeate flux
t = 25.0 #Enter Temperature (celcius) 
u0 = 0.31 #Enter feed cross-flow velocity (m/s)
recovery = 64 #Enter Recovey Ratio (%)
#pressure_drop = 0.03 #Enter total pressure drop (bars)

## Viscosity Parameters
a1 = 1.5700386464E-01; a2 = 6.4992620050E+01; a3 = -9.1296496657E+01
a4 = 4.2844324477E-05; a5 = 1.5409136040E+00; a6 = 1.9981117208E-02
a7 = -9.5203865864E-05; a8 = 7.9739318223E+00; a9 = -7.5614568881E-02
a10 = 4.7237011074E-04

"""Enter Membrane Constants at 25C. If unavailable enter 0 and it will be estimated by the software according to membrane manufacturer performance report"""
Pw0 = 1.6667e-6 #1.084e-6 #Enter water permeabiliy (if unavailable enter 0 - value will be derived from manufacturer data)
Ps0 = 2.9712986e-7 #1.946e-8 #7.77e-8 #Enter NaCl permeabiliy (if unavailable enter 0)
ks = 2.14e-5 #7.73e-6  #2.32e-5 ##Enter average mass transfer coefficient for charged solutes (if unavailable enter 0 - value will be derived from Sherwood correlations)

"""Enter manufacturer results from standard test conditions for estimating missing membrane constants"""
P_std = 41.0 #Enter standard pressure (bars)
NaCl_std = 32.0 #Enter standard NaCl concentration (g/l)
recovery_std = 15.0 #Enter recovery at standard conditions(%)
A = 7.9 #Enter Membrane surface area (m^2)
Qw = 4.7 #Enter Permeate flow at standard test conditions (m^3/d)
Rej_NaCl = 99.5 #Enter NaCl rejection at standard test conditions (%)
d_mil = 28.0 #enter feed spacer height (mil)

"""The call for the function"""
(r, Jw,Cb,Cp,Cm,osmotic_pressure,Pbar,pH_b)= AnMBR_Analysis(Ca, K, Mg, Na, Cl,SO4, P,Si, J_permeate,t,recovery,u0, ks,P_std,NaCl_std,A,Qw,Rej_NaCl,d_mil,Pw0,Ps0, a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,feed_pH,Alk_feed,Ct_feed)

import xlsxwriter
# Create folder
folder_name = 'AnMBR_Analysis_Results'
# Check if the folder exists, create it if it doesn't
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
folder_path = r'C:\Users\Mangu\Desktop\Nir Water Lab\High-Recovery-Effluent-RO\AnMBR_Analysis_Results'  # replace with your desired path 
os.makedirs(folder_path, exist_ok=True)

# define filename and check for existing files with the same name
filename = 'AnMBR_Result.xlsx'
i = 1
while os.path.exists(os.path.join(folder_path, filename)):
    filename = f'AnMBR_Result{i}.xlsx'
    i += 1

# Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook(os.path.join(folder_path, filename))
worksheet = workbook.add_worksheet()
# Start from the first cell. Rows and columns are zero indexed.
row = 1
col = 0
r = np.linspace(0, int(recovery), int(recovery + 1))
#r = np.linspace(0, int(recovery), 65)

#write data to worksheet
headers = ['Recovery', 'Jw(m/s)', 'Cb(M)', 'Cp(M)', 'Cm(M)','osmotic_pressure','Pbar','Brine pH']

for i, header in enumerate(headers):
    worksheet.write(0, i, header)

for i in range(len(r)):
    worksheet.write(row, 0, r[i])
    worksheet.write(row, 1, Jw[i])
    worksheet.write(row, 2, Cb[i])
    worksheet.write(row, 3, Cp[i])
    worksheet.write(row, 4, Cm[i])
    worksheet.write(row,5,osmotic_pressure[i])
    worksheet.write(row,6,Pbar[i])
    worksheet.write(row,7,pH_b)
    #worksheet.write(row,8,Cl[i])
    # worksheet.write(row,9,pH_m[i])
    # worksheet.write(row,10,Alkb[i])
    # worksheet.write(row,11,Alkm)
    # worksheet.write(row,12,Alkp[i])
    # worksheet.write(row,13,Ctb[i])
    # worksheet.write(row,14,Ctp[i])

    row+= 1

workbook.close()

end_time = time.time()  
elapsed_time = end_time - start_time

print(f"Elapsed time: {elapsed_time:.4f} seconds")

print(f"File saved to {folder_path}")
    
