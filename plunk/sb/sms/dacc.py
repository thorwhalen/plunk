from tabled import DfLocalFileReader as Reader
from plunk.sb.sms.utils import metadata_store, data_store
from dol import lazyprop

import os


path = '~/Dropbox/_odata/sound/induction_motor_data/Healthy/Healthy_750rpm/'
DFLT_LOCAL_SOURCE_DIR = os.path.expanduser(path)


def mk_dacc():
    return Dacc(root_dir=DFLT_LOCAL_SOURCE_DIR)


class Dacc:
    def __init__(self, root_dir=DFLT_LOCAL_SOURCE_DIR):
        self.global_store = Reader(root_dir)

    @lazyprop
    def metadata(self):
        return metadata_store(self.global_store)

    @lazyprop
    def data(self):
        return data_store(self.global_store)
