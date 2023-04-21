from i2 import FuncFactory
from olab import simple_chunker, simple_featurizer

from platform_poc.data.store_factory import mk_ram_store


mall = dict(tagged_data=mk_ram_store(), sessions=mk_ram_store(),)
