import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
def extraction_WIND(chemin):
    df=pd.read_csv(chemin,sep=';',encoding="latin-1")
    Date=df['Horodate']
    Puiss=df[(df['Filière de production']=='F4 : Eolien')]
#On fait ici la liste des Horodates différentes, en effet comme il est possible d'avoir jusqu'à 13 consommations
# et production par horodate il est préférable de les regrouper pour les tracers futurs.
    L_Horodate=[Date[1]]
    for date in Date:
        if date != L_Horodate[-1]:
            L_Horodate.append(date)
#On rempli maintenant les puissances par horodate si nécessaire
    P=[]
    for horodate in L_Horodate:
        P.append(sum(Puiss[(Puiss['Horodate']== horodate)]['Total énergie injectée (Wh)']))
    plt.figure()
    plt.plot(np.arange(0,len(L_Horodate)/2,0.5),P,linestyle='solid')
    plt.xlabel('Time (h)')
    plt.ylabel('Energy (TWh)')
    plt.show()
extraction_WIND("C:/Users/Thiba/OneDrive/Documents/2021_2022/TAF/ARPE/Data_PV_Wind/prod_Eolien_OCC_5_mai_puissance_sup_12MW.csv")