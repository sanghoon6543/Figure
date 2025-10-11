
from tkinter import *
import pathlib
import matplotlib.pyplot as plt

import UI_Config as UI
import DrawingUtility as UTIL


fd = pathlib.Path(__file__).parent.resolve()
fh = 400
fw = fh*2
fs = (fw/200, 0.7*fh/100)

class Clipboard2Fig:
    def __init__(self, window):
        self.window = UI.UI_tkinter.MakeWindow(window, 'DrawFigure', fw, fh, False, background='grey94')
        self.__main__()
        self.InputInfo = self.EntryAddress.copy()

    def Event_ApplyInfo(self, frame, entryadress, ftstyle='Calibri', ftsize=24, tickftsize=10):

        ### Update Ipuntinfo
        for key in entryadress:
            self.InputInfo[key] = UTIL.DataProcessing.GetEntry(entryadress[key])

        ### legend split
        self.InputInfo['Legend'] = self.InputInfo['Legend'].split(', ')

        ## Make Preview Widget
        if not hasattr(self, 'ax'):
            self.ax, self.canvas = UTIL.FigureConfig.MakeFigureWidget(frame, fs)

        ### Draw Preview Figure
        self.ax.cla()
        UTIL.FigureConfig.FigureConfiguration(self.ax, self.InputInfo, ftstyle, ftsize, tickftsize)
        UTIL.FigureConfig.forceAspect(self.ax, self.InputInfo['xScale'], self.InputInfo['yScale'], aspect=1)
        self.canvas.draw()
        plt.close(plt.gcf())

    def Event_NewFigure(self, inputinfo, ftstyle='Calibri', ftsize=24, tickftsize=10):
        self.drawax, self.color = UTIL.FigureConfig.MakeFigure(fs, inputinfo['Legend'], inputinfo['ColorStyleAlpha_0'])
        UTIL.FigureConfig.FigureConfiguration(self.drawax, inputinfo, ftstyle, ftsize, tickftsize)
        UTIL.FigureConfig.forceAspect(self.drawax, inputinfo['xScale'], inputinfo['yScale'], aspect=1)

    def Event_DrawCurve(self, ax, color, legendinfo, alphavalue, marker='None', ftsize=16):

        data = UTIL.DataProcessing.ReadClipboard()
        c = next(color)

        ax.plot(data[0], data[1], marker, c=c, alpha=alphavalue)

        ax.legend(legendinfo[:], loc='best', fontsize=ftsize)
        plt.pause(0.001)

    def Event_Paint(self, ax, center, color='g', alpha=0.2, width=10):
        ax.axvspan(center - width, center + width, facecolor=color, alpha=alpha)
        plt.pause(0.001)

    def __main__(self):
        self.InputInfoFrame = UI.UI_tkinter.MakeFrameLabel(self.window, fw, fh, 0, 0, "Plot Configuration")
        self.OutputFrame = UI.UI_tkinter.MakeFrameLabel(self.window, fw, fh, 1, 0, "Figure Preview")

        ### Input UI

        colspan = 0

        LabelInfos = ["Title", "x-Axis Title", "y-Axis Title", "xLim", "yLim", "MajorTick X Y", "Legend", "Color Style Alpha"]
        for n, t in enumerate(LabelInfos):
            UI.UI_tkinter.UI_Labels(self.InputInfoFrame, t=t, row=n)

        colspan += 3

        EntryInfos = {'Title': 'Title', 'xAxisTitle': 'x-Axis Title', 'yAxisTitle': 'y-Axis Title',
                      'xLim': (0, 1), 'yLim': (0, 1), 'MajorTickXY': (1, 1), 'Legend': 'a, b, c',
                      'ColorStyleAlpha': ('bwr', 'None', 0.6)}
        self.EntryAddress = {}

        for k, key in enumerate(EntryInfos):
            if type(EntryInfos[key]) is tuple:
                n = EntryInfos[key].__len__()
                for t1, tt in enumerate(EntryInfos[key]):
                    self.EntryAddress[key + f'_{t1}'] = UI.UI_tkinter.UI_InputEntry(self.InputInfoFrame, tt, row=k, col=1+t1, width=6)

            elif type(EntryInfos[key]) is int:
                self.EntryAddress[key] = UI.UI_tkinter.UI_InputEntry(self.InputInfoFrame, EntryInfos[key], row=k-n, col=1+n, width=9)
                n = 1 - n
            else:
                self.EntryAddress[key] = UI.UI_tkinter.UI_InputEntry(self.InputInfoFrame, EntryInfos[key], row=k, col=1, colspan=colspan, width=24)

        CBoxInfos = {'xScale': ["Linear", "SymLog"], 'yScale': ["Linear", "SymLog"], 'Grid': ["Grid ON", "Grid Off"]}
        for k, key in enumerate(CBoxInfos):
            self.EntryAddress[key] = UI.UI_tkinter.UI_CBox(self.InputInfoFrame, CBoxInfos[key], row=k+3, col=3, width=6, padx=1, pady=1, ftsize=8)

        colspan += 1

        ButtonInfos = ['ApplyInfo']
        self.ButtonAddress = {}
        for n, t in enumerate(ButtonInfos):
            self.ButtonAddress[t] = UI.UI_tkinter.UI_Button(self.InputInfoFrame, t, row=LabelInfos.__len__(), col=0, colspan=colspan, width=30, height=1)

        ### Output UI

        self.OutputPlotFrame = UI.UI_tkinter.MakeFrame(self.OutputFrame, 100*fs[0], 95*fs[1], 0, 0, 3)

        ButtonInfos = ["Clipboard to Figure", "New Figure", "Paint"]
        for n, t in enumerate(ButtonInfos):
            if t == 'Paint':
                self.ButtonAddress[t] = UI.UI_tkinter.UI_Button(self.OutputFrame, t, 2, n, rowspan=1, width=8, height=1, padx=1, pady=1)
                continue
            self.ButtonAddress[t] = UI.UI_tkinter.UI_Button(self.OutputFrame, t, 1, n, 2)

        EntryInfos = {'PaintCenter': 0}
        for k, key in enumerate(EntryInfos):
                self.EntryAddress[key] = UI.UI_tkinter.UI_InputEntry(self.OutputFrame, EntryInfos[key], row=1, col=2, width=8, padx=1, pady=1)

        ### Designate Button Callback Function
        self.ButtonAddress['ApplyInfo'].configure(command=lambda: self.Event_ApplyInfo(self.OutputPlotFrame, self.EntryAddress))
        self.ButtonAddress['New Figure'].configure(command=lambda: self.Event_NewFigure(self.InputInfo.copy()))
        self.ButtonAddress['Clipboard to Figure'].configure(command=lambda: self.Event_DrawCurve(self.drawax, self.color, self.InputInfo['Legend'], float(self.InputInfo['ColorStyleAlpha_2']), self.InputInfo['ColorStyleAlpha_1']))
        self.ButtonAddress['Paint'].configure(command=lambda: self.Event_Paint(self.drawax, float(self.EntryAddress['PaintCenter'].get()), 'g', 0.2, 1))


if __name__ == '__main__':
    window = Tk()
    Clipboard2Fig(window)
    window.mainloop()