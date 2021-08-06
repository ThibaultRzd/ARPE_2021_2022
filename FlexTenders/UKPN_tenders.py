# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 23:51:11 2020

@author: U546416
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


folder = r'c:\user\U546416\Documents\PhD\Data\FlexTenders\UKPN\\'
file = 'Flexibility-Post-Tender-Report-Bids-2020_'
secure = pd.read_excel(folder + file + 'secure.xlsx', sheet_name=1)
sustain = pd.read_excel(folder + file + 'sustain.xlsx', sheet_name=1)
dynamic = pd.read_excel(folder + file + 'dynamic.xlsx', sheet_name=1)

secure.columns = ['Result', 'Alternative_offer', 'Competition',
                   'Bid_Grouping', 'Company', 'Capacity_MW',
                   'Bid_Availability_Fee', 'Bid_Utilisation_Fee',
                   'Alt_Av_Fee',
                   'Alt_Ut_Fee', 'Max_Run_Time',
                   'Period', 'Month_From', 'Month_To', 'Season',
                   'Window_From', 'Window_To', 'Day']
sustain.columns = ['Result', 'Competition', 'Bid_Grouping', 'Company',
                   'Capacity_MW', 'Fee', 'Max_Run_Time',
                   'Period', 'Month_From', 'Month_To', 'Season',
                   'Window_From', 'Window_To', 'Day']
dynamic.columns = ['Competition', 'Company', 'Capacity_MW',
                   'Utilisation_Fee']

companies = ['Electric Miles Ltd', 'EV Chargers (EVC)',
       'Urban Reserve (AssetCo) Limited',
       'Conrad Energy (Trading) Limited',
       'SUEZ RECYCLING AND RECOVERY UK LTD', 'Flexitricity Limited',
       'ev.energy', 'E.on', 'GridBeyond Limited', 'Bankenergi Limited',
       'City Energy Management', 'Foresight Group', 'KiWi Power',
       'Intelligent Energy Technology Ltd', 'Moixa Technology Limited']

evcs = ['Electric Miles Ltd', 'EV Chargers (EVC)','ev.energy']
battcs = ['Moixa Technology Limited','Urban Reserve (AssetCo) Limited']
fuelcell = ['Intelligent Energy Technology Ltd']
DRcs = ['KiWi Power', 'Bankenergi Limited',]
DG = ['Conrad Energy (Trading) Limited', 'Flexitricity Limited']

secure.Window_From.loc[384] = secure.Window_From.loc[383]
#%% Plot 2d secure Bids

# Computing availability hours
mult = secure.Day.apply(lambda x: 1 if x=='All' else 5/7)
secure['Av_Days'] = (secure.Month_To-secure.Month_From).dt.days * mult
secure['Window_hours'] = secure.apply(lambda x: ((int(x.Window_To[0:2]) + int(x.Window_To[3:5])/60) - 
                                                  (int(x.Window_From[0:2]) + int(x.Window_From[3:5])/60)),
                                        axis=1)
secure['Av_hours'] = secure.Window_hours * secure.Av_Days

finals = secure[~(secure.Result == 'Rejected') & ~(secure.Alternative_offer == 'Award Rejected')]
finals['final_av'] = finals.apply(lambda x: x.Alt_Av_Fee 
                                      if x.Alternative_offer in ['Award Accepted', 'Awarded'] 
                                      else x.Bid_Availability_Fee, axis=1)
finals['final_ut']= finals.apply(lambda x: x.Alt_Ut_Fee 
                                      if x.Alternative_offer in ['Award Accepted', 'Awarded'] 
                                      else x.Bid_Utilisation_Fee, axis=1) 
finals['EVc'] = finals.Company.isin(evcs)

# Estimating £/kW
nevents = 7
finals['Equivalent_Capacity_Payment'] = (finals.Av_hours * finals.final_av + nevents * finals.final_ut)/1000


bids_evs = finals[finals.EVc][['Competition', 'Bid_Grouping', 'Capacity_MW', 'final_av', 'final_ut','Equivalent_Capacity_Payment']].groupby('Bid_Grouping').mean()
bids_oth = finals[~finals.EVc][['Competition', 'Bid_Grouping', 'Capacity_MW', 'final_av', 'final_ut', 'Equivalent_Capacity_Payment']].groupby('Bid_Grouping').mean()

avg_cap_pay = ((bids_evs.Equivalent_Capacity_Payment  * bids_evs.Capacity_MW).sum() + 
               (bids_oth.Equivalent_Capacity_Payment * bids_oth.Capacity_MW).sum()) / (bids_evs.Capacity_MW.sum() + bids_oth.Capacity_MW.sum())

f,axs=plt.subplots(1,2)
m = 20
plt.sca(axs[0])
plt.scatter(bids_evs.final_av, bids_evs.final_ut, s=bids_evs.Capacity_MW * m, label='EV companies')
plt.scatter(bids_oth.final_av, bids_oth.final_ut, s=bids_oth.Capacity_MW * m, label='Other companies')
plt.yscale('log')
plt.xscale('log')
#plt.title('UKPN April 2020 results')
plt.xlabel('Availability Payment [£/MW.h]')
plt.ylabel('Utilisation Payment [£/MWh]')
plt.legend()
plt.grid('--', alpha=0.8)

plt.sca(axs[1])
j = finals[['Bid_Grouping', 'Equivalent_Capacity_Payment', 'EVc', 'Capacity_MW']].groupby('Bid_Grouping').mean()
j.sort_values('Equivalent_Capacity_Payment', inplace=True)
j.reset_index(inplace=True)
plt.scatter(j[j.EVc].index, j[j.EVc].Equivalent_Capacity_Payment, s=j[~j.EVc].Capacity_MW*m, label='EV companies')
plt.scatter(j[~j.EVc].index, j[~j.EVc].Equivalent_Capacity_Payment, s=j[~j.EVc].Capacity_MW*m, label='Other companies')
plt.axhline(avg_cap_pay, linestyle='--', color='r', label='Average payment')
#plt.title('UKPN April 2020, Equivalent Service Fee [£/kW.y]')
plt.xlabel('Bid number')
plt.ylabel('Equivalent Service Payment [£/kW.y]')
axs[0].set_title('(a) Flexibility payments', y=-0.25)
axs[1].set_title('(b) Annual payment', y=-0.25)
plt.legend()
plt.grid('--', alpha=0.8)
f.set_size_inches(9,4)
plt.tight_layout()
f.savefig(r'c:\user\U546416\Pictures\UKPN tenders\ukpn2020v2.png')
f.savefig(r'c:\user\U546416\Pictures\UKPN tenders\ukpn2020v2.pdf')