import numpy as np
from pandapower.control.controller.const_control import ConstControl
from pandapower.timeseries.output_writer import OutputWriter
from pandapower.timeseries.run_time_series import run_timeseries
from create_reseau_dataset import create_troyes_net, create_data_source
from pandapower.timeseries.data_sources.frame_data import DFData
import pandas as pd
import matplotlib.pyplot as plt
import torch


def check_lin(lamb):
    # Définitions des paramètres
    scenario = 'business'

    l_pv_gen = []
    l_ev = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    l_ret = []

    for mult in [0, 1, lamb]:
        df = create_data_source(scenario)

        df['Load_EV'] = mult * df['Load_EV']
        ds = DFData(df)
        list_name = []
        for i in range(26):
            list_name.append("loadp_%s" % i)
        for i in range(len(l_ev)):
            list_name.append("Load_EV")

        net = create_troyes_net(l_pv_gen, l_ev)
        ###
        print()
        ###
        ConstControl(net, "sgen", "p_mw", element_index=net.sgen.index, profile_name=["sgenp"] * len(l_pv_gen),
                     data_source=ds)
        ConstControl(net, "load", "p_mw", element_index=net.load.index, profile_name=list_name, data_source=ds)

        # Partie sauvegarde des données au format csv
        ow = OutputWriter(net, time_steps=np.arange(0, 335), output_path="./results/", output_file_type=".csv")
        ow.log_variable("res_bus", "vm_pu")
        ow.log_variable("res_line", "loading_percent")

        run_timeseries(net, time_steps=np.arange(0, 335))

        df_result_percent = pd.read_csv("results/res_line/loading_percent.csv", sep=';', encoding='latin-1')
        df_result_percent = df_result_percent.drop(['Unnamed: 0'], axis=1)
        l_ret.append(df_result_percent)

    tab_1, tab_2, tab_3 = [i.to_numpy() for i in l_ret]
    condition = tab_3-tab_1 - lamb*(tab_2-tab_1)
    # erreur = np.linalg.norm(condition)/np.linalg.norm(tab_1)
    erreur = condition.max()
    return erreur


def run_reseau(profil):
    scenario = 'grid'

    l_pv_gen = []
    l_ev = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    l_ret = []
    df = create_data_source(scenario, profil)
    ds = DFData(df)
    list_name = []
    for i in range(26):
        list_name.append("loadp_%s" % i)
    for i in range(len(l_ev)):
        list_name.append("Load_EV")

    net = create_troyes_net(l_pv_gen, l_ev)
    ###
    print()
    ###
    ConstControl(net, "sgen", "p_mw", element_index=net.sgen.index, profile_name=["sgenp"] * len(l_pv_gen),
                 data_source=ds)
    ConstControl(net, "load", "p_mw", element_index=net.load.index, profile_name=list_name, data_source=ds)

    # Partie sauvegarde des données au format csv
    ow = OutputWriter(net, time_steps=np.arange(0, 335), output_path="./results/", output_file_type=".csv")
    ow.log_variable("res_bus", "vm_pu")
    ow.log_variable("res_line", "loading_percent")

    run_timeseries(net, time_steps=np.arange(0, 335))

    df_result_percent = pd.read_csv("results/res_line/loading_percent.csv", sep=';', encoding='latin-1')
    return(df_result_percent)

#lambs = np.linspace(0, 6, 20)
#ords = np.zeros_like(lambs)
#for i, lamb in enumerate(lambs):
#    ords[i] = check_lin(lamb)
#plt.plot(lambs, ords)
#plt.show()

def create_dataset(n, shape_entree=(35, 336
                                    ), val_split_ratio=.1):
    entrees = torch.zeros((n, *shape_entree))
    sorties = torch.zeros((n, shape_entree[1]))
    for i in range(n):
        sorties[i][:] = torch.tensor(courbe_conso_aleatoire())
        entrees[i] = torch.tensor(run_reseau(sorties[i]))

    dataset = torch.utils.TensorDataSet(entrees, sorties)
    length_test = int(n*val_split_ratio)
    length_train = n - length_test
    train, test = torch.utils.data.random_split(dataset, [length_train, length_test])
    return train, test


def courbe_conso_aleatoire():

    #  Cette fonction permet de générer une courbe de charge de véhicule électrique aléatoire respectant certaines
    #  règles :
    #  - La charge ne peut pas être supérieure à 3.7KW (taille d'un chargeur type)
    #  - L'énergie consommée (intégrale de la courbe) sur une semaine doit correspondre à la consommation
    #  d'un utilisateur moyen (à savoir conso_utilisateur_semaine)

    #  Le véhicule peut être utilisé en journée, on cherche un optimal de consommation
    #  Le pas de temps est la demi-heure


    # Consommation d'une renault Zoe dernière génération, la voiture la plus vendue en France
    conso_voiture_1km = 17.55 * 1000 / 100
    # Distance moyenne parcourue par un Français en 2021
    dist_moy_francais = 42
    # Efficacité du chargeur, elle est en général entre 90% et 95%
    eff_chargeur = 0.90
    # Consommation électrique d'un Français moyen sur une semaine
    conso_utilisateur_semaine = dist_moy_francais * 7 * conso_voiture_1km / eff_chargeur


    courbe_conso = np.random.uniform(low=-3700, high=3700, size=336)
    integer = 0
    for i in range(335):
        integer += (courbe_conso[i] + courbe_conso[i + 1]) * 0.5 / 2  # time step (dt) vaut une demi heure soit 0.5h
    courbe_conso = conso_utilisateur_semaine*courbe_conso/integer
    return courbe_conso


create_dataset(10)
