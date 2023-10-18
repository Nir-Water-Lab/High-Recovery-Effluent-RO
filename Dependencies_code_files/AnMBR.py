def AnMBR_Analysis (Ca, K, Mg, Na, Cl,SO4,P,Si, J_permeate,t,recovery,u0, ks,P_std,NaCl_std,A,Qw,Rej_NaCl,d_mil,Pw0,Ps0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,feed_pH,Alk_feed,Ct_feed):
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
    # def func(pbar):
        # z = exp (Jw[i] / k[i])
        # cm = ((Ps + Jw[i]) * Cb[i] * z) / (Jw[i] + Ps * z)
        # cp = Ps * Cb[i] * z / (Jw[i] + Ps * z)            
        # return (Jw[i]/Pw) + ((PHI * cm - 0.98 * cp) * T *0.083145) - pbar
    
    """Number of Steps in the Process"""
    step_num = int(recovery + 1)
    #step_num = 31
    """Initialization of variables"""
    T = t + 273.15
    #Ppa = P_feed * 1e5
    kphi = 0;   PHI = 1.0;  PHI_old = 0

    r_f = recovery/100.0;   r = np.linspace(0, r_f, step_num) 
    dr = r[1] - r[0]    # step size
    #print(r)
    d = d_mil * 2.54e-5;    Pbar = np.zeros(len(r))    
    S = np.zeros(len(r));   Cb = np.zeros(len(r))
    S0 = (Cl * 35.453 + Na * 22.98977 + Mg * 24.305 + Ca * 40.078 + K * 39.098 + SO4 * 96.0626 + P *30.974 + Si * 28.086)
    Cb[0] = (Na + Mg + Ca + K + SO4 + P + Si ) #
     

    Cp = np.zeros(len(r));  Cm = np.zeros(len(r))
    k = np.zeros(len(r));   Jw = np.zeros(len(r))
    CFb = np.zeros(len(r)); CF = np.zeros(len(r))
    Mcp = np.zeros(len(r)); Ctb = np.zeros(len(r))      #Total carbonate in bulk
    Alkb = np.zeros(len(r)); 
    CPF = np.zeros(len(r))
    osmotic_pressure = np.zeros(len(r))
    Pbar = np.zeros(len(r))
    
    pressure_drop = np.zeros(len(r)); U = np.zeros(len(r))
    Re_c = np.zeros(len(r)); Sh = np.zeros(len(r)); pH_b = np.zeros(len(r))
    Ctb=np.zeros(len(r));Ctp=np.zeros(len(r));Alkb=np.zeros(len(r));Alkp=np.zeros(len(r))
    pH_m=np.zeros(len(r)); pH_p=np.zeros(len(r))
    CO2_b=np.zeros(len(r));HCO3_b=np.zeros(len(r));CO3_b=np.zeros(len(r))
    Theta=np.zeros(len(r)); w_H_eff=np.zeros(len(r)); w_OH_eff=np.zeros(len(r))
    Ptb =np.zeros(len(r))

    pH = np.zeros(len(r))
    pH1 = np.zeros(len(r))
    pH2 = np.zeros(len(r))
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
    if Pw0==0:
        Pw0=Pw_std
    if Ps0==0:
        Ps0=Ps_std

    Pw= Pw0*exp(0.0093*(T - 298.15))  #Taniguchi et al. 2001
    Ps= Ps0*exp(0.0483*(T - 298.15))  #Taniguchi et al. 2001 

    #Cl =np.zeros(len(r)) 
    #Cl_Added =np.zeros(len(r)) 
    #Cl =np.linspace(0.009421,0.0846191,99)
    #Cl =np.linspace(0.011959,0.0940682,41)
    #pH =np.linspace(8.27,9.31,99)
    #pH2 = np.linspace(8.27, 9.31, 49)
    # pH = np.concatenate((pH1, pH2))
    #pH = np.linspace(8.45,9.31,31)
    #print(len(r))

    Feed = """
            SOLUTION 1 seawater
            units     mol/l
            temp     %f
            pH       %f
            Na       %e
            Mg       %e
            K        %e
            Ca       %e
            S(6)     %e 
            P        %e
            Si       %e 
            USE solution 1
            USER_PUNCH
            -headings ALK Ct Pt RHO
            -start
            10 PUNCH ALK
            20 PUNCH TOT("C")
            30 PUNCH TOT("P")
            40 PUNCH RHO
             -end
            SELECTED_OUTPUT
            -reset          false
            -user_punch     true
            -high_precision     true
            END"""%(t,feed_pH,Na,Mg,K,Ca,SO4,P,Si)

    sol_feed = phreecalc(Feed)
    #print(sol_feed)

    Alkb[0]=sol_feed[1][0] #/((1+S0/1000)/(rho/1000))
    Ctb[0]=sol_feed[1][1] #/((1+S0/1000)/(rho/1000))
    Ptb[0]=sol_feed[1][2]
    rho= sol_feed[1][3] 

    print ('Calculating Osmotic Pressure and salt concentration:'    )   

    for i in range (len(r)):
        
        U[i] = u0 * (1.0-r[i])

        # def func(pbar):
            # z = exp (Jw[i] / k[i])
            # cm = ((Ps + Jw[i]) * Cb[i] * z) / (Jw[i] + Ps * z)
            # cp = Ps * Cb[i] * z / (Jw[i] + Ps * z)            
            # return (Jw[i]/Pw) + ((PHI * cm - 0.98 * cp) * T *0.083145) - pbar
        PHI = 1.0
        """Mass transfer coefficient"""
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
                Si       %e
                USE solution 1 
                USER_PUNCH
                -headings RHO osmotic_coefficient 
                -start
                10 PUNCH RHO
                20 PUNCH OSMOTIC
                 -end
                SELECTED_OUTPUT
                -reset          false
                -user_punch     true
                 END"""%(t,7,Cl/(1-r[i]),Na/(1-r[i]),Mg/(1-r[i]),K/(1-r[i]),Ca/(1-r[i]),S/(1-r[i])) 
            sol_rho = phreecalc(RHO_PHREE)
            #print(sol_rho)
            rho = 1000*sol_rho[1][0]
            PHI = sol_rho[1][1] 

            S[i]=S0/(1-r[i])    # bulk salinity in kg/m^3 
            visc = visco(t, S[i])

            D_NaCl = (6.725 * 10 ** -6) * exp(0.1546 * S[i] * 10 ** -3 - 2513 / T)  # Diffusivity  of NaCl in seawater in  m^2/s  from taniguchi et al 2001
            Sc = visc / (rho * D_NaCl)          #Schmidths number 
            Re_c[i] = (rho * U[i] * 2 * d ) / visc
            Sh[i] = 0.065*(Re_c[i] ** 0.875) * (Sc ** 0.25)             #Schock and Miquel 1987
            k[i] = Sh[i] * D_NaCl / d                                   # mass transfer coefficient in m/sec

        Jw[i] = J_permeate 
        """find Pbar(i), Cm(i) and PHI(i)"""
        CF[i] = 1/(1-r[i])
        PHI_old =10
        while (abs(PHI-PHI_old)>0.001):
            PHI_old=PHI
            osmo_phree = """
                SOLUTION 1 efluent 
                units      mol/l
                temp       %f
                pH         %f 
                Na         %e
                Mg         %e
                Ca         %e
                K          %e
                SO4        %e
                P          %e
                Si         %e
                C(4)       %f   mg/l
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
                -high_precision     true
                -pH             true
                END"""%(t,6.5,Na,Mg,Ca,K,SO4,P,Si,Ct_feed)
            sol_osm=phreecalc(osmo_phree)
            pH_b = sol_osm[1][0]
            PHI = sol_osm[1][1] 
            rho = sol_osm[1][2]
            #Pbar[i] = optimize.bisect(func,0 ,30, xtol = 3, rtol = 20, maxiter = 500)
            
            #Cp[i] = (Cl[i]*Ps*exp(Jw[i]/k[i]))/(Jw[i]+Ps*exp(Jw[i]/k[i]))           #SD model
            Cp[i] = (Cb[i]*Ps*exp(Jw[i]/k[i]))/(Jw[i]+Ps*exp(Jw[i]/k[i]))
            Cm[i] = Cp[i] +(Cb[i]-Cp[i])*exp(Jw[i]/k[i])    #, film theory
            CF[i] = Cm[i]/Cb[0]       #concentration polarization factor (CF) for the i-th stage of the reverse osmosis process
            
            
            kphi=kphi+1 

        
        #print(f"i: {i}, Cb[i]: {Cb[i]}, Ps: {Ps}, Jw[i]: {Jw[i]}, k[i]: {k[i]}")

        osmotic_pressure[i] = (PHI * Cm[i] - 0.98 * Cp[i]) * T *0.083145
        if r[i]<recovery/100:
            Cb[i+1] = (Cb[i] *(1-r[i]) - dr*Cp[i])/(1-r[i+1])   
        CFb[i] = Cb[i]/Cb[0] 
        
        Pbar[i]= (Jw[i]/Pw) + ((PHI * Cm[i] - 0.98 * Cp[i]) * T *0.083145)
    #print(Cb[50])
    #print(pH[i])    


    print ('Done \n\n'  )

    return r, Jw,Cb,Cp,Cm,osmotic_pressure,Pbar,pH_b

            