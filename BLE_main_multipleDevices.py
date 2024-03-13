import asyncio
import logging
import bleak
from bleak import BleakClient, BleakScanner, BLEDevice
from functools import partial
from MyBleakClient import MyBleakClient
from datetime import datetime


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",)

NOTIFICATION_UUID = "5a3b0203-f6dd-4c45-b31f-e89c05ae3390"

async def discoverNodes(name: str) -> BLEDevice | None:
    """ Discovering devices and return object of device """
    logging.info("scanning...")
    devices = await BleakScanner.discover()
    for d in devices:
        if d.name == name:
            logging.info(d.details)
            return d
    return None

async def conectToNode(lock: asyncio.Lock,name: str) -> BleakClient | None:
    """
    Finds device with device name and connects to it
    Args:
        name (str): device name
        lock (asyncio.Lock): Lock used to prevent simultaneous use of BlueZ discovery procedure.
    """

    async with lock:  # lock is used to prevent simultaneous use of BlueZ discovery procedure
        logging.info("Connecting to device " + name )
        device = await BleakScanner.find_device_by_name(name)
    if not device:
        logging.info("FAILED: connection to device " + name)
        return None, None
    client = MyBleakClient(device, disconnected_callback=disconnected_callback)
    await client.connect()
    if client.is_connected:
        logging.info("connected to device " + name)
        return device, client
    else:
        logging.info("FAILED: connection to device " + name)
        return None, None


async def my_notification_callback_with_client_input(client: BleakClient, sender: int, data: bytearray) -> None:
    """
    Notification callback with client awareness, i.e. the client is passed in as an argument.
    Reads notification data and saves it to csv file.
    Args:
        client (BleakClient): The client that is calling the callback.
        sender (int): The handle of the characteristic sending the notification.
        data (bytearray): The data returned in the notification.
    """
    data = int.from_bytes(data, "big")
    client.write2csv([data])


def disconnected_callback(client: BleakClient): -> None:
    """
    Disconnected callback handler. Called when the device connection is lost.
    Args:
        client (BleakClient): The client that got disconnected.
    """
    logging.info(str(client.address) + " disconnected")


async def NotificationRoutine(lock:asyncio.Lock, device_name:str) -> None:
    """
    Routine that connects to device and starts notification callback.
    Args:
        lock (asyncio.Lock): Lock used to prevent simultaneous use of BlueZ discovery procedure.
        device_name (str): Name of the device to connect to.
    """

    connection_task = asyncio.create_task(conectToNode(lock, device_name))
    device, client = await connection_task
    while(True):
        try:
            await client.start_notify(NOTIFICATION_UUID, partial(my_notification_callback_with_client_input, client))
        except Exception as e:
            ##print("error with", str(e))   <- e is not printed, probably bleak specific
            connection_task = asyncio.create_task(conectToNode(lock,device_name))
            device, client = await connection_task


async def main():
    """ Main function, defines device names and starts notification routines for each device. """

    device_names = ['P0','P1']
    lock = asyncio.Lock()
    device = await asyncio.gather(*(NotificationRoutine(lock,name) for name in device_names))






if __name__ == '__main__':
    asyncio.run(main())