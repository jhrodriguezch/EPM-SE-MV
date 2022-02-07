# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 10:25:20 2022

@author: mrsao

Modelo Mineria
"""
import numpy as np
import pandas as pd
import os, sys

directory = os.path.dirname(os.path.realpath(__file__))
directory = '\\'.join(directory.split('\\')[:-1])

sys.path.insert(1, directory)
from auxiliar import rk4, inter_pol_fun

class ModeloGanaderia:
    
    def __init__(self, hd_data, para, past_inu = 0):
        """
        Modelo de ganadería

        Parameters
        ----------
        hd_data : pandas.DataFrame
            Resultados trayectoría hidrodinámica.
            
            hd_data = pandas.DataFrame(
                data = {'Date' : [...], # format = '%Y-%m-%d'
                        'Nivel': [...]}
                )
            
        para : dict
            
            para = { ...
                    'Tasa de reforestación',
                    'Tasa de deforestación',
                    'Tasa de pastos a cultivos',
                    'Tasa de cultivos a pastos',
                    'Tasa de poterización',
                    'Tiempo de desinundación',
                    'CC por hectareas',
                    'Tasa de mortalidad natural',
                    'Porcentaje por ventas',
                    'Tasa de natalidad vs rel. vacas - Tasa de natalidad',
                    'Tasa de natalidad vs rel. vacas - Relación vacas CC',
                    ... }.
            
        past_inu : pandas.DataFrame()
        
        Returns
        -------
        None.

        """
        self.hd_resultados = hd_data
        self.para = para
        self.past_inu = past_inu
    
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
    
    
    def eco_area(self, init_val):
        """
        Modelo del ecosistema para la ganadería

        Parameters
        ----------
        init_val : list
            Valores iniciales de los diferentes tipos de coberturas
            encontradas en el sector de estudio.
            
            inti_val = [init_pasto,
                        init_bosque,
                        init_terriotorios agricolas,
                        init_Áreas humedas continentales,
                        init_Patos inundados]

        Returns
        -------
        None.

        """
        # CONSTANTS
        t_reforest = self.para['Tasa de reforestación']
        t_deforest = self.para['Tasa de deforestación']
        t_pas_cult = self.para['Tasa de pastos a cultivos']
        t_cult_pas = self.para['Tasa de cultivos a pastos']
        t_potreriz = self.para['Tasa de poterización']
        t_tim_desi = self.para['Tiempo de desinundación']
        
        df_res = pd.DataFrame(data = {'Fecha'  : self.date})
        
        por_pas_ini = 0
        self.por_pas_ini = por_pas_ini
        
        # FLOWS CONSTANTS
        # N/A
        
        # FLOWS VAR
        reforet_fun = lambda x : t_reforest * x
        defores_fun = lambda x : t_deforest * x
        pas_cul_fun = lambda x : t_pas_cult * x
        cul_pas_fun = lambda x : t_cult_pas * x
        potreri_fun = lambda x : t_potreriz * x
        inundac_fun = lambda x : self.por_pas_ini * x
        desecac_fun = lambda x : 0 if por_pas_ini == 0 else x / t_tim_desi
        
        pas_init = init_val[0]
        bos_init = init_val[1]
        agr_init = init_val[2]
        ahc_init = init_val[3]
        pin_init = init_val[4]
        
        pas_lst = [pas_init]
        bos_lst = [bos_init]
        agr_lst = [agr_init]
        ahc_lst = [ahc_init]
        pin_lst = [pin_init]
        
        # STOCKS
        # Bosque = reforestacion - deforestacion
        bos_stock_fun = lambda init, ctes : reforet_fun(ctes[0]) - defores_fun(init)
        # Terr. Agricolas = PasToCul - CulToPas
        agr_stock_fun = lambda init, ctes : pas_cul_fun(ctes[0]) - cul_pas_fun(init)
        # Pastos inundados = Inundación - Desecación
        pin_stock_fun = lambda init, ctes : inundac_fun(ctes[0]) - desecac_fun(init)
        # Áreas húmedas continentales = - potrerización
        ahc_stock_fun = lambda init, ctes : - potreri_fun(init)
        # Pastos = deforestacion + CultToPas + potrerizacion + desecacion 
        #          - reforestacion - pasToCult - Inundacion
        pas_stock_fun = lambda init, ctes : defores_fun(ctes[0]) + cul_pas_fun(ctes[1]) +\
            potreri_fun(ctes[2]) + desecac_fun(ctes[3]) - reforet_fun(init) - pas_cul_fun(init) -\
            inundac_fun(init)
            
        for _, row in df_res.iterrows():
            
            for ii_pas in np.arange(10):
                
                cte_bos = [pas_init]
                cte_agr = [pas_init]
                cte_pin = [pas_init]
                cte_ahc = [pas_init]
                
                cte_pas = [bos_init, agr_init, ahc_init, pin_init]
                
                res_bos = max( 0, rk4(bos_stock_fun, bos_init, cte_bos, 1/10))
                res_agr = max( 0, rk4(agr_stock_fun, agr_init, cte_agr, 1/10))
                res_pin = max( 0, rk4(pin_stock_fun, pin_init, cte_pin, 1/10))
                res_ahc = max( 0, rk4(ahc_stock_fun, ahc_init, cte_ahc, 1/10))
                res_pas = max( 0, rk4(pas_stock_fun, pas_init, cte_pas, 1/10))
                
                pas_init = res_pas
                bos_init = res_bos
                agr_init = res_agr
                ahc_init = res_ahc
                pin_init = res_pin
                
            pas_lst.append(pas_init)
            bos_lst.append(bos_init)
            agr_lst.append(agr_init)
            ahc_lst.append(ahc_init)
            pin_lst.append(pin_init)
        
        df_res['Pastos'] = pas_lst[:-1]
        df_res['Bosque'] = bos_lst[:-1]
        df_res['Territorios agrícolas'] = agr_lst[:-1]
        df_res['Área humedas continentales'] = ahc_lst[:-1]
        df_res['Pastos inundados'] = pin_lst[:-1]
        
        return df_res
    
    
    def ganaderia(self, init_val, df_eco):
        """
        Modelo servicio ecosistémico ganadería.

        Parameters
        ----------
        init_val : FlOAT
            Cantodad de cabeza de gano por ha inicial.
        df_eco : pandas.DataFrame.
            DataFrame con los resultados del Modelo del ecosistema para la ganadería.

        Returns
        -------
        df_res : pandas.DataFrame.
            DataFrame con los resultados del Modelo de servicios ecosistémicos ganadería.

        """
        
        # CONSTANTS
        cc_ha = self.para['CC por hectareas']
        t_mort_nat = self.para['Tasa de mortalidad natural']
        p_ventas = self.para['Porcentaje por ventas']
        
        relvac_tnata_x = self.para['Tasa de natalidad vs rel. vacas - Tasa de natalidad']
        relvac_tnata_y = self.para['Tasa de natalidad vs rel. vacas - Relación vacas CC']
        df_res = pd.DataFrame(data = {'Fecha'  : self.date})
        
        # FLOWS CONSTANTS
        # N/A
        
        # FLOWS VAR
        rel_vac_cc_fun = lambda init: init / cc_ha
        t_nata_fun = lambda init : inter_pol_fun(rel_vac_cc_fun(init),
                                                 relvac_tnata_x, 
                                                 relvac_tnata_y)
        cg_nue_fun = lambda init : init * t_nata_fun(init)
        
        cg_mue_inu_fun = lambda init : init * self.por_pas_ini
        cg_mue_fun = lambda init : init * t_mort_nat + cg_mue_inu_fun(init)
        
        cg_ven_fun = lambda init : init * p_ventas
        
        cg_lst = [init_val] 
        cg_nue_lst = [float('nan')]
        cg_mue_lst = [float('nan')]
        cg_ven_lst = [float('nan')]
        
        # STOCKS
        # Cabezas de ganado por ha
        cg_fun = lambda init, ctes : cg_nue_fun(init) - cg_mue_fun(init) - \
            cg_ven_fun(init)
        
        for _, row in df_res.iterrows():
            for ii_pas in np.arange(10):
                cte = []
                res = max(0, rk4(cg_fun, init_val, cte, 1/10))
                init_val = res
                
                cg_nue = cg_nue_fun(init_val)
                cg_mue = cg_mue_fun(init_val)
                cg_ven = cg_ven_fun(init_val)
                
            cg_lst.append(res)
            cg_nue_lst.append(cg_nue)
            cg_mue_lst.append(cg_mue)
            cg_ven_lst.append(cg_ven)
            
        df_res['Cabezas de ganado por ha'] = cg_lst[:-1]
        
        df_res['Cabezas nuevas'] = cg_nue_lst[:-1]
        df_res['Muertes cabezas de ganado'] = cg_mue_lst[:-1]
        df_res['Cabezas vendidas'] = cg_ven_lst[:-1]
        
        df_res['Total Cabezas de ganado'] = df_res['Cabezas de ganado por ha'] * df_eco['Pastos']
        
        return df_res
    
    def kf_modelo_ganaderia(self, init_val, gan_df, df_eco):
        # CONSTANTS
        p_macho = self.para['Precio por macho']
        p_hembra = self.para['Precio por hembra']
        f_macho = self.para['Fración machos']
        f_hembra = self.para['Fracción hembras']
        insumos = self.para['Insumos']
        
        afvsdis_x = self.para['Afectación al KF vs Pas. inundados - Pas. inundados']
        afvsdis_y = self.para['Afectación al KF vs Pas. inundados - Afectación al KF']
        
        kfg_lst = [init_val] 
        inv_lst = [float('nan')]
        dis_kf_lst = [float('nan')]
        
        df_res = pd.DataFrame(data = {'Fecha'  : self.date})
        
        # FLOWS CONSTANTS
        df_res['Ventas totales'] = gan_df['Cabezas vendidas'] * \
            (p_macho * f_macho + p_hembra * f_hembra)
        df_res.loc[df_res['Ventas totales'].isna() ,'Ventas totales']  = 0
        
        # FLOWS VAR
        inv_fun = lambda init : insumos * init
        dis_kf_fun = lambda init : init * inter_pol_fun(self.por_pas_ini,
                                                        afvsdis_x,
                                                        afvsdis_y,
                                                        yx_men = 0,
                                                        yx_may = 2)
        
        # STOCKS
        # Capital financiero
        kf_gan_fun = lambda init, ctes : ctes[0] - inv_fun(init) - dis_kf_fun(init)
        
        for _, row in df_res.iterrows():
            
            inv_lst.append(inv_fun(init_val))
            dis_kf_lst.append(dis_kf_fun(init_val))
            
            for ii_pas in np.arange(10):
                cte = [row['Ventas totales']]
                res = max(0, rk4(kf_gan_fun, init_val, cte, 1/10))
                init_val = res
            
            kfg_lst.append(res)
        
        df_res['Inversion'] = inv_lst[:-1]
        df_res['Disminución de KF'] = dis_kf_lst[:-1]
        df_res['K Financiero'] = kfg_lst[:-1]
        
        df_res['K Finaciero Tramo'] = df_res['K Financiero'] * df_eco['Pastos']
        
        return df_res
    
    
if __name__ == '__main__':
    os.chdir(os.getcwd())
    tray = os.path.join(directory, 'input\\SINPRESA_MIROC_RCP_4.5_SocialInput.csv')
    hd_data_full = pd.read_csv(tray, header=[1,2,3])
    hd_data_fill = pd.DataFrame(data={'Date' : hd_data_full[('Sector',
                                                             'Especie',
                                                             'Variable.1')],
                                      'Nivel' : hd_data_full[('Cano',
                                                              'Nivel',
                                                              'Promedio_Nivel_(m)')]})
    
    para = {'Tasa de reforestación' : 0.00116667,
            'Tasa de deforestación' : 0.12,
            'Tasa de pastos a cultivos' : 0.24,
            'Tasa de cultivos a pastos' : 0.24,
            'Tasa de poterización' : 0.02,
            'Tiempo de desinundación' : 1,
            
            'CC por hectareas' : 2,
            'Tasa de mortalidad natural' : 0.1,
            'Porcentaje por ventas' : 0.2,
            'Tasa de natalidad vs rel. vacas - Tasa de natalidad': [0.0,
                                                                    0.2,
                                                                    0.4,
                                                                    0.6,
                                                                    0.8,
                                                                    1.0,
                                                                    1.2,
                                                                    1.4,
                                                                    1.6,
                                                                    1.8,
                                                                    2.0],
            'Tasa de natalidad vs rel. vacas - Relación vacas CC': [0.9933,
                                                                    0.982,
                                                                    0.9526,
                                                                    0.8808,
                                                                    0.7311,
                                                                    0.3,
                                                                    0.192,
                                                                    0.1192,
                                                                    0.04743,
                                                                    0.01799,
                                                                    0.006693],
            
            'Precio por macho' : 2090000,
            'Precio por hembra' : 1382500,
            'Fración machos' : 0.38,
            'Fracción hembras' : 0.62,
            'Insumos' : 0.9,
            'Afectación al KF vs Pas. inundados - Pas. inundados' : [0.0000,
                                                                     0.09091,
                                                                     0.1818,
                                                                     0.2727,
                                                                     0.3636,
                                                                     0.4545,
                                                                     0.5455,
                                                                     0.6364,
                                                                     0.7273,
                                                                     0.8182,
                                                                     0.9091,
                                                                     1.000],
            
            'Afectación al KF vs Pas. inundados - Afectación al KF' : [0.000,
                                                                       0.1818,
                                                                       0.3636,
                                                                       0.5455,
                                                                       0.7273,
                                                                       0.9091,
                                                                       1.091,
                                                                       1.273,
                                                                       1.455,
                                                                       1.636,
                                                                       1.818,
                                                                       2.000],
            }
    
    init_area = [549555,
                 138368,
                 289196,
                 242597,
                 0]
    init_gan = 1
    init_kfg = 330000
    
    foo = ModeloGanaderia(hd_data=hd_data_fill, para=para)
    foo.precalc()
    eco_df = foo.eco_area(init_area)
    gan_df = foo.ganaderia(init_gan, eco_df)
    kfg_df = foo.kf_modelo_ganaderia(init_kfg, gan_df, eco_df)
