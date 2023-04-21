from i2 import FuncFactory
from olab import simple_chunker, simple_featurizer

from platform_poc.data.store_factory import mk_ram_store


mall = dict(
    tagged_data=mk_ram_store(),
    step_factories=mk_ram_store(
        chunker=FuncFactory(simple_chunker), featurizer=FuncFactory(simple_featurizer),
    ),
    # steps=mk_mongodb_store(collection_name="steps"),
    # pipelines=mk_mongodb_store(collection_name="pipelines"),
    steps=mk_ram_store(),
    pipelines=mk_ram_store(),
    learned_models=mk_ram_store(),
    model_outputs=mk_ram_store(),
    sessions=mk_ram_store(),
)
