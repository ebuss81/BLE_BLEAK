
from bleak import BleakClient
from datetime import datetime
from pathlib import Path
import csv

class MyBleakClient(BleakClient):
    def __init__(self, device, **kwargs, ):
        super().__init__(device, **kwargs)
        self.device = device
        #self.disconnected_callback = disconnected_callback
        #self.is_connected = False

        ## CSV - new
        self.file_path = '/home/poggers/Desktop/measurment/' + self.device.name + '/'
        Path(self.file_path).mkdir(parents=True, exist_ok=True)  # make new directory
        self.file_name = f"{self.device.name}_{datetime.now().strftime('%Y_%m_%d-%H_%M_%S')}.csv"
        self.csvfile = open(self.file_path + self.file_name, 'w')
        self.csvwriter = csv.writer(self.csvfile)

        # Data fields are loaded in their original order by default
        # and we always want to add our timestamp.
        header = ['timestamp', 'differential_potential']
        self.csvwriter.writerow(header)


    """
    async def connect(self):
        await super().connect()
        self.is_connected = True

    async def disconnect(self):
        await super().disconnect()
        self.is_connected = False

    def close_file(self):
        self.csvfile.close()
    """
    def write2csv(self, data):
        try:

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data4csv = [timestamp, data[0]]
            # print(data4csv)
            self.csvfile = open(self.file_path + self.file_name, 'a')
            self.csvwriter = csv.writer(self.csvfile)
            self.csvwriter.writerow(data4csv)
            self.csvfile.close()

        except Exception as e:
            return e

