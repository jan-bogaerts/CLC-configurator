__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.properties import StringProperty, ObjectProperty

from errors import *
import outputItem as out

inputWidgets = []

class InputItem(Widget):
    """the data for configuring a single input pin"""
    mode = StringProperty("Disabled")
    label = StringProperty("")
    outputLabel = StringProperty("None")
    value = StringProperty('normal')            # the current value of the sensor, pressed or not, or the value

    def __init__(self,number, name, **kwargs):
        self.number = number
        self.assetName = name
        self.assetId = None
        self.output = None
        self.labelChanged = False
        super(InputItem, self).__init__(**kwargs)

    def showOutputs(self, relativeTo):
        """show a list of possible outputs"""
        if self.mode != 'Disabled':
            try:
                dropdown = DropDown(auto_width=True)

                btn = Button(text="None", markup=True,  size_hint_y=None, height='44dp')
                btn.dataItem = None
                btn.bind(on_press=lambda btn: dropdown.select(btn.dataItem))
                dropdown.add_widget(btn)

                for item in out.outputs:
                    if item.isActive == True:
                        btn = Button(text=str(item.number) + " (" + item.assetLabel + ")", markup=True,  size_hint_y=None, height='44dp')
                        btn.dataItem = item
                        btn.bind(on_press=lambda btn: dropdown.select(btn.dataItem))
                        dropdown.add_widget(btn)
                for item in out.relays:
                    if item.isActive == True:
                        btn = Button(text=str(item.number) + " (" + item.assetLabel + ")", markup=True,  size_hint_y=None, height='44dp')
                        btn.dataItem = item
                        btn.bind(on_press=lambda btn: dropdown.select(btn.dataItem))
                        dropdown.add_widget(btn)
                dropdown.bind(on_select=self.OutputSelected)
                dropdown.open(relativeTo)
            except Exception as e:
                showError(e)

    def OutputSelected(self,instance, value):
        self.output = value
        if value:
            self.outputLabel = str(value.number) + " (" + str(value.assetLabel) + ")"
        else:
            self.outputLabel = "None"

    def showModes(self, relativeTo):
        """show the list of modes"""
        try:
            dropdown = DropDown(auto_width=True)

            btn = Button(text='Disabled', markup=True,  size_hint_y=None, height='44dp')
            btn.bind(on_press=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)

            btn = Button(text='Toggle', markup=True,  size_hint_y=None, height='44dp')
            btn.bind(on_press=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)

            btn = Button(text='Button', markup=True,  size_hint_y=None, height='44dp')
            btn.bind(on_press=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)

            btn = Button(text='Analog', markup=True,  size_hint_y=None, height='44dp')
            btn.bind(on_press=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)

            dropdown.bind(on_select=self.ModeSelected)
            dropdown.open(relativeTo)
        except Exception as e:
            showError(e)

    def ModeSelected(self, instance, value):
        self.mode = value

    def on_valueChanged(self, value):
        if 'value' in value:
            value = value['value']
        elif 'Value' in value:
            value = value['Value']

        if self.mode == "Analog":
            self.value = str(value)
        else:
            self.value = 'down' if value == True else 'normal'

    def on_label(self, instance, value):
        self.labelChanged = True