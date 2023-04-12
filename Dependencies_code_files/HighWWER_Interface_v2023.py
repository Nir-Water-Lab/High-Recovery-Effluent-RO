import os
import numpy as np
from Water_Salt_Transport import WATRO

"""Enter major ions concentrations in mol/l"""
Cl=0.567125511; SO4=0.033763917; Na=0.497273368; Mg=0.052867719
K=0.011085392; Ca=0.010279573; Sr=0.0000776; Br=0.0

"""Enter acid-base parameters"""
"""
---------------------------------
feed_pH : pH, feed (float)
Bt_feed : total boron (float)
Alk_feed : Feed alkalinity (float)
""" 
feed_pH = 8.0 # Enter pH 
Bt_feed = 5.0 # Enter total boron (mg/l)
Alk_feed = 0.002524

"""Enter process operational conditions"""
"""
---------------------------------------
P_feed : Pressure (float)
t : Temperature (float)
u0 : cross-flow velocity (float)
recovery : recovery (float)
pressure_drop : total pressure drop (float)
"""
P_feed = 46.2 #Enter Pressure (bars) 
t = 25.0 #Enter Temperature (celcius) 
u0 = 0.17 #Enter feed cross-flow velocity (m/s)
recovery = 52.0 #Enter Recovey Ratio (%)
pressure_drop = 0.3 #Enter total pressure drop (bars)

"""Enter Membrane Constants at 25C. If unavailable enter 0 and it will be estimated by the software according to membrane manufacturer performance report"""
"""
--------------------------------------------
Pw0 : Water permeability (float)
Ps0 : Salt permeability (float)
Pb0 : B(OH)3 permeability (float)
ks : Average mass transfer for charged solutes (float)
kb : Average mass transfer for uncharged (float)
"""
Pw0 = 5.793e-7 #1.084e-6 #Enter water permeabiliy (if unavailable enter 0 - value will be derived from manufacturer data)
Ps0 = 1.946e-8 #7.77e-8 #Enter NaCl permeabiliy (if unavailable enter 0)
ks = 2.32e-5 #7.73e-6 #Enter average mass transfer coefficient for charged solutes (if unavailable enter 0 - value will be derived from Sherwood correlations)
#Pb0 = 1.875e-6 #2.78e-5 #Enter B(OH)3 permeabiliy (if unavailable enter 0)
#kb = 1.0e-3 #1.62e-5 #Enter average mass transfer coefficient for unchraged solutes (if unavailable enter 0)
 
"""Enter manufacturer results from standard test conditions for estimating missing membrane constants"""
"""
---------------------------------------------
P_std : Standard pressure (float)
NaCl_std : Standard NaCl concentration (float)
B_std : Standard Boron concentration (float)
recovery_std : Recovery at standard test conditions (float)
A : Membrane surface Area (float)
Qw : Permeate flow rate (float)
Rej_NaCl : NaCl rejection at standard test condtions (float)
Rej_B : Boron Rejection at standard test constions (float)
d_mil : feed spacer height (float)
"""
P_std = 41.0 #Enter standard pressure (bars)
NaCl_std = 32.0 #Enter standard NaCl concentration (g/l)
B_std = 5.0 #Enter standard B concentration (mg/l)
recovery_std = 15.0 #Enter recovery at standard conditions(%)
A = 7.9 #Enter Membrane surface area (m^2)
Qw = 4.7 #Enter Permeate flow at standard test conditions (m^3/d)
Rej_NaCl = 99.5 #Enter NaCl rejection at standard test conditions (%)
Rej_B = 83.0 # Enter B rejection at standard test conditions (%)
d_mil = 28.0 #enter feed spacer height (mil)

"""Run the program by pressing F5"""

"""The call for the function"""
(r,Jw,Cb,Cp,Cm,Pbar)=WATRO(Cl,SO4,Na,Mg,K,Ca,Sr,Br,Bt_feed,P_feed,t,u0,recovery,Pw0,Ps0,ks,P_std,NaCl_std,A,Qw,Rej_NaCl,d_mil,pressure_drop)


import xlsxwriter
# Create folder
folder_name = 'Wastewater_Effluent_Filtration'
# Check if the folder exists, create it if it doesn't
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
folder_path = r'C:\Users\Mangu\Desktop\Nir Water Lab\WATRO\Wastewater_Effluent_Filtration'  # replace with your desired path
os.makedirs(folder_path, exist_ok=True)

# define filename and check for existing files with the same name
filename = 'Water_Salt_Transport.xlsx'
i = 1
while os.path.exists(os.path.join(folder_path, filename)):
    filename = f'Water_Salt_Transport_{i}.xlsx'
    i += 1

# Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook(os.path.join(folder_path, filename))
worksheet = workbook.add_worksheet()
# Start from the first cell. Rows and columns are zero indexed.
row = 1
col = 0
r = np.linspace(0, int(recovery), int(recovery + 1))

# write data to worksheet
headers = ['Recovery', 'Jw(m/s)', 'Cb(M)', 'Cp(M)', 'Cm(M)', 'P(Bar)']
for i, header in enumerate(headers):
    worksheet.write(0, i, header)

for i in range(len(r)):
    worksheet.write(row, 0, r[i])
    worksheet.write(row, 1, Jw[i])
    worksheet.write(row, 2, Cb[i])
    worksheet.write(row, 3, Cp[i])
    worksheet.write(row, 4, Cm[i])
    worksheet.write(row, 5, Pbar[i])
    
    row += 1

workbook.close()

print(f"File saved to {folder_path}")
