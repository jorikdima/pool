import paho.mqtt.client as mqtt
import time

# 1. Create a client instance
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# 2. (Optional) Set user/password for secured brokers
client.username_pw_set("dk", "dk")

# 3. Connect to a broker (e.g., HiveMQ, Mosquitto, or local)
client.connect("localhost", 1883, 60)

# 4. Start the network loop in the background
client.loop_start()

info = None

try:
    while True:
        # 5. Publish the message
        # topic: name of the channel, payload: the actual data
        info = client.publish(r"aqualinkd/CHEM/ORP/set", payload=610, qos=1)
        time.sleep(1)
        if info.is_published():
            print("published1")
        info = client.publish(r"aqualinkd/CHEM/pH/set", payload=7.1, qos=1)
        time.sleep(1)
        if info.is_published():
            print("published2")

        time.sleep(1)
except KeyboardInterrupt:
    # 6. Cleanly disconnect
    client.loop_stop()
    client.disconnect()
