"""
This module provides functions to plot radial velocity curves and apparent orbits on the sky.
This module is developed with matplotlib 3.1.1. and numpy 1.17.2.

Author:
Matthias Fabry, Instituut voor Sterrekunde, KU Leuven, Belgium

Date:
29 Oct 2019
"""
import corner
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import EllipseCollection

plt.rc('text', usetex=True)
plt.rc('font', size=16)


def make_plots():
    """
    Makes two plot objects, and formats one to display RV curves, and the other for relative astrometry
    :return: RV figure, AS figure, RV axis, AS axis
    """
    fig1 = plt.figure(figsize=(10, 5))
    fig2 = plt.figure(figsize=(10, 5))
    ax1 = fig1.add_subplot(111)
    ax2 = fig2.add_subplot(111, aspect=1)
    setup_rvax(ax1)
    setup_asax(ax2)
    fig1.tight_layout()
    fig2.tight_layout()
    return fig1, fig2, ax1, ax2


def setup_asax(asax):
    """
    sets up a given axis for the plotting of the relative orbit
    :param asax: axis to format
    """

    asax.set_xlim((-10, 10))
    asax.invert_xaxis()
    asax.set_ylim((-10, 10))
    asax.set_xlabel(r'$East (mas)$')
    asax.set_ylabel(r'$North (mas)$')
    asax.axhline(linestyle=':', color='black')
    asax.axvline(linestyle=':', color='black')
    asax.grid()


def setup_rvax(rvax):
    """
    sets up a given axis for the plotting of radial velocity curves
    :param rvax: axis to format
    """
    rvax.set_xlabel(r'$orbital$ $phase$')
    rvax.set_ylabel(r'$RV (km s^{-1})$')
    rvax.set_xlim((-0.18, 1.18))
    rvax.set_ylim((-50, 50))
    rvax.axhline(linestyle=':', color='black')
    rvax.grid()


def plot_rv_curves(ax, system):
    """
    Plots RV curves for both components of a given system on a given axis
    :param ax: axis to plot on
    :param system: system to get orbital parameters from
    """
    num = 200
    phases = np.linspace(-0.15, 1.15, num=num)
    vrads1 = system.primary.radial_velocity_of_phases(phases)
    vrads2 = system.secondary.radial_velocity_of_phases(phases)
    ax.plot(phases, vrads1, label='primary', color='b', ls='--')
    ax.plot(phases, vrads2, label='secondary', color='r', ls='--')
    ax.axis('auto')


def plot_relative_orbit(ax, system):
    """
    Plots the relative orbit of a given system on a given axis
    :param ax: axis to plot on
    :param system: system to get orbital parameters from
    """
    num = 200
    ecc_anoms = np.linspace(0, 2 * np.pi, num)
    norths = system.relative.north_of_ecc(ecc_anoms)
    easts = system.relative.east_of_ecc(ecc_anoms)
    ax.plot([system.relative.east_of_ecc(0)], [system.relative.north_of_ecc(0)], marker='s', fillstyle='none',
            label='periastron')
    ax.plot(easts, norths, label='relative orbit', color='r')
    ax.plot([system.relative.east_of_true(-system.relative.omega),
             system.relative.east_of_true(-system.relative.omega + np.pi)],
            [system.relative.north_of_true(-system.relative.omega),
             system.relative.north_of_true(-system.relative.omega + np.pi)], color='0.5', ls='--',
            label='line of nodes')
    ax.axis('image')


def plot_rv_data(rvax, datadict, system):
    """
    Plots the given rv data for a given system on the given axes
    :param rvax: RV axis to plot RV data on
    :param datadict: dictionary with observational data
    :param system: system to get orbital parameters from
    """
    for key, data in datadict.items():
        if key == 'RV1' or key == 'RV2':
            phases, rv, err = system.create_phase_extended_RV(datadict[key], 0.15)
            if key == 'RV1':
                color = 'blue'
            else:
                color = 'red'
            rvax.errorbar(phases, rv, yerr=err, ls='', capsize=0.1, marker='o', ms=5, color=color)
            rvax.axis('auto')


def plot_as_data(asax, datadict):
    """
    Plots the given as data for a given system on the given axes
    :param asax: AS axis to plot astrometric data on
    :param datadict: dictionary with observational data
    """
    for key, data in datadict.items():
        if key == 'AS':
            asax.plot(data['easts'], data['norths'], 'r.')
            ellipses = EllipseCollection(2 * data['majors'], 2 * data['minors'], data['pas'] - 90,
                                         offsets=np.column_stack((data['easts'], data['norths'])),
                                         transOffset=asax.transData,
                                         units='x', edgecolors='k', facecolors=(0, 0, 0, 0))
            asax.add_collection(ellipses)
            plotmin = min(min(data['easts']), min(data['norths']))
            plotmax = max(max(data['easts']), max(data['norths']))
            asax.set_xlim([plotmax + 2, plotmin - 2])
            asax.set_ylim([plotmin - 2, plotmax + 2])
            asax.axis('image')


def plot_corner_diagram(mcmcresult):
    return corner.corner(mcmcresult.flatchain, labels=mcmcresult.var_names,
                         truths=list(mcmcresult.params.valuesdict().values()))
