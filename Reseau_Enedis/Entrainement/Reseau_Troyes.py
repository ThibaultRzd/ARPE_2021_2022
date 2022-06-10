import numpy as np
import pandapower as pp
import pandas as pd
import xlrd
import pandapower.plotting as ppp
#Création de la database de la ligne d'étude à Noës-près-Troyes : La Database des bus sera constitué de leur numéro,
#position géographique, consommation annuelle moyenne (le voltage sera pris arbitrairement car pas encore connu, l'abonnement sera de 10kv).
Nb_hous=[14,26,10,16,15,15,1,1,15,15,1,1,1,15,1,1,1,1,1,1,1,1,1,1,1,1]

print(len(Nb_hous))
def create_Troyes_net(L_PV_gen):
    #Liste des consommations annuelles des bus
    Conso_mw=[19,52,13,23,22.5,22.5,1.5,94,22.5,22.5,1.4,1.2,1.3,22.8,1.5,1.5,1.5,1.3,1.5,1.5,1.4,1.5,1.5,1.5,1.2,1.1]
    #Nombre d'habitations par bus, on en déduis ensuite la puissance de raccordement ()
    Nb_hous=[14,26,10,16,15,15,1,1,15,15,1,1,1,15,1,1,1,1,1,1,1,1,1,1,1,1]

    #Création des positions des bus d 'habitation (avec une remise à l'origine)
    X_pos_tempo=[251,343,254,231,386,412,407,309,400,295,259,245,219,233,411,456,464,436,420,377,291,269,256,234,221,193]
    Y_pos_tempo=[498,512,518,545,461,483,518,436,472,408,421,433,463,446,546,578,583,562,552,525,536,563,575,483,479,468]
    xmin=min(X_pos_tempo)
    ymin=min(Y_pos_tempo)
    X_pos=[x-xmin for x in X_pos_tempo]
    Y_pos=[y-ymin for y in Y_pos_tempo]

    #Création des positions des bus des embranchements
    X_pos_emb=[393-xmin,320-xmin,211-xmin,293-xmin]
    Y_pos_emb=[536-ymin,504-ymin,481-ymin,500-ymin]

    #Création des dataframe des lignes
    From_bus=['Bus 16','Bus 15','Bus 17','Bus 18','Bus 14','Croisement 0','Bus 6','Bus 5','Bus 8','Croisement 0','Bus 19','Bus 1','Croisement 1','Bus 20','Bus 21','Croisement 1','Poste Source BT','Bus 9','Bus 10','Bus 11','Bus 13','Croisement 2','Croisement 2','Bus 24','Bus 23','Poste Source BT','Croisement 3','Croisement 3','Bus 2','Poste Source BT']
    To_bus=['Bus 15','Bus 17','Bus 18','Bus 14','Croisement 0','Bus 6','Bus 5','Bus 8','Bus 4','Bus 19','Bus 1','Croisement 1','Bus 20','Bus 21','Bus 22','Poste Source BT','Bus 9','Bus 10','Bus 11','Bus 13','Bus 12','Bus 25','Bus 24','Bus 23','Poste Source BT','Croisement 3','Bus 0','Bus 2','Bus 3','Bus 7']
    length=[10,23,15,12,20,20,50,18,20,20,40,25,42,35,15,85,52,48,14,30,13,22,2,25,124,70,35,47,37,10]



    net_noes_pres_troyes=pp.create_empty_network()
    pp.set_user_pf_options(net_noes_pres_troyes, init_vm_pu = "flat", init_va_degree = "dc", calculate_voltage_angles=True)
    #Création du Poste Source HT et du BT
    pp.create_bus(net_noes_pres_troyes,vn_kv=0.4,geodata=[313-xmin,436-ymin],name='Poste Source BT')
    pp.create_bus(net_noes_pres_troyes,vn_kv=20,geodata=[313-xmin,436-ymin],name='Poste Source HT')
    #Création de tous les maisons de la zone étudiée
    for i in range(26):
        pp.create_bus(net_noes_pres_troyes,vn_kv=0.4,geodata=[X_pos[i],Y_pos[i]],name='Bus %s' % i)
    #Création des bus pour les embranchements
    for i in range(4):
        pp.create_bus(net_noes_pres_troyes,vn_kv=0.4,geodata=[X_pos_emb[i],Y_pos_emb[i]],name='Croisement %s' %i)

    #création des lignes, il y en a 31
    for i in range(30):
        f=pp.get_element_index(net_noes_pres_troyes,"bus",name=From_bus[i])
        t=pp.get_element_index(net_noes_pres_troyes,"bus",name=To_bus[i])
        pp.create_line(net_noes_pres_troyes,f,t,length_km=length[i]/1000,std_type="NAYY 4x120 SE",name='Ligne %s' %i)

    #Création du transformateur 20kv -> 400v
    hv_bus = pp.get_element_index(net_noes_pres_troyes, "bus", "Poste Source HT")
    lv_bus = pp.get_element_index(net_noes_pres_troyes, "bus", "Poste Source BT")
    pp.create_transformer(net_noes_pres_troyes,hv_bus,lv_bus,std_type='0.63 MVA 20/0.4 kV',name='Transfo 1')

    #Création des consommations des habitations :
    for i in range(26):
        bus_idx=pp.get_element_index(net_noes_pres_troyes,element="bus",name="Bus %s" %i)
        pp.create_load(net_noes_pres_troyes,bus=bus_idx,p_mw=Nb_hous[i]*0.015, name= 'Load %s' %i)

    #Création des productions PV (en moyenne 22KW d'installation en France) :
    for PV in L_PV_gen:
        pp.create_sgen(net_noes_pres_troyes,bus=PV,p_mw=0.022,name='Sgen %s' %str(PV))
    return(net_noes_pres_troyes)

net=create_Troyes_net([1,5,6,8])
print(pp.get_element_index(net,element='bus',name='Bus %s' %1))