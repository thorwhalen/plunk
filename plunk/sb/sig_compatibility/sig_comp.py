from dataclasses import dataclass
from typing import Optional
from collections import Counter
from i2 import Sig
from i2.signatures import PK, VP, VK, PO, KO


def transform_key(d, func):
    return {func(k): v for k, v in d.items()}


kind_to_symbol = {PO: "PO", PK: "PK", VP: "VP", KO: "KO", VK: "VK"}


def param_kind_counter(func):
    sig = Sig(func)
    param_list = [param.kind for param in sig.parameters.values()]
    cc = Counter(param_list)
    res = transform_key(dict(cc), kind_to_symbol_func)
    return res


def kind_to_symbol_func(k):
    return kind_to_symbol[k]


@dataclass
class DefinitionSig:
    PO: Optional[int] = 0
    PK: Optional[int] = 0
    VP: Optional[int] = 0
    KO: Optional[int] = 0
    VK: Optional[int] = 0


@dataclass
class CallSig:
    pos: int = 0
    k: int = 0


def point_is_in_region(point, segment, region_type):
    x, y = point
    po, pk, ko = segment

    if region_type == 0:
        return po <= x <= po + pk and x + y == sum(list(segment))
    if region_type == 1:
        return ko + pk >= y >= ko and x + y >= sum(list(segment))
    if region_type == 2:
        return po <= x <= po + pk and x + y >= sum(list(segment))
    if region_type == 3:
        return x >= po and y >= ko and x + y >= sum(list(segment))


def segment_is_in_region(segment_1, segment_2, region_type):
    po_1, pk_1, ko_1 = segment_1
    point_a = (po_1, pk_1 + ko_1)
    point_b = (po_1 + pk_1, ko_1)

    cond_a = point_is_in_region(point_a, segment_2, region_type)
    cond_b = point_is_in_region(point_b, segment_2, region_type)

    return cond_a and cond_b


def segment_from_definition_sig(d: DefinitionSig):
    segment = (d.PO, d.PK, d.KO)
    return segment


def region_type(d: DefinitionSig):
    vp, vk = d.VP, d.VK
    return 2 * vk + vp


def is_compatible_with(d: DefinitionSig, e: DefinitionSig):
    region_type_d = region_type(d)
    region_type_e = region_type(e)
    if (region_type_d, region_type_e) in [
        (1, 2),
        (2, 1),
        (1, 0),
        (2, 0),
        (3, 0),
        (3, 1),
        (3, 2),
    ]:
        return False

    segment_d = segment_from_definition_sig(d)
    segment_e = segment_from_definition_sig(e)
    return segment_is_in_region(segment_d, segment_e, region_type_e)


def call_is_compatible(d: DefinitionSig, c=CallSig):
    point_c = (c.pos, c.k)
    region_type_d = region_type(d)
    segment_d = segment_from_definition_sig(d)

    cond = point_is_in_region(point_c, segment_d, region_type_d)

    return cond
