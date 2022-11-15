from dataclasses import dataclass
from front.elements import OutputBase
import streamlit as st
import matplotlib.pyplot as plt


@dataclass
class AudioArrayDisplay(OutputBase):
    def render(self):
        sound, tag = self.output
        # if not isinstance(sound, str):
        # if not isinstance(sound, bytes):

        #     sound = sound.getvalue()

        # arr = sf.read(BytesIO(sound), dtype="int16")[0]
        # st.write(type(arr))
        tab1, tab2 = st.tabs(["Audio Player", "Waveform"])
        with tab1:
            st.audio(sound)
        with tab2:
            fig, ax = plt.subplots(figsize=(15, 5))
            ax.plot(sound, label=f"Tag={tag}")
            ax.legend()
            st.pyplot(fig)
            # st.write(arr[:10])


@dataclass
class GraphOutput(OutputBase):
    use_container_width: bool = False

    def render(self):
        # with st.expander(self.name, True): #cannot nest expanders
        dag = self.output
        st.graphviz_chart(
            figure_or_dot=dag.dot_digraph(),
            use_container_width=self.use_container_width,
        )


@dataclass
class ArrayPlotter(OutputBase):
    def render(self):
        # st.write(f"output = {self.output}")
        X = self.output
        fig, ax = plt.subplots(figsize=(15, 5))
        ax.plot(X)
        # ax.vlines(range(len(X)), ymin=np.min(X), ymax=X)
        ax.legend()
        st.pyplot(fig)
