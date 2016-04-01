__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

import sys, os
if sys.executable.endswith("pythonw.exe"):
  sys.stdout = open(os.devnull, "w");
  sys.stderr = open(os.path.join(os.getenv("TEMP"), "stderr-"+os.path.basename(sys.argv[0])), "w")

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
from kivy.core.window import Window

from errors import *
from inputItem import InputItem, inputWidgets
import outputItem
import iotUserClient.attiotuserclient as IOT
from iotUserClient.popups.credentials import Credentials, CredentialsDialog
import data
import controllino

usedOutputsId = '94'
usedRelaysId = '97'
pinTypesId = '98'
ioMapId = '99'

class OutputsScreen(Screen):
    relays = ObjectProperty()
    outputs = ObjectProperty()

    def __init__(self, **kwargs):
        super(OutputsScreen, self).__init__(**kwargs)
        outputItem.relays = []                                     # always reset before we fill the lists.
        outputItem.outputs = []

    def clearOutputs(self):
        if self.relays:
            self.relays.clear_widgets()
            outputItem.relays = []
        if self.outputs:
            self.outputs.clear_widgets()
            outputItem.outputs = []

    def on_relays(self, instance, value):
        if self.outputs and self.relays and _Main and _Main.currentDevice:
            _Main.dataToWidgets()

    def on_outputs(self, instance, value):
        if self.outputs and self.relays and _Main and _Main.currentDevice:
            _Main.dataToWidgets()

    def loadOutputs(self):
        '''load the widgets for the relay grid'''
        for i in range(1, 17):
            item = outputItem.OutputItem(i, controllino.relaysPins[i - 1])
            item.bind(isActive=_Main.dataChanged)
            item.bind(assetLabel=_Main.dataChanged)
            self.relays.add_widget(item)
            outputItem.relays.append(item)

        for i in range(1, 17):
            item = outputItem.OutputItem(i, controllino.outputPins[i - 1])
            item.bind(isActive=_Main.dataChanged)
            item.bind(assetLabel=_Main.dataChanged)
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
        self.layout = layout

    def clearInputs(self):
        global inputWidgets
        if self.layout:
            self.layout.clear_widgets()
        inputWidgets = []

    def loadInputs(self):
        for i in range(1, 22):
            item = InputItem(i, controllino.inputPins[i - 1])
            item.bind(mode=_Main.dataChanged)
            item.bind(label=_Main.dataChanged)
            item.bind(outputLabel=_Main.dataChanged)
            self.layout.add_widget(item)
            inputWidgets.append(item)

