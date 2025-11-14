"""Tool to get a timestamped transcription of a video file.

Supports .mov files.


"""

import moviepy.editor as mp
import speech_recognition as sr


def mov_to_transcription(mov_filepath: str):
    """
    Transcribes the audio from a MOV file using Google Speech Recognition API.

    :param mov_filepath: Filepath of .mov file
    :return: A dict whose keys are timestamps (seconds offset) and values are
    transcribed text
    """
    # Note that this implementation uses a temporary WAV file to store the audio
    # extracted from the MOV file. This is necessary because the SpeechRecognition
    # library only supports audio files in certain formats, including WAV.
    # Once the audio has been transcribed, the temporary file is deleted.
    # TODO: Use an actual temp file (file not even deleted here).

    # Load the MOV file and extract the audio
    video = mp.VideoFileClip(mov_filepath)
    audio = video.audio.to_audiofile('temp.wav')

    # Transcribe the audio using Google Speech Recognition API
    recognizer = sr.Recognizer()
    with sr.AudioFile('temp.wav') as source:
        audio = recognizer.record(source)
    transcription = recognizer.recognize_google(audio)

    # Convert the transcription to a dictionary of timestamped text
    words = transcription.split()
    duration = video.duration
    # TODO: Perhaps int (floor) better than round?
    timestamps = [round((i / len(words)) * duration, 2) for i in range(len(words))]
    result = {timestamps[i]: words[i] for i in range(len(words))}

    return result


def mov_to_mp4(
    mov_filepath: str,
    output_file_path=None,
    output_format='mp4',
    output_codec='libx264',
    audio_codec='acc',
):
    from moviepy.editor import VideoFileClip

    if output_file_path is None:
        import os

        output_file_path = os.path.splitext(mov_filepath)[0] + f'.{output_format}'

    # Load the video file
    video = VideoFileClip(mov_filepath)

    # Convert the video to mp4 format
    video.write_videofile(
        output_file_path, codec=output_codec, audio=True, audio_codec=audio_codec
    )

    # Close the video file
    video.close()
