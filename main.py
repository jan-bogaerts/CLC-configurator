__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

import kivy
kivy.require('1.9.1')   # replace with your current kivy version !

import logging
logging.getLogger().setLevel(logging.INFO)

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty
from kivy.uix.actionbar import ActionButton

from errors import *
from inputItem import InputItem, inputWidgets
import outputItem
import iotUserClient.attiotuserclient as IOT
from iotUserClient.popups.credentials import Credentials, CredentialsDialog
import data
import controllino

usedOutputsId = '94'
usedRelaysId = '97'

class OutputsScreen(Screen):
    relays = ObjectProperty()
    outputs = ObjectProperty()

    def __init__(self, **kwargs):
        super(OutputsScreen, self).__init__(**kwargs)
        outputItem.relays = []                                     # always reset before we fill the lists.
        outputItem.outputs = []


    def on_relays(self, instance, value):
        '''load the widgets for the relay grid'''
        for i in range(1, 17):
            item = outputItem.OutputItem(i, controllino.relaysPins[i - 1])
            self.relays.add_widget(item)
            outputItem.relays.append(item)
    def on_outputs(self, instance, value):
        '''load the widgets for the output grid'''
        for i in range(1, 17):
            item = outputItem.OutputItem(i, controllino.outputPins[i - 1])
            self.outputs.add_widget(item)
            outputItem.outputs.append(item)


class InputsScreen(Screen):
    def __init__(self, **kwargs):
        super(InputsScreen, self).__init__(**kwargs)
        scroll = ScrollView()
        scroll.size_hint = (1, 1)
        self.add_widget(scroll)
        layout = GridLayout()
        layout.cols = 3
        layout.padding = '8dp'
        layout.spacing = '8dp'
        layout.size_hint_y = None
        layout.bind(minimum_height=layout.setter('height'))
        scroll.add_widget(layout)
        for i in range(1, 21):
            item = InputItem(i, controllino.inputPins[i - 1])
            layout.add_widget(item)
            inputWidgets.append(item)

