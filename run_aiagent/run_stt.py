import os
import argparse

from utils import *
from glob import glob


def stt_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', default='stt', type=str)
    parser.add_argument('--name', default='large-v3', type=str, help='[tiny, base, small, medium, large, large-v2]')
    parser.add_argument('--subject', default=0, type=int)
    parser.add_argument('--stt_all', action='store_true')
    parser.add_argument('--lang_ko', action='store_true')
    parser.add_argument('--age', default='under50', type=str)
    parser.add_argument('--gender', default='female', type=str)
    parser.add_argument('--accent', default='standard', type=str)
    parser.add_argument('--w_wt', help='stands for with word timestamps.', action='store_true')
    parser.add_argument('--show', help='Show STT output.', action='store_true')
    return parser.parse_args()

eng2kor={
    'under50':'10~50대',
    'over50':'50대',
    'male':'남성',
    'female':'여성',
    'standard':'서울',
    'southwestern':'호남',
    'southeastern':'영남',
}

def load_files(args):
    gender = eng2kor[args.gender]
    accent = eng2kor[args.accent]

    customer_path = f'../data/audio/customer/{args.age}/{args.gender}/{args.accent}/{args.subject}/'
    agent_path = f'../data/audio/agent/{args.gender}/{args.subject}/'

    f_name_customer = f'{args.subject}_*_{gender}_{accent}_민원인_*.wav'
    f_name_agent = f'{args.subject}_{gender}_상담사_*.wav'

    files_list_customer = glob(os.path.join(customer_path, f_name_customer))
    files_list_customer = sorted(files_list_customer, key=lambda x: int(x.split("_")[-1].split(".wav")[0]))
    files_list_agent = glob(os.path.join(agent_path, f_name_agent))
    files_list_agent = sorted(files_list_agent, key=lambda x: int(x.split("_")[-1].split(".wav")[0]))

    return files_list_agent, files_list_customer

def load_files_each(args, speaker):
    gender = eng2kor[args.gender]
    accent = eng2kor[args.accent]

    if speaker == 'customer':
        path = f'../data/audio/customer/{args.age}/{args.gender}/{args.accent}/{args.subject}/'
        f_name_customer = f'{args.subject}_*_{gender}_{accent}_민원인_*.wav'
        file_path = os.path.join(path, f_name_customer)

        files_list_customer = glob(file_path)

        if len(files_list_customer) > 0:
            files_list = sorted(files_list_customer, key=lambda x: int(x.split("_")[-1].split(".wav")[0]))
        else:
            f_name_customer = f'{args.subject}_{args.age}_{gender}_{accent}_민원인*.wav'
            file_path = os.path.join(path, f_name_customer)
            files_list_customer = glob(file_path)
            files_list = sorted(files_list_customer, key=lambda x: int(x.split("_민원인")[-1].split(".wav")[0]))

    elif speaker == 'agent':
        path = f'../data/audio/agent/{args.gender}/{args.subject}/'
        f_name_agent = f'{args.subject}_{gender}_상담사_*.wav'
        file_path = os.path.join(path, f_name_agent)

        files_list_agent = glob(file_path)

        if len(files_list_agent) > 0:
            files_list = sorted(files_list_agent, key=lambda x: int(x.split("_")[-1].split(".wav")[0]))
        else:
            f_name_agent = f'{args.subject}_{gender}_상담사*.wav'
            file_path = os.path.join(path, f_name_agent)
            files_list_agent = glob(file_path)
            files_list = sorted(files_list_agent, key=lambda x: int(x.split("_상담사")[-1].split(".wav")[0]))

    return files_list

def is_stt_result_exist(args, role, results_save_path):
    gender = eng2kor[args.gender]
    accent = eng2kor[args.accent]

    if role == 'customer':
        if args.age == "under50":
            age = '10~50대'
        else:
            age = '50대이상'

        save_path = results_save_path + f'/민원인/'

        if not os.path.exists(save_path):
            os.mkdir(save_path)

        if args.w_wt:
            text_file_name = f"stt_result_subject_{args.subject}_{age}_{gender}_{accent}_wt_민원인.txt"
        else:
            text_file_name = f"stt_result_subject_{args.subject}_{age}_{gender}_{accent}_민원인.txt"

    elif role=='agent':
        save_path = results_save_path + f'/상담사/'

        if not os.path.exists(save_path):
            os.mkdir(save_path)

        if args.w_wt:
            text_file_name = f"stt_result_subject_{args.subject}_{gender}_wt_상담사.txt"
        else:
            text_file_name = f"stt_result_subject_{args.subject}_{gender}_상담사.txt"

    path = os.path.join(save_path, text_file_name)
    if os.path.exists(path):
        return os.path.getsize(path)
    else:
        return False

