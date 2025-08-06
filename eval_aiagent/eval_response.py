import os
import time
import pandas as pd
import argparse
from tqdm import tqdm
import sys
sys.path.append('../')
from llms_engine import gpt_engine, llama_engine

parser = argparse.ArgumentParser(prog='Survey_w_LLMs')
parser.add_argument("--API_ENGINE", type=str, choices=['gpt-4-0125-preview', 'meta-llama/Meta-Llama-3-70B-Instruct', 'None'])
parser.add_argument("--ai_agent", type=str, default='gpt', choices=['gpt', 'llama'])
parser.add_argument('--stage', type=str, default='dialog')
parser.add_argument('--lang', type=str, default='eng')
args = parser.parse_args()

if args.API_ENGINE.split("-")[0] == 'gpt':
    LLM='gpt4'
    llm_engine=gpt_engine.GPTEngine(args.API_ENGINE)
elif args.API_ENGINE.split("-")[0] == 'meta':
    LLM='llama'
    llm_engine=llama_engine.LlamaEngine(args.API_ENGINE)
AGENT = args.ai_agent

def get_fact_check_prompt(row, lang):
    if lang == 'eng':
        input_prompt=""
        input_prompt+=row.instruction_eng
        input_prompt+="\n\n"
        input_prompt+=row.doc
        input_prompt+="\nDialogue:\n"
        input_prompt+=row.turn
        input_prompt+="\n\n"
        input_prompt+=row.question_eng
    elif lang == 'kor':
        input_prompt=""
        input_prompt+=row.instruction_kor
        input_prompt+="\n\n"
        input_prompt+=row.doc
        input_prompt+="\nDialogue:\n"
        input_prompt+=row.turn
        input_prompt+="\n\n"
        input_prompt+=row.question_kor
    return input_prompt

def data_load(stage, lang=None):
    if stage == 'dialog':
        return pd.read_csv(f"../results/eval_results/{AGENT}_survey_input_stage_1.csv")
    elif stage == 'fact':
        if not lang == None:
            return pd.read_csv(f'../results/eval_results/{AGENT}_survey_input_stage2_{LLM}_{lang}.csv')

def eval_dialog(lang):
    system_message = "You are an expert in the role of evaluating an agent's responses to a given criterion based on a given dialog."

    data = data_load(stage='dialog')

    cols_list = data.columns.to_list()
    cols_list.append("response")
    df_eval = pd.DataFrame(columns=cols_list)

    total_api_time = 0

    for i, row in tqdm(data.iterrows(), total=len(data)):
        print(f'{i}th dialog evaluating')
        new_row = row[['title', 'case', 'loc', 'dialog', 'survey_kor', 'survey_eng']]        
        dia = row.dialog
        suv = row[f'survey_{lang}']
        input_prompt = dia+"\n\n------------\n\n"+suv

        messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": input_prompt},
            ]

        try:
            start_time = time.time()
            response = llm_engine.get_chat_response(messages, seed=0, temperature=1, max_tokens=500, n=args.num_resp)
            end_time = time.time()

            api_call_time = end_time - start_time
            total_api_time += api_call_time
        except:
            print(f"{i}th dialog evaluation failed")
            continue

        new_row['response']=response
        print(f"Response: {response}")

        df_new = pd.DataFrame.from_records([new_row])
        df_eval=pd.concat([df_eval, df_new])

    df_eval = df_eval.reset_index(drop=True)
    df_eval.to_csv(f"../results/eval_results/{LLM}/agent_{AGENT}_results_{LLM}_api_{lang}_survey_stage_1.csv", index=False)

    print(f"Total API call time: {total_api_time:.2f} seconds")
    with open(f"../results/eval_results/{LLM}/total_api_time.txt", "w") as f:
        f.write(f"Total API call time: {total_api_time:.2f} seconds")

def eval_fact(lang):
    data =data_load(stage='fact', lang=lang)
    cols_list = data.columns.to_list()
    cols_list.append('response')
    df_eval = pd.DataFrame(columns=cols_list)

    for i, row in tqdm(data.iterrows(), total=len(data)):
        print(f'{i}th turn evaluating')
        new_row = row[['title', 'case', 'loc', 'dialog', 'survey_kor', 'survey_eng', 'turn_x', 'doc',
                       'instruction_eng', 'question_eng', 'instruction_kor', 'question_kor', 'turn']]
        
        input_prompt = get_fact_check_prompt(row, lang)
        response=get_chat_response(input_prompt=input_prompt, seed=0, max_tokens=256)

        new_row['response']=response

        print(f"Response: {response}")

        df_new = pd.DataFrame.from_records([new_row])
        df_eval = pd.concat([df_eval, df_new])

    df_eval = df_eval.reset_index(drop=True)
    df_eval.to_csv(f"./agent_{AGENT}_results_gpt_api_{lang}_survey_stage_2.csv", index=False)

if __name__=='__main__':
    if args.stage == 'dialog':
        eval_dialog(lang=args.lang)
    elif args.stage == 'fact':
        eval_fact(lang=args.lang)