import pandas as pd
import matplotlib.pyplot as plt

df_result_percent = pd.read_csv("results/res_line/loading_percent.csv", sep=';', encoding='latin-1')
df_resul_vn = pd.read_csv("results/res_bus/vm_pu.csv", sep=';', encoding='latin-1')
# On enlève la première colonne qui est inutile et donne juste le numéro de la ligne du dataframe
df_resul_vn = df_resul_vn.drop(['Unnamed: 0'], axis=1)
df_result_percent = df_result_percent.drop(['Unnamed: 0'], axis=1)
print(df_result_percent)
df_result_percent.plot()
plt.title('load_Percent')
#df_resul_vn.plot()
#plt.title('Tension Nominale')
#plt.show()