def save_results(args, results, role, results_save_path):
    text=""
    for k, v in results.items():
        if not len(v) == 0:
            text += v
            if v[-1] in [".", "!", "?"]:
                text += "\n"
            else:
                text += ".\n"

    text = text.replace("  ", " ")
    text = text[:-1]

    gender = eng2kor[args.gender]
    accent = eng2kor[args.accent]

    if role == 'customer':
        if args.age == "under50":
            age = '50대미만'
        else:
            age = '50대이상'

        save_path = results_save_path + f'/민원인/'

        if not os.path.exists(save_path):
            os.mkdir(save_path)

        if args.w_wt:
            text_file_name = f"stt_result_subject_{args.subject}_{age}_{gender}_{accent}_wt_민원인.txt"
        else:
            text_file_name = f"stt_result_subject_{args.subject}_{age}_{gender}_{accent}_민원인.txt"

        with open(f"{save_path}/{text_file_name}", "w") as f:
            f.write(text)

    elif role=='agent':
        save_path = results_save_path + f'/상담사/'

        if not os.path.exists(save_path):
            os.mkdir(save_path)

        if args.w_wt:
            text_file_name = f"stt_result_subject_{args.subject}_{gender}_wt_상담사.txt"
        else:
            text_file_name = f"stt_result_subject_{args.subject}_{gender}_상담사.txt"

        with open(f"{save_path}/{text_file_name}", "w") as f:
            f.write(text)

def main(args, model):
    if args.name=='large-v2' and args.lang_ko:
        results_save_path = f"../results/stt_results/whisper_v2_kor/{args.subject}"
    elif args.name=='large-v2' and not args.lang_ko:
        results_save_path = f"../results/stt_results/whisper_v2/{args.subject}"
    os.makedirs(results_save_path, exist_ok=True)

    if is_stt_result_exist(args=args, role='agent', results_save_path=results_save_path):
        files_list_agent = None
        print(f"STT for agent is already done!!!")
    else:
        files_list_agent = load_files_each(args, 'agent')

    if is_stt_result_exist(args=args, role='customer', results_save_path=results_save_path):
        files_list_customer = None
        print("STT is cutomer already done!!!")
    else:
        files_list_customer = load_files_each(args, 'customer')

    if not files_list_customer == None:
        for d in files_list_customer:
            check_audio_quality(d)

        customer_results = {}
        for d in files_list_customer:
            audio_name = d.split("/")[-1][:-4]
            result = sp2txt(model, d, lang_ko=args.lang_ko, use_wt=args.w_wt, show_output=True)
            customer_results[audio_name] = result['text']

        save_results(args, customer_results, role='customer', results_save_path=results_save_path)

    if not files_list_agent == None:
        for d in files_list_agent:
            check_audio_quality(d)

        agent_results={}
        for d in files_list_agent:
            audio_name = d.split("/")[-1][:-4]
            result = sp2txt(model, d, lang_ko=args.lang_ko, use_wt=args.w_wt, show_output=True)
            agent_results[audio_name] = result['text']

        save_results(args, agent_results, role='agent', results_save_path=results_save_path)

if __name__ == '__main__':
    args = stt_parser()

    print(f"Model[{args.name}] Loading")
    model = load_model(args.mode, args.name)
    print("model loading finished!!!")

    if args.stt_all:
        for i in range(1, 57):
            for s in ['male', 'female']:
                for a in ['under50', 'over50']:
                    for loc in ['standard', 'southeastern', 'southwestern']:
                        args.subject = i
                        args.gender = s
                        args.age = a
                        args.accent = loc

                        main(args, model)
    else:
        main(args, model)