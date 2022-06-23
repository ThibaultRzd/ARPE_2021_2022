import numpy as np
from pandapower.control.controller.const_control import ConstControl
from pandapower.timeseries.output_writer import OutputWriter
from pandapower.timeseries.run_time_series import run_timeseries
from create_reseau_dataset import create_troyes_net, create_data_source
from pandapower.timeseries.data_sources.frame_data import DFData
import pandas as pd
import matplotlib.pyplot as plt



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
        l_ret.append(df_result_percent)

    tab_1, tab_2, tab_3 = [i.to_numpy() for i in l_ret]
    condition = tab_3-tab_1 - lamb*(tab_2-tab_1)
    # erreur = np.linalg.norm(condition)/np.linalg.norm(tab_1)
    erreur = condition.max()
    return erreur


lambs = np.linspace(0, 6, 20)
ords = np.zeros_like(lambs)
for i, lamb in enumerate(lambs):
    ords[i] = check_lin(lamb)


plt.plot(lambs, ords)
plt.show()
