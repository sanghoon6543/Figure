import numpy as np
import pandas as pd

import xlsxwriter

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.pyplot import tight_layout, xscale
from matplotlib.ticker import MultipleLocator, Locator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.image as mImage

import tkinter
from tkinter import *
import pathlib
from os.path import isfile, join


colorstyle = plt.cm.bwr
# colorstyle = plt.cm.gist_rainbow
alphavalue = 0.6


fh = 400
fw = fh*2
fs = (fw/200, 0.7*fh/100)

class FigureConfig:
    @staticmethod
    def MakeFigureWidget(frame, figuresize):
        fig, ax = plt.subplots(figsize=figuresize, tight_layout=True)
        tk_plt = FigureCanvasTkAgg(fig, frame)
        tk_plt.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=1)
        plt.close(fig)
        return ax, tk_plt

    @staticmethod
    def MakeFigure(figuresize, legendinfo):
        color = iter(colorstyle(np.linspace(1, 0, legendinfo.__len__())))
        fig, ax = plt.subplots(figsize=figuresize, tight_layout=True)
        return ax, color

    @staticmethod
    def FigureConfiguration(ax, inputinfo, ftstyle='Calibri', ftsize=24, tickftsize=10):
        ax.set_title(inputinfo['Title'], font=ftstyle, fontsize=ftsize)
        ax.set_xlabel(inputinfo['xAxisTitle'], font=ftstyle, fontsize=ftsize)
        ax.set_ylabel(inputinfo['yAxisTitle'], font=ftstyle, fontsize=ftsize)
        ax.set_xlim((float(inputinfo['xLim_0']), float(inputinfo['xLim_1'])))
        ax.set_ylim((float(inputinfo['yLim_0']), float(inputinfo['yLim_1'])))

        if inputinfo['xScale'] == 'Linear':
            ax.xaxis.set_major_locator(MultipleLocator(float(inputinfo['MajorTickXY_0'])))
        elif inputinfo['xScale'] == 'SymLog':
            FigureConfig.SymlogScale(ax, float(inputinfo['xLim_0']), float(inputinfo['xLim_1']), float(inputinfo['xLim_0']), float(inputinfo['MajorTickXY_0']), 'x')

        if inputinfo['yScale'] == 'Linear':
            ax.yaxis.set_major_locator(MultipleLocator(float(inputinfo['MajorTickXY_1'])))
        elif inputinfo['yScale'] == 'SymLog':
            FigureConfig.SymlogScale(ax, float(inputinfo['yLim_0']), float(inputinfo['yLim_1']), float(inputinfo['yLim_0']), float(inputinfo['MajorTickXY_1']), 'y')

        if inputinfo['Grid'] == 'Grid ON':
            ax.grid(True)
        ax.tick_params(axis='x', labelsize=tickftsize)
        ax.tick_params(axis='y', labelsize=tickftsize)
        plt.tight_layout()

    @staticmethod
    def SymlogScale(ax, linthresh, up, dn, interval, axis):

        tickorder = np.arange(np.log10(up), np.log10(dn), -np.log10(interval))
        if tickorder[-1] != np.log10(dn):
            tickorder = np.append(tickorder, np.log10(dn))
        tick = 10 ** tickorder

        if axis == 'x':
            ax.set_xscale("symlog", linthresh=linthresh)
            ax.set_xticks(tick)
            ax.xaxis.set_minor_locator(MinorSymLogLocator(linthresh, (dn, up)))

        if axis == 'y':
            ax.set_yscale("symlog", linthresh=linthresh)
            ax.set_yticks(tick)
            ax.yaxis.set_minor_locator(MinorSymLogLocator(linthresh, (dn, up)))


    @staticmethod
    def forceAspect(ax, xscale, yscale, aspect=1):
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        if xscale == yscale:
            ax.set_aspect(abs((xlim[1] - xlim[0]) / (ylim[1] - ylim[0])) / aspect)
        elif xscale == "SymLog" and yscale == "Linear":
            ax.set_aspect(0.1*abs((np.log10(xlim[1]) - np.log10(xlim[0])) / (ylim[1] - ylim[0])) / aspect)
        elif xscale == "Linear" and yscale == "SymLog":
            ax.set_aspect(10*abs((xlim[1] - xlim[0]) / (np.log10(ylim[1]) - np.log10(ylim[0]))) / aspect)


class DataProcessing:
    @staticmethod
    def ReadClipboard():
        return pd.read_clipboard(header=None)

    @staticmethod
    def GetEntry(EntryAddress):
        return EntryAddress.get()


class MinorSymLogLocator(Locator):
    """
    Dynamically find minor tick positions based on the positions of
    major ticks for a symlog scaling.
    """

    def __init__(self, linthresh, datarange):
        """
        Ticks will be placed between the major ticks.
        The placement is linear for x between -linthresh and linthresh,
        otherwise its logarithmically
        """
        self.datarange = datarange
        self.linthresh = linthresh

    def __call__(self):
        'Return the locations of the ticks'
        # majorlocs = self.axis.get_majorticklocs()
        majorlocs = 10 ** np.arange(np.log10(self.datarange[1]),
                                    np.log10(self.datarange[0]) - 1, -1)

        # iterate through minor locs
        minorlocs = []

        # handle the lowest part
        for i in range(1, len(majorlocs)):
            majorstep = majorlocs[i] - majorlocs[i - 1]
            if abs(majorlocs[i - 1] + majorstep / 2) < self.linthresh:
                ndivs = 10
            else:
                ndivs = 9
            minorstep = majorstep / ndivs
            locs = np.arange(majorlocs[i - 1], majorlocs[i], minorstep)[1:]
            minorlocs.extend(locs)

        return self.raise_if_exceeds(np.array(minorlocs))

    def tick_values(self, vmin, vmax):
        raise NotImplementedError('Cannot get tick locations for a '
                                  '%s type.' % type(self))

    #
    # def TextatTargetPos(self, xval, data):
    #     yidx = (np.abs(data[0]-xval)).argmin()
    #     TextHere = f"Deviation: {np.abs(100*data[1][yidx]/(self.data1[0] - data[1][yidx]))}"
    #     self.drawax.text(xval, data[1][yidx], TextHere, fontsize=fontstyle['FontSize'])
    #
    # def SaveFigure(self):
    #
    #     filepath = tkinter.filedialog.asksaveasfilename(initialdir=f"{fd}/",
    #                                                     title="Save as",
    #                                                     filetypes=(("png", ".png"),
    #                                                                ("all files", "*")))
    #     filepath = f"{filepath}.png"
    #
    #     self.fig.savefig(filepath)
    #
