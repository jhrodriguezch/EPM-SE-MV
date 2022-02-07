# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 11:19:35 2022

@author: mrsao

auxiliar

"""
import numpy as np
import sys

def rk4(fun, var_ini, cte, dt):
    """
    Runge Kutta 4th order
    :param fun: function
    :param var_ini: Any
    :param cte: List
    :param dt: Any
    :return: var_end: Any

    Example:
    fun = lambda var, cte: cte[0] - var * cte[1]
    fun(var) = cte[0] - var * cte[1]
    """
    k1 = dt * fun(var_ini, cte)
    k2 = dt * fun(var_ini + 1 / 2 * k1, cte)
    k3 = dt * fun(var_ini + 1 / 2 * k2, cte)
    k4 = dt * fun(var_ini + k3, cte)
    return var_ini + (k1 + 2 * k2 + 2 * k3 + k4) / 6.

def inter_pol_fun(x, x_lst, y_lst, yx_men = 1, yx_may = 0):
    
    x_lst = np.array(x_lst)
    y_lst = np.array(y_lst)
    
    # TEST
    if len(x_lst) != len(y_lst):
        sys.exit('x list and y list should be same leng')
    
    # MAIN
    if x <= min(x_lst):
        return  yx_men
    elif x >= max(x_lst):
        return yx_may
    else:
        return np.interp(x, x_lst, y_lst)
