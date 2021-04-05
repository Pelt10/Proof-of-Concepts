import json

from dmidecode import DMIDecode
from dotenv import load_dotenv
import subprocess
import pynetbox
import os
import utils
from models import BaseBord, Processor, MemoryDevice, Bios, DiskDevice

# Setup environment
load_dotenv()
netbox = pynetbox.api(
    os.environ.get("NETBOX_URL", 'http://localhost:8000'),
    token=os.environ.get("NETBOX_TOKEN")
)
print("Netbox %s connected on \"%s\"" % (netbox.status()["netbox-version"], netbox.base_url))

# Loading DMI
dmi = DMIDecode(command=["ssh", os.environ.get("INVENTORY_HOST"), "sudo", "dmidecode"])

# Internal representation of a device
device_data = {
    "name": os.environ.get("INVENTORY_HOST"),
    "device_role": utils.goc_device_role(netbox, "Unknown"),
    "manufacturer": utils.goc_manufacturer(netbox, dmi.get("System")[0].get("Manufacturer", "Unknown")),
    "serial": dmi.get("System")[0].get("Serial Number", "Unknown"),
    "asset_tag": dmi.get("System")[0].get("UUID", "Unknown")
}
device_data["device_type"] = utils.goc_device_type(netbox, dmi.get("System")[0].get("Product Name", "Unknown"),
                                                   device_data["manufacturer"])
# Get or Create device
device = utils.goc_device(netbox, device_data)
print(" => %s " % device.name)

# All device get with dmidecode
item_types = {
    "BIOS": lambda item_data: Bios(item_data),
    "Baseboard": lambda item_data: BaseBord(item_data),
    "Processor": lambda item_data: Processor(item_data),
    "Memory Device": lambda item_data: MemoryDevice(item_data),
}
for item_type, item_func in item_types.items():
    print(item_type)
    for item in dmi.get(item_type):
        item_func(item).create(device, netbox)

# Get disks
lsblk_command = "lsblk -SJ -o KNAME,VENDOR,MODEL,SERIAL,REV,SIZE,STATE"
proc = subprocess.Popen(
    ["ssh", os.environ.get("INVENTORY_HOST"), "sudo"] + lsblk_command.split(" "),
    stderr=subprocess.STDOUT,
    stdout=subprocess.PIPE
)
stdout, stderr = proc.communicate()

if proc.returncode > 0:
    raise RuntimeError("{} failed with an error:\n{}".format(lsblk_command, stdout.decode()))

print("Disks")
for disk in json.loads(stdout.decode())["blockdevices"]:
    DiskDevice(disk).create(device, netbox)
