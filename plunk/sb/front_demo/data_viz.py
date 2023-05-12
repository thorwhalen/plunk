from dataclasses import dataclass
import streamlit as st
import numpy as np
import pandas as pd
from front.crude import Crudifier
import matplotlib.pyplot as plt
from typing import Any

# from plunk.sb.front_experiments.data_visualizer.dags.wfstore_and_annots_to_dataset import (
#     load_dataset,
# )
# from plunk.sb.front_experiments.data_visualizer.components.elements import (
#     # DataLoader,
#     # DataLoader2,
#     ZipWavDataLoader,
# )
# from functools import partial
from plunk.sb.front_experiments.data_visualizer.utils import tools as tls
from streamlitfront import mk_app, binder as b
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY
from streamlitfront.elements import SelectBox
from front.elements import OutputBase
import umap

# import umap.plot
from hear import WavLocalFileStore


root_dir = '/Users/sylvain/Dropbox/_odata/sound/vacuum'
annots_path = '/Users/sylvain/Desktop/dev/otosense/plunk/plunk/sb/front_experiments/data_visualizer/data/annots_vacuum.csv'


# ============ BACKEND ============


def load_dataset(folder_path: str = root_dir, annot_path: str = annots_path):
    wf_store = WavLocalFileStore(folder_path)
    df = pd.read_csv(annot_path)
    key_fvs = tls.store_to_key_fvs(wf_store)
    tag_fv_iterator = tls.key_fvs_to_tag_fvs(key_fvs, annots_df=df)
    X, y = tls.mk_Xy(tag_fv_iterator)  # Cmd+]

    return X, y


def plot_umap(Xy: Any):
    return Xy


# ============ END BACKEND ============


# ============ FRONT END   ============


if not b.mall():
    b.mall = dict(Xy={})
mall = b.mall()

load_dataset = Crudifier(output_store='Xy', mall=mall)(load_dataset)


def debug():
    st.write(mall)


plot_umap = Crudifier(param_to_mall_map=dict(Xy='Xy'), mall=mall)(plot_umap)


@dataclass
class UmapPlotter(OutputBase):
    def render(self):
        from sklearn.manifold import TSNE

        X, y = self.output
        projected = TSNE(
            n_components=2, learning_rate='auto', init='random', perplexity=3
        ).fit_transform(X)
        # projected = umap.UMAP().fit_transform(X)
        fig, ax = plt.subplots()
        show_legend = st.checkbox(label='Show legend')
        plt.scatter(projected[:, 0], projected[:, 1], c=y, s=0.1, cmap='Spectral')
        # umap.plot.points(mapper, labels=np.array(y), show_legend=show_legend, ax=ax)
        st.pyplot(fig)


config_ = {
    APP_KEY: {'title': 'Data Visualizer'},
    RENDERING_KEY: {
        'plot_umap': {
            'execution': {
                # 'inputs': {
                #     'Xy': {ELEMENT_KEY: SelectBox, 'options': mall['Xy']},
                # },
                'output': {ELEMENT_KEY: UmapPlotter},
            },
        },
    },
}
# ============ END FRONTEND ============

if __name__ == '__main__':
    app = mk_app([load_dataset, plot_umap, debug], config=config_)
    app()
