from typing import TypedDict


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