class MainWindow(Widget):

    editbar = ObjectProperty()
    outputsPage = ObjectProperty()
    inputsPage = ObjectProperty()

    def __init__(self, **kwargs):
        #self.data = None
        global _Main
        _Main = self
        self.isChanged = False
        self.isLoading = False                  # so we don't show the save/undo buttons after loading the config.
        self.currentDevice = None
        self.editButtons = []                    # the X and V buttons
        Window.softinput_mode = 'below_target'  # so the screen resizes when the keybaord is shown, otherwise it hides editing.
        super(MainWindow, self).__init__(**kwargs)
        if len(data.devices) > 0:
            self.loadDevice(data.devices[0])

    def on_outputsPage(self, instance, value):
        if self.inputsPage and self.outputsPage and self.currentDevice:
            self.dataToWidgets()

    def on_inputsPage(self, instance, value):
        if self.inputsPage and self.outputsPage and self.currentDevice:
            self.dataToWidgets()

    def showCredentials(self):
        dlg = CredentialsDialog(data.credentials, self.credentialsChanged)
        dlg.open()

    def credentialsChanged(self, value):
        """called when the user closed the credentials dialog"""
        IOT.disconnect(False)
        data.credentials = value

        popup = Popup(title='connecting', content=Label(text='searching for devices,\nand syncing...'),
                      size_hint=(None, None), size=(400, 250), auto_dismiss=False)
        popup.bind(on_open=self._syncWithCloud)
        popup.open()

    def _syncWithCloud(self, instance):
        try:
            Application.connect()
            self.scanDevices()
            data.saveSettings()
            if len(data.devices) > 0:
                self.loadDevice(data.devices[0])
        finally:
            instance.dismiss()

    def scanDevices(self):
        """scan for controllino devices and add them to the list."""
        data.devices = []
        grounds = IOT.getGrounds(False)
        for ground in grounds:
            devices = IOT.getDevices(ground['id'])
            for device in devices:
                try:
                    ver = IOT.getAssetByName(device['id'], '90')    # 90 = application
                    if ver and 'state' in ver:
                        ver = ver['state']['value']
                except:
                    ver = None
                if ver and str(ver) == 'Controllino mega - light control':    # found a controllino
                    data.devices.append(device['id'])

    def loadDevice(self, device):
        """loads the configuration data of the controllino and displays it."""
        self.isLoading = True
        try:
            self.currentDevice = device
            data.ioMap = self.getAssetValue(device, ioMapId)
            data.pinTypes = self.getAssetValue(device, pinTypesId)
            data.usedRelays = self.getAssetValue(device, usedRelaysId)
            if not data.usedRelays:
                data.usedRelays = 0
            data.usedOutputs = self.getAssetValue(device, usedOutputsId)
            if not data.usedOutputs:
                data.usedOutputs = 0
            self.dataToWidgets()
        finally:
            self.isLoading = False

    def getAssetValue(self, device, asset):
        result = IOT.getAssetByName(device, asset)
        if result:
            result = result['state']
            if result:
                result = result['value']
        return result

    def dataToWidgets(self):
        if self.inputsPage and self.outputsPage:
            self.inputsPage.clearInputs()
            self.outputsPage.clearOutputs()
            self.inputsPage.loadInputs()
            self.outputsPage.loadOutputs()
            self.outputsToWidgets(outputItem.outputs, data.usedOutputs)
            self.outputsToWidgets(outputItem.relays, data.usedRelays)
            self.inputsToWidgets()

    def inputsToWidgets(self):
        for index in range(0, len(inputWidgets)):
            input = inputWidgets[index]
            sensor = IOT.getAssetByName(self.currentDevice, input.assetName)
            input.assetId = sensor['id']
            input.label = sensor['title']
            input.labelChanged = False
            if sensor['state']:
                input.on_valueChanged(sensor['state'])
            IOT.subscribe(input.assetId, input.on_valueChanged)
            input.mode = "Disabled"
            if data.pinTypes:
                if data.pinTypes[index] == 'T':
                    input.mode = "Toggle"
                elif data.pinTypes[index] == 'B':
                    input.mode = "Button"
                elif data.pinTypes[index] == 'A':
                    input.mode = "Analog"
            if data.ioMap and data.ioMap[index] != 0xFF:
                try:
                    outIndex = controllino.relaysPins.index(data.ioMap[index])
                    input.OutputSelected(None, outputItem.relays[outIndex])
                except:
                    outIndex = controllino.outputPins.index(data.ioMap[index])
                    input.OutputSelected(None, outputItem.outputs[outIndex])
            else:
                input.OutputSelected(self, None)


    def outputsToWidgets(self, widgets, outputPins):
        bitIndex = 1
        for index in range(0, len(widgets)):
            output = widgets[index]
            if outputPins & bitIndex > 0:
                output.isActive = True
                try:
                    asset = IOT.getAssetByName(self.currentDevice, str(output.assetName))
                except:
                    asset = None
                if asset:
                    if asset['state']:                              # do before storing the id, so that we don't send a command upon storing the current state.
                        output.value = asset['state']['value']
                        output.cloudValue = output.value
                    output.assetId = asset['id']
                    output.assetLabel = asset['title']
                output.assetLabelChanged = False
                IOT.subscribe(output.assetId, output.on_valueChanged)
            else:
                output.assetLabel = ''
                if output.assetId:
                    IOT.unsubscribe(output.assetId)
                    output.assetId = None
            bitIndex = bitIndex << 1

    def sendSettingsToDevice(self, instance):
        popup = Popup(title='updating', content=Label(text='sending settings to device,\n please wait...'),
                      size_hint=(None, None), size=(400, 250), auto_dismiss=False)

        popup.bind(on_open=self.widgetsToData)
        popup.open()

    def widgetsToData(self, instance):
        """store the data in the widgets in the cloud (and in the data module"""
        try:
            data.usedOutputs = self.widgetsToOutputs(outputItem.outputs, usedOutputsId, data.usedOutputs)
            data.usedRelays = self.widgetsToOutputs(outputItem.relays, usedRelaysId, data.usedRelays)
            newPinTypes = list(data.pinTypes)
            ioMapChanged = False
            for index in range(0, len(inputWidgets)):
                try:
                    input = inputWidgets[index]
                    newPinTypes[index] = input.mode[0]
                    ioMapChanged |= self.setIoMap(input, index)
                    if input.labelChanged:
                        IOT.updateAsset(_Main.currentDevice, input.assetName, {'title': input.label, 'is': 'sensor', 'id': input.assetId})
                        input.labelChanged = False
                    if input.mode[0] == 'D' and data.pinTypes[index] != 'D':            # the input got disabled, so remove the asset (not done by the device, it only creates asssets)
                        IOT.deleteAssetbyName(self.currentDevice, input.assetName)
                except Exception as e:
                    showError(e)
            newPinTypes = "".join(newPinTypes)
            if newPinTypes != data.pinTypes:
                IOT.sendByName(self.currentDevice, pinTypesId, newPinTypes)
                data.pinTypes = newPinTypes
            if ioMapChanged:
                IOT.sendByName(self.currentDevice, ioMapId, data.ioMap)
        except Exception as e:
            showError(e)
        finally:
            instance.dismiss()
            self.removeEditButtons()
            self.isChanged = False

    def setIoMap(self, input, index):
        if input.output:
            result = not data.ioMap[index] == input.output.assetName
            data.ioMap[index] = input.output.assetName
        else:
            result = not data.ioMap[index] == 0xFF
            data.ioMap[index] = 0xFF
        return result

    def widgetsToOutputs(self, list, configAssetId, curVal):
        result = 0
        bitIndex = 1
        for item in list:
            try:
                if item.isActive:
                    result += bitIndex
                    if item.assetLabelChanged:
                        IOT.updateAsset(_Main.currentDevice, item.assetName, {'title': item.assetLabel, 'is': 'actuator', 'id': item.assetId})
                        item.assetLabelChanged = False
                elif curVal & bitIndex > 0:
                    IOT.deleteAssetbyName(self.currentDevice, item.assetName)
            except Exception as e:
                showError(e)
            bitIndex = bitIndex << 1
        if result != curVal:                            #only send if there was a change.
            IOT.sendByName(self.currentDevice, configAssetId, result)
        return result

    def dataChanged(self, instance, value):
        """"called when some part of the data is changed. So we can show the edit buttons"""
        if not self.isChanged and not self.isLoading:
            btn = ActionButton(text = 'V', on_press=self.sendSettingsToDevice)
            self.editbar.add_widget(btn, 1)
            self.editButtons.append(btn)
            btn = ActionButton(text = 'X', on_press=self.undoEdit)
            self.editbar.add_widget(btn, 1)
            self.editButtons.append(btn)
            self.isChanged = True

    def undoEdit(self, instance):

        popup = Popup(title='Test popup', content=Label(text='retrieving settings from device,\nplease wait...'), size_hint=(None, None), size=(400, 250), auto_dismiss=False)
        popup.bind(on_open=self.on_undo_opened)
        popup.open()

    def on_undo_opened(self, instance):
        self.isLoading = True
        try:
            self.dataToWidgets()
            self.removeEditButtons()
        finally:
            instance.dismiss()
            self.isLoading = False
            self.isChanged = False

    def removeEditButtons(self):
        if len(self.editButtons) > 0:
            map(self.editbar.remove_widget, self.editButtons)
            self.editButtons = []

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
_Main = None                       # so that the inputs can access the main window and bind to it upon creation.

if __name__ == '__main__':
    try:
        Application.run()
    except Exception as e:
        showError(e, "fatal error")