def WATRO(Cl,SO4,Na,Mg,K,Ca,Sr,Br,Bt_feed,P_feed,t,u0,recovery,Pw0,Ps0,ks,P_std,NaCl_std,A,Qw,Rej_NaCl,d_mil,pressure_drop):
    
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
        a1 = 1.5700386464E-01
        a2 = 6.4992620050E+01
        a3 = -9.1296496657E+01
        a4 = 4.2844324477E-05
        mu_w = a4 + 1 / (a1 * (T + a2) ** 2 + a3)
        a5 = 1.5409136040E+00
        a6 = 1.9981117208E-02
        a7 = -9.5203865864E-05
        a8 = 7.9739318223E+00
        a9 = -7.5614568881E-02
        a10 = 4.7237011074E-04
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

    S0 = (Cl * 35.453 + Na * 22.98977 + SO4 * 96.0626 + Mg * 24.305 + Ca * 40.078 + K * 39.098 + Br * 79.904 + Sr * 87.62 + Bt_feed/1000)
    Cb[0] = (Cl + Na + SO4 + Mg + Ca + K + Br + Sr + Bt_feed/10811)
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
    Pw0 = Pw_std if Pw0 == 0 else Pw0       
    Ps0 = Ps_std if Ps0 == 0 else Ps0
    
    Pw= Pw0*exp(0.0093*(T - 298.15))  #Taniguchi et al. 2001
    Ps= Ps0*exp(0.0483*(T - 298.15))  #Taniguchi et al. 2001


    first_stage = len(r) * 0.50 / 0.99 
    second_stage = len(r) * (0.80 - 0.50) / 0.99
    third_stage = len(r) * (0.925 - 0.80) / 0.99
    fourth_stage = len(r) * (0.975 - 0.925) / 0.99
    fifth_stage = len(r) * (0.99 - 0.975) / 0.99

    #calculates pressure in Bar, 

        # Define the pressure components for each stage
    pressure_boost = [5, 7, 9, 11]    
    for i in range(len(r)):
        if i < first_stage:
            Pbar[i] = P_feed - pressure_drop * (r[i] / r[-1])       #*calculates the ratio of the current recovery value r[i] to the maximum recovery value r[len(r) - 1], scale pressure drop
        elif i < second_stage:
            Pbar[i] = P_feed + pressure_boost[0] - pressure_drop * (r[i] / r[-1])
        elif i < third_stage:
            Pbar[i] = P_feed + pressure_boost[1] - pressure_drop * (r[i] / r[-1])
        elif i < fourth_stage:
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
                S(6)     %e
                Br       %e   
                Na       %e
                Mg       %e
                K        %e
                Ca       %e
                Sr       %e
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
                END"""%(t,7,Cl/(1-r[i]),SO4/(1-r[i]),Br/(1-r[i]),Na/(1-r[i]),Mg/(1-r[i]),K/(1-r[i]),Ca/(1-r[i]),Sr/(1-r[i]),Pbar[i])
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
                S(6)       %e 
                Br         %e  
                Na         %e 
                Mg         %e 
                K          %e 
                Ca         %e 
                Sr         %e              
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
                 END"""%(t,7,Cl*CF[i],SO4*CF[i],Br*CF[i],Na*CF[i],Mg*CF[i],K*CF[i],Ca*CF[i],Sr*CF[i])
            sol_osm=phreecalc(osmo_phree)
            #print(sol_osm)
            PHI = sol_osm[1][0] 
            rho = sol_osm[1][1]

            Jw[i] = optimize.bisect(func, 1e-8 ,1e-4 , xtol = 1e-17, rtol = 5e-15, maxiter = 500)   #uses the fuct fucntion to find JW, leveraging Scipy lib
            Cp[i] = (Cb[i]*Ps*exp(Jw[i]/k[i]))/(Jw[i]+Ps*exp(Jw[i]/k[i]))           #SD model
            Cm[i] = Cp[i] +(Cb[i]-Cp[i])*exp(Jw[i]/k[i])    # mass balance, film theory
            CF[i] = Cm[i]/Cb[0]       #concentration ploarization factor (CF) for the i-th stage of the reverse osmosis process            
            kphi=kphi+1

        if r[i]<recovery/100:       #checks if the current recovery rate r[i] is less than the target recovery rate 
            Cb[i+1] = (Cb[i]*(1-r[i]) - dr*Cp[i])/(1-r[i+1])        
        CFb[i] = Cb[i]/Cb[0]        
    print ('Done \n\n'  )

    return r,Jw,Cb,Cp,Cm,Pbar
