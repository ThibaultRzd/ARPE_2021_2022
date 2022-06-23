import numpy as np
import pandas as pd
import scipy.interpolate as interp
import pandapower as pp
from pandapower.timeseries.data_sources.frame_data import DFData
import matplotlib.pyplot as plt
# from Scenar_Grid import scenar_grid


def profil_conso(scenario, **kwargs):
    if scenario == 'consommateur':
        # Consommation d'une renault Zoe dernière génération, la voiture la plus vendue en France
        conso_voiture_1km = 17.55*1000/100
        # Distance moyenne parcourue par un Français en 2021
        dist_moy_francais = 42
        # Efficacité du chargeur, elle est en général entre 90% et 95%
        eff_chargeur = 0.90
        # Consommation électrique d'un Français moyen sur une semaine
        conso_utilisateur_semaine = dist_moy_francais*7*conso_voiture_1km/eff_chargeur
        # Cette consommation sert à donner la bonne échelle à la courbe de puissance du véhicule, en effet l'énergie
        # consommée dans la semaine doit correspondre à la consommation de la voiture

        l_prix_elec_enedis = np.array(
            [45.06, 42.11, 40.00, 35.45, 28.03, 37.00, 57.12, 69.99, 74.07, 59.56, 53.48, 54.40, 54.81, 46.28, 47.44,
             53.25, 57.63, 65.92, 73.03, 83.94, 90.12, 84.00, 79.91, 68.00, 70.00, 64.92, 60.39, 56.67, 57.37, 63.09,
             76.97, 85.99, 93.37, 85.71, 79.48, 77.66, 74.25, 69.16, 61.06, 62.05, 62.12, 69.43, 81.19, 80.00, 79.62,
             75.34, 68.62, 62.26, 58.20, 56.31, 54.81, 55.01, 58.84, 69.99, 79.37, 86.12, 80.10, 75.78, 73.84, 69.43,
             62.06, 60.06, 60.00, 62.75, 70.00, 74.97, 80.97, 80.97, 78.08, 74.51, 66.01, 65.04, 63.15, 60.74, 60.85,
             59.90, 60.69, 60.33, 62.87, 67.64, 63.00, 60.69, 57.96, 58.78, 51.63, 48.96, 48.00, 49.78, 57.00, 64.03,
             75.91, 77.76, 79.96, 78.35, 72.63, 75.38, 69.00, 65.65, 62.20, 62.20, 68.00, 73.78, 80.00, 82.14, 78.96,
             70.00, 67.21, 67.21, 63.00, 60.70, 60.00, 60.05, 65.00, 71.74, 79.07, 84.71, 87.02, 85.00, 78.69, 72.39,
             66.75, 60.90, 57.77, 55.80, 54.01, 54.35, 60.75, 60.60, 60.09, 55.73, 53.03, 51.96, 48.49, 44.98, 35.26,
             25.85, 42.06, 59.67, 75.29, 75.65, 72.64, 70.73, 65.00, 53.05, 47.56, 41.21, 22.09, 21.90, 21.80, 22.08,
             25.25, 31.39, 30.91, 24.22, 29.20, 28.96, 9.93, 1.95, 1.00, 1.95, 4.57, 8.05, 36.00, 53.44, 70.99, 70.53,
             65.05, 53.02, 47.56])
        interpolation_prix = interp.interp1d(np.arange(0, 169, 1), l_prix_elec_enedis, )
        l_prix_elec = interpolation_prix(np.arange(0, 168, .5))
        # On se place en milieu rural ou la charge s'effectue à la maison, donc entre 8h et 18h en semaine le véhicule
        # ne se charge pas
        filtre_conso = np.ones(336)
        for i in range(5):
            filtre_conso[48 * i + 16:48 * i + 36] = 0
        l_prix_elec = l_prix_elec * filtre_conso
        # Calcul de l'énergie avec la méthode des trapèzes :
        integer = 0
        for i in range(335):
            integer += (l_prix_elec[i] + l_prix_elec[i + 1]) * 0.5 / 2  # time step (dt) vaut une demi heure soit 0.5h
        # On adapte l'aire sous courbe de la puissance pour avoir la consommation moyenne correspondant à celle du
        # consommateur
        courbe_charge = l_prix_elec * conso_utilisateur_semaine/integer
    elif scenario == 'business':

        cap_bat_wh = 50*10**3  # Capacité de la batterie d'une Renault Zoe moderne
        l_prix_elec_enedis = [45.06, 42.11, 40.00, 35.45, 28.03, 37.00, 57.12, 69.99, 74.07, 59.56, 53.48, 54.40, 54.81,
                              46.28, 47.44, 53.25, 57.63, 65.92, 73.03, 83.94, 90.12, 84.00, 79.91, 68.00, 70.00, 64.92,
                              60.39, 56.67, 57.37, 63.09, 76.97, 85.99, 93.37, 85.71, 79.48, 77.66, 74.25, 69.16, 61.06,
                              62.05, 62.12, 69.43, 81.19, 80.00, 79.62, 75.34, 68.62, 62.26, 58.20, 56.31, 54.81, 55.01,
                              58.84, 69.99, 79.37, 86.12, 80.10, 75.78, 73.84, 69.43, 62.06, 60.06, 60.00, 62.75, 70.00,
                              74.97, 80.97, 80.97, 78.08, 74.51, 66.01, 65.04, 63.15, 60.74, 60.85, 59.90, 60.69, 60.33,
                              62.87, 67.64, 63.00, 60.69, 57.96, 58.78, 51.63, 48.96, 48.00, 49.78, 57.00, 64.03, 75.91,
                              77.76, 79.96, 78.35, 72.63, 75.38, 69.00, 65.65, 62.20, 62.20, 68.00, 73.78, 80.00, 82.14,
                              78.96, 70.00, 67.21, 67.21, 63.00, 60.70, 60.00, 60.05, 65.00, 71.74, 79.07, 84.71, 87.02,
                              85.00, 78.69, 72.39, 66.75, 60.90, 57.77, 55.80, 54.01, 54.35, 60.75, 60.60, 60.09, 55.73,
                              53.03, 51.96, 48.49, 44.98, 35.26, 25.85, 42.06, 59.67, 75.29, 75.65, 72.64, 70.73, 65.00,
                              53.05, 47.56, 41.21, 22.09, 21.90, 21.80, 22.08, 25.25, 31.39, 30.91, 24.22, 29.20, 28.96,
                              9.93, 1.95, 1.00, 1.95, 4.57, 8.05, 36.00, 53.44, 70.99, 70.53, 65.05, 53.02, 47.56]
        interpolation_prix = interp.interp1d(np.arange(0, 169, 1), l_prix_elec_enedis, )
        l_prix_elec = interpolation_prix(np.arange(0, 168, .5))
        # On veut ici maximiser le profit sans charger la voiture, donc on veut une énergie moyenne nulle.
        # Calcul de l'énergie avec la méthode des trapèzes :
        integer = 0
        for i in range(335):
            integer += (l_prix_elec[i] + l_prix_elec[i + 1]) * 0.5 / 2  # time step (dt) vaut une demi heure soit 0.5h
        conso = l_prix_elec - integer / 335 * 2
        prix_max = conso.min()
        courbe_charge = -conso*cap_bat_wh*0.05/prix_max
    elif scenario == 'Grid':
        courbe_charge = scenar_grid(**kwargs)
    else:
        raise NotImplementedError()
    return courbe_charge


