import sys
sys.path.append('../')

import os
import json
import openai
import argparse
import pandas as pd

from utils import gen_dialog
from llms_engine import gpt_engine, llama_engine, claude_engine
from glob import glob
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument("--title", type=str)
parser.add_argument("--case", type=int)
parser.add_argument("--API_ENGINE", type=str, choices=['gpt-4-1106-preview', 'meta-llama/Meta-Llama-3.1-8B-Instruct', 'meta-llama/Meta-Llama-3.1-70B-Instruct', 'claude-3-sonnet-20240229'])
parser.add_argument('--accent', type=str, default='standard', help='standard, southwestern, southeastern')
parser.add_argument('--gender', type=str, default='female', help='female, male')
parser.add_argument('--age', type=str, default='over50', help='under50, over50')
args = parser.parse_args()

eng2kor={
    'under50':'50대미만',
    'over50':'50대이상',
    'male':'남성',
    'female':'여성',
    'standard':'서울',
    'southwestern':'호남',
    'southeastern':'영남',
}

if args.API_ENGINE.split("-")[0] == 'gpt':
    LLM='gpt4'
    llm_engine=gpt_engine.GPTEngine(args.API_ENGINE)
elif args.API_ENGINE.split("-")[0] == 'meta':
    LLM='llama'
    LLM+=args.API_ENGINE.split("-")[4]
    llm_engine=llama_engine.LlamaEngine(args.API_ENGINE)

def get_stt_results(accent, gender, age):
    age = eng2kor[age]
    gender = eng2kor[gender]
    accent = eng2kor[accent]
    
    idx_title_num = {}
    data_path = glob(f"../data/script/customer_standard/*.xlsx")
    for d in data_path:
        df = pd.read_excel(d)
        title = d.split('/')[-1].split('.xlsx')[0]
        unique_nums = [int(i.split('-')[-1])-1 for i in list(df['대화셋일련번호'].unique())]
        idxes = [int(j) for j in list(df['스크립트번호'].unique())]
        for n, i in zip(unique_nums, idxes):
            tmp = f'{title}_{n}'
            idx_title_num[i]=tmp

    script_dict = defaultdict(dict)
    for subject in range(1, 57):
        txt = []
        path = f'../results/stt_results/whisper_v2_kor/{subject}/민원인/stt_result_subject_{subject}_{age}_{gender}_{accent}_wt_민원인.txt'
        with open(path, 'r') as f:
            for l in f:
                txt.append(l[1:].strip())
        title = '_'.join(idx_title_num[subject].split('_')[:-1])
        num = idx_title_num[subject].split('_')[-1]
        
        script_dict[title][num]=txt
    script_dict = dict(script_dict)
    return script_dict

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

def main(args):
    entire_history = ""
    system_history = ""
    user_history = ""

    system_prompt_path = f"../system_prompt/system_prompt.text"
    result_path = f'../results/response_results/{LLM}/{args.gender}/{args.age}'

    with open(system_prompt_path, "r") as f:
        system_prompt = f.read().rstrip()

    messages = [{"role": 'system',
                "content": system_prompt}]

    city_script_dict = get_stt_results(args.accent, args.gender, args.age)
    print(city_script_dict.keys())

    queries = city_script_dict[args.title][str(args.case)]

    dialog_title = args.title

    if not os.path.exists(f"{result_path}/{args.accent}/{dialog_title}"):
        os.makedirs(f"{result_path}/{args.accent}/{dialog_title}")
        print(f"Directory created at {result_path}/{args.accent}/{dialog_title}")
    else:
        print(f"Directory already exists at {result_path}/{args.accent}/{dialog_title}")

    for q in queries:
        query = q

        user_dict = {"role": "user",
                     "content": query}
        messages.append(user_dict)

        response = llm_engine.get_chat_response(messages, seed=0, max_tokens=4095)

        entire_history, system_history, user_history = \
            save_history(query, response,
                         entire_history, system_history, user_history)

        assistant_response = {"role": "system",
                              "content": response}
        messages.append(assistant_response)

        print("Citizen: ", query)
        print("Assistant: ", response, "\n")

    with open(f"{result_path}/{args.accent}/{dialog_title}/{dialog_title}_idx_{args.case}_entire_history.txt", 'w') as f:
        f.write(entire_history)

    with open(f"{result_path}/{args.accent}/{dialog_title}/{dialog_title}_idx_{args.case}_gpt_history.txt", 'w') as f:
        f.write(system_history)

    with open(f"{result_path}/{args.accent}/{dialog_title}/{dialog_title}_idx_{args.case}_entire_history.txt", 'r') as f:
        text = f.readlines()
        
        transcript = [t.split("\n")[0] for t in text]
        dialog = gen_dialog(transcript)

    with open(f"{result_path}/{args.accent}/{dialog_title}/{dialog_title}_idx_{args.case}_dialog.txt", 'w') as f:
        f.write(dialog)

if __name__ == '__main__':
    main(args)