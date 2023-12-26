def Effluent(Ca, K, Mg, Na, Cl,SO4,P, Fe, P_feed,t,recovery,kt, ks,P_std,NaCl_std,A,Qw,Rej_NaCl,d_mil,Pw1,Ps1,Pw2,Ps2,Pw3,Ps3,Pw4,Ps4,Pco2,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,C,GR,alpha,gamma,sigma,L,feed_pH,Nt_feed,Ct_feed,Alk_feed,first_stage, second_stage, third_stage, fourth_stage):
     
    # Import standard library modules first.
    #import sys
    # Then get third party modules.
    from win32com.client import Dispatch 
    #import matplotlib.pyplot as plt 
    import numpy as np 
    from math import exp,sqrt
    #from mpmath import mp
    import scipy.optimize as optimize


    
    def selected_array(db_path1, input_string):
        """Load databases via COM and run input string."""
        dbase1 = Dispatch('IPhreeqcCOM.Object')
        # Load the first database
        dbase1.LoadDatabase(db_path1)

        # Run the input script for both databases
        dbase1.RunString(input_string)

        return dbase1.GetSelectedOutputArray()


    def selected_arrayy(db_path2, input_stringg):
        """Load databases via COM and run input string."""
        dbase2 = Dispatch('IPhreeqcCOM.Object')
    
        # Load the second database
        dbase2.LoadDatabase(db_path2)

        # Run the input script for both databases
        dbase2.RunString(input_stringg)

        # Return the results from both databases
        return dbase2.GetSelectedOutputArray()


    def phreecalc(input_string):
        """Get results from PHREEQC"""
        pitzer_result = selected_array('sit.dat',  input_string)
        return pitzer_result
    
    def phreecalc1(input_stringg):
        """Get results from PHREEQC"""
        minteq_result = selected_arrayy('minteq.v4.dat', input_stringg)
        return minteq_result
    

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

    S0 = (Cl * 35.453 + Na * 22.98977 + Mg * 24.305 + Ca * 40.078 + K * 39.098 + SO4 * 32.065 + Fe * 55.845 + P * 30.974)
    Cb[0] = (Cl + Na + Mg + Ca + K + SO4 + Fe + P + Ct_feed + Nt_feed/14011)
    
    
    Cp = np.zeros(len(r));  Cm = np.zeros(len(r))
    k = np.zeros(len(r));   Jw = np.zeros(len(r))
    CFb = np.zeros(len(r)); CF = np.zeros(len(r))
    Mcp = np.zeros(len(r)); Ctb = np.zeros(len(r))      #Total carbonate in bulk
    Alkb = np.zeros(len(r)); Ctp=np.zeros(len(r))
    Alkp=np.zeros(len(r))
    Ptb = np.zeros(len(r))
    Ptp = np.zeros(len(r))
    Ntb = np.zeros(len(r))
    Ntp = np.zeros(len(r))
    Ntp_Accum =np.zeros(len(r))

    pressure_drop = np.zeros(len(r));   Fd = np.zeros(len(r)); U = np.zeros(len(r))
    Re_c = np.zeros(len(r));    Sh = np.zeros(len(r)); pH_b = np.zeros(len(r))    
    pH_m = np.zeros(len(r));    pH_p=np.zeros(len(r));  Theta=np.zeros(len(r))     
    w_H_eff=np.zeros(len(r));   w_OH_eff=np.zeros(len(r))
    

    # Carbonate Species
    HCO3_b=np.zeros(len(r));    CO3_b=np.zeros(len(r)); H2CO3_b = np.zeros(len(r)) ; CO2_b = np.zeros(len(r))
    HCO3_bt = np.zeros(len(r)); CO3_bt = np.zeros(len(r))
    #Phosphate Species
    HPO4_2_b = np.zeros(len(r)); HPO4_2_p = np.zeros(len(r)); PO4_3_b = np.zeros(len(r))
    PO4_3_p = np.zeros(len(r)); H2PO4_b = np.zeros(len(r)); H2PO4_p = np.zeros(len(r)); H3PO4_b = np.zeros(len(r)); H3PO4_p = np.zeros(len(r))

    HPO4_2_bt = np.zeros(len(r)); PO4_3_bt = np.zeros(len(r)); H2PO4_bt = np.zeros(len(r)); H3PO4_bt = np.zeros(len(r))

    #Ammonium Species
    NH4_b = np.zeros(len(r)); NH4_p = np.zeros(len(r)); NH3_b = np.zeros(len(r)); NH3_p = np.zeros(len(r))
    NH4_bt = np.zeros(len(r)); NH3_bt = np.zeros(len(r))

    Pnh4 = np.zeros(len(r))  #Pnh4 Ammonium ion permeability
    theta_m = np.zeros(len(r))
    """SI """
     
    d_CaPhosphate = np.zeros(len(r))
    SI_Armp_CaPhosphate = np.zeros(len(r))




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

    # Pw0 = Pw_std if Pw0 == 0 else Pw0
    # Ps0 = Ps_std if Ps0 == 0 else Pw0

    Pw1 = Pw_std if Pw1 == 0 else Pw1       
    Ps1 = Ps_std if Ps1 == 0 else Ps1

    Pw2 = Pw_std if Pw2 == 0 else Pw2       
    Ps2 = Ps_std if Ps2 == 0 else Ps2

    Pw3 = Pw_std if Pw3 == 0 else Pw3       
    Ps3 = Ps_std if Ps3 == 0 else Ps3

    Pw4 = Pw_std if Pw4 == 0 else Pw4       
    Ps4 = Ps_std if Ps4 == 0 else Ps4


    """Temperature corrections for permeability constants"""
    Pw1= Pw1*exp(0.0093*(T - 298.15))  #Taniguchi et al. 2001
    Ps1= Ps1*exp(0.0483*(T - 298.15))  #Taniguchi et al. 2001
    Pw2= Pw2*exp(0.0093*(T - 298.15))  #Taniguchi et al. 2001
    Ps2= Ps2*exp(0.0483*(T - 298.15))  #Taniguchi et al. 2001
    Pw3= Pw3*exp(0.0093*(T - 298.15))  #Taniguchi et al. 2001
    Ps3= Ps3*exp(0.0483*(T - 298.15))  #Taniguchi et al. 2001
    Pw4= Pw4*exp(0.0093*(T - 298.15))  #Taniguchi et al. 2001
    Ps4= Ps4*exp(0.0483*(T - 298.15))  #Taniguchi et al. 2001

    # """Pw=Pw0*exp(2640*(1/T-1/298.15))  #alternative ROSA equation"""
    
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
            S(6)      %e
            Fe       %e
            P        %e
            N(-3)        %f mg/l
            C(4)        %e
            USE solution 1
            USER_PUNCH
            -headings ALK Ct Pt Nt  RHO  
            -start           
            10 PUNCH ALK
            20 PUNCH TOT("C")
            30 PUNCH TOT("P")
            40 PUNCH TOT("N")
            50 PUNCH RHO
             -end
            SELECTED_OUTPUT
            -reset          false
            -user_punch     true
            END"""%(t,feed_pH,Cl,Na,Mg,K,Ca,SO4,Fe,P,Nt_feed,Ct_feed)
    #sol_feed = phreecalc(Feed)
     
    sol_feed_minteq = phreecalc1(Feed)
    #print(sol_feed)
    #print(sol_feed_sit)
    #print(sol_feed_minteq)

    Alkb[0]=sol_feed_minteq[1][0]
    Ctb[0]=sol_feed_minteq[1][1] 
    Ptb[0]=sol_feed_minteq[1][2]
    Ntb[0]= sol_feed_minteq[1][3]
    rho= sol_feed_minteq[1][4]
    
    

    
    
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
        # # #Crossflow velocity corrections per stage
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
        if ks == 0:     #If ks is not provided, it computes for the value of ks as below and assigns it for each recovery step
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
                Fe       %e
                USE solution 1
                REACTION_PRESSURE 1
                %f
                USER_PUNCH
                -headings RHO osmotic_coefficient 
                -start
                10 PUNCH RHO
                20 PUNCH OSMOTIC
                 -end
                SELECTED_OUTPUT
                -reset          false
                -user_punch     true
                END"""%(t,7,Cl/(1-r[i]),Na/(1-r[i]),Mg/(1-r[i]),K/(1-r[i]),Ca/(1-r[i]),SO4/(1-r[i]),Fe/(1-r[i]),  Pbar[i])
            
            sol_rho_sit = phreecalc(RHO_PHREE)
            rho = 1000*sol_rho_sit[2][0]
            PHI = sol_rho_sit[2][1]
            """Mass Transfer
            Re_c = Reynolds number, crossflow velocity
            rho = fluid density
            D_Nacl = Solute Diffusivity
            d = filament Diamter
            visc = dynamic viscosity
            Sh = Sherwoods Number
            Sc = Schmidts  Number
            """
            if i <= third_stage:
                S[i] = S0 / (1 - r[i])      # bulk salinity in kg/m^3
            else:
                S[i] = S0/ (2-r[i])
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
            #u5 = (U[94] + U[98])/2      
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
            else:
                pressure_drop[i] = (Fd[i]*rho * (u4*u4)*L)/2*d

            
            ## Concentration Polarization Modulus
            Mcp[i] = C * (Re_c[i] ** alpha) * (Sc ** gamma) * (GR ** sigma) + 1 
                       
            #Calculating pressure per stage [0.67, 0.37, 2.58, 7.0 ]
        pressure_boost = [1.01, 1.5, 5.2]
        if i <= first_stage:
            Pbar[i] = P_feed - pressure_drop[i] * (r[i]/r[len(r)-1])
        elif first_stage < i <= second_stage:
            Pbar[i] = Pbar[first_stage] + pressure_boost[0] - pressure_drop[i] * (r[i]/r[len(r)-1])
        elif second_stage < i <= third_stage:
            Pbar[i] = Pbar[second_stage] + pressure_boost[1] - pressure_drop[i] * (r[i]/r[len(r)-1])
        else:
            Pbar[i] = Pbar[third_stage] + pressure_boost[2] - pressure_drop[i] * (r[i]/r[len(r)-1])
        #else:
            #Pbar[i] = Pbar[fourth_stage] + pressure_boost[3] - pressure_drop[i] * (r[i]/r[len(r)-1])

            
        
        """find Jw(i), Cm(i) and PHI(i)"""
        CF[i] = 1/(1-r[i])         #Concentration factor    
        PHI_old =10
        while (abs(PHI-PHI_old)>0.001):     # loop that runs until the absolute difference between PHI and PHI_old is less than or equal to 0.001
            
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
                Fe         %e
                C          %e          
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
                 END"""%(t,7,Cl*CF[i],Na*CF[i],Mg*CF[i],K*CF[i],Ca*CF[i],SO4*CF[i],Fe*CF[i], Ctb[i])
            sol_osm_sit = phreecalc(osmo_phree)
            PHI = sol_osm_sit[1][0] 
            rho = sol_osm_sit[1][1]
            #print(PHI,rho)
            Jw[i] = optimize.bisect(func,1e-8 ,1e-4, xtol = 1e-17, rtol = 5e-15, maxiter = 500)   #uses the bisection method to find Jw within the boundary conditions
             

            Cp[i] = (Cb[i]*Ps*exp(Jw[i]/k[i]))/(Jw[i]+Ps*exp(Jw[i]/k[i]))           #SD model
            Cm[i] = Cp[i] +(Cb[i]-Cp[i])*exp(Jw[i]/k[i])    # eqn1 WATRO mass balance, film theory
            CF[i] = Cm[i]/Cb[0]       #concentration factor (CF) for the i-th stage of the reverse osmosis process            
            kphi=kphi+1


        if r[i]< recovery/100:       #checks if the current recovery rate r[i] is less than the target recovery rate 
            Cb[i+1] = (Cb[i]*(1-r[i]) - dr*Cp[i])/(1-r[i+1])          
        CFb[i] = Cb[i]/Cb[0]

        """Calculate average flux per stage"""
        first_stage_Avg_flux = (sum(Jw[:first_stage + 1]) / (first_stage + 1)) * 3600000 
        second_stage_Avg_flux = (sum(Jw[first_stage + 1:second_stage + 1]) / (second_stage - first_stage)) * 3600000
        third_stage_Avg_flux = (sum(Jw[second_stage + 1:third_stage + 1]) / (third_stage - second_stage)) * 3600000 
        fourth_stage_Avg_flux = (sum(Jw[third_stage + 1:fourth_stage + 1]) / (fourth_stage - third_stage)) * 3600000
        #fifth_stage_Avg_flux = (sum(Jw[fourth_stage + 1:]) / (fifth_stage - fourth_stage + 1)) * 3600000  
        

    

    #print(first_stage_Avg_flux,second_stage_Avg_flux,third_stage_Avg_flux,fourth_stage_Avg_flux)

    for i in range(len(r) - 1):

        bulk_speciation = """
            SOLUTION 1 effluent
            units     mol/kgw
            temp        %f
            pH          %f
            Cl          %e
            S(6)        %e   
            Na          %e 
            Mg          %e 
            K           %e 
            Ca          %e 
            Fe          %e
            C(4)        %e
            P           %e
            N(-3)       %e
            Alkalinity    %e
            USE solution 1
            REACTION_PRESSURE 1
            %f
            SELECTED_OUTPUT
            -reset    false
            -high_precision     true
            -ph       true
            -molalities    HCO3-  H2CO3  CO3-2  PO4-3  HPO4-2  H2PO4-  H3PO4  NH4+  NH3  OH-  H+  MgOH+  HSO4-  MgCO3  NH4SO4-  MgPO4-  CaHCO3+  NaHCO3  CaCO3  MgHCO3+  NaCO3-  FeHCO3+
                CaHPO4 FeHPO4  KHPO4-  MgHPO4  NaHPO4-  FeHPO4+ CaH2PO4+  FeH2PO4+  FeH2PO4+2  MgH2PO4+  CaNH3+2  Ca(NH3)2+2  CaOH+  FeOH+  Fe(OH)2  Fe(OH)3-  Fe(OH)4-  FeOH+2  Fe2(OH)2+4
            -saturation_indices  Ca3(PO4)2(beta)
            -equilibrium_phases  Ca3(PO4)2(beta) 
            EQUILIBRIUM_PHASES 1
                Ca3(PO4)2(beta) 0 0        
            END"""%(t,7.0,Cl*CFb[i],SO4/(1-r[i]),Na*CFb[i],Mg/(1-r[i]),K*CFb[i],Ca/(1-r[i]),Fe/(1-r[i]),Ctb[i],Ptb[i],Ntb[i],Alkb[i],Pbar[i])
        
        
        sol_bulk_minteq = phreecalc1(bulk_speciation)
        #print(sol_bulk_minteq)
        
        pH_b[i]=sol_bulk_minteq[2][0];  
        HCO3_b[i]=sol_bulk_minteq[2][1];  CO2_b[i]=sol_bulk_minteq[2][2] ; #CO3_b[i] = sol_bulk_minteq[2][3]
        HPO4_2_b[i] = sol_bulk_minteq[2][5];  H2PO4_b[i] = sol_bulk_minteq[2][6]; H3PO4_b[i] =sol_bulk_minteq[2][7]
        #print(pH_b)
        NH3_b[i] = sol_bulk_minteq[2][9]
        OH_b=sol_bulk_minteq[2][10]; H_b=sol_bulk_minteq[2][11]; MgOH_b=sol_bulk_minteq[2][12]; HSO4_b = sol_bulk_minteq[2][13]; MgCO3_b = sol_bulk_minteq[2][14]
        MgPO4_b =sol_bulk_minteq[2][15]; CaHCO3_b = sol_bulk_minteq[2][16]; NaHCO3_b = sol_bulk_minteq[2][17]; CaCO3_b = sol_bulk_minteq[2][18]; MgHCO3_b = sol_bulk_minteq[2][19]; 
        NaCO3_b = sol_bulk_minteq[2][20];   FeHCO3_b = sol_bulk_minteq[2][21]
        CaHPO4_b =sol_bulk_minteq[2][22]  ; FeHPO4_b =sol_bulk_minteq[2][23] ; KHPO4_b = sol_bulk_minteq[2][24] ; MgHPO4_b = sol_bulk_minteq[2][25] ; NaHPO4_b = sol_bulk_minteq[2][26]; FeHPO4_b1 = sol_bulk_minteq[2][27]
        CaH2PO4_b = sol_bulk_minteq[2][28]; FeH2PO4_b = sol_bulk_minteq[2][29]; FeH2PO42_b = sol_bulk_minteq[2][30];  MgH2PO4_b = sol_bulk_minteq[2][31]
        CaNH3_2b = sol_bulk_minteq[2][32]; CaNH322_b = sol_bulk_minteq[2][33]
        CaOH_b = sol_bulk_minteq[2][34];  FeOH_b = sol_bulk_minteq[2][35]; Fe_OH_2b = sol_bulk_minteq[2][36]; Fe_OH_3_b = sol_bulk_minteq[2][37];  Fe_OH_4_b = sol_bulk_minteq[2][38];  FeOH_2b = sol_bulk_minteq[2][39];  Fe2_OH_2_4b = sol_bulk_minteq[2][40] 
        
        d_CaPhosphate[i] = sol_bulk_minteq[2][42]; SI_Armp_CaPhosphate[i] = sol_bulk_minteq[2][43]

        "Summing Ion-pairs"
        OH_bt = OH_b + MgOH_b + CaOH_b + FeOH_b + Fe_OH_2b + Fe_OH_3_b + Fe_OH_4_b + FeOH_2b + Fe2_OH_2_4b
        H_bt = H_b + HSO4_b 
        HCO3_bt[i] = HCO3_b[i] + CaHCO3_b + NaHCO3_b + MgHCO3_b + FeHCO3_b 
        CO3_b[i] = Ctb[i] - HCO3_bt[i] - CO2_b[i]

        HPO4_2_bt[i] = HPO4_2_b[i] +  CaHPO4_b + FeHPO4_b + KHPO4_b + MgHPO4_b +  NaHPO4_b + FeHPO4_b1
        H2PO4_bt[i] = H2PO4_b[i] + CaH2PO4_b +  FeH2PO4_b +  FeH2PO42_b +   MgH2PO4_b   
        PO4_3_b[i] = Ptb[i] - HPO4_2_bt[i] - H2PO4_bt[i] - H3PO4_b[i]

        NH3_bt[i] = NH3_b[i] + CaNH3_2b + CaNH322_b
        NH4_b[i] = Ntb[i] - NH3_bt[i]

        """Using a Linear Function to find NH4+ permeability over the pH range of 4.5, 7 (interpolating), > 8.5 permeability maintained"""
        if pH_b[i] < 8.5:
            Pnh4[i] = (-5e-8*pH_b[i]) + 2e-6   
        else:
            Pnh4[i] = 1.2e-6
        
    
        """Resolving Cpt using SDEF theory"""
        omega_cat = 0.549e-6 #Na
        Omega_an = 0.310e-6 #Cl
        zs_cat = 1#Na

        zs_an = -1#Cl
        Rs = 1-Cp[i]/Cm[i]
        theta_m[i] = -0.0486* (pH_b[i]*pH_b[i]) + (0.7373*pH_b[i]) - 2.6937       #BW30LE
        #theta_m[i] = -0.031* (pH_b[i]*pH_b[i]) + (0.5433*pH_b[i]) - 2.0069      # XLE
        #theta_m[i] = -0.0323* (pH_b[i]*pH_b[i]) + (0.6078*pH_b[i]) - 2.3605       #SW30HRLE
        denum1 = Pnh4[i]*(1-Rs)**(theta_m[i])
        denum2 = Jw[i]*(1-(1-Rs)**(1-theta_m[i]))/(Rs*(1-theta_m[i])) 
        """NH4_m using RO Case for trace ion CP;Analytical solution for trace ion CP"""
        Ds_cat = 1.334e-9 #Diffusion Coeff. Na
        Ds_an = 2.031e-9  #Diffusion Coeff. Cl
        Ds = ((zs_cat - zs_an)* (Ds_cat*Ds_an))/(zs_cat*Ds_cat - zs_an*Ds_an) #Diffusion coefficient of the dominant salt
        delta = Ds/k[i]        #Boundary layer thickness
        Dt = 1.98e-9           #Diffusion coef. of NH4+ 
        theta_delta = (Ds_cat - Ds_an)/(zs_cat * Ds_cat - zs_an * Ds_an)
   
        #Using the solution-diffusion-film model, transport; HPO4_2, H2PO4, H3PO4,  HCO3, CO2
        if i==0:
            """Carbonate system"""
            HCO3_p= (Ps*HCO3_bt[0]*exp(Jw[i]/k[i]))/(Jw[0]+Ps*exp(Jw[i]/k[i])) 
            CO2_p=  (Pco2 *CO2_b[0] *exp(Jw[i]/k[i]))/(Jw[0]+Pco2*exp(Jw[i]/k[i]))
            #CO2_p=  CO2_b[i]
            Ctp[0]=HCO3_p+CO2_p 
            """Phosphate system"""
            H2PO4_p =  (Ps*H2PO4_bt[0]*exp(Jw[i]/k[i]))/(Jw[0]+Ps*exp(Jw[i]/k[i]))
            H3PO4_p = (Ps*H3PO4_b[0]*exp(Jw[i]/k[i]))/(Jw[0]+Ps*exp(Jw[i]/k[i]))    
            #H3PO4_p = H3PO4_b[i]
            Ptp[0] =  H2PO4_p  + H3PO4_p
            """Ammonium System"""
            #NH4_p = (Pnh4*NH4_b[0]*exp(Jw[i]/k[i]))/(Jw[0]+Pnh4*exp(Jw[i]/k[i])) # SD Theory
            #NH4_p = (Pnh4* NH4_b[0] * exp((Jw[i]*delta)/Dt)*exp((Jw[i]*theta_delta)/k[i]))/(denum1 + denum2) #SDEF
            #NH3_p = NH3_b[i]
            #NH3_p=  (Pco2 *NH3_bt[0] *exp(Jw[i]/k[i]))/(Jw[0]+Pco2*exp(Jw[i]/k[i]))      #Assuming same  permeability as C02
            # Ntp[0] = NH4_p + NH3_p
            # Ntp_Accum[0] = Ntp[0]

            OH_p = 0
            H_p = 0
    
        CO3_m=CO3_b[i]*exp(Jw[i]/k[i])
        PO4_3_m = PO4_3_b[i]*exp(Jw[i]/k[i])
        HPO4_2_m = HPO4_2_bt[i]*exp(Jw[i]/k[i])
        CO2_m = CO2_b[i] 
        H3PO4_m = H3PO4_b[i]
        NH3_m = NH3_bt[i]
        """Estimation of weak acid species concentration in the film layer"""
        HCO3_m=HCO3_p+(HCO3_bt[i]-HCO3_p)*exp(Jw[i]/k[i]) 
        H2PO4_m = H2PO4_p + (H2PO4_bt[i] - H2PO4_p)*exp(Jw[i]/k[i])
        #NH4_m = NH4_p + (NH4_b[i] - NH4_p)*exp(Jw[i]/k[i]) #
        """NH4_m using RO Case for trace ion CP;Analytical solution for trace ion CP"""
        #Ds_cat = 1.334e-9 #Diffusion Coeff. Na
        #Ds_an = 2.031e-9  #Diffusion Coeff. Cl
        #Ds = ((zs_cat - zs_an)* (Ds_cat*Ds_an))/(zs_cat*Ds_cat - zs_an*Ds_an) #Diffusion coefficient of the dominant salt
        #delta = Ds/k[i]        #Boundary layer thickness
        #Dt = 1.98e-9           #Diffusion coef. of NH4+ 
        #theta_delta = (Ds_cat - Ds_an)/(zs_cat * Ds_cat - zs_an * Ds_an)
        NH4_m = NH4_b[i] * exp((Jw[i]*delta)/Dt)*exp((Jw[i]*theta_delta)/k[i])

        OH_m = OH_p+(OH_bt-OH_p)*exp(Jw[i]/(3.34*k[i]))   ## ?????
        H_m = H_p+(H_bt-H_p)*exp(Jw[i]/(5.62*k[i])) 

        """Weak acid species Mass balance in the film layer"""
        Ctm = CO3_m + HCO3_m + CO2_m 
        Ptm = PO4_3_m + HPO4_2_m+ H2PO4_m + H3PO4_m
        Ntm = NH4_m + NH3_m 
        #print(HPO4_2_m, H2PO4_m, H3PO4_m, PO4_3_m)
        """Alkalinity mass balance in the film layer""" 
        Alkm= HCO3_m + (2*CO3_m) - H3PO4_m +  HPO4_2_m + (2 * PO4_3_m) + NH3_m +  OH_m - H_m   
        #print(Alkm)
        film_speciation = """
            SOLUTION 1 effluent
            units     mol/kgw
            temp        %f
            pH          %f
            Cl          %e
            S(6)        %e   
            Na          %e 
            Mg          %e 
            K           %e 
            Ca          %e
            Fe          %e
            C(4)        %e
            P           %e
            N(-3)       %e
            Alkalinity    %e 
            USE solution 1
            REACTION_PRESSURE 1
            %f
            SELECTED_OUTPUT
            -reset    false
            -high_precision     true
            -ph       true
            -molalities    HCO3-  H2CO3  CO3-2  PO4-3  HPO4-2  H2PO4-  H3PO4  NH4+  NH3  OH-  H+  MgOH+  HSO4-  MgCO3  NH4SO4-  MgPO4-  CaHCO3+  NaHCO3  CaCO3  MgHCO3+  NaCO3-  FeHCO3+
                CaHPO4 FeHPO4  KHPO4-  MgHPO4  NaHPO4-  FeHPO4+ CaH2PO4+  FeH2PO4+  FeH2PO4+2  MgH2PO4+  CaNH3+2  Ca(NH3)2+2  CaOH+  FeOH+  Fe(OH)2  Fe(OH)3-  Fe(OH)4-  FeOH+2  Fe2(OH)2+4  
            END"""%(t,7,CF[i]*Cl,CF[i]*SO4,CF[i]*Na,CF[i]*Mg,CF[i]*K,CF[i]*Ca,CF[i]*Fe,Ctm,Ptm,Ntm,Alkm,Pbar[i])
            
            
        sol_film_minteq = phreecalc1(film_speciation)
        #print(sol_film_minteq)
        pH_m[i]=sol_film_minteq[2][0];  
        HCO3_m=sol_film_minteq[2][1];  H2CO3_m = sol_film_minteq[2][2] ; #CO3_m[i] = sol_film_minteq[2][3]
        HPO4_2_m = sol_film_minteq[2][5];  H2PO4_m = sol_film_minteq[2][6]; H3PO4_m =sol_film_minteq[2][7]
        #print(pH_b)
        NH3_m = sol_film_minteq[2][9]
        OH_m=sol_film_minteq[2][10]; H_m=sol_film_minteq[2][11]; MgOH_m=sol_film_minteq[2][12]; HSO4_m = sol_film_minteq[2][13]; MgCO3_m = sol_film_minteq[2][14]
        MgPO4_m =sol_film_minteq[2][15]; CaHCO3_m = sol_film_minteq[2][16]; NaHCO3_m = sol_film_minteq[2][17]; CaCO3_m = sol_film_minteq[2][18]; MgHCO3_m = sol_film_minteq[2][19]; 
        NaCO3_m = sol_film_minteq[2][20];   FeHCO3_m = sol_film_minteq[2][21]
        CaHPO4_m =sol_film_minteq[2][22]  ; FeHPO4_m =sol_film_minteq[2][23] ; KHPO4_m = sol_film_minteq[2][24] ; MgHPO4_m = sol_film_minteq[2][25] ; NaHPO4_m = sol_film_minteq[2][26]; FeHPO4_m1 = sol_film_minteq[2][27]
        CaH2PO4_m = sol_film_minteq[2][28]; FeH2PO4_m = sol_film_minteq[2][29]; FeH2PO42_m = sol_film_minteq[2][30];  MgH2PO4_m = sol_film_minteq[2][31]
        CaNH3_2m = sol_film_minteq[2][32]; CaNH322_m = sol_film_minteq[2][33]
        CaOH_m = sol_film_minteq[2][34];  FeOH_m = sol_film_minteq[2][35]; Fe_OH_2m = sol_film_minteq[2][36]; Fe_OH_3_m = sol_film_minteq[2][37];  Fe_OH_4_m = sol_film_minteq[2][38];  FeOH_2m = sol_film_minteq[2][39];  Fe2_OH_2_4m = sol_film_minteq[2][40] 
            
        """ Summing Ion-pairs"""
        "Summing Ion-pairs"
        OH_mt = OH_m + MgOH_m + CaOH_m + FeOH_m + Fe_OH_2m + Fe_OH_3_m + Fe_OH_4_m + FeOH_2m + Fe2_OH_2_4m
        H_mt = H_m + HSO4_m 
        HCO3_mt = HCO3_m + CaHCO3_m + NaHCO3_m + MgHCO3_m + FeHCO3_m 
        CO3_m = Ctm - HCO3_mt - H2CO3_m
        HPO4_2_mt = HPO4_2_m +  CaHPO4_m + FeHPO4_m + KHPO4_m + MgHPO4_m +  NaHPO4_m + FeHPO4_m1
        H2PO4_mt = H2PO4_m + CaH2PO4_m +  FeH2PO4_m +  FeH2PO42_m +   MgH2PO4_m  
        PO4_3_m = Ptm - HPO4_2_mt - H2PO4_mt - H3PO4_m
        NH3_mt = NH3_m + CaNH3_2m + CaNH322_m
        NH4_m = Ntm - NH3_mt
            

        """Permeate concentrations of Ammonium, carbonate and phosphate species"""
        HCO3_p= (Ps*HCO3_mt)/(Jw[i]+Ps)
        #CO2_p= (Pco2*CO2_m)/(Jw[i]+Pco2)
        H2PO4_p = (Ps*H2PO4_mt)/(Jw[i]+Ps)
        #NH4_p = (Pnh4*NH4_m)/(Jw[i]+Pnh4)
        #kk=kk+1
        H2CO3_p = (Pco2*H2CO3_m)/(Jw[i]+Pco2)
        H3PO4_p = (Ps*H3PO4_m)/(Jw[i]+Ps)
        NH3_p = (Pco2*NH3_mt)/(Jw[i]+Pco2)
        # H2CO3_p = H2CO3_m
        # H3PO4_p = H3PO4_m
        # NH3_p = NH3_m

        """Permeation of alkalinity due to NH4 diffusion electromigration"""
        num1 = NH4_m * Pnh4[i]
        NH4_p = num1/(denum1+denum2)
        
        """Weak-acid species mass balance in the permeate"""

        Ctp[i] = HCO3_p + H2CO3_p     
        Ptp[i] = H2PO4_p + H3PO4_p
        Ntp[i] = NH4_p + NH3_p
        Alkp[i]= HCO3_p - H3PO4_p + NH3_p + OH_p - H_p     #Alkalinity mass balance in the permeate


        permeate_speciation = """
            SOLUTION 1 permeate
            units         mol/kgw
            temp          %f
            pH            %f
            Na            %e 
            Cl            %e
            C(4)          %e
            P             %e
            N(-3)         %e
            Alkalinity    %e
            USE solution 1
            SELECTED_OUTPUT
            -reset    false
            -ph       true
            -molalities      HCO3-  H2CO3  CO3-2  PO4-3  HPO4-2  H2PO4-  H3PO4  NH4+  NH3  OH-  H+  NaHCO3  NaCO3-  NaHPO4-                   
             END"""%(t,7,Cp[i]/2,Cp[i]/2,Ctp[i],Ptp[i],Ntp[i],Alkp[i])
        
        sol_permeate_minteq = phreecalc1(permeate_speciation)
        #print(sol_permeate_minteq)
        pH_p[i]=sol_permeate_minteq[1][0];  
        HCO3_p=sol_permeate_minteq[1][1]; H2CO3_p=sol_permeate_minteq[1][2]; CO3_p = sol_permeate_minteq[1][3];  OH_p=sol_permeate_minteq[1][4]; H_p=sol_permeate_minteq[1][5]; 
        PO4_3_p =sol_permeate_minteq[1][6]; HPO4_2_p = sol_permeate_minteq[1][7];  H2PO4_p = sol_permeate_minteq[1][8]; H3PO4_p =sol_permeate_minteq[1][9]
        NH4_p = sol_permeate_minteq[1][10]; NH3_p = sol_permeate_minteq[1][11]; NaHCO3_p = sol_permeate_minteq[1][12]; NaCO3_p = sol_permeate_minteq[1][13]; NaHPO4_p = sol_permeate_minteq[1][14]

        """Summing Ion-pairs"""
        HCO3_p = sol_permeate_minteq[1][1] + NaHCO3_p
        
    
        
        """Phosphate, Carbonate, Ammonium and alkalinity mass balance"""
        if r[i]< recovery/100:       #checks if the current recovery rate r[i]
            Ctb[i+1] = (Ctb[i]*(1-r[i]) - dr*Ctp[i])/(1-r[i+1])
            Ptb[i+1] = (Ptb[i]*(1-r[i]) - dr*Ptp[i])/(1-r[i+1])
            Ntb[i+1] = (Ntb[i]*(1-r[i]) - dr*Ntp[i])/(1-r[i+1])
            Alkb[i+1] = (Alkb[i]*(1-r[i]) - dr*Alkp[i])/(1-r[i+1])

    for i in range(len(r)):
        Ntp_Accum[i] = np.average(Ntp[0:i+1])
    Ntp_Accum_mgl = 14011*Ntp_Accum
                 
    #print(Pnh4)
 

    return r,Jw,Cb,Cp,Cm,Pbar,first_stage_Avg_flux, second_stage_Avg_flux, third_stage_Avg_flux, fourth_stage_Avg_flux, pH_b,pH_p,pH_m,Alkb,Alkm,Alkp,Ctb,Ctp,Ptb,Ptp,Ntb,Ntp,Ntp_Accum_mgl,d_CaPhosphate, SI_Armp_CaPhosphate,Pnh4

    

            
        
           
