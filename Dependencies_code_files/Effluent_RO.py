def WATRO(Ca, P, K, Mg, Na, S, Cl,a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, P_feed,t,u0,visco,recovery,Pw1,Ps1,Pw2,Ps2,Pw3,Ps3,Pw4,Ps4,ks,P_std,NaCl_std,A,Qw,Rej_NaCl,d_mil,pressure_drop):
    
    # Import standard library modules first.
    #import os
    #import sys
    # Then get third party modules.
    from win32com.client import Dispatch 
    #import matplotlib.pyplot as plt 
    import numpy as np 
    from math import exp,sqrt
    import scipy.optimize as optimize

    def selected_array(db_path, input_string):
        """Load database via COM and run input string."""
        dbase = Dispatch('IPhreeqcCOM.Object')
        dbase.LoadDatabase(db_path)
        dbase.RunString(input_string)
        return dbase.GetSelectedOutputArray()

    def phreecalc(input_string):
        """Get results from PHREEQC"""
        pitzer_result = selected_array('pitzer.dat', input_string)
        return pitzer_result
    
    def visco(T, S):
        S = S / 1000
        mu_w = a4 + 1 / (a1 * (T + a2) ** 2 + a3)
        A = a5 + a6 * T + a7 * T ** 2
        B = a8 + a9 * T + a10 * T ** 2
        mu = mu_w * (1 + A * S + B * S ** 2)
        return mu


    def func(jw):
        z = exp (jw / k[i])
        cm = ((Ps + jw) * Cb[i] * z) / (jw + Ps * z)
        cp = Ps * Cb[i] * z / (jw + Ps * z)             #From Eqn 8 in WATRO Paper
        return Pw * (Pbar[i] - (PHI * cm - 0.98 * cp) * T *0.083145) - jw
    

    """Number of Steps in the Process"""
    step_num = int(recovery + 1)
    T = t + 273.15
    Ppa = P_feed * 1e5
    kphi = 0
    PHI = 1.0
    PHI_old = 0
    
    r_f = recovery/100.0
    r = np.linspace(0, r_f, step_num) 
    dr = r[1] - r[0]    # step size
    d = d_mil * 2.54e-5
    Pbar = np.zeros(len(r))    
    
    S = np.zeros(len(r))
    Cb = np.zeros(len(r))

    S0 = (Cl * 35.453 + Na * 22.98977 + Mg * 24.305 + Ca * 40.078 + K * 39.098)
    Cb[0] = (Cl + Na + Mg + Ca + K)
    
    Cp = np.zeros(len(r))
    Cm = np.zeros(len(r))
    k = np.zeros(len(r))
    Jw = np.zeros(len(r))
    CFb = np.zeros(len(r))
    CF = np.zeros(len(r))

    
    """Get constants from standard test conditions"""
    NaClp = NaCl_std * (1 - Rej_NaCl / 100)
    Jw_avg = Qw / ( A * 24 * 3600)
    PHI_avg = 0.98

    if NaCl_std>30.0:
        PHI_avg=0.922

    Pi= PHI_avg * 2 * (NaCl_std /58.443) * 0.083145 * T     #Pi: osmotic pressure
    Pw_std = Jw_avg /(P_std - Pi )              #Water Transport, pressure differential as driving force
    Ps_std = (Jw_avg * NaClp) / (NaCl_std - NaClp)  #Salt Transport, Concentration Differential as driving force
    
    
    """Temperature corrections for permeability constants"""


    Pw1 = Pw_std if Pw1 == 0 else Pw1       
    Ps1 = Ps_std if Ps1 == 0 else Ps1

    Pw2 = Pw_std if Pw2 == 0 else Pw2       
    Ps2 = Ps_std if Ps2 == 0 else Ps2

    Pw3 = Pw_std if Pw3 == 0 else Pw3       
    Ps3 = Ps_std if Ps3 == 0 else Ps3

    Pw4 = Pw_std if Pw4 == 0 else Pw4       
    Ps4 = Ps_std if Ps4 == 0 else Ps4

    first_stage = int(len(r) * 0.495 / 0.99) 
    second_stage = int(len(r) * (0.79) / 0.99)
    third_stage = int(len(r) * (0.91) / 0.99)
    fourth_stage = int(len(r) * (0.96) / 0.99)
    fifth_stage = int(len(r) * (0.98) / 0.99)

    Pw= Pw1*exp(0.0093*(T - 298.15))  #Taniguchi et al. 2001
    Ps= Ps1*exp(0.0483*(T - 298.15))  #Taniguchi et al. 2001

    Pw= Pw2*exp(0.0093*(T - 298.15))  #Taniguchi et al. 2001
    Ps= Ps2*exp(0.0483*(T - 298.15))  #Taniguchi et al. 2001

    Pw= Pw3*exp(0.0093*(T - 298.15))  #Taniguchi et al. 2001
    Ps= Ps3*exp(0.0483*(T - 298.15))  #Taniguchi et al. 2001

    Pw= Pw4*exp(0.0093*(T - 298.15))  #Taniguchi et al. 2001
    Ps= Ps4*exp(0.0483*(T - 298.15))  #Taniguchi et al. 2001


    # assign Pw and Ps values based on the stage
    for i in range(len(r)):
        if i <= first_stage:
            Pw, Ps = Pw1, Ps1
        elif first_stage < i <= second_stage:
            Pw, Ps = Pw2, Ps2
        elif second_stage < i <= third_stage:
            Pw, Ps = Pw3, Ps3
        else:
            Pw, Ps = Pw4, Ps4

    


    pressure_boost = [3, 5, 7, 9]
    for i in range(len(r)):
        if i <= first_stage:
            Pbar[i] = P_feed - pressure_drop * (r[i] / r[-1])
        elif first_stage < i <= second_stage:
            Pbar[i] = P_feed + pressure_boost[0] - pressure_drop * (r[i] / r[-1])
        elif second_stage < i <= third_stage:
            Pbar[i] = P_feed + pressure_boost[1] - pressure_drop * (r[i] / r[-1])
        elif third_stage < i <= fourth_stage:
            Pbar[i] = P_feed + pressure_boost[2] - pressure_drop * (r[i] / r[-1])
        else:
            Pbar[i] = P_feed + pressure_boost[3] - pressure_drop * (r[i] / r[-1])


    
        PHI = 1.0
        """mass transfer coefficient"""
        k[i] = ks
        if ks == 0:     #If ks is not provided, it computes for the value of ks as below and assigns it for each recovery step
            RHO_PHREE = """
                SOLUTION 1 seawater
                units     mol/l
                temp     %f
                pH       %f
                Cl       %e   
                Na       %e
                Mg       %e
                K        %e
                Ca       %e
                USE solution 1
                REACTION_PRESSURE 1
                %f
                USER_PUNCH
                -headings RHO osmotic_coefficient ALK Ct Bt
                -start
                10 PUNCH RHO
                20 PUNCH OSMOTIC
                 -end
                SELECTED_OUTPUT
                -reset          false
                -user_punch     true
                END"""%(t,7,Cl/(1-r[i]),Na/(1-r[i]),Mg/(1-r[i]),K/(1-r[i]),Ca/(1-r[i]),Pbar[i])
            sol_rho = phreecalc(RHO_PHREE)
            #print(sol_rho)
            rho = 1000*sol_rho[2][0]
            S[i] = S0 / (1 - r[i])      # bulk salinity in kg/m^3
            visc = visco(t, S[i])       # (1.234*10**-6)*exp(0.00212*S[i]+1965/T) seawater viscocity in pa*s  from Sharkwy et al. 2009
            D_NaCl = (6.725 * 10 ** -6) * exp(0.1546 * S[i] * 10 ** -3 - 2513 / T)  # Diffusivity  of NaCl in seawater in  m^2/s  from taniguchi et al 2001
            Sh = 0.065 * ((rho * u0 * (1 - r[i]) * 2 * d / visc) ** 0.875) * (visc / (rho * D_NaCl)) ** 0.25    # sherwood number  from taniguchi et al 2001
            k[i] = Sh * D_NaCl / d  # mass transfer coefficient in m/sec


        """find Jw(i), Cm(i) and PHI(i)"""
        CF[i] = 1/(1-r[i])         #Concentration factor 
        PHI_old =10
        while (abs(PHI-PHI_old)>0.001):     # loop that runs until the absolute difference between PHI and PHI_old is less than or equal to 0.001
            PHI_old=PHI
            osmo_phree = """
                SOLUTION 1 mediterranean seawater
                units      mol/l
                temp       %f
                pH         %f
                Cl         %e   
                Na         %e 
                Mg         %e 
                K          %e 
                Ca         %e               
                USE solution 1            
                USER_PUNCH
                -headings osmotic_coefficient
                -start
                10 PUNCH OSMOTIC
                20 PUNCH RHO
                 -end
                SELECTED_OUTPUT
                -reset                false
                -user_punch           true
                 END"""%(t,7,Cl*CF[i],Na*CF[i],Mg*CF[i],K*CF[i],Ca*CF[i])
            sol_osm=phreecalc(osmo_phree)
            #print(sol_osm)
            PHI = sol_osm[1][0] 
            rho = sol_osm[1][1]

            Jw[i] = optimize.bisect(func, 1e-8 ,1e-4 , xtol = 1e-17, rtol = 5e-15, maxiter = 500)   #uses the bisection method to find Jw within the boundary conditions
            #print(Jw)
            
            #Calculate average flux per stage
            first_stage_Avg_flux = (sum(Jw[:first_stage + 1]) / (first_stage + 1)) * 3600000 
            second_stage_Avg_flux = (sum(Jw[first_stage + 1:second_stage + 1]) / (second_stage - first_stage)) * 3600000 
            third_stage_Avg_flux = (sum(Jw[second_stage + 1:third_stage + 1]) / (third_stage - second_stage)) * 3600000 
            fourth_stage_Avg_flux = (sum(Jw[third_stage + 1:fourth_stage + 1]) / (fourth_stage - third_stage)) * 3600000 
            fifth_stage_Avg_flux = (sum(Jw[fourth_stage + 1:]) / (len(r) - fourth_stage - 1)) * 3600000  


            Cp[i] = (Cb[i]*Ps*exp(Jw[i]/k[i]))/(Jw[i]+Ps*exp(Jw[i]/k[i]))           #SD model
            Cm[i] = Cp[i] +(Cb[i]-Cp[i])*exp(Jw[i]/k[i])    # mass balance, film theory
            CF[i] = Cm[i]/Cb[0]       #concentration ploarization factor (CF) for the i-th stage of the reverse osmosis process            
            kphi=kphi+1

        if r[i]<recovery/100:       #checks if the current recovery rate r[i] is less than the target recovery rate 
            Cb[i+1] = (Cb[i]*(1-r[i]) - dr*Cp[i])/(1-r[i+1])        
        CFb[i] = Cb[i]/Cb[0]        
    print ('Done \n\n'  )

    return r,Jw,Cb,Cp,Cm,Pbar,first_stage_Avg_flux, second_stage_Avg_flux, third_stage_Avg_flux, fourth_stage_Avg_flux, fifth_stage_Avg_flux
