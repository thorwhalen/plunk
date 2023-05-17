from dataclasses import dataclass
import streamlit as st
import numpy as np
import pandas as pd
from front.crude import Crudifier
import matplotlib.pyplot as plt
from typing import Any
from streamlitfront.elements import (
    SuccessNotification,
)

# from plunk.sb.front_experiments.data_visualizer.dags.wfstore_and_annots_to_dataset import (
#     load_dataset,
# )
# from plunk.sb.front_experiments.data_visualizer.components.elements import (
#     # DataLoader,
#     # DataLoader2,
#     ZipWavDataLoader,
# )
# from functools import partial
from plunk.sb.front_experiments.data_visualizer.utils.tools import (
    store_to_key_fvs,
    key_fvs_to_tag_fvs,
    mk_Xy,
)
from streamlitfront import mk_app, binder as b
from front import APP_KEY, RENDERING_KEY, ELEMENT_KEY, NAME_KEY
from streamlitfront.elements import SelectBox
from front.elements import OutputBase


from hear import WavLocalFileStore


root_dir = '/Users/sylvain/Dropbox/_odata/sound/vacuum'
annots_path = '../data/annots_vacuum.csv'


# ============ BACKEND ============


def load_dataset(folder_path: str = root_dir, annot_path: str = annots_path):
    wf_store = WavLocalFileStore(folder_path)
    df = pd.read_csv(annot_path)
    key_fvs = store_to_key_fvs(wf_store)
    tag_fv_iterator = key_fvs_to_tag_fvs(key_fvs, annots_df=df)
    X, y = mk_Xy(tag_fv_iterator)  # Cmd+]

    return X, y


def visualize_data(Xy: Any):
    return Xy


# ============ END BACKEND ============


# ============ FRONT END   ============


if not b.mall():
    b.mall = dict(Xy={})
mall = b.mall()

load_dataset = Crudifier(output_store='Xy', mall=mall)(load_dataset)

visualize_data = Crudifier(param_to_mall_map=['Xy'], mall=mall)(visualize_data)


@dataclass
class TsnePlotter(OutputBase):
    def render(self):
        from sklearn.manifold import TSNE
        from sklearn import preprocessing

        X, y = self.output

        X_embedded = TSNE(
            n_components=2, learning_rate='auto', init='random', perplexity=3
        ).fit_transform(X)
        fig, ax = plt.subplots()

        lb = preprocessing.LabelBinarizer()
        colors = lb.fit_transform(y)
        ax.scatter(X_embedded[:, 0], X_embedded[:, 1], alpha=0.5, c=colors)
        st.pyplot(fig)


@dataclass
class PCAPlotter(OutputBase):
    def render(self):
        X, y = self.output
        from sklearn.decomposition import PCA
        from sklearn import preprocessing

        lb = preprocessing.LabelBinarizer()
        colors = lb.fit_transform(y)
        pca = PCA(n_components=2)
        X_embedded = pca.fit_transform(X)
        fig, ax = plt.subplots()
        ax.scatter(X_embedded[:, 0], X_embedded[:, 1], alpha=0.5, c=colors)
        st.pyplot(fig)


config_ = {
    APP_KEY: {'title': 'Data Visualizer'},
    RENDERING_KEY: {
        'load_dataset': {
            NAME_KEY: "Get Data",
            # "description": {"content": get_data_description},
            "execution": {
                "inputs": {
                    "folder_path": {ELEMENT_KEY: SelectBox, 'options': [root_dir]},
                    "annot_path": {ELEMENT_KEY: SelectBox, 'options': [annots_path]},
                },
                'output': {
                    ELEMENT_KEY: SuccessNotification,
                    'message': 'The step has been created successfully.',
                },
            },
        },
        'visualize_data': {
            NAME_KEY: "Visualize Data",
            # "description": {"content": get_data_description},
            'execution': {
                # 'inputs': {
                #     'Xy': {ELEMENT_KEY: SelectBox, 'options': mall['Xy']},
                # },
                'output': {ELEMENT_KEY: PCAPlotter},
                # "auto_submit": True,
            },
        },
    },
}
# ============ END FRONTEND ============

if __name__ == '__main__':
    app = mk_app([load_dataset, visualize_data], config=config_)
    app()
st.write(mall)
