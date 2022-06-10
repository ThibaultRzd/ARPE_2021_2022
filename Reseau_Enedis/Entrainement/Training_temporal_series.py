import os
import numpy as np
import pandas as pd
import tempfile
import matplotlib.pyplot as plt
import pandapower as pp
import pandapower.plotting as ppp
from pandapower.timeseries import DFData
from pandapower.timeseries import OutputWriter
from pandapower.timeseries.run_time_series import run_timeseries
from pandapower.control import ConstControl


def timeseries_Noes(output_dir):
    L_PV_gen = []  # Liste à remplir avec les bus (donc logements) arborant des panneaux solaires
    # 1. create test net
    net = create_Troyes_net(L_PV_gen)

    # 2. create (random) data source
    n_timesteps = 336
    profiles, ds = create_data_source()
    # 3. create controllers (to control values of the load and the sgen)
    create_controllers(net, ds, L_PV_gen)

    # time steps to be calculated. Could also be a list with non-consecutive time steps
    time_steps = range(0, n_timesteps)

    # 4. the output writer with the desired results to be stored to files.
    #ow = create_output_writer(net, time_steps, output_dir=output_dir)

    # 5. the main time series function
    run_timeseries(net,time_steps)



def create_Troyes_net(L_PV_gen):
    #Cette première partie est la définition des dataframes, idéalement elles se trouveraient sous la forme de dossiers XLS ou CSV
    ############################################
    ############################################
    ############################################


    # Nombre d'habitations par bus, on en déduis ensuite la puissance de raccordement ()
    Nb_hous = [14, 26, 10, 16, 15, 15, 1, 1, 15, 15, 1, 1, 1, 15, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    # Création des positions des bus d 'habitation (avec une remise à l'origine)
    X_pos_tempo = [251, 343, 254, 231, 386, 412, 407, 309, 400, 295, 259, 245, 219, 233, 411, 456, 464, 436, 420, 377, 291, 269, 256, 234, 221, 193]
    Y_pos_tempo = [498, 512, 518, 545, 461, 483, 518, 436, 472, 408, 421, 433, 463, 446, 546, 578, 583, 562, 552, 525, 536, 563, 575, 483, 479, 468]
    xmin = min(X_pos_tempo)
    ymin = min(Y_pos_tempo)
    X_pos = [x - xmin for x in X_pos_tempo]
    Y_pos = [y - ymin for y in Y_pos_tempo]

    # Création des positions des bus des embranchements
    X_pos_emb = [393 - xmin, 320 - xmin, 211 - xmin, 293 - xmin]
    Y_pos_emb = [536 - ymin, 504 - ymin, 481 - ymin, 500 - ymin]

    # Création des dataframe des lignes
    From_bus = ['Bus 16', 'Bus 15', 'Bus 17', 'Bus 18', 'Bus 14', 'Croisement 0', 'Bus 6', 'Bus 5', 'Bus 8','Croisement 0', 'Bus 19', 'Bus 1', 'Croisement 1', 'Bus 20', 'Bus 21', 'Croisement 1','Poste Source BT', 'Bus 9', 'Bus 10', 'Bus 11', 'Bus 13', 'Croisement 2', 'Croisement 2', 'Bus 24','Bus 23', 'Poste Source BT', 'Croisement 3', 'Croisement 3', 'Bus 2', 'Poste Source BT']
    To_bus = ['Bus 15', 'Bus 17', 'Bus 18', 'Bus 14', 'Croisement 0', 'Bus 6', 'Bus 5', 'Bus 8', 'Bus 4', 'Bus 19','Bus 1', 'Croisement 1', 'Bus 20', 'Bus 21', 'Bus 22', 'Poste Source BT', 'Bus 9', 'Bus 10', 'Bus 11','Bus 13', 'Bus 12', 'Bus 25', 'Bus 24', 'Bus 23', 'Poste Source BT', 'Croisement 3', 'Bus 0', 'Bus 2','Bus 3', 'Bus 7']
    length = [10, 23, 15, 12, 20, 20, 50, 18, 20, 20, 40, 25, 42, 35, 15, 85, 52, 48, 14, 30, 13, 22, 2, 25, 124, 70, 35, 47, 37, 10]
    ############################################
    ############################################
    ############################################
    #Création du réseau en lui même
    net_noes_pres_troyes = pp.create_empty_network()
    pp.set_user_pf_options(net_noes_pres_troyes, init_vm_pu="flat", init_va_degree="dc",
                           calculate_voltage_angles=True)
    # Création du Poste Source HT et du BT
    pp.create_bus(net_noes_pres_troyes, vn_kv=0.4, geodata=[313 - xmin, 436 - ymin], name='Poste Source BT')
    pp.create_bus(net_noes_pres_troyes, vn_kv=20, geodata=[313 - xmin, 436 - ymin], name='Poste Source HT')
    # Création de tous les maisons de la zone étudiée
    for i in range(26):
        pp.create_bus(net_noes_pres_troyes, vn_kv=0.4, geodata=[X_pos[i], Y_pos[i]], name='Bus %s' % i)

    # Création des bus pour les embranchements, ils n'auront pas de productions ni de consommation, cependant ils sont intéressant car ils sont l'intersection de plusieurs lignes
    for i in range(4):
        pp.create_bus(net_noes_pres_troyes, vn_kv=0.4, geodata=[X_pos_emb[i], Y_pos_emb[i]],name='Croisement %s' % i)

    # création des lignes, il y en a 31
    for i in range(30):
        f = pp.get_element_index(net_noes_pres_troyes, "bus", name=From_bus[i])
        t = pp.get_element_index(net_noes_pres_troyes, "bus", name=To_bus[i])
        pp.create_line(net_noes_pres_troyes, f, t, length_km=length[i] / 1000, std_type="NAYY 4x120 SE",name='Ligne %s' % i)

    # Création du transformateur 20kv -> 400v
    hv_bus = pp.get_element_index(net_noes_pres_troyes, "bus", "Poste Source HT")
    lv_bus = pp.get_element_index(net_noes_pres_troyes, "bus", "Poste Source BT")
    pp.create_transformer(net_noes_pres_troyes, hv_bus, lv_bus, std_type='0.63 MVA 20/0.4 kV', name='Transfo 1')
    #Création du réseau extérieur :
    pp.create_ext_grid(net_noes_pres_troyes,bus=hv_bus)
    # Création des consommations des habitations :
    for i in range(26):
        bus_idx = pp.get_element_index(net_noes_pres_troyes, element="bus", name="Bus %s" % i)
        pp.create_load(net_noes_pres_troyes, bus=bus_idx, p_mw=Nb_hous[i] * 0.015, name='Load %s' % i)

    # Création des productions PV (en moyenne 22KW d'installation en France) :
    for PV in L_PV_gen:
        pp.create_sgen(net_noes_pres_troyes, bus=PV, p_mw=0.022, name='Sgen %s' % str(PV))
    return (net_noes_pres_troyes)


def create_data_source():
    #Pour obtenir la consommation d'un foyer moyen français vivant en Occitanie, on extrait des dataset le nombre de points de soutirage
    #ainsi que ceux d'injection (PV) cela permet d'avoir la courbe moyenne pour 1 seul foyer/poste photovoltaique
    Nb_point_soutirage_OCC=3890838
    Nb_point_injection_OCC=76688

    #Import des données de consommation
    dfprod = pd.read_csv("C:/Users/Thiba/OneDrive/Documents/2021_2022/TAF/ARPE/Data_PV_Wind/Prod Occitanie ete.csv",sep=';',encoding="latin-1")
    Sol =dfprod['Total énergie injectée (Wh)'][dfprod['Filière de production']=='F5 : Solaire']
    Solaire =[]
    for s in Sol:
        if np.isnan(s):
            Solaire.append(0)
        else:
            Solaire.append(s)
    #Import des données de consommation inférieure à 36 kVA + traitement (on regroupe les 14 profils différents par horodate)
    dfconso=pd.read_csv("C:/Users/Thiba/OneDrive/Documents/2021_2022/TAF/ARPE/Data_PV_Wind/conso inf36 Occ ete.csv",sep=';',encoding="latin-1")
    Date = dfconso['Horodate']
    #Liste des horodates différentes
    L_Horodate = [Date[1]]
    for date in Date:
        if date != L_Horodate[-1]:
            L_Horodate.append(date)
    Conso = []
    #Somme des profils par horodate
    for horodate in L_Horodate:
        Conso.append(np.nansum(list(dfconso['Total énergie soutirée (Wh)'][dfconso['Horodate'] == horodate])))
    ############################################
    ############################################
    ############################################
    #Mise à l'échelle des données, ce sont des données globales régionales, il faut les mettre par logement, pour la production PV il suffit de diviser la valeur par le nombre de points de soutirage,
    #Cependant les consommation des maisons ne sont pas les mêmes, seuls les profils sont les mêmes, il faut donc normer par les consommations  et en fabriquer une par type de bus
    Conso_moy_mwh=4.76 #Consommation moyenne d'un client Enedis en résidence
    # Liste des consommations annuelles des bus
    Conso_mwh = [19, 52, 13, 23, 22.5, 22.5, 1.5, 94, 22.5, 22.5, 1.4, 1.2, 1.3, 22.8, 1.5, 1.5, 1.5, 1.3, 1.5, 1.5, 1.4, 1.5, 1.5, 1.5, 1.2, 1.1]
    # Nombre d'habitations par bus
    Nb_hous = [14, 26, 10, 16, 15, 15, 1, 1, 15, 15, 1, 1, 1, 15, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]



    #Création d'un second dataframe avec le bon format pour utiliser les séries temporelles
    profiles = pd.DataFrame()
    for i in range (26):
        profiles['loadp_%s'%i] = np.array([x*Conso_mwh[i]*Nb_hous[i]/(10**6*Nb_point_soutirage_OCC*Conso_moy_mwh) for x in Conso]) # Un profil de consommation par bus car chaque bus n'a pas forcément le même nombre d'habitation ni la même consommation, et cette dernière n'est même pas la même que la moyenne natianale

    profiles['sgenp'] = np.array([x/Nb_point_injection_OCC/10**6 for x in Solaire]) # profil de production solaire

    ds = DFData(profiles)

    return profiles, ds

def create_controllers(net, ds, L_PV_gen):

    for i in range(26):
        bus_idx = pp.get_element_index(net, element="bus", name="Bus %s" % i)
        ConstControl(net, element='load', variable='p_mw', element_index=bus_idx, data_source=ds, profile_name=["loadp_%s" %i])
    for Pv in L_PV_gen:
        bus_idx = pp.get_element_index(net_noes_pres_troyes, element="bus", name="Bus %s" % str(Pv))
        ConstControl(net, element='sgen', variable='p_mw', element_index=bus_idx, data_source=ds, profile_name=["sgenp"])

def create_output_writer(net, time_steps, output_dir):
    ow = OutputWriter(net, time_steps, output_path=output_dir, output_file_type=".xlsx", log_variables=list())
    # these variables are saved to the harddisk after / during the time series loop
    ow.log_variable('res_load', 'p_mw')
    ow.log_variable('res_bus', 'vm_pu')
    ow.log_variable('res_line', 'loading_percent')
    ow.log_variable('res_line', 'i_ka')
    return ow

output_dir = os.path.join("/", "time_series_example")
print("Results can be found in your local temp folder: {}".format(output_dir))
if not os.path.exists(output_dir):
    os.mkdir(output_dir)
timeseries_Noes(output_dir)

ppp.simple_plotly(net)

# voltage results
fig,axs=plt.subplots(3)
vm_pu_file = os.path.join(output_dir, "res_bus", "vm_pu.xlsx")
vm_pu = pd.read_excel(vm_pu_file, index_col=0)
axs[0].plot(vm_pu)
axs[0].set(ylabel="voltage mag. [p.u.]")
axs[0].set_title("Voltage Magnitude")
plt.grid()

#line loading results
ll_file = os.path.join(output_dir, "res_line", "loading_percent.xlsx")
line_loading = pd.read_excel(ll_file, index_col=0)
axs[1].plot(line_loading)
axs[1].set(ylabel="line loading [%]")
axs[1].set_title("Line Loading")
plt.grid()
#load results
load_file = os.path.join(output_dir, "res_load", "p_mw.xlsx")
load = pd.read_excel(load_file, index_col=0)
axs[2].plot(load)
axs[2].set_title('Grid Load (MW)')
axs[2].set(ylabel="P [MW]")
plt.xlabel("time step")
plt.grid()
plt.show()
