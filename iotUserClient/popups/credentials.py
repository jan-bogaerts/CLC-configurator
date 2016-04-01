__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

import kivy

from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.lang import Builder

Builder.load_string("""
<CredentialsDialog>:
    userNameInput: txtUserName
    pwdInput: txtPwd
    serverInput: txtServer
    brokerInput: txtBroker
    auto_dismiss: False
    title: 'Credentials'
    size_hint: None, None
    width: '300dp'
    height:  grdMain.minimum_height + dp(60) # '440dp'
    pos_hint:{'center_x': .5, 'center_y': .5}
    GridLayout:
        id: grdMain
        cols: 1
        spacing: '8dp'
        size_hint: 1, 1
		padding: '10dp'
        TextInput:
            id: txtUserName
            focus: True
            write_tab: False
            hint_text: 'User name'
            size_hint_y: None
            height:'32dp'
        TextInput:
            id: txtPwd
            write_tab: False
            hint_text: 'Password'
            size_hint_y: None
            height:'32dp'
        TextInput:
            id: txtServer
            write_tab: False
            hint_text: 'server address'
            size_hint_y: None
            height:'32dp'
        TextInput:
            id: txtBroker
            write_tab: False
            hint_text: 'broker address'
            size_hint_y: None
            height:'32dp'
        Button:
            text: 'Cancel'
            on_press: root.dismiss()
            size_hint_y: None
            height:'32dp'
        Button:
            text: 'Ok'
            on_press: root.dismissOk()
            size_hint_y: None
            height:'32dp'
""")

class Credentials():
    def __init__(self):
        self.userName = ''
        self.password = ''
        self.server = ''
        self.broker = ''

    def isDefined(self):
        '''returns true if all fields are filled in'''
        return self.userName and self.password and self.server and self.broker


class CredentialsDialog(Popup):
    "set credentials"
    userNameInput = ObjectProperty()
    pwdInput = ObjectProperty()

    serverInput = ObjectProperty()
    brokerInput = ObjectProperty()

    def __init__(self, credentials, callback, **kwargs):
        self.callback = callback
        super(CredentialsDialog, self).__init__(**kwargs)
        if credentials:
            self.userNameInput.text = credentials.userName
            self.pwdInput.text = credentials.password
            if hasattr(credentials, 'server') and credentials.server:
                self.serverInput.text = credentials.server
            else:
                self.serverInput.text = 'api.smartliving.io'
            if hasattr(credentials, 'broker') and credentials.broker:
                self.brokerInput.text = credentials.broker
            else:
                self.brokerInput.text = 'broker.smartliving.io'
        else:
            self.serverInput.text = 'api.smartliving.io'
            self.brokerInput.text = 'broker.smartliving.io'

    def dismissOk(self):
        self.dismiss()
        if self.callback:
            credentials = Credentials()
            credentials.userName = self.userNameInput.text
            credentials.password = self.pwdInput.text
            credentials.server = self.serverInput.text
            credentials.broker = self.brokerInput.text
            self.callback(credentials)