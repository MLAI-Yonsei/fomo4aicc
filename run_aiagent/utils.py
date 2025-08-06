import re
import json
import whisper

from glob import glob

def load_model(mode, name):
    if mode == 'stt':
        model = whisper.load_model(name, download_root='./model_checkpoint')
    return model

def load_data(path, test_only=False, print_info=False):
    '''
    Parameters
    ----------
    path : list
    test_only : bool
    -------
    '''

    if path.split('.')[-1] == 'wav':
        file_list = glob(f"{path}/*.wav")
    else:
        paths = glob(path)
        paths = list(map(lambda x: x.split('.')[-1], paths))
        while not 'wav' in paths:
            path += '/*'
            paths = glob(path)
            paths = list(map(lambda x: x.split('.')[-1], paths))
        file_list = glob(f"{path}.wav")

    file_list = sorted(file_list)

    if not test_only:
        gt_script = json.load(open(f"{path}/script/*.json"))
        reference = list(gt_script.values())

    if print_info:
        print("====================")
        print("Sample path of Audio")
        print(f"{file_list[0]}")
        print("====================\n")

    if not test_only:
        return file_list, reference
    else:
        return file_list

def check_audio_quality(path):
    from pydub import AudioSegment
    audio = AudioSegment.from_wav(f'{path}')
    rate = audio.frame_rate
    print("====================")
    print(f"Audio path : ")
    print(f"{path}")
    print(f"Audio Rate : ")
    print(f"{rate}")
    print("====================\n")

def get_auido_length(path):
    from pydub import AudioSegment
    audio = AudioSegment.from_wav(f'{path}')
    length = audio.duration_seconds
    return length

def sp2txt(model, data, lang_ko, use_wt=False, show_output=False):
    if lang_ko:
        options = dict(language='korean', without_timestamps=use_wt)
    else:
        options = dict(without_timestamps=use_wt)
    transcribe_options = dict(task='transcribe', **options)
    result = model.transcribe(data, **transcribe_options)
    if show_output:
        print("====================")
        print(f"Audio path : ")
        print(f"{data}")
        print(f"Transform result : ")
        print(f"{result}")
        print("====================\n")

    return result

def gen_dialog(prompt):
    text="Dialog\n"
    
    len_dialog = len(prompt)
    if len_dialog == 0:
        return None
    
    for t, i in enumerate(range(1, len_dialog, 2)):
        text+=f'[turn-{t}]\n'
        text+=f'user: {prompt[i-1]}\n'
        text+=f'agent: {prompt[i]}\n'
    return text

def save_history(input, output, total, gpt_history, user_history):
    input = str(input)
    output = str(output)
    if input[-1] not in [".", "!", "?"]:
        input += "."
    user_history = user_history + input + "\n"

    if output[-1] not in [".", "!", "?"]:
        output += "."
    output = output.replace("\n", " ")

    gpt_history = gpt_history + output + "\n"
    total += input + "\n" + output + "\n"

    return total, gpt_history, user_history