# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 09:12:16 2022

@author: mrsao

Capital financiero
"""
import pandas as pd
import numpy as np
import sys, os

directory = os.path.dirname(os.path.realpath(__file__))
directory = '\\'.join(directory.split('\\')[:-1])

sys.path.insert(1, directory)
from auxiliar import rk4

def main(init_val, para, 
         min_kf_df, pesca_kf_df,
         gan_kf_df, agric_kf_df):
    
    # TEST
    if (min_kf_df.shape[0] != pesca_kf_df.shape[0]) or\
       (min_kf_df.shape[0] != gan_kf_df.shape[0])   or\
       (min_kf_df.shape[0] != agric_kf_df.shape[0]) or\
       (pesca_kf_df.shape[0] != gan_kf_df.shape[0])  or\
       (pesca_kf_df.shape[0] != agric_kf_df.shape[0] or\
       (gan_kf_df.shape[0] != agric_kf_df.shape[0])):
           sys.exit('No son fechas comparables')
        
    
    # CONSTANST
    
    n_pasos = min_kf_df.shape[0]
    df_res = pd.DataFrame(data={'Fecha' : min_kf_df['Fecha']})
    smmlv = para['Salario mínimo legal vigente - 2020']
    
    # Agricultura, especies menores, Pesca
    aem_pesca = para['Agricultura, especies menores, pesca']
    # Agricultura, especies menores, Actividades no agropecuarias
    aem_act_N_agro = para['Agricultura, especies menores, Actividades no agropecuarias']
    # Agricultura y especies menores
    aye_men = para['Agricultura y especies menores']
    
    # Agricultura, especies menores, Pesca - 1
    aem_pesca_1 = para['Agricultura, especies menores, pesca - 1']
    # Agricultura, especies menores, Actividades no agropecuarias 1
    aem_act_N_agro_1 = para['Agricultura, especies menores, Actividades no agropecuarias 1']
    # Agricultura y especies menores 1
    aye_men_1 = para['Agricultura y especies menores - 1'] 
    
    # Agricultura, especies menores, Pesca - 2
    aem_pesca_2 = para['Agricultura, especies menores, pesca - 2']
    # Agricultura, especies menores, Actividades no agropecuarias 2
    aem_act_N_agro_2 = para['Agricultura, especies menores, Actividades no agropecuarias 2']
    # Agricultura y especies menores 2
    aye_men_2 = para['Agricultura y especies menores - 2']  
    
    # Agricultura, especies menores, Pesca - 3
    aem_pesca_3 = para['Agricultura, especies menores, pesca - 3']
    # Agricultura, especies menores, Actividades no agropecuarias 3
    aem_act_N_agro_3 = para['Agricultura, especies menores, Actividades no agropecuarias 3']
    # Agricultura y especies menores 3
    aye_men_3 = para['Agricultura y especies menores - 3']
    
    # Costos ganaderia - list - [cop]
    cos_gan = gan_kf_df['Inversion']
    # Costos totales agrícolas - list - [cop]
    cos_agr = agric_kf_df['Costos agricolas']
    # Costos pesca - list - [cop]
    cos_pes = pesca_kf_df['Costos']
    # Costos mineria - list - [cop]
    cos_min = min_kf_df['Costos minería']
    # Costos mantenimiento infraestructura manejo inundación - list - [cop]
    cos_maninfmagin = [aem_pesca_3 + aem_act_N_agro_3 + aye_men_3] * n_pasos
    
    # Ingresos jornales - list - [cop]
    ing_jor = [aem_pesca_2 + aem_act_N_agro_2 + aye_men_2] * n_pasos
    # Ingresos remesas - list - [cop]
    ing_rem = [aem_pesca_1 + aem_act_N_agro_1 + aye_men_1] * n_pasos
    
    # FLOWS - CONSTANTS
    
    # Donaciones - list - [cop]
    don = [aem_pesca + aem_act_N_agro + aye_men] * n_pasos
    
    # Ingresos totales
    # !!! TODO cambiar *Ventas agrícolas* por el nombre real
    ing_total = min_kf_df['Ingresos totales KFM'] + pesca_kf_df['Ventas pesca'] +\
                gan_kf_df['Ventas totales'] + agric_kf_df['Ventas agrícolas'] + \
                np.array(ing_jor) + np.array(ing_rem)
    
    # Costos totales
    cos_tot = cos_gan + cos_agr + cos_pes + cos_min + cos_maninfmagin
    
    # Add flows
    df_res['Donaciones'] = don
    df_res['Ingresos totales'] = ing_total
    df_res['Costos totales'] = cos_tot
    
    df_res['_Ingresos Jornales'] = ing_jor
    df_res['_Ingresos Remesas'] = ing_rem
    df_res['_Costos mantenimiento infraestructura manejo inundación'] = cos_maninfmagin
    
    df_res['Capital financiero instantaneo'] = df_res['Ingresos totales'] + df_res['Donaciones'] - df_res['Costos totales']
    
    tmp_KFInst_dis_smmlv = df_res['Capital financiero instantaneo'] / smmlv
    KFInst_dis_smmlv_lst = []
    for tmp_KFInst_dis_smmlv_uni in tmp_KFInst_dis_smmlv:
        if tmp_KFInst_dis_smmlv_uni <= 100:
            KFInst_dis_smmlv_lst.append(12.5)
        elif 100 < tmp_KFInst_dis_smmlv_uni and 200 >= tmp_KFInst_dis_smmlv_uni:
            KFInst_dis_smmlv_lst.append(25)
        elif 200 < tmp_KFInst_dis_smmlv_uni and 300 >= tmp_KFInst_dis_smmlv_uni:
            KFInst_dis_smmlv_lst.append(37.5)
        elif 300 < tmp_KFInst_dis_smmlv_uni and 400 >= tmp_KFInst_dis_smmlv_uni:
            KFInst_dis_smmlv_lst.append(50)
        elif 400 < tmp_KFInst_dis_smmlv_uni and 500 >= tmp_KFInst_dis_smmlv_uni:
            KFInst_dis_smmlv_lst.append(62.5)
        elif 500 < tmp_KFInst_dis_smmlv_uni and 600 >= tmp_KFInst_dis_smmlv_uni:
            KFInst_dis_smmlv_lst.append(75)
        elif 600 < tmp_KFInst_dis_smmlv_uni and 700 >= tmp_KFInst_dis_smmlv_uni:
            KFInst_dis_smmlv_lst.append(87.5)
        elif 700 < tmp_KFInst_dis_smmlv_uni:
            KFInst_dis_smmlv_lst.append(100)
        else:
            KFInst_dis_smmlv_lst.append(12.5)
    
    df_res['KFT instantánero discretizado'] = KFInst_dis_smmlv_lst
    
    # STOCK
    # Results
    res_lts = [init_val]
    
    # function
    kFt_fun = lambda init, ctes: ctes[0] + ctes[1] - ctes[2]
    
    for _, row in df_res.iterrows():
        cte = [row['Ingresos totales'],
               row['Donaciones'],
               row['Costos totales']]
        
        for ii_pas in np.arange(10): 
            res = rk4(kFt_fun, init_val, cte, 1/10)
            init_val = res
        
        res_lts.append(res)
        
    # Add stokcs results
    df_res['KHT'] = res_lts[:-1]
    
    return df_res
            
if __name__ == '__main__':
    para = {'Agricultura, especies menores, pesca' : 87251,
            'Agricultura y especies menores' : 116207,
            'Agricultura, especies menores, Actividades no agropecuarias' : 93367,
            
            'Agricultura, especies menores, pesca - 1' : 120588,
            'Agricultura, especies menores, Actividades no agropecuarias 1' : 207143,
            'Agricultura y especies menores - 1' : 81531,
            
            'Agricultura, especies menores, pesca - 2' : 185516,
            'Agricultura, especies menores, Actividades no agropecuarias 2' : 256650,
            'Agricultura y especies menores - 2' : 143353,
            
            'Agricultura, especies menores, pesca - 3' : 4064694,
            'Agricultura, especies menores, Actividades no agropecuarias 3' : 6826230,
            'Agricultura y especies menores - 3' : 5839102,
            
            'Salario mínimo legal vigente - 2020' : 877802
            }
    
    min_kf_df   = pd.DataFrame(data={'Fecha': ['2022-01-01', '2022-02-01', '2022-03-01'],
                                     'Costos minería': [10000, 10000, 10000],
                                     'Ingresos totales KFM' : [100000000, 100000000, 100000000]})
    pesca_kf_df = pd.DataFrame(data={'Fecha': ['2022-01-01', '2022-02-01', '2022-03-01'],
                                     'Costos' : [10000, 10000, 10000],
                                     'Ventas' : [30000000, 300000000, 300000000]})
    gan_kf_df   = pd.DataFrame(data={'Fecha': ['2022-01-01', '2022-02-01', '2022-03-01'],
                                     'Inversion': [10000, 10000, 10000],
                                     'Ventas totales': [60000000, 60000000, 60000000]})
    agric_kf_df = pd.DataFrame(data={'Fecha': ['2022-01-01', '2022-02-01', '2022-03-01'],
                                     'Costos agricolas' : [10000, 10000, 10000],
                                     'Ventas agrícolas' : [12000000, 12000000, 12000000]})
    
    # list_date = ['2022-01-01', '2022-02-01', '2022-03-01']
    res = main(0, para, 
               min_kf_df, pesca_kf_df,
               gan_kf_df, agric_kf_df)
    # print(res)