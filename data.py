__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

from iotUserClient.popups.credentials import Credentials
from ConfigParser import *

devices = []
credentials = None
config = ConfigParser()
ioMap = None
pinTypes = None
usedRelays = None
usedOutputs = None
appConfigFileName = 'app.config'


def loadSettings():
    global credentials, devices
    credentials = Credentials()
    if config.read(appConfigFileName):
        if config.has_option('general', 'username'):
            credentials.userName = config.get('general', 'username')
        if config.has_option('general', 'password'):
            credentials.password = config.get('general', 'password')
        if config.has_option('general', 'server'):
            credentials.server = config.get('general', 'server')
        if config.has_option('general', 'broker'):
            credentials.broker = config.get('general', 'broker')
        if configs.has_option('general', 'devices'):
            devices = configs.get('general', 'devices')

def saveSettings():
    config.set('general', 'username', credentials.userName)
    config.set('general', 'password', credentials.password)
    config.set('general', 'server', credentials.server)
    config.set('general', 'broker', credentials.broker)
    config.set('general', 'devices', devices)
    with open(appConfigFileName, 'w') as f:
        config.write(f)