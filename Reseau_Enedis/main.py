import numpy as np
from pandapower.control.controller.const_control import ConstControl
from pandapower.timeseries.output_writer import OutputWriter
from pandapower.timeseries.run_time_series import run_timeseries
from Calcul import create_troyes_net, create_data_source



def main():
    # Définitions des paramètres

    scenario = 'business'

    l_pv_gen = []
    l_ev = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    ds = create_data_source(scenario)
    #ds['Load_EV'] = 2 * ds['Load_EV']
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


if __name__ == '__main__':
    main()
