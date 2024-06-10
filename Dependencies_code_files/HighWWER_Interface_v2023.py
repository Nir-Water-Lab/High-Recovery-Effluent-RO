import os
import numpy as np
from Effluent_RO import Effluent
import xlsxwriter
import time

start_time = time.time()



"""Enter major ions concentrations in mol/l"""
mw_Na = 22989.77; mw_Mg = 24305; mw_Ca = 40078 ; mw_Cl = 35453
mw_P = 30974; mw_Si = 28086; mw_K = 39098; mw_SO4 = 96062.6; mw_Fe = 55845

# Ca = 43/mw_Ca;	Cl = 334/mw_Cl; K = 12/mw_K;	P = 27/mw_P
# Mg = 9/mw_Mg; Na = 303/mw_Na;	Fe = 0.0/mw_Fe                      #P_Unrecovered
# SO4 = 10/mw_SO4; 
# 
# Ca = 22/mw_Ca;	Cl = 162/mw_Cl; K = 12/mw_K;	P = 0.1/mw_P
# Mg = 5/mw_Mg; Na = 250/mw_Na;	Fe = 0.0/mw_Fe                      #P_recovered
# SO4 = 9.8/mw_SO4

# Ca = 38.41/mw_Ca;	Cl = 123.13/mw_Cl; K = 22.51/mw_K;	P = 9.88/mw_P
# Mg = 7.7/mw_Mg; Na = 131.33/mw_Na;	Fe = 0.0/mw_Fe                      #NH3 unrecovered
# SO4 = 6.99/mw_SO4

Ca = 24.24/mw_Ca;	Cl = 116.4/mw_Cl; K = 5.82/mw_K;	P = 6.76/mw_P
Mg = 5.68/mw_Mg; Na = 386.48/mw_Na;	Fe = 0.0/mw_Fe                         #NH3 recovered  
SO4 = 4.8/mw_SO4


"""Enter acid-base parameters"""
"""
---------------------------------
feed_pH : pH, feed (float)
Bt_feed : total boron (float)
Alk_feed : Feed alkalinity (float)
""" 
feed_pH = 6.2 # Enter pH 
Ct_feed = 0.008167    # 0.00875  #0.0153  #Enter total inorganic carbon (mol/l)
Nt_feed = 2.0  # 35.6 #mg/l 151.6
Alk_feed = 0.0 #eq/L ignored

"""Enter process operational conditions"""
"""
---------------------------------------
P_feed : Pressure (float)
t : Temperature (float)
u0 : cross-flow velocity (float)
recovery : recovery (float)
pressure_drop : total pressure drop (float)
"""
P_feed = 6.6 #Enter Pressure (bars) 
t = 25.0 #Enter Temperature (celcius) 
#u0 = 0.17 #Enter feed cross-flow velocity (m/s)
recovery = 95.0 #Enter Recovey Ratio (%)
first_stage = 45
second_stage =  70
third_stage = 85
fourth_stage = 95
#pressure_drop = 0.3 #Enter total pressure drop (bars)

## Viscosity Parameters
a1 = 1.5700386464E-01; a2 = 6.4992620050E+01; a3 = -9.1296496657E+01
a4 = 4.2844324477E-05; a5 = 1.5409136040E+00; a6 = 1.9981117208E-02
a7 = -9.5203865864E-05; a8 = 7.9739318223E+00; a9 = -7.5614568881E-02
a10 = 4.7237011074E-04

##Pressure drop parameters
C = 5.5e-3; GR = 1.98
alpha = - 0.422; gamma = 0.672
sigma = 0.536; L = 7.0

"""Number of Steps in the Process"""

step_num = int(recovery + 1)
r_f = recovery/100.0;   r = np.linspace(0, r_f, step_num) 

