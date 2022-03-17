# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 09:24:34 2022

@author: mrsao

kst
Capital Social
"""
import pandas as pd
import numpy as np
import sys, os

directory = os.path.dirname(os.path.realpath(__file__))
directory = '\\'.join(directory.split('\\')[:-1])

sys.path.insert(1, directory)
from auxiliar import rk4

def main(init_val, para, list_date, clim_type):
    """
    Capital finacierp

    Parameters
    ----------
    init_val : FLOAT
        Valor de capital social inicial
    
    para : dict
        Parámetros de construcción.
        
        para = {...
                'Tasa de vinculación comunitaria' : FLOAT,
                'Tasa de grupo de apoyo ante eventos' : FLOAT,
                'Union de la comunidad ante eventos' : FLOAT,
                'Tasa de percepción positiva de ayudas del gobierno' : FLOAT,
                'Tasa de vinculación productiva' : FLOAT,
                'Tasa de percepción de funcionalidad' : FLOAT,
                'Tasa de no vinculación con organizaciones relacionadas a eventos externos' : FLOAT,
                'Tasa de vinculación familiar' : FLOAT,
                'union de la comunidad ante eventos' : FLOAT,
                ...}
        
    list_date : list
        Listado de las fechas. Format [%Y-%m-%d]
        
        list_date = ['2022-01-01',
                     '2022-02-01',
                     ...
                     '2070-12-01']

    Returns
    -------
    df_res: pandas.DataFrame
        Resultados.

    """
    
    # Lista con el tipo de clima, 0: neutro  1: seco y 2: humedo
    EvExtr = clim_type
    
    # CONSTANTES
    tv_com = para['Tasa de vinculación comunitaria']
    tg_aae = para['Tasa de grupo de apoyo ante eventos']
    tp_p_ag = para['Tasa de percepción positiva de ayudas del gobierno']
    tv_prod = para['Tasa de vinculación productiva']
    # tp_fun = para['Tasa de percepción de funcionalidad']
    tnv_oree = para['Tasa de no vinculación con organizaciones relacionadas a eventos externos']
    tv_fam = para['Tasa de vinculación familiar']
    uc_ae = para['Union de la comunidad ante eventos']
    
    # MAIN
    df_result = pd.DataFrame(data={'Fecha' : list_date})
    num_pass = len(list_date)
    
    # FLOWS - CONSTANTS
    
    # Tasa de percepción de la funcionalidad
    tp_fun = 0.1 * para['Percepción de funcionalidad : Nada -     3'] +\
             0.5 * para['Percepción de funcionalidad :    4 -     7'] +\
               1 * para['Percepción de funcionalidad :    8 - Mucho']
    
    # Beneficios pertenencia organización comunitaria
    bp_oc = [np.mean([tv_com, uc_ae, tg_aae])] * num_pass
    
    # Beneficios pertenencia asociación productiva
    bp_ap = [tv_prod] * num_pass
    
    # Ayudas del gobierno
    ag = [0 if ii == 0 else tp_p_ag for ii in EvExtr]

    
    # Aprendizaje de comportamientos comunitarios y sociales ante eventos 
    # extremos
    accs_aee = [tp_fun] * num_pass
    
    # Desvinculación con organizaciones relacionadas a los eventos extremos
    doree = [tnv_oree * tv_fam / 100] * num_pass
    
    # Add flows to res
    df_result['Beneficios pertenencia organización comunitaria'] = bp_oc
    df_result['Beneficios pertenencia asociación productiva'] = bp_ap
    df_result['Ayudas del gobierno'] = ag
    df_result['Aprendizaje de comportamientos comunitarios y sociales ante eventos extremos'] = accs_aee
    df_result['Desvinculación con organizaciones relacionadas a los eventos extremos'] = doree
    
    # df_result['Capital social instantaneo'] = np.mean([np.array(bp_oc), np.array(bp_ap),
    #                                                   np.array(ag), np.array(accs_aee)], 
    #                                                   axis=0) - np.array(doree)
    
    df_result['Capital social instantaneo'] = np.mean([np.array(bp_oc) + np.array(bp_ap) +\
                                                      np.array(ag) + np.array(accs_aee)], 
                                                      axis=0) - np.array(doree)
    
    # STOCKS
    # Results
    res_lts = [init_val]
    
    # function
    kst_fun = lambda init, ctes : ctes[0] +ctes[1] + ctes[2] + ctes[3] - ctes[4]
    
    for _, row in df_result.iterrows():
        
        cte = [row['Beneficios pertenencia organización comunitaria'],
               row['Beneficios pertenencia asociación productiva'],
               row['Ayudas del gobierno'],
               row['Aprendizaje de comportamientos comunitarios y sociales ante eventos extremos'],
               row['Desvinculación con organizaciones relacionadas a los eventos extremos']]
        
        for ii_pas in np.arange(10): 
            res = rk4(kst_fun, init_val, cte, 1/10)
            init_val = res
        
        res_lts.append(res)
    
    # Add stokcs results
    df_result['KST'] = res_lts[:-1]
    
    
    return df_result

if __name__ == '__main__':
    para = {'Tasa de vinculación comunitaria':0.4,
            'Tasa de grupo de apoyo ante eventos':0.4,
            'Tasa de percepción positiva de ayudas del gobierno':0.4,
            'Tasa de vinculación productiva':0.4,
            # 'Tasa de percepción de funcionalidad':0.4,
            'Tasa de no vinculación con organizaciones relacionadas a eventos externos':0.4,
            'Tasa de vinculación familiar':0.4,
            'Union de la comunidad ante eventos':0.4,
            'Percepción de funcionalidad : Nada -     3': 0.4,
            'Percepción de funcionalidad :    4 -     7': 0.4,
            'Percepción de funcionalidad :    8 - Mucho': 0.4}
            
    list_date = ['2022-01-01', '2022-02-01', '2022-03-01']
    
    clim_type = [0, 1, 2]
    res = main(0, para, list_date, clim_type)
    print(res)
