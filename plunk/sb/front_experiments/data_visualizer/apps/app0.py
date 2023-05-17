import streamlit as st
from hear import WavLocalFileStore
from plunk.sb.front_experiments.data_visualizer.utils.tools import (
    store_to_key_fvs,
    key_fvs_to_tag_fvs,
    mk_Xy,
)
import umap

# import umap.plot
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


root_dir = '/Users/sylvain/Dropbox/_odata/sound/vacuum'
wf_store = WavLocalFileStore(root_dir)
annots_path = '../data/annots_vacuum.csv'
df = pd.read_csv(annots_path)


key_fvs = store_to_key_fvs(wf_store)
tag_fv_iterator = key_fvs_to_tag_fvs(key_fvs, annots_df=df)
X, y = mk_Xy(tag_fv_iterator)

st.title('visualizer')


def plot_umap(X, y, show_legend=True):
    from sklearn.manifold import TSNE

    X_embedded = TSNE(
        n_components=2, learning_rate='auto', init='random', perplexity=3
    ).fit_transform(X)
    # mapper = umap.UMAP().fit(X)
    fig, ax = plt.subplots()
    ax.scatter(X_embedded[:, 0], X_embedded[:, 1])
    # umap.plot.points(mapper, labels=np.array(y), show_legend=show_legend, ax=ax)
    st.pyplot(fig)


plot_umap(X, y)
