# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 07:46:50 2022

@author: mrsao

Modelo de mineria
"""
import numpy as np
import pandas as pd
import os, sys

directory = os.path.dirname(os.path.realpath(__file__))
directory = '\\'.join(directory.split('\\')[:-1])

sys.path.insert(1, directory)
from auxiliar import rk4

class ModeloMineria:
    def __init__(self, hd_data, para):
        """
        Modelo de mineria __init__        
        
        Parameters
        ----------
        hd_data : pandas.DataFrame
            pd.Dataframe(data = { 'Nivel' : [2.1, 2.2, ... 3.0],
                                  'Date'  : ['2022-01-01', '2022-02-01', ... 
                                             '2070-12-01']})
            Nivel: Profundidad en m
            Date:  format %Y-%m-%d
            
        para : dict
            para = { ...
                    'Nivel referencia de productividad',
                    'Productividad por área',
                    'Oro vendido',
                    'Precio gramo de oro',
                    'Costos',
                    ... }
        Returns
        -------
        None.

        """
        self.hd_resultados = hd_data
        self.para = para
    
    
    def precalc(self):
        '''
        Pre calculos modelo de mineria

        Returns
        -------
        None.

        '''
        date = pd.to_datetime(self.hd_resultados['Date'], format='%d-%m-%Y')
        num_pass = len(date)
        
        self.date = date
        self.num_pass = num_pass
        
    
    def oro_extraido(self, init_val):
        """
        Modelo oro extraido, parte del modelo de mineria

        Parameters
        ----------
        init_val : Float
            Valor inicial del oro extraido.

        Returns
        -------
        df_result : pandas.DataFrame
            pandas.DataFrame(data = {'Fecha' : [...],
                                     'Incremento de productividad por área' : [...],
                                     'Extracción de oro' : [...],
                                     'Ventas' : [...],
                                     'Oro extraido' : [...]})
        """
        
        # CONSTANTS
        df_result = pd.DataFrame(data={'Fecha' : self.date})
        prod_area = self.para['Productividad por área']
        oro_vendido = self.para['Oro vendido']
        
        # Incremento de productividad por área
        ref_niv_prod = self.para['Nivel referencia de productividad']
        df_result['Incremento de productividad por área'] = \
            [ 1.0 if nivel < ref_niv_prod else 1.3 for nivel in \
             list(self.hd_resultados['Nivel'])]
        
        # FLOWS = CONTANTS
        # Extracción de oro
        df_result['Extracción de oro'] = prod_area * \
            df_result['Incremento de productividad por área']
            
        # Ventas
        df_result['Ventas oro'] = [oro_vendido] * self.num_pass
        
        # STOCKS
        # Results
        res_lts = [init_val]
        
        # function
        min_fun = lambda init, ctes : ctes[0] - ctes[1]
        
        for _, row in df_result.iterrows():
        
            cte = [row['Extracción de oro'],
                   row['Ventas oro']]
            
            for ii_pas in np.arange(10): 
                res = rk4(min_fun, init_val, cte, 1/10)
                init_val = res
            
            res_lts.append(res)
        
        # Add stokcs results
        df_result['Oro extraido'] = res_lts[:-1]
        
        return df_result
    
    def kf_modelo_mineria(self, init_val, df_oro_extraido):
        # CONSTANTS
        df_result = pd.DataFrame(data={'Fecha' : self.date})
        
        ventas = df_oro_extraido['Ventas oro']
        precio_gr_oro = self.para['Precio gramo de oro']
        costos = self.para['Costos']
        
        # FLOWS - CONSTANTS
        df_result['Ingresos totales KFM'] = ventas * precio_gr_oro
        df_result['Costos minería'] = costos
        
        # STOCKS
        # Results
        res_lts = [init_val]
        
        # Function
        kfm_fun = lambda init, ctes : ctes[0] - ctes[1]
        
        for _, row in df_result.iterrows():
        
            cte = [row['Ingresos totales KFM'],
                   row['Costos minería']]
            
            for ii_pas in np.arange(10): 
                res = rk4(kfm_fun, init_val, cte, 1/10)
                init_val = res
            
            res_lts.append(res)
        
        # Add stokcs results
        df_result['KF Mineria'] = res_lts[:-1]
        
        return df_result

if __name__ == '__main__':
    os.chdir(os.getcwd())
    tray = r'input\SINPRESA_MIROC_RCP_4.5_SocialInput.csv'
    hd_data_full = pd.read_csv(tray, header=[1,2,3])
    hd_data_fill = pd.DataFrame(data={'Date' : hd_data_full[('Sector',
                                                             'Especie',
                                                             'Variable.1')],
                                      'Nivel' : hd_data_full[('Cano',
                                                              'Nivel',
                                                              'Promedio_Nivel_(m)')]})
    
    para = {'Nivel referencia de productividad': 28.5,
            'Productividad por área': 842.61355937,
            'Oro vendido': 302.6224991,
            'Precio gramo de oro' : 207842.96,
            'Costos': 95681.64}
    
    init_oro = 0
    init_kfm = 0
    
    foo = ModeloMineria(hd_data=hd_data_fill, para=para)
    foo.precalc()
    oro_df = foo.oro_extraido(init_oro)
    kfmin_df = foo.kf_modelo_mineria(init_kfm, oro_df)