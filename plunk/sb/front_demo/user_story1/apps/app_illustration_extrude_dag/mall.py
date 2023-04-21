from platform_poc.data.store_factory import mk_ram_store


mall = dict(msg_store=mk_ram_store())

# same as:
# mall = {'x_store': dict()}
