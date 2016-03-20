import paho.mqtt.client as mqtt
import time
import sys
import array

ClientId = "KardCard"
DeviceId = "jfxvrU9wq41ofxkBbGYqMBC"
brokerid = ClientId + ':' + ClientId
brokerpwd = '42pprmkiubr'

ioMapTopic = "client/" + ClientId + "/in/device/" + DeviceId + "/asset/" + DeviceId + "99/command"
outputsTopic = "client/" + ClientId + "/in/device/" + DeviceId + "/asset/" + DeviceId + "94/command"
relaysTopic = "client/" + ClientId + "/in/device/" + DeviceId + "/asset/" + DeviceId + "97/command"
pinTypesTopic = "client/" + ClientId + "/in/device/" + DeviceId + "/asset/" + DeviceId + "98/command"


pinTypes = 'TNNNNNNNNNNNNNNNNNNNN' #'TTTTTTTTTTTTTTTTTTTNN'
outputs = 0   # 0xFFFFFFFF
relays = 0x8000    #0xFFFF
ioMap = '25 FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF'


_mqttClient = None

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    if rc == 0:
        print( "Connected to mqtt broker with result code "+str(rc))

        ioMapOutput = bytearray.fromhex(ioMap)
        print("sending io map: " + str(ioMapOutput) + "topic = " + ioMapTopic)
        _mqttClient.publish(ioMapTopic, ioMapOutput, 0, False)
        print("sending outputs: " + str(outputs))
        _mqttClient.publish(outputsTopic, outputs, 0, False)
        print("sending relays: " + str(relays))
        _mqttClient.publish(relaysTopic, relays, 0, False)
        print("sending pin types: " + str(pinTypes))
        _mqttClient.publish(pinTypesTopic, pinTypes, 0, False)
        print "Messages sent"
        _mqttClient.disconnect()
        sys.exit()
        
    else:
        print("Failed to connect to mqtt broker: "  + mqtt.connack_string(rc))


def subscribe(mqttServer = "broker.smartliving.io", port = 1883):
    '''start the mqtt client and make certain that it can receive data from the IOT platform
	   mqttServer: (optional): the address of the mqtt server. Only supply this value if you want to a none standard server.
	   port: (optional) the port number to communicate on with the mqtt server.
    '''
    global _mqttClient
    mqttId = "controllino_config"
    _mqttClient = mqtt.Client(mqttId)
    _mqttClient.on_connect = on_connect
    brokerId = brokerid
    _mqttClient.username_pw_set(brokerId, brokerpwd)
    _mqttClient.connect(mqttServer, port, 60)
    _mqttClient.loop_start()


subscribe('broker.smartliving.io', 1883)
