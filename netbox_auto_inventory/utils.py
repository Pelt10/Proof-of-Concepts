def goc_manufacturer(netbox, name):
	if name is None or len(name.strip()) == 0:
		name = "Unknown"
	manufacturer = netbox.dcim.manufacturers.get(slug=slugify(name))
	if manufacturer is None:
		manufacturer = netbox.dcim.manufacturers.create(
			name=name,
			slug=slugify(name)
		)
	return manufacturer


def goc_device_type(netbox, model, manufacturer):
	if model is None or len(model.strip()) == 0:
		model = "Unknown"
	device_type = netbox.dcim.device_types.get(model=model)
	if device_type is None:
		device_type = netbox.dcim.device_types.create(
			manufacturer=manufacturer.id,
			model=model,
			slug=slugify(model)
		)
	return device_type


def goc_device_role(netbox, name):
	if name is None or len(name.strip()) == 0:
		name = "Unknown"
	device_role = netbox.dcim.device_roles.get(name=name)
	if device_role is None:
		device_role = netbox.dcim.device_roles.create(
			name=name,
			slug=slugify(name)
		)
	return device_role


def goc_device(netbox, device_data):
	device = netbox.dcim.devices.get(name=device_data["name"])
	if device is None:
		device = netbox.dcim.devices.create(
			name=device_data["name"],
			device_type=device_data["device_type"].id,
			device_role=device_data["device_role"].id,
			serial=device_data["serial"],
			asset_tag=device_data["asset_tag"],
			site=1 # Static site ! 
		)
	return device


def goc_inventory_item(netbox, item_data):
	item = netbox.dcim.inventory_items.get(manufacturer_id=item_data["manufacturer"].id, serial=item_data["serial"])
	if item is None:
		item = netbox.dcim.inventory_items.create(**item_data)
	return item


def slugify(value):
	import re
	value = re.sub(r'[^\w\s-]', '', value.lower())
	return re.sub(r'[-\s]+', '-', value).strip('-_')
