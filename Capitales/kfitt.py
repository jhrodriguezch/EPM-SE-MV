# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 12:33:49 2022

@author: mrsao

Capital físico
"""
import pandas as pd
import numpy as np
import sys, os

directory = os.path.dirname(os.path.realpath(__file__))
directory = '\\'.join(directory.split('\\')[:-1])

sys.path.insert(1, directory)
from auxiliar import rk4

def main(init_val, para,
         kst_df, kht_df):
    """
    Calculo del capital físico

    Parameters
    ----------
    init_val : FLOAT
        Valore del capital físico.
    para : dict
        Parámetros de construcción.
        
        para = {...
                'Vivienda - Propia' : FLOAT,
                'Vivienda - Arriendo' : FLOAT,
                'Vivienda - Aparceria' : FLOAT,
                'Vivienda - Usufructo' : FLOAT,
                'Vivienda - Comodato' : FLOAT,
                'Vivienda - Ocupación de hecho' : FLOAT,
                'Vivienda - Propiedad colectiva' : FLOAT,
                'Vivienda - Adjudicatario' : FLOAT,
                'Porcentaje de no obtención - Automovil o moto' : FLOAT,
                'Porcentaje de no obtención - Tractor' : FLOAT,
                'Porcentaje de no obtención - Inta. especiales' : FLOAT,
                'Porcentaje de no obtención - Herr. agrícolas' : FLOAT,
                'Porcentaje de SI actuación miembros del hogar' : FLOAT,
                'Promedio de rangos de uso de la tierra' : FLOAT,
                'rango' : FLOAT,
                ...}

    Returns
    -------
    df_res: pandas.DataFrame
        Resultados.
    """
    # CONSTANTES
    v_pro     = para['Vivienda - Propia']
    v_arr     = para['Vivienda - Arriendo']
    v_apa     = para['Vivienda - Aparceria']
    v_usu     = para['Vivienda - Usufructo']
    v_com     = para['Vivienda - Comodato']
    v_ocuhec  = para['Vivienda - Ocupación de hecho']
    v_pro_col = para['Vivienda - Propiedad colectiva']
    v_adj     = para['Vivienda - Adjudicatario']
    
    pno_auto       = para['Porcentaje de no obtención - Automovil o moto']
    pno_trac       = para['Porcentaje de no obtención - Tractor']
    pno_iesp       = para['Porcentaje de no obtención - Inta. especiales']
    pno_herr       = para['Porcentaje de no obtención - Herr. agrícolas']
    inf_or_man_eve = para['Porcentaje de SI actuación miembros del hogar']
    inf_agr_pec    = para['Promedio de rangos de uso de la tierra']
    rang_kfitt     = para['Rango capital físico : Infraestructura disponible']
    
    # MAIN
    df_result = pd.DataFrame(data={'Fecha' : list(kst_df['Fecha'])})
    num_pass = len(kst_df)
    
    # FLOWS - CONSTANTS
    # Tipoficación de vivienda - list
    tip_viv = [1 * v_pro + 0.8 * v_arr + 0.2 * v_apa + 0.2 * v_ocuhec + 0.5 *\
               v_usu + 0.1 * v_com + 0.1 * v_pro_col + 0 * v_adj] * num_pass
        
    # Infraestructura disponible - list
    if rang_kfitt > 0 and rang_kfitt <= 0.25:
        rang_kfitt_fix = 25
    elif rang_kfitt > 0.25 and rang_kfitt <= 0.5:
        rang_kfitt_fix = 50
    elif rang_kfitt > 0.5 and rang_kfitt <= 0.99:
        rang_kfitt_fix = 75
    elif rang_kfitt > 0.99:
        rang_kfitt_fix = 100
    else:
        sys.error('Rango valor incorrecto. Debe ser mayor a 0')
    
    inf_dis = [inf_agr_pec * rang_kfitt_fix] * num_pass
    
    # Falta de recursos    
    fal_rec = [np.mean([pno_auto, pno_trac, pno_iesp, pno_herr], axis=0)] * num_pass
    
    # FLOWS - VAR
    # Infraestructura productiva - list
    
    inf_pro = np.mean([inf_dis, 
                      kst_df['Beneficios pertenencia organización comunitaria'],
                      kst_df['Beneficios pertenencia asociación productiva']], 
                      axis=0)
    
    # Infraestructura manejo de eventos - list
    # inf_man_eve = list(inf_or_man_eve * kht_df['Experiencia manejo de eventos'])
    inf_man_eve = inf_or_man_eve * kht_df['Experiencia manejo de eventos']
    
    # Add flows to res
    df_result['Tipificación de vivienda'] = tip_viv
    df_result['Infraestructura productiva'] = inf_pro
    df_result['Infraestructura manejo de eventos'] = inf_man_eve
    df_result['Falta de recursos'] = fal_rec
    df_result['_Infraestructura disponible'] = inf_dis
    
    df_result['Capital físico instantaneo'] = \
        np.mean([inf_pro, tip_viv, inf_man_eve], axis=0) - np.mean([fal_rec], axis=0)
    
    # STOCKS
    # Results
    res_lts = [init_val]
    
    # function
    kfitt_fun = lambda init, ctes: ctes[0] + ctes[1] + ctes[2] - ctes[3]
    
    for _, row in df_result.iterrows():
        
        cte = [row['Tipificación de vivienda'],
               row['Infraestructura productiva'],
               row['Infraestructura manejo de eventos'],
               row['Falta de recursos']
               ]
        
        for ii_pas in np.arange(10): 
            res = rk4(kfitt_fun, init_val, cte, 1/10)
            init_val = res
        
        res_lts.append(res)
    
    # Add stokcs results
    df_result['KFITT'] = res_lts[:-1]
    
    return df_result

if __name__ == '__main__':
    init_val = 0
    para = {'Vivienda - Propia' : 0.4,
            'Vivienda - Arriendo' : 0.4,
            'Vivienda - Aparceria' : 0.4,
            'Vivienda - Usufructo' : 0.4,
            'Vivienda - Comodato' : 0.4,
            'Vivienda - Ocupación de hecho' : 0.4,
            'Vivienda - Propiedad colectiva' : 0.4,
            'Vivienda - Adjudicatario' : 0.4,
            'Porcentaje de no obtención - Automovil o moto' : 0.4,
            'Porcentaje de no obtención - Tractor' : 0.4,
            'Porcentaje de no obtención - Inta. especiales' : 0.4,
            'Porcentaje de no obtención - Herr. agrícolas' : 0.4,
            'Porcentaje de SI actuación miembros del hogar' : 0.4,
            'Promedio de rangos de uso de la tierra' : 0.4,
            'Rango capital físico : Infraestructura disponible' : 0.2}
    
    kst_df = pd.DataFrame(data={'Fecha': ['2022-01-01', '2022-02-01', '2022-03-01'],
                                'Beneficios pertenencia organización comunitaria': [0.4, 0.4, 0.4],
                                'Beneficios pertenencia asociación productiva': [0.4, 0.4, 0.4]})
    kht_df = pd.DataFrame(data={'Experiencia manejo de eventos': [0.5, 0.5, 0.5]})
    
    res = main(init_val, para,
                kst_df, kht_df)
    print(res)