class MainWindow(Widget):

    editbar = ObjectProperty()

    def __init__(self, **kwargs):
        #self.data = None
        self.isChanged = False
        super(MainWindow, self).__init__(**kwargs)
        if len(data.devices) > 0:
            self.loadDevice(data.devices[0])

    def showCredentials(self):
        dlg = CredentialsDialog(data.credentials, self.credentialsChanged)
        dlg.open()

    def credentialsChanged(self, value):
        """called when the user closed the credentials dialog"""
        IOT.disconnect(False)
        data.credentials = value
        Application.connect()
        self.scanDevices()
        data.saveSettings()
        if len(data.devices) > 0:
            self.loadDevice(data.devices[0])

    def scanDevices(self):
        """scan for controllino devices and add them to the list."""
        data.devices = []
        grounds = IOT.getGrounds(False)
        for ground in grounds:
            devices = IOT.getDevices(ground['id'])
            for device in devices:
                ver = IOT.getAssetByName(device['id'], '90')    # 90 = application
                if ver and ver == 'Controllino mega - light control':    # found a controllino
                    data.devices.append(device['id'])

    def loadDevice(self, device):
        """loads the configuration data of the controllino and displays it."""
        data.ioMap = IOT.getAssetByName(device, '99')
        data.pinTypes = IOT.getAssetByName(device, '98')
        data.usedRelays = IOT.getAssetByName(device, usedRelaysId)
        data.usedOutputs = IOT.getAssetByName(device, usedOutputsId)
        self.dataToWidgets(device)

    def dataToWidgets(self, device):
        self.outputsToWidgets(device, outputItem.outputs, data.usedOutputs)
        self.outputsToWidgets(device, outputItem.relays, data.usedRelays)
        for index in range(0, len(inputWidgets)):
            input = input[index]
            sensor = IOT.getAssetByName(device, input.assetName)
            input.assetId = sensor['id']
            input.label = sensor['label']
            input.labelChanged = False
            IOT.subscribe(input.assetId, input.on_valueChanged)
            if data.pinTypes[index] == 'T':
                input.mode = "Toggle"
            elif data.pinTypes[index] == 'B':
                input.mode = "Button"
            elif data.pinTypes[index] == 'A':
                input.mode = "Analog"
            else:
                input.mode = "Disabled"

            if data.ioMap[index] != 0xFF:
                outIndex = controllino.relaysPins.index(data.ioMap[index])
                if outIndex == -1:
                    outIndex = controllino.outputPins.index(data.ioMap[index])
                    input.OutputSelected(None, outputItem.outputs[outIndex])
                else:
                    input.OutputSelected(None, outputItem.relays[outIndex])
            else:
                input.OutputSelected(None)


    def outputsToWidgets(self, device, widgets, outputPins):
        bitIndex = 1
        for index in range(0, len(widgets)):
            output = widgets[index]
            if outputPins & bitIndex > 0:
                output.isActive = True
                asset = IOT.getAssetByName(device, str(output.assetName))
                output.assetId = asset['id']
                output.assetLabel = asset['label']
                output.assetLabelChanged = False
                IOT.subscribe(output.assetId, output.on_valueChanged)
            else:
                output.assetLabel = ''
                if output.assetId:
                    IOT.unsubscribe(output.assetId)
                    output.assetId = None
            bitIndex = bitIndex < 1

    def widgetsToData(self):
        """store the data in the widgets in the cloud (and in the data module"""
        data.usedOutputs = self.widgetsToOutputs(outputItem.outputs, usedOutputsId)
        data.usedRelays = self.widgetsToOutputs(outputItem.relays, usedRelaysId)
        for index in range(0, len(inputWidgets)):
            input = input[index]
            data.pinTypes[index] = input.mode[0]
            if input.output:
                data.ioMap[index] = input.output.assetName
            else:
                data.ioMap[index] = 0xFF
            if input.labelChanged:
                IOT.updateAsset({'id': input.assetId, 'label': input.label})

    def widgetsToOutputs(self, list, configAssetId):
        result = 0
        bitIndex = 1
        for item in list:
            if item.isActive:
                result += bitIndex
            if item.assetLabelChanged:
                IOT.updateAsset({'id': item.assetId, 'label': item.assetLabel})
            bitIndex = bitIndex < 1
        IOT.send(configAssetId, result)
        return result

    def dataChanged(self):
        """"called when some part of the data is changed. So we can show the edit buttons"""
        if not self.isChanged:
            btn = ActionButton(text = 'V', on_press=self.widgetsToData)
            self.editbar.add_widget(btn)
            btn = ActionButton(text = 'X', on_press=self.undoEdit)
            self.editbar.add_widget(btn)

    def undoEdit(self):
        self.dataToWidgets(data.devices[0])

class CIConfigApp(App):
    def build(self):
        data.loadSettings()
        self.connect()
        self._main = MainWindow()
        return self._main

    def on_pause(self):
        self.saveState(True)
        return True

    def on_resume(self):
        try:
            if data.credentials:
                IOT.reconnect(data.credentials.server, data.credentials.broker)
                logging.info("reconnected after resume")
        except Exception as e:
            showError(e)

    def connect(self):
        try:
            if data.credentials and data.credentials.isDefined():
                IOT.connect(data.credentials.userName, data.credentials.password, data.credentials.server, data.credentials.broker)
                logging.info("reconnected after resume")
        except Exception as e:
            showError(e)

    def on_stop(self):
        self.saveState(False)

    def saveState(self, recoverable):
        '''close the connection, save the settings.'''
        try:
            #data.saveSettings() not required, already done after changing the settings.
            IOT.disconnect(recoverable)                        # close network connection, for cleanup
        except:
            logging.exception('failed to save application state')


Application = CIConfigApp()

if __name__ == '__main__':
    Application.run()