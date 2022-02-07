# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 11:31:33 2022

@author: mrsao
Capital humano
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
    Capital humano

    Parameters
    ----------
    init_val : FLOAT
        Valore inicial de capital humano.
        
    para : dict
        para = {...
                ...}
        
    list_date : list
        list_date = ['2022-01-01',
                     '2022-02-01',
                     ...
                     '2070-01-01'].

    Returns
    -------
    df_result : pandas.DataFrame
        Dataframe con la series de variables obtenidas.

    """
    # CONSTANTES
    n_pasos = len(list_date)
    Ev_ex   = clim_type
    nh      = para['Hogares']
    nhm_dI  = para['Número de hogares que migraron debido a la inundacion']
    nhm_dS  = para['Número de hogares que migraron debido a la sequia']
    t_salud = para['Porcentaje estado de salud - [0-100]']
    agri    = para['Actividad desarrollada - agricultura']
    gana    = para['Actividad desarrollada - ganaderia']
    pesc    = para['Actividad desarrollada - pesca']
    fore    = para['Actividad desarrollada - forestal']
    come    = para['Actividad desarrollada - comercio']
    acCm    = para['Actividad desarrollada - actividad de campo']
    aNagr   = para['Actividad desarrollada - actividad no agropecuaria']
    comb    = para['Actividad desarrollada - Combinación']
    
    df_result = pd.DataFrame(data = {'Fecha' : list_date})
    
    # MAIN
    # Migracion inundacion - list [0 - 100]
    mig_inund = [100 * nhm_dI / nh] * n_pasos
    
    # Migracion sequia - list [0 - 100]
    mig_sequia = [100 * nhm_dS / nh] * n_pasos
    
    #Migracion total - list [0 - 100]
    mig_total = list(np.array(mig_inund) + np.array(mig_sequia))
    
    # Rango de edades
    rang_edades = "Entre 19 y 60 años"
    
    # Edad promedio
    if rang_edades == "Menores de 6 años":
        edad_prom = 0
    elif rang_edades == 'Entre 6 y 18 años':
        edad_prom = 0.33
    elif rang_edades == "Entre 19 y 60 años":
        edad_prom = 1
    elif rang_edades == "Mayores a 60 años":
        edad_prom = 0.67    
    
    # FLOWS - CONSTANTS
    # Nivel de educación formal - list - [0 - 100]
    if para['Nivel de educación'] == "Ninguno":
        n_eduf = [0] * n_pasos
    elif para['Nivel de educación'] == "Preescolar":
        n_eduf = [16] * n_pasos
    elif para['Nivel de educación'] == "Básica Primaria":
        n_eduf = [33] * n_pasos
    elif para['Nivel de educación'] == "Básica secundaria":
        n_eduf = [50] * n_pasos
    elif para['Nivel de educación'] == "Educación media":
        n_eduf = [67] * n_pasos
    elif para['Nivel de educación'] == "Tecnológica":
        n_eduf = [83] * n_pasos
    elif para['Nivel de educación'] == "Universitaria":
        n_eduf = [100] * n_pasos
    else:
        sys.exit('Nivel de educación incorrecto')
    
    # Migracion - [0-100]
    mig = [0 if ii != 0 else mig_inund[0] + mig_sequia[0] for ii in  Ev_ex]
    
    # Migracion 1 - [0-100]
    mig_1 = np.array([mig_sequia[0] if ii == 1 else 0 for ii in Ev_ex]) +\
        np.array([mig_inund[0] if ii == 2 else 0 for ii in Ev_ex])
    
    # Habilidad manejo de inundacion
    # !!! TODO añadir rango
    hmi = [(0.1) + (0.5) + (1)] * n_pasos
    # !!! end TODO añadir rango
    
    # Mano de obra disponible familiar
    modf = [100 - (t_salud * edad_prom)] * n_pasos
    
    # Habilidades actividades productivas
    hap = [100 * np.mean([agri, gana, pesc, fore, come, acCm,
                         aNagr, comb]) / nh] * n_pasos
    
    # FLOWS - VARIABLES
    
    # Add results to dataframe
    df_result['Migración'] = mig
    df_result['Migración 1'] = mig_1
    df_result['Habilidad Manejo de inundación'] = hmi
    df_result['Mano de obra disponible familiar'] = modf
    df_result['Nivel de educación formal'] = n_eduf
    df_result['Habilidad actividades productivas'] = hap    
    df_result['KHT instantáneo'] = np.mean([mig, hmi, modf, n_eduf,
                                            hap], axis=0) - np.array(mig_1)
    
    # STOCKS
    # Results
    res_lts = [init_val]
    
    # function
    kht_fun = lambda init, ctes: ctes[0] + ctes[1] + ctes[2] + ctes[3] \
        + ctes[4] - ctes[5]
    
    for _, row in df_result.iterrows():
        cte = [row['Migración'],
               row['Habilidad Manejo de inundación'],
               row['Mano de obra disponible familiar'],
               row['Habilidad actividades productivas'],
               row['Nivel de educación formal'],
               row['Migración 1']]
        
        for ii_pas in np.arange(10): 
            res = rk4(kht_fun, init_val, cte, 1/10)
            init_val = res
        
        res_lts.append(res)
        
    # Add stokcs results
    df_result['KHT'] = res_lts[:-1]
    
    return df_result

if __name__ == '__main__':
    init_val = 0
    list_date = ['2022-01-01', '2022-02-01', '2022-03-01']
    para = {'Hogares' : 100,
            'Número de hogares que migraron debido a la inundacion' : 20,
            'Número de hogares que migraron debido a la sequia' : 30,
            'Porcentaje estado de salud - [0-100]': 60,
            'Actividad desarrollada - agricultura': 2,
            'Actividad desarrollada - ganaderia': 5,
            'Actividad desarrollada - pesca': 7,
            'Actividad desarrollada - forestal': 12,
            'Actividad desarrollada - comercio': 1,
            'Actividad desarrollada - actividad de campo': 3,
            'Actividad desarrollada - actividad no agropecuaria': 7,
            'Actividad desarrollada - Combinación': 5,
            'Nivel de educación': 'Básica Primaria'}
    
    # neutro: 0, seco: 1, humedo: 2
    clim_type = [0, 1, 2]
    
    res = main(init_val, para, list_date, clim_type)