def create_troyes_net(l_pv_gen, l_ev):
    # Nombre d'habitations par bus, on en déduit ensuite la puissance de raccordement ()
    nb_hous = np.array([14, 26, 10, 16, 15, 15, 1, 1, 15, 15, 1, 1, 1, 15, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                       dtype='float')

    # Création des positions des bus d'habitation (avec une remise à l'origine)
    x_pos_tempo = np.array([251, 343, 254, 231, 386, 412, 407, 309, 400, 295, 259, 245, 219, 233, 411, 456, 
                            464, 436, 420, 377, 291, 269, 256, 234, 221, 193], dtype='float')
    y_pos_tempo = np.array([498, 512, 518, 545, 461, 483, 518, 436, 472, 408, 421, 433, 463, 446, 546, 578, 583, 562, 
                            552, 525, 536, 563, 575, 483, 479, 468], dtype='float')
    xmin = min(x_pos_tempo)
    ymin = min(y_pos_tempo)
    x_pos = np.array([x-xmin for x in x_pos_tempo], dtype='float')
    y_pos = np.array([y-ymin for y in y_pos_tempo], dtype='float')

    # Création des positions des bus des embranchements
    x_pos_emb = np.array([393-xmin, 320-xmin, 211-xmin, 293-xmin], dtype='float')
    y_pos_emb = np.array([536-ymin, 504-ymin, 481-ymin, 500-ymin], dtype='float')

    # Création des dataframe des lignes
    from_bus = ['Bus 16', 'Bus 15', 'Bus 17', 'Bus 18', 'Bus 14', 'Croisement 0', 'Bus 6', 'Bus 5', 'Bus 8',
                'Croisement 0', 'Bus 19', 'Bus 1', 'Croisement 1', 'Bus 20', 'Bus 21', 'Croisement 1',
                'Poste Source BT', 'Bus 9', 'Bus 10', 'Bus 11', 'Bus 13', 'Croisement 2', 'Croisement 2', 'Bus 24',
                'Bus 23', 'Poste Source BT', 'Croisement 3', 'Croisement 3', 'Bus 2', 'Poste Source BT']

    to_bus = ['Bus 15', 'Bus 17', 'Bus 18', 'Bus 14', 'Croisement 0', 'Bus 6', 'Bus 5', 'Bus 8', 'Bus 4', 'Bus 19',
              'Bus 1', 'Croisement 1', 'Bus 20', 'Bus 21', 'Bus 22', 'Poste Source BT', 'Bus 9', 'Bus 10', 'Bus 11',
              'Bus 13', 'Bus 12', 'Bus 25', 'Bus 24', 'Bus 23', 'Poste Source BT', 'Croisement 3', 'Bus 0', 'Bus 2',
              'Bus 3', 'Bus 7']

    length = np.array([10, 23, 15, 12, 20, 20, 50, 18, 20, 20, 40, 25, 42, 35, 15, 85, 52, 48, 14, 30, 13, 22, 2,
                       25, 124, 70, 35, 47, 37, 10], dtype='float')
    net_noes_pres_troyes = pp.create_empty_network()
    
    # Création du Poste Source HT et du BT
    pp.create_bus(net_noes_pres_troyes, vn_kv=0.4, geodata=[313-xmin, 436-ymin], name='Poste Source BT')
    pp.create_bus(net_noes_pres_troyes, vn_kv=20, geodata=[313-xmin, 436-ymin], name='Poste Source HT')
    
    # Création de toutes les maisons de la zone étudiée
    for i in range(26):
        pp.create_bus(net_noes_pres_troyes, vn_kv=0.4, geodata=[x_pos[i], y_pos[i]], name='Bus %s' % i)
        
    # Création des bus pour les embranchements
    for i in range(4):
        pp.create_bus(net_noes_pres_troyes, vn_kv=0.4, geodata=[x_pos_emb[i], y_pos_emb[i]], name='Croisement %s' % i)

    # Création des lignes, il y en a 31 :
    for i in range(30):
        f = pp.get_element_index(net_noes_pres_troyes, "bus", name=from_bus[i])
        t = pp.get_element_index(net_noes_pres_troyes, "bus", name=to_bus[i])
        pp.create_line(net_noes_pres_troyes, f, t, length_km=length[i]/1000, std_type="NAYY 4x120 SE", name='Ligne %s'
                                                                                                            % i)

    # Création du transformateur 20kv -> 400v
    hv_bus = pp.get_element_index(net_noes_pres_troyes, "bus", "Poste Source HT")
    lv_bus = pp.get_element_index(net_noes_pres_troyes, "bus", "Poste Source BT")
    pp.create_transformer(net_noes_pres_troyes, hv_bus, lv_bus, std_type='0.63 MVA 20/0.4 kV', name='Transfo 1')
    pp.create_ext_grid(net_noes_pres_troyes, bus=hv_bus)
    # Création des consommations des habitations :
    for i in range(26):
        bus_idx = pp.get_element_index(net_noes_pres_troyes, element="bus", name="Bus %s" % i)
        pp.create_load(net_noes_pres_troyes, bus=bus_idx, p_mw=nb_hous[i]*0.015, name='Load %s' % i)

    # Création des productions PV (en moyenne 22KW d'installation en France) :
    for PV in l_pv_gen:
        bus_idx = pp.get_element_index(net_noes_pres_troyes, element="bus", name="Bus %s" % str(PV))
        pp.create_sgen(net_noes_pres_troyes, bus=bus_idx, p_mw=0.022, name='Sgen %s' % str(PV))
    # Création des véhicules électriques et de la consommation :
    for EV in l_ev:
        bus_idx = pp.get_element_index(net_noes_pres_troyes, element='bus', name="Bus %s" % str(EV))
        pp.create_load(net_noes_pres_troyes, bus=bus_idx, p_mw=nb_hous[EV]*7/1000, name=("Load_EV %s" % str(EV)))
    return net_noes_pres_troyes


def create_data_source(scenario, **kwargs):
    """Pour obtenir la consommation d'un foyer moyen français vivant en Occitanie, on extrait des dataset le nombre 
    de points de soutirage ainsi que ceux d'injection (PV) cela permet d'avoir la courbe moyenne pour 1 seul 
    foyer/poste photovoltaïque :"""
    nb_point_soutirage_occ = 3890838
    nb_point_injection_occ = 76688

    # Import des données de consommation
    df_prod = pd.read_csv("C:/Users/Thiba/OneDrive/Documents/2021_2022/TAF/ARPE/Data_PV_Wind/Prod Occitanie ete.csv",
                          sep=';', encoding="latin-1")
    sol = df_prod['Total énergie injectée (Wh)'][df_prod['Filière de production'] == 'F5 : Solaire']
    solaire = np.nan_to_num(sol)
    # Import des données de consommation inférieure à 36 kVA + traitement 
    # (on regroupe les 14 profils différents par horodate)
    df_conso = pd.read_csv("C:/Users/Thiba/OneDrive/Documents/2021_2022/TAF/ARPE/Data_PV_Wind/conso inf36 Occ ete.csv",
                           sep=';', encoding="latin-1")
    date = df_conso['Horodate']
    # Liste des horodates différentes
    l_horodate = [date[1]]
    for jour in date:
        if jour != l_horodate[-1]:
            l_horodate.append(jour)
    conso = np.zeros_like(l_horodate, dtype='float')
    # Somme des profils par horodate
    for i, horodate in enumerate(l_horodate):
        conso[i] = np.nansum(df_conso['Total énergie soutirée (Wh)'][df_conso['Horodate'] == horodate])
    ############################################
    # Mise à l'échelle des données, ce sont des données globales régionales, il faut les mettre par logement, pour la 
    # production PV il suffit de diviser la valeur par le nombre de points de soutirage,
    # Cependant les consommations des maisons ne sont pas les mêmes, seuls les profils sont les mêmes, il faut donc 
    # normer par les consommations et en fabriquer une par type de bus
    conso_moy_mwh = 4.76  # Consommation moyenne d'un client Enedis en résidence
    # Liste des consommations annuelles des bus
    conso_mwh = np.array([19, 52, 13, 23, 22.5, 22.5, 1.5, 94., 22.5, 22.5, 1.4, 1.2, 1.3, 22.8, 1.5, 1.5, 1.5, 1.3,
                          1.5, 1.5, 1.4, 1.5, 1.5, 1.5, 1.2, 1.1], dtype=float)
    # Création d'un second dataframe avec le bon format pour utiliser les séries temporelles
    profiles = pd.DataFrame()
    # Un profil de consommation par bus, car chaque bus n'a pas forcément le même nombre d'habitations ni la même
    # consommation, de plus cette dernière n'est même pas la même que la moyenne nationale
    for i in range(26):
        profiles['loadp_%s' % i] = conso*conso_mwh[i]/(10**6*nb_point_soutirage_occ*conso_moy_mwh)
    # Profil de production # solaire
    profiles['sgenp'] = solaire/nb_point_injection_occ/10**6 
    profiles['Load_EV'] = profil_conso(scenario, **kwargs)/10**6
    df = pd.DataFrame(profiles)
    #ds = DFData(df)
    return df
