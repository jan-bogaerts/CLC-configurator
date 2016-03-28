__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty, StringProperty

import iotUserClient.attiotuserclient as iot

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
        super(OutputItem, self).__init__(**kwargs)

    def on_valueChanged(self, value):
        """callback for the iot pub-sub."""
        if 'value' in value:
            self.cloudValue = value['value']
        elif 'Value' in value:
            self.cloudValue = value['Value']
        self.value = self.cloudValue

    def on_value(self, instance, value):
        '''send command to platform'''
        if self.assetId:                            # when just activated, but not yet commited, there is no id yet to send to.
            iot.send(self.assetId, value)

    def on_assetLabel(self, instance, value):
        self.assetLabelChanged = True