"""Enter Membrane Constants at 25C. If unavailable enter 0 and it will be estimated by the software according to membrane manufacturer performance report"""
"""
--------------------------------------------
Pw : Water permeability (float)
Ps : Salt permeability (float)
ks : Average mass transfer for charged solutes (float)
kb : Average mass transfer for uncharged (float)
"""
# #1.084e-6 #5.793e-7 #1.084e-6 #Enter water permeabiliy (if unavailable enter 0 - value will be derived from manufacturer data)
# #7.77e-8 #1.946e-8 #7.77e-8 #Enter NaCl permeabiliy (if unavailable enter 0)
ks = 0 #2.32e-5 #2.9404e-4 #2.32e-5 #7.73e-6 #Enter average mass transfer coefficient for charged solutes (if unavailable enter 0 - value will be derived from Sherwood correlations)
kt = 0
#Salt_Permeability1 = (-2E-08 * (feed_pH*feed_pH)) + (3E-07* feed_pH) - 7.3E-07 
#Ps1 = Ps2 = Ps3 = Ps4 = Salt_Permeability1

if feed_pH <7:
    Salt_Permeability1 = 3.48e-7 + (feed_pH - 4.5)* 1.92e-8    # XLE 
    Ps1 = Ps2=Ps3 = Ps4   = Salt_Permeability1     
    # Salt_Permeability2 = 2.82e-7 + (feed_pH - 4.5)* -2.7e-8     # BW30 LE
    # Ps3 = Ps4 = Salt_Permeability2
    Water_Permeability1 = 9.56e-07 + (feed_pH - 4.5)* -4.11e-9    # XLE
    Pw1 = Pw2 =Pw3 = Pw4 = Water_Permeability1
    # Water_Permeability2 = 1.0e-6 + (feed_pH - 4.5)* -1.44e-7    # BW30LE
    # Pw3 = Pw4 = Water_Permeability2
elif feed_pH >= 7:
    Salt_Permeability1 = 3.96e-7 + (feed_pH - 7.0)* -7.07e-8    # XLE
    Ps1 = Ps2 =Ps3 = Ps4 = Salt_Permeability1
    # Salt_Permeability2 = 2.55E-7        # BW30 LE
    # Ps3 = Ps4 = Salt_Permeability2    
    Water_Permeability1 = 9.45e-7 + (feed_pH - 7.0)* -2.611e-8  #XLE
    Pw1 = Pw2 = Pw3 = Pw4 = Water_Permeability1
    # Water_Permeability2 = 6.39E-7 + (feed_pH - 7.0)* 3.7e-8     #BW30 LE
    # Pw3 = Pw4 = Water_Permeability2      


 

#print(Ps1,Ps2,Ps3, Ps4,Pw1,Pw2,Pw3, Pw4)

Pco2 = 1.5e-1 #Assumed Permeability of CO2

"""Enter manufacturer results from standard test conditions for estimating missing membrane constants"""
"""
---------------------------------------------
P_std : Standard pressure (float)
NaCl_std : Standard NaCl concentration (float)
recovery_std : Recovery at standard test conditions (float)
A : Membrane surface Area (float)
Qw : Permeate flow rate (float)
Rej_NaCl : NaCl rejection at standard test condtions (float)
Rej_B : Boron Rejection at standard test constions (float)
d_mil : feed spacer height (float)
"""
P_std = 41.0 #Enter standard pressure (bars)
NaCl_std = 32.0 #Enter standard NaCl concentration (g/l)            
recovery_std = 15.0 #Enter recovery at standard conditions(%)
A = 7.9 #Enter Membrane surface area (m^2)
Qw = 4.7 #Enter Permeate flow at standard test conditions (m^3/d)
Rej_NaCl = 99.5 #Enter NaCl rejection at standard test conditions (%)
d_mil = 28.0 #enter feed spacer height (mil)

