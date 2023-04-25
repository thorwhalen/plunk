

import random
from typing import List, TypedDict

Annotation = TypedDict(
	'Annotation',
    name=str,
    kind=str,
    bt=int,
    tt=int,
)

TimestampedData = TypedDict(
    'TimestampedData',
    data=bytes,
    bt=int,
)


class DPP:
	
    def __init__(self):
        self._init_aggregation_props()
	
    def run(self, timestamped_data: TimestampedData, aggregate: bool = False) -> List[Annotation]:
        return list(self._generate_outputs(timestamped_data, aggregate))
                
    def _generate_outputs(self, timestamped_data, aggregate):
        if aggregate and self._aggregation_bt is None:
            self._aggregation_bt = timestamped_data['bt']

        # 20% chance of returning an outlier per block
        if not random.randint(0,4):
            result = Annotation(
                name='Outlier detected in block!',
                kind='DPP',
                bt=timestamped_data['bt'],
                tt=timestamped_data['tt'],
		    )
            yield result
            if aggregate:
                self._outlier_detected_in_session = True
        if not aggregate:
            if self._outlier_detected_in_session:
                yield Annotation(
                    name='Outlier detected in session!',
                    kind='DPP',
                    bt=self._aggregation_bt,
                    tt=timestamped_data['tt'],
                )
            self._init_aggregation_props()

    def _init_aggregation_props(self):
        self._aggregation_bt = None
        self._outlier_detected_in_session = False

    __call__ = run
