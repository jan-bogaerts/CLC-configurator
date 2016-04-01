__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

from kivy.uix.widget import Widget

from kivy.properties import BooleanProperty, StringProperty

import iotUserClient.attiotuserclient as iot
from errors import *

#list of available outputs
outputs = []
#list of available relays
relays = []





class OutputItem(Widget):
    isActive = BooleanProperty(False)
    value = BooleanProperty(False)
    cloudValue = BooleanProperty(False)
    assetLabel = StringProperty('')
    assetId = StringProperty('')

    def __init__(self, number, name, **kwargs):
        self.number = number
        self.assetName = name
        self.assetLabelChanged = False
        self._valueUpdated = False
        super(OutputItem, self).__init__(**kwargs)

    def on_valueChanged(self, value):
        """callback for the iot pub-sub."""
        self._valueUpdated = True
        try:
            if 'value' in value:
                self.cloudValue = value['value']
            elif 'Value' in value:
                self.cloudValue = value['Value']
            self.value = self.cloudValue
        finally:
            self._valueUpdated = False

    def on_value(self, instance, value):
        '''send command to platform'''
        try:
            if self._valueUpdated == False and self.assetId:                            # when just activated, but not yet commited, there is no id yet to send to.
                iot.send(self.assetId, value)
        except Exception as e:
            if e.message:
                showError(e)
            else:
                showErrorMsg("There was a communication problem, please try again")


    def on_assetLabel(self, instance, value):
        self.assetLabelChanged = True