"""The call for the function"""
(r,Jw,Cb,Cp,Cm,Pbar,first_stage_Avg_flux, second_stage_Avg_flux, third_stage_Avg_flux, fourth_stage_Avg_flux,
 pH_b,pH_p,pH_m,Alkb,Alkm,Alkp,Ctb,Ctp,Ptb,Ptp,Ntb,Ntp,Ntp_Accum_mgl, SI_Armp_CaPhosphate,d_CaPhosphate,d_Calcite,  SI_Calcite,Pnh4,osmotic_pressure,NH3_p,NH4_p)=Effluent(Ca, K, Mg, Na, Cl,SO4,P,Fe, P_feed,t,recovery,kt, ks,P_std,NaCl_std,A,Qw,Rej_NaCl,d_mil,Pw1,Ps1,Pw2,Ps2,Pw3,Ps3,Pw4,Ps4,Pco2,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,C,GR,alpha,gamma,sigma,L,feed_pH,Nt_feed,Ct_feed,Alk_feed,first_stage, second_stage, third_stage, fourth_stage)
 
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
headers = ['Recovery', 'Jw(m/s)', 'Cb(M)', 'Cp(M)', 'Cm(M)', 'P(Bar)','first_stage_Avg_flux(LMH)', 'second_stage_Avg_flux(LMH)', 'third_stage_Avg_flux(LMH)', 'fourth_stage_Avg_flux(LMH)',
           'Brine pH','Permeate pH','Film layer pH','Brine Alkalinity','Permeate Alkalinity','Trace Conc. of C in Brine','Trace Conc. of C in Permeate','Ptb','Ptp','Ntb','Ntp','Ntp_Accum_mgl','SI_Armp_CaPhosphate','d_CaPhosphate','d_Calcite',  'SI_Calcite','Pnh4','osmotic_pressure','NH3_p', 'NH4_p']
#, , 

for i, header in enumerate(headers):
    worksheet.write(0, i, header)

for i in range(len(r)):
    worksheet.write(row, 0, r[i])
    worksheet.write(row, 1, Jw[i])
    worksheet.write(row, 2, Cb[i])
    worksheet.write(row, 3, Cp[i])
    worksheet.write(row, 4, Cm[i])
    worksheet.write(row, 5, Pbar[i])
    

    worksheet.write(1, 6, first_stage_Avg_flux)
    worksheet.write(1, 7, second_stage_Avg_flux)
    worksheet.write(1, 8, third_stage_Avg_flux)
    worksheet.write(1, 9, fourth_stage_Avg_flux)
    #worksheet.write(1, 10, fifth_stage_Avg_flux)

    worksheet.write(row,10, pH_b[i])
    worksheet.write(row,11, pH_p[i])
    worksheet.write(row,12, pH_m[i])
    worksheet.write(row,13, Alkb[i]) 
    worksheet.write(row,14, Alkp[i]) 
    worksheet.write(row,15, Ctb[i])
    worksheet.write(row,16, Ctp[i]) 
    worksheet.write(row,17, Ptb[i])
    worksheet.write(row,18, Ptp[i]) 
    worksheet.write(row,19, Ntb[i]) 
    worksheet.write(row,20,Ntp[i])
    worksheet.write(row,21,Ntp_Accum_mgl[i])
    worksheet.write(row,22,SI_Armp_CaPhosphate[i])
    worksheet.write(row,23,d_CaPhosphate[i])
    worksheet.write(row,24, d_Calcite[i])   
    worksheet.write(row,25,SI_Calcite[i])
    worksheet.write(row,26,Pnh4[i])
    worksheet.write(row,27,osmotic_pressure[i])
    worksheet.write(row,28,NH3_p[i])
    worksheet.write(row,29,NH4_p[i])
    
    
    
    #worksheet.write(row, 25, l[i])
    
    

    row += 1



workbook.close()

end_time = time.time()
elapsed_time = end_time - start_time

print(f"Elapsed time: {elapsed_time:.4f} seconds")

print(f"File saved to {folder_path}")
