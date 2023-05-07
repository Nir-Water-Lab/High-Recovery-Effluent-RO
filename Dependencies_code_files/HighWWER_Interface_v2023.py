import os
import numpy as np
from Effluent_RO import WATRO

"""Enter major ions concentrations in mol/l"""
Ca = 0.001;	P = 0.00007;	K = 0.00060;	
Mg = 0.00035; Na = 0.00593;	Sl = 0.00089; Cl = 0.00593

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
P_feed = 15.0 #Enter Pressure (bars)
P_permeate = 0.01 
t = 25.0 #Enter Temperature (celcius) 
u0 = 0.17 #Enter feed cross-flow velocity (m/s)
recovery = 98.0 #Enter Recovey Ratio (%)
pressure_drop = 0.3 #Enter total pressure drop (bars)

## Viscosity Parameters

a1 = 1.5700386464E-01
a2 = 6.4992620050E+01
a3 = -9.1296496657E+01
a4 = 4.2844324477E-05
a5 = 1.5409136040E+00
a6 = 1.9981117208E-02
a7 = -9.5203865864E-05
a8 = 7.9739318223E+00
a9 = -7.5614568881E-02
a10 = 4.7237011074E-04

"""Enter Membrane Constants at 25C. If unavailable enter 0 and it will be estimated by the software according to membrane manufacturer performance report"""
"""
--------------------------------------------
Pw0 : Water permeability (float)
Ps0 : Salt permeability (float)
Pb0 : B(OH)3 permeability (float)
ks : Average mass transfer for charged solutes (float)
kb : Average mass transfer for uncharged (float)
"""
Pw0 = 12.65e-7 #1.084e-6 #5.793e-7 #1.084e-6 #Enter water permeabiliy (if unavailable enter 0 - value will be derived from manufacturer data)
Ps0 = 9.404e-8 #7.77e-8 #1.946e-8 #7.77e-8 #Enter NaCl permeabiliy (if unavailable enter 0)
ks = 2.9404e-4 #2.32e-5 #7.73e-6 #Enter average mass transfer coefficient for charged solutes (if unavailable enter 0 - value will be derived from Sherwood correlations)
Pw1, Ps1 = 1.208e-6, 2.414e-8 #LCLE(2021), Rejection ,= 99.40 10.65e-7, 7.404e-8
Pw2, Ps2 = 1.222e-6, 2.533e-8  #4040-XRLE(2020), 8.65e-7,5.404e-8
Pw3, Ps3 = 1.817e-6, 2.56e-8 #TMG20D-440, Rejection = 99.82, 6.65e-7, 3.404e-8
Pw4, Ps4 = 2.05e-6, 2.439e-8 #TMH20A-440C, Rejection = 99.81, 4.65e-7, 1.404e-8

# """Number of Steps in the Process"""
# step_num = int(recovery + 1)
# r_f = recovery/100.0
# r = np.linspace(0, r_f, step_num) 


 
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
(r,Jw,Cb,Cp,Cm,Pbar,first_stage_Avg_flux, second_stage_Avg_flux, third_stage_Avg_flux, fourth_stage_Avg_flux, fifth_stage_Avg_flux, SEC_1, SEC_2, SEC_3, SEC_4, SEC_5, Total_SEC, rho, S)=WATRO(Ca, P, K, Mg, Na, Sl, Cl,a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, P_feed,P_permeate,pressure_drop,t,u0,recovery,Pw0, Ps0, ks,P_std,NaCl_std,A,Qw,Rej_NaCl,d_mil,Pw1,Ps1,Pw2,Ps2,Pw3,Ps3,Pw4,Ps4)
 
import xlsxwriter
# Create folder
folder_name = 'Wastewater_Effluent_Filtration'
# Check if the folder exists, create it if it doesn't
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
folder_path = r'C:\Users\Mangu\Desktop\Nir Water Lab\High-Recovery-Effluent-RO\Wastewater_Effluent_Filtration'  # replace with your desired path 
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
headers = ['Recovery', 'Jw(m/s)', 'Cb(M)', 'Cp(M)', 'Cm(M)', 'P(Bar)','first_stage_Avg_flux(LMH)', 'second_stage_Avg_flux(LMH)', 'third_stage_Avg_flux(LMH)', 'fourth_stage_Avg_flux(LMH)', 'fifth_stage_Avg_flux(LMH)', 'SEC_1 (kWh/m3)', 'SEC_2 (kWh/m3)', 'SEC_3 (kWh/m3)', 'SEC_4 (kWh/m3)', 'SEC_5 (kWh/m3)', 'Total_SEC (kWh/m3)','Density','Salinity']
#'CP modulus ', 'CP modulus Corr', ' Pressure drop Corr'

for i, header in enumerate(headers):
    worksheet.write(0, i, header)

for i in range(len(r)):
    worksheet.write(row, 0, r[i])
    worksheet.write(row, 1, Jw[i])
    worksheet.write(row, 2, Cb[i])
    worksheet.write(row, 3, Cp[i])
    worksheet.write(row, 4, Cm[i])
    worksheet.write(row, 5, Pbar[i])
    
    
    # worksheet.write(row,9, CF[i]) 
    # worksheet.write(row,10, Mcp[i])
    # worksheet.write(row, 11, pressure_drop[i])

    worksheet.write(1, 6, first_stage_Avg_flux)
    worksheet.write(1, 7, second_stage_Avg_flux)
    worksheet.write(1, 8, third_stage_Avg_flux)
    worksheet.write(1, 9, fourth_stage_Avg_flux)
    worksheet.write(1, 10, fifth_stage_Avg_flux)
    
    
    worksheet.write(1, 11, SEC_1)
    worksheet.write(1, 12, SEC_2)
    worksheet.write(1, 13, SEC_3)
    worksheet.write(1, 14, SEC_4)
    worksheet.write(1, 15, SEC_5)
    worksheet.write(1, 16, Total_SEC)
    worksheet.write(1,17,rho)
    worksheet.write(row,18, S[i])         
    
   
    
    

    row += 1



workbook.close()

print(f"File saved to {folder_path}")
