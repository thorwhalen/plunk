from hear import WavSerializationTrans, WavLocalFileStore
from hum import disp_wf, plot_wf

my_wav_store = WavLocalFileStore("./data/ClickDetection")
click_template = my_wav_store["base_click.wav"]
wf_base = my_wav_store["wf_base.wav"]

print(len(wf_base))


if __name__ == "__main__":
    from hear import WavSerializationTrans, WavLocalFileStore
    from hum import disp_wf, plot_wf

    my_wav_store = WavLocalFileStore("./data/ClickDetection")
    click_template = my_wav_store["base_click.wav"]
    wf_base = my_wav_store["wf_base.wav"]

    print(len(wf_base))
