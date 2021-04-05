import utils


class BaseHardware:
    unknown_list = [
        "To be filled by O.E.M.",
        "Not Specified",
        "UNKNOWN",
        "Default string",
        "Fill By OEM"
    ]

    def __init__(self, item):
        self.item = item

    def get_name(self) -> str or None:
        return None

    def get_label(self) -> str:
        return self.item.get("Product Name")

    def get_manufacturer(self, netbox) -> int:
        return utils.goc_manufacturer(netbox, self.item.get("Manufacturer", "Unknown"))

    def get_part_id(self) -> str:
        return ""

    def get_serial(self) -> str:
        return self.item.get("Serial Number") if self.item.get("Serial Number") not in self.unknown_list else ""

    def get_asset_tag(self) -> str or None:
        return self.item.get("Asset Tag") if self.item.get("Asset Tag") not in self.unknown_list else None

    def get_discovered(self) -> bool:
        return True

    def get_description(self) -> str:
        return ""

    def create(self, device, netbox):
        print("    - Create %s(%s) - \"%s\"" % (self.get_name(), self.get_label(), self.get_asset_tag()))
        return netbox.dcim.inventory_items.create(
            device=device.id,
            name=self.get_name(),
            label=self.get_label(),
            manufacturer=self.get_manufacturer(netbox).id,
            part_id=self.get_part_id(),
            serial=self.get_serial(),
            asset_tag=self.get_asset_tag(),
            discovered=self.get_discovered(),
            description=self.get_description()
        )


class Bios(BaseHardware):
    def get_name(self) -> str or None:
        return "BIOS"

    def get_manufacturer(self, netbox) -> int:
        return utils.goc_manufacturer(netbox, self.item.get("Vendor"))

    def get_label(self) -> str:
        return "Version: %s" % self.item.get("Version")

    def get_serial(self) -> str:
        return ""

    def get_asset_tag(self) -> str or None:
        return None

    def get_description(self) -> str:
        return "Release Date: %s" % self.item.get("Release Date")


class BaseBord(BaseHardware):

    def get_name(self) -> str or None:
        return "Base Board"

    def get_part_id(self) -> str or None:
        return ""

    def get_description(self) -> str:
        return "Version: %s" % (self.item.get("Version"))


class Processor(BaseHardware):

    def get_name(self) -> str or None:
        return self.item.get("Socket Designation")

    def get_label(self) -> str:
        return self.item.get("Version")

    def get_part_id(self) -> str or None:
        return self.item.get("ID")


class MemoryDevice(BaseHardware):

    def get_name(self) -> str or None:
        return self.item.get("Locator")

    def get_label(self) -> str:
        return "%s - %s" % (
            self.item.get("Type"),
            self.item.get("Size")
        )

    def get_part_id(self) -> str or None:
        return self.item.get("Part Number")

    def get_asset_tag(self) -> str or None:
        if self.get_part_id() == "NO DIMM":
            return None
        return "%s - %s" % (self.get_serial(), self.item.get("Asset Tag"))\
            if self.item.get("Asset Tag") not in self.unknown_list \
            else None


class DiskDevice(BaseHardware):

    def get_name(self) -> str or None:
        return "Disk %s" % self.item["kname"]

    def get_label(self) -> str:
        return self.item["model"]

    def get_manufacturer(self, netbox) -> int:
        return utils.goc_manufacturer(netbox, self.item["vendor"])

    def get_serial(self) -> str:
        return self.item["serial"]

    def get_asset_tag(self) -> str or None:
        return None
