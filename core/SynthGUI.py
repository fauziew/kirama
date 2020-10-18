from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import pickle
import core.Synth as Synth

Parameters ={'Peak Amplitude':[0,100,100],
            'Sustain Amplitude':[0,100,50],
            'Attack Time':[0,2,0.1],
            'Decay Time':[0,2,0.1],
            'Sustain Time':[0,2,1],
            'Release Time':[0,2,0.1],
            'Frequency Ratio':[100,10000,100],
            'Phase':[0,180,0]}

# QSlider widget that can accept float
class FloatSlider(QtWidgets.QSlider):
    def __init__(self):
        super().__init__()
        self.selfChanged = True

    def setSettings(self, Settings):
        self.label = Settings[0]
        self.minval = Settings[1]
        self.maxval = Settings[2]
        self.setval = Settings[3]

        self.setMinimum(0)
        self.setMaximum(100)

        self.selfChanged = False
        self.setValue(self.Real2Index(self.setval))
        self.selfChanged = True

        self.valueChanged.connect(self.Slided)

    def Real2Index(self,value):
        return int(((value-self.minval)/(self.maxval-self.minval))*100)

    def Index2Real(self,value):
        return round ((self.minval + (self.maxval-self.minval)*(value/100)),1)

    def Slided(self):
        if self.selfChanged == True:
            self.setval = self.Index2Real(self.value())

class Slider(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Create Widgets
        self.label = QtWidgets.QLabel()
        self.Slider = FloatSlider()
        self.Textbox = QtWidgets.QLineEdit()

        # Create Events
        self.SliderSelfChanged = True
        self.Slider.valueChanged.connect(self.Slided)
        self.Textbox.editingFinished.connect(self.TextChanged)

        # Layout
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.Slider)
        self.layout.addWidget(self.Textbox)

    def setSettings(self,Settings):
        # settings [ 'label', [min value, max value, set value]]
        self.label.setText(Settings[0])
        self.Slider.setSettings(Settings)
        self.Textbox.setText(str(self.Slider.setval))

    def Slided(self):
        if self.SliderSelfChanged:
            self.Textbox.setText(str(self.Slider.setval))

    def TextChanged(self):
        try:
            value = float(self.Textbox.text())
            self.SliderSelfChanged = False
            self.Slider.setValue(self.Slider.Real2Index(value))
            self.SliderSelfChanged = True
        except ValueError:
            self.Textbox.setText(str(self.Slider.setval))

class Equalizer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Create Widgets
        self.Controller = [Slider()]
        self.Overtone_no = 1

        # Layout
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)

        self.layout.addWidget(self.Controller[0])

    def setSettings(self,Parameter):
        i = 0
        while i < self.Overtone_no:
            Settings = [str(i)] + Parameters[Parameter][0:2] + [Parameters[Parameter][i+2]]
            self.Controller[i].setSettings(Settings)
            i += 1

    def addOvertones(self,synth):
        # Read new parameter values from synth
        Parameters['Peak Amplitude'].append(synth.Peak_A[-1])
        Parameters['Sustain Amplitude'].append(synth.Sustain_A[-1])
        Parameters['Attack Time'].append(synth.Attack[-1])
        Parameters['Decay Time'].append(synth.Decay[-1])
        Parameters['Sustain Time'].append(synth.Sustain[-1])
        Parameters['Release Time'].append(synth.Release[-1])
        Parameters['Frequency Ratio'].append(synth.FreqRatio[-1])
        Parameters['Phase'].append(synth.Phase[-1])

        # Create new sliders
        self.Controller.append(Slider())
        self.layout.addWidget(self.Controller[self.Overtone_no])
        self.Overtone_no += 1

    def delOvertones(self):
        for x in Parameters:
            del Parameters[x][-1]
        self.layout.removeWidget(self.Controller[-1])
        self.Controller[-1].setParent(None)
        del self.Controller[-1]
        self.Overtone_no -= 1

class ButtonBox(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Create Widgets
        self.Test = QtWidgets.QPushButton()
        self.Update = QtWidgets.QPushButton()
        self.AddOv = QtWidgets.QPushButton()
        self.DelOv = QtWidgets.QPushButton()
        self.Save = QtWidgets.QPushButton()
        self.Load = QtWidgets.QPushButton()
        self.Close = QtWidgets.QPushButton()

        # Set Properties
        self.Test.setText('Test')
        self.Update.setText('Update')
        self.AddOv.setText('Add Overtone')
        self.DelOv.setText('Delete Overtone')
        self.Save.setText('Save')
        self.Load.setText('Load')
        self.Close.setText('Close')

        # Layout
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.Test)
        self.layout.addWidget(self.Update)
        self.layout.addWidget(self.AddOv)
        self.layout.addWidget(self.DelOv)
        self.layout.addWidget(self.Save)
        self.layout.addWidget(self.Load)
        self.layout.addWidget(self.Close)

class SoundEditorWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Synth Editor')

        # Create instrument
        self.synth = Synth.Synth()

        # Create Widgets
        self.ButtonBox = ButtonBox()
        self.graph = pg.PlotWidget()
        self.curve = self.graph.plot()
        self.Fundamental = Slider()
        self.Volume = Slider()
        self.EQ = Equalizer()
        self.Properties = QtWidgets.QListWidget()

        # Set Properties
        self.curve.setData(self.synth.Time,self.synth.audiograph)
        self.Fundamental.setSettings(['Fundamental Frequency',27.5,4186.00,440])
        self.Volume.setSettings(['Volume',0.0,100,25])
        self.Properties.Items = Parameters.keys()
        self.Properties.addItems(self.Properties.Items)
        self.Properties.setCurrentRow(0)
        self.mode = (self.Properties.currentItem().text())
        self.EQ.setSettings(self.mode)

        # Create events
        self.ButtonBox.Test.clicked.connect(self.synth.Play)
        self.ButtonBox.Update.clicked.connect(self.updateSynth)
        self.ButtonBox.AddOv.clicked.connect(self.addOvertones)
        self.ButtonBox.DelOv.clicked.connect(self.delOvertones)
        self.ButtonBox.Save.clicked.connect(self.saveFiles)
        self.ButtonBox.Load.clicked.connect(self.loadFiles)
        self.ButtonBox.Close.clicked.connect(self.closeSynth)
        self.Fundamental.Slider.valueChanged.connect(self.changeFundamental)
        self.Volume.Slider.valueChanged.connect(self.changeVolume)
        self.Properties.currentItemChanged.connect(self.changeProperties)

        # Layout
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.graph,0,0,1,5)
        self.layout.addWidget(self.Properties,1,0,1,1)
        self.layout.addWidget(self.EQ,1,1,1,1)
        self.layout.addWidget(self.Fundamental,1,2,1,1)
        self.layout.addWidget(self.Volume,1,3,1,1)
        self.layout.addWidget(self.ButtonBox,1,4,1,1)
        
    def addOvertones(self):
        self.synth.addOvertones()
        self.EQ.addOvertones(self.synth)
        self.EQ.setSettings(self.mode)

    def delOvertones(self):
        if self.synth.Overtone_no > 1:
            self.synth.delOvertones()
            self.EQ.delOvertones()

    def updateSynth(self):
        i = 0
        j = 2
        while i < self.synth.Overtone_no:
            Parameters[self.mode][j] = float(self.EQ.Controller[i].Textbox.text())

            self.synth.Peak_A[i]=Parameters['Peak Amplitude'][j]
            self.synth.Sustain_A[i]=Parameters['Sustain Amplitude'][j]
            self.synth.Attack[i]=Parameters['Attack Time'][j]
            self.synth.Decay[i]=Parameters['Decay Time'][j]
            self.synth.Sustain[i]=Parameters['Sustain Time'][j]
            self.synth.Release[i]=Parameters['Release Time'][j]
            self.synth.FreqRatio[i]=Parameters['Frequency Ratio'][j]
            self.synth.Phase[i]=Parameters['Phase'][j]

            i += 1
            j += 1

        self.synth.Reset()
        self.synth.GetWaveform()
        self.curve.setData(self.synth.Time,self.synth.audiograph)

    def changeFundamental(self):
        try:
            value = float(self.Fundamental.Textbox.text())
            self.synth.setFundamental(value)
        except ValueError:
            pass

    def changeVolume(self):
        try:
            value = float(self.Volume.Textbox.text())
            self.synth.setVolume(value)
        except ValueError:
            pass

    def changeProperties(self):
        # save old parameters
        i = 0
        j = 2
        while i<self.EQ.Overtone_no:
            Parameters[self.mode][j] = float(self.EQ.Controller[i].Textbox.text())
            i += 1
            j += 1

        # set new parameters
        self.mode = self.Properties.currentItem().text()
        self.EQ.setSettings(self.mode)

    def loadFiles(self):
        FileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', 'data/synthesizer/', '*.syn')
        if FileName:
            # Read file
            f = open(FileName,'rb')
            LoadedData = pickle.load(f)
            f.close()
    
            # Unpack data
            for x in Parameters:
                Parameters[x] = LoadedData[3][x]

            # Set EQ and Synth
            self.setSettings(LoadedData[0], LoadedData[1], LoadedData[2])

    def setSettings(self, Overtone_no, Fundamental, Volume):
            # reset EQ
            i = self.synth.Overtone_no
            while i > 0:
                self.EQ.layout.removeWidget(self.EQ.Controller[-1])
                self.EQ.Controller[-1].setParent(None)
                del self.EQ.Controller[-1]
                i -= 1

            # Copy Overtone_no of EQ from synth
            self.EQ.Overtone_no = Overtone_no
            
            # Set Synth
            self.synth.setSettings(Overtone_no, Fundamental, Volume, Parameters)

            # Update EQ 
            i = 0
            while i < self.synth.Overtone_no:
                self.EQ.Controller.append(Slider())
                self.EQ.layout.addWidget(self.EQ.Controller[-1])
                i += 1

            # Update synth slider, graph, equalizer settings
            self.Fundamental.setSettings(['Fundamental Frequency',27.5,4186.00,self.synth.Fundamental])
            self.Volume.setSettings(['Volume',0.0,100,self.synth.Volume])
            self.mode = self.Properties.currentItem().text()
            self.EQ.setSettings(self.mode)
            self.curve.setData(self.synth.Time,self.synth.audiograph)

    def saveFiles(self):
        FileName, _  = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', 'data/synthesizer/', '*.syn')
        if FileName:
            f = open(FileName,'wb')
            DataToSave = [self.synth.Overtone_no, self.synth.Fundamental, self.synth.Volume, Parameters]
            pickle.dump(DataToSave,f)
            f.close()

    def closeSynth(self):
        self.Parameters = Parameters
        self.close()
        # exit()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    Win = SoundEditorWindow()
    Win.show()

    while True:
        QtWidgets.QApplication.processEvents()

    app.exec_()
