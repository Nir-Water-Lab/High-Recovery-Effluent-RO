def SEC_Analysis (Ca, K, Mg, Na, Cl,SO4,Hq,Bq, P_feed,t,recovery, ks,khq,kbq,P_std,NaCl_std,A,Qw,Rej_NaCl,d_mil,Phq,Pbq,Pw1,Ps1,Pw2,Ps2,Pw3,Ps3,Pw4,Ps4,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,C,GR,alpha,gamma,sigma,L,feed_pH,Alk_feed):
    # Import standard library modules first.
    #import sys
    # Then get third party modules.
    from win32com.client import Dispatch
    #import matplotlib.pyplot as plt 
    import numpy as np 
    from math import exp,sqrt
    #from mpmath import mp
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
        """Calculate sewater viscosity based on Sharqawy et al. 2009"""
        S=S/1000
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
    """Initialization of variables"""
    T = t + 273.15
    Ppa = P_feed * 1e5
    kphi = 0;   PHI = 1.0;  PHI_old = 0
    
    
    r_f = recovery/100.0;   r = np.linspace(0, r_f, step_num) 
    dr = r[1] - r[0]    # step size
    d = d_mil * 2.54e-5;    Pbar = np.zeros(len(r))    
    S = np.zeros(len(r));   Cb = np.zeros(len(r))
    S0 = (Cl * 35.453 + Na * 22.98977 + Mg * 24.305 + Ca * 40.078 + K * 39.098 + SO4 * 32.065 + Hq * 110.12 + Bq * 108.09 )
    Cb[0] = (Cl + Na + Mg + Ca + K + SO4 + Hq + Bq)

    Cp = np.zeros(len(r));  Cm = np.zeros(len(r))
    k = np.zeros(len(r));   Jw = np.zeros(len(r))
    CFb = np.zeros(len(r)); CF = np.zeros(len(r))
    Mcp = np.zeros(len(r)); Ctb = np.zeros(len(r))      #Total carbonate in bulk
    Alkb = np.zeros(len(r)); Ctp=np.zeros(len(r))
    Alkp=np.zeros(len(r))

    pressure_drop = np.zeros(len(r));   Fd = np.zeros(len(r)); U = np.zeros(len(r))
    Re_c = np.zeros(len(r)); Sh = np.zeros(len(r)); pH_b = np.zeros(len(r))    
    pH_m = np.zeros(len(r));   pH_p=np.zeros(len(r)); CO2_b=np.zeros(len(r))    
    HCO3_b=np.zeros(len(r));   CO3_b=np.zeros(len(r)); Theta=np.zeros(len(r))     
    w_H_eff=np.zeros(len(r));   w_OH_eff=np.zeros(len(r))

    """Parameters for Hydroquinone and Benzoquinone"""
    Hq_Accum = np.zeros(len(r))
    Bq_Accum = np.zeros(len(r))
    Hq_Accum_Mgl = np.zeros(len(r))
    Bq_Accum_Mgl = np.zeros(len(r))
    Hq_p = np.zeros(len(r))
    Bq_p = np.zeros(len(r))
    Hq_b = np.zeros(len(r))
    Bq_b = np.zeros(len(r))

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

    """ Recovery rates"""
    first_stage = int(len(r) * 0.495 / 0.98) 
    second_stage = int(len(r) * (0.74) / 0.98)
    third_stage = int(len(r) * (0.86) / 0.98)
    fourth_stage = int(len(r) * (0.93) / 0.98)
    fifth_stage = int(len(r) * (0.97) / 0.98)

    """Temperature corrections for permeability constants"""
    Pw= Pw1*exp(0.0093*(T - 298.15))  #Taniguchi et al. 2001
    Ps= Ps1*exp(0.0483*(T - 298.15))  #Taniguchi et al. 2001
    Pw= Pw2*exp(0.0093*(T - 298.15))  #Taniguchi et al. 2001
    Ps= Ps2*exp(0.0483*(T - 298.15))  #Taniguchi et al. 2001
    Pw= Pw3*exp(0.0093*(T - 298.15))  #Taniguchi et al. 2001
    Ps= Ps3*exp(0.0483*(T - 298.15))  #Taniguchi et al. 2001
    Pw= Pw4*exp(0.0093*(T - 298.15))  #Taniguchi et al. 2001
    Ps= Ps4*exp(0.0483*(T - 298.15))  #Taniguchi et al. 2001
    Phq = Phq*exp(0.0483*(T - 298.15))
    Pbq = Pbq*exp(0.0483*(T - 298.15)) 

    Feed  = """
            SOLUTION 1 effluent
            units     mol/l
            temp     %f
            pH       %f
            Cl       %e  
            Na       %e
            Mg       %e
            K        %e
            Ca       %e
            S(6)     %e
            Alkalinity       %e
            USE solution 1
            USER_PUNCH
            -headings ALK Ct RHO  
            -start           
            10 PUNCH ALK
            20 PUNCH TOT("C")
            30 PUNCH RHO
             -end
            SELECTED_OUTPUT
            -reset          false
            -user_punch     true
            END"""%(t,feed_pH,Cl,Na,Mg,K,Ca,SO4,Alk_feed)
    sol_feed = phreecalc(Feed)
    #print(sol_feed)
    rho= sol_feed[1][2]
    Alkb[0]=sol_feed[1][0] #/((1+S0/1000)/(rho/1000))
    Hq_b[0] = Hq
    Bq_b[0] = Bq

    # assign Pw and Ps values based on the stage
    for i in range(len(r)):
        """Water Flux and salt passage model""" 
        if i <= first_stage:
            Pw, Ps = Pw1, Ps1
        elif first_stage < i <= second_stage:
            Pw, Ps = Pw2, Ps2
        elif second_stage < i <= third_stage:
            Pw, Ps = Pw3, Ps3
        else:
            Pw, Ps = Pw4, Ps4


        u0 = [0.17, 0.35, 0.68, 1.31, 2.83]
         #Crossflow velocity corrections per stage
        if i <= first_stage:
            U[i] = u0[0]*(1.0-r[i])
        elif first_stage < i <= second_stage:
            U[i] = u0[1]*(1.0-r[i])
        elif second_stage < i <= third_stage:
            U[i] = u0[2]*(1.0-r[i])
        elif third_stage < i <= fourth_stage:
            U[i] = u0[3]*(1.0-r[i])
        else:
            U[i] = u0[4]*(1.0-r[i])

        
        PHI = 1.0
        """mass transfer coefficient"""
        #ks = 2.9404e-4
        k[i] = ks
        if ks == 0:
            RHO_PHREE = """
                SOLUTION 1 effluent
                units     mol/l
                temp     %f 
                pH       %f
                Cl       %e   
                Na       %e
                Mg       %e
                K        %e
                Ca       %e
                S(6)     %e
                USE solution 1
                REACTION_PRESSURE 1
                %f
                USER_PUNCH
                -headings RHO osmotic_coefficient ALK Ct  
                -start
                10 PUNCH RHO
                20 PUNCH OSMOTIC
                 -end
                SELECTED_OUTPUT
                -reset          false
                -user_punch     true
                END"""%(t,7,Cl/(1-r[i]),Na/(1-r[i]),Mg/(1-r[i]),K/(1-r[i]),Ca/(1-r[i]),SO4/(1-r[i]), Pbar[i])
            sol_rho = phreecalc(RHO_PHREE)
            #print(sol_rho)
            rho = 1000*sol_rho[2][0]
            PHI = sol_rho[2][1]

            """Mass Transfer
            Re_c = Reynolds number, crossflow velocity
            rho = fluid density
            D_Nacl = Solute Diffusivity
            d = filament Diamter
            visc = dynamic viscosity
            Sh = Sherwoods Number
            Sc = Schmidts  Number
            """
            S[i] = S0 / (1 - r[i])      # bulk salinity in kg/m^3
            visc = visco(t, S[i])       # (1.234*10**-6)*exp(0.00212*S[i]+1965/T) seawater viscocity in pa*s  from Sharkwy et al. 2009
            #print(visc)
            D_NaCl = (6.725 * 10 ** -6) * exp(0.1546 * S[i] * 10 ** -3 - 2513 / T)  # Diffusivity  of NaCl in seawater in  m^2/s  from taniguchi et al 2001
            Sc = visc / (rho * D_NaCl)          #Schmidths number 
            Re_c[i] = (rho * U[i] * 2 * d ) / visc
            Sh[i] = 0.065*(Re_c[i] ** 0.875) * (Sc ** 0.25)             #Schock and Miquel 1987
            k[i] = Sh[i] * D_NaCl / d                                   # mass transfer coefficient in m/sec


            """ Pressure Drop
            L = Length of pressure vessel
            Fd = friction coefficient
            d = hydraulic diameter
            """
            """ Correlation for CP Modulus and Pressure drop Correlations
            GR = filament spacing to diameter ratio
            Lf = filament spacing
            Df = filament Diameter
            C, alpha, Beta, Gamma, Sigma = Coefficients and exponents
            Mcp = Concentration Polarisation Modulus
            """   
            # #Calculate Average velocity per stage
            u1 = (U[0] + U[50])/ 2
            u2 = (U[51] + U[74])/2
            u3 = (U[75] + U[86])/2
            u4 = (U[87] + U[93])/2
            u5 = (U[94] + U[98])/2      
            #Fd[i]= (6.23*Re_c[i])**-0.3         #friction_factor Boram Gu et al
            Fd[i] = (100*Re_c[i])**-0.25              #friction_factor Blasuis et al

            """
            Calculating pressure drop per stage
            """
            
            if i <= first_stage:
                pressure_drop[i] = (Fd[i]*rho * (u1*u1)*L)/2*d
            elif first_stage < i <= second_stage:
                pressure_drop[i] = (Fd[i]*rho * (u2*u2)*L)/2*d
            elif second_stage < i <= third_stage:
                pressure_drop[i] = (Fd[i]*rho * (u3*u3)*L)/2*d
            elif third_stage < i <= fourth_stage:
                pressure_drop[i] = (Fd[i]*rho * (u4*u4)*L)/2*d
            else:
                pressure_drop[i] = (Fd[i]*rho * (u5*u5)*L)/2*d

            
            ## Concentration Polarization Modulus
            Mcp[i] = C * (Re_c[i] ** alpha) * (Sc ** gamma) * (GR ** sigma) + 1

            #Calculating pressure per stage [0.67, 0.37, 2.58, 7.0 ]

        pressure_boost = [0.53, 0.11, 1.29, 5.47 ]
        if i <= first_stage:
            Pbar[i] = P_feed - pressure_drop[i] * (r[i]/r[len(r)-1])
        elif first_stage < i <= second_stage:
            Pbar[i] = P_feed + pressure_boost[0] - pressure_drop[i] * (r[i]/r[len(r)-1])
        elif second_stage < i <= third_stage:
            Pbar[i] = P_feed + pressure_boost[1] - pressure_drop[i] * (r[i]/r[len(r)-1])
        elif third_stage < i <= fourth_stage:
            Pbar[i] = P_feed + pressure_boost[2] - pressure_drop[i] * (r[i]/r[len(r)-1])
        else:
            Pbar[i] = P_feed + pressure_boost[3] - pressure_drop[i] * (r[i]/r[len(r)-1])


        """find Jw(i), Cm(i) and PHI(i)"""
        CF[i] = 1/(1-r[i])         #Correction factor
        PHI_old =10
        while (abs(PHI-PHI_old)>0.001): 

            PHI_old=PHI
            osmo_phree = """
                SOLUTION 1 efluent 
                units      mol/l
                temp       %f
                pH         %f
                Cl         %e   
                Na         %e 
                Mg         %e 
                K          %e 
                Ca         %e
                S(6)       %e          
                USE solution 1 
                USER_PUNCH
                -headings osmotic_coefficient   RHO
                -start
                10 PUNCH OSMOTIC
                20 PUNCH RHO
                 -end
                SELECTED_OUTPUT
                -reset          false
                -user_punch     true 
                 END"""%(t,7,Cl*CF[i],Na*CF[i],Mg*CF[i],K*CF[i],Ca*CF[i],SO4*CF[i])
            sol_osm=phreecalc(osmo_phree)
            PHI = sol_osm[1][0] 
            rho = sol_osm[1][1]
            Jw[i] = optimize.bisect(func,1e-8 ,1e-4, xtol = 1e-17, rtol = 5e-15, maxiter = 500) 


            Cp[i] = (Cb[i]*Ps*exp(Jw[i]/k[i]))/(Jw[i]+Ps*exp(Jw[i]/k[i]))           #SD model
            Cm[i] = Cp[i] +(Cb[i]-Cp[i])*exp(Jw[i]/k[i])    # eqn1 WATRO mass balance, film theory
            CF[i] = Cm[i]/Cb[0]       #concentration factor (CF) for the i-th stage of the reverse osmosis process 
            kphi=kphi+1 

        if r[i]<recovery/100:       #checks if the current recovery rate r[i] is less than the target recovery rate
            Cb[i+1] = (Cb[i]*(1-r[i]) - dr*Cp[i])/(1-r[i+1])        
        CFb[i] = Cb[i]/Cb[0]  

        """Calculate average flux per stage"""
        first_stage_Avg_flux = (sum(Jw[:first_stage + 1]) / (first_stage + 1)) * 3600000 
        second_stage_Avg_flux = (sum(Jw[first_stage + 1:second_stage + 1]) / (second_stage - first_stage)) * 3600000
        third_stage_Avg_flux = (sum(Jw[second_stage + 1:third_stage + 1]) / (third_stage - second_stage)) * 3600000 
        fourth_stage_Avg_flux = (sum(Jw[third_stage + 1:fourth_stage + 1]) / (fourth_stage - third_stage)) * 3600000
        fifth_stage_Avg_flux = (sum(Jw[fourth_stage + 1:]) / (fifth_stage - fourth_stage)) * 3600000  

        """Specific Energy Consumption """
        SEC_1 = ((1 - r[0])/r[-1]) * (Pbar[i] * 0.02778)
        SEC_2 = ((1 - r[first_stage + 1])/r[-1]) * (pressure_boost[0] * 0.02778)
        SEC_3 = ((1 - r[second_stage + 1])/r[-1]) * (pressure_boost[1] * 0.02778)
        SEC_4 = ((1 - r[third_stage + 1])/r[-1]) * (pressure_boost[2] * 0.02778)
        SEC_5 =  ((1 - r[fourth_stage + 1])/r[-1]) * (pressure_boost[3] * 0.02778)
        Total_SEC = SEC_1 + SEC_2 + SEC_3 + SEC_4 + SEC_5

        """Hydroquinone Transport"""
        khq = khq or 2 * k[i]
        kbq = kbq or 2 * k[i]

        # Initialize a variable to keep track of the previous Hq_b value
        
        if r[i] < recovery/100:
            Hq_b[i+1] = (Hq_b[i]*(1-r[i]) - dr*Hq_p[i])/(1-r[i+1])
            Bq_b[i+1] = (Bq_b[i]*(1-r[i]) - dr*Bq_p[i])/(1-r[i+1])

        #Using the SD_film Model transport; Hydroquinone
        Hq_p[i] = (Phq * Hq_b[i]* exp(Jw[i] / khq)) / (Jw[0] + Phq * exp(Jw[i] / khq))
        Bq_p[i] = (Pbq * Bq_b[i]* exp(Jw[i] / kbq)) / (Jw[0] + Pbq * exp(Jw[i] / kbq))


        Hq_Accum[0] = Hq_p[0]
        Bq_Accum[0] = Bq_p[0]

    
        Hq_Accum[i] = np.average(Hq_p[0:i+1])
        Bq_Accum[i] = np.average(Bq_p[0:i+1])
    Hq_Accum_Mgl = Hq_Accum *110120
    Bq_Accum_Mgl = Bq_Accum *108094

    return r,Jw,Cb,Cp,Cm,Pbar,first_stage_Avg_flux, second_stage_Avg_flux, third_stage_Avg_flux, fourth_stage_Avg_flux, fifth_stage_Avg_flux, SEC_1, SEC_2, SEC_3, SEC_4, SEC_5, Total_SEC, rho, k, pressure_drop, Mcp, U,Hq_p,Hq_b,Hq_Accum_Mgl,Bq_p,Bq_b,Bq_Accum_Mgl      
