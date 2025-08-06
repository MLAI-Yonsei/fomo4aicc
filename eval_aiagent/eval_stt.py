import os
import json
import jiwer
import numpy as np
import pandas as pd
from glob import glob
from collections import defaultdict

def levenshtein_distance(ref, hyp):
    m, n = len(ref), len(hyp)
    # Initialize matrix
    dp = [[0] * (n+1) for _ in range(m+1)]

    # Initialize the first column and row
    for i in range(1, m+1):
        dp[i][0] = i
    for j in range(1, n+1):
        dp[0][j] = j

    # Fill the matrix
    for i in range(1, m+1):
        for j in range(1, n+1):
            cost = 0 if ref[i-1] == hyp[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,      # Deletion
                dp[i][j-1] + 1,      # Insertion
                dp[i-1][j-1] + cost  # Substitution
            )
    return dp[m][n]

def word_error_rate(ref, hyp):
    """
    Calculates the Word Error Rate (WER).
    ref: list of reference words
    hyp: list of hypothesis words
    """
    # Split the sentences into words if they are not already in list form
    ref_words = ref.split() if type(ref) is str else ref
    hyp_words = hyp.split() if type(hyp) is str else hyp

    # Compute Levenshtein distance
    distance = levenshtein_distance(ref_words, hyp_words)
    # Calculate WER
    wer = distance / float(len(ref_words))
    return wer

def character_error_rate(ref, hyp):
    """
    Calculates the Character Error Rate (CER).
    ref: string of reference
    hyp: string of hypothesis
    """
    # Compute Levenshtein distance
    distance = levenshtein_distance(ref, hyp)
    # Calculate CER
    cer = distance / float(len(ref))
    return cer

def get_wer_cer_scores(stt_dict, gt_dict):
    total_rows = []
    for k in stt_dict.keys():
        for exp in stt_dict[k].keys():
            agent_city = exp.split("_")[-1]
            if agent_city == '민원인':
                age=exp.split("_")[4]
                gender=exp.split("_")[5]
                loc = exp.split("_")[6]
            else:
                age="empty"
                gender=exp.split("_")[4]
                loc = "empty"
            
            ref = gt_dict[k]
            ref = " ".join(ref)
                
            hyp = stt_dict[k][exp]
            hyp = " ".join(hyp)
            
            wer = jiwer.wer(ref, hyp)
            cer = jiwer.cer(ref, hyp)
            
            total_rows.append([k, age, gender, loc, agent_city, wer, cer, exp])
    
    result_df = pd.DataFrame(data=total_rows, columns=["Case", "Age", "Gender", "Location", "agent_City", "wer", "cer", "file_name"])
    return result_df

def get_text_dict(df_name, turn):
    df = pd.read_excel(df_name,  engine='openpyxl')
    df.dropna(subset=[f'{turn} 발화'], inplace=True)
    df = df.reset_index()

    script = dict([(k, df.loc[df['스크립트번호']==k, :][f'{turn} 발화'].tolist()) for k in df["스크립트번호"].unique().tolist()])
    for k, vs in script.items():
        tmp = []
        for v in vs:
            tmp.append(v.replace("\n", " "))
        script[k]=tmp
    return script

def main():
    customer_whisper_result_list = glob("../results/stt_results/whisper_v2/*/민원인/*.txt")
    agent_whisper_result_list = glob("../results/stt_results/whisper_v2/*/상담사/*.txt")

    customer_whisper_standard_dict=defaultdict(dict)
    customer_whisper_east_dict=defaultdict(dict)
    customer_whisper_west_dict=defaultdict(dict)

    for t in customer_whisper_result_list:
        case_num = int(t.split("/")[4])
        sample_name = t.split("/")[-1].split(".txt")[0]
        loc = t.split("/")[-1].split("_")[6]
        
        with open(t, 'r') as f:
            txt = f.read()
            txt_list = txt.splitlines()

        if loc == '서울':
            customer_whisper_standard_dict[case_num][sample_name]= txt_list
        elif loc == '영남':
            customer_whisper_east_dict[case_num][sample_name]= txt_list
        elif loc == '호남':
            customer_whisper_west_dict[case_num][sample_name]= txt_list

    customer_whisper_standard_dict = dict(sorted(customer_whisper_standard_dict.items()))
    customer_whisper_east_dict = dict(sorted(customer_whisper_east_dict.items()))
    customer_whisper_west_dict = dict(sorted(customer_whisper_west_dict.items()))

    agent_whisper_result_dict=defaultdict(dict)
    for t in agent_whisper_result_list:
        case_num = int(t.split("/")[4])
        sample_name = t.split("/")[-1].split(".txt")[0]
        
        with open(t, 'r') as f:
            txt = f.read()
            txt_list = txt.splitlines()
            
        agent_whisper_result_dict[case_num][sample_name]= txt_list
    agent_whisper_result_dict = dict(sorted(agent_whisper_result_dict.items()))


    customer_standard_df_list = glob("../data/script/customer_standard/*.xlsx")
    customer_east_df_list = glob("../data/script/customer_southeastern/*.xlsx")
    customer_west_df_list = glob("../data/script/customer_southwestern/*.xlsx")
    agent_df_list = glob("../data/script/agent_standard/*.xlsx")

    customer_standard_ground_truth_dict = {}
    for f in customer_standard_df_list:
        gt_dict = get_text_dict(f, turn='시민')

        for k, v in gt_dict.items():
            customer_standard_ground_truth_dict[k]=v
    customer_standard_ground_truth_dict = dict(sorted(customer_standard_ground_truth_dict.items(), key=lambda x: x[0]))

    customer_east_ground_truth_dict = {}
    for f in customer_east_df_list:
        gt_dict = get_text_dict(f, turn='시민')

        for k, v in gt_dict.items():
            customer_east_ground_truth_dict[k]=v
    customer_east_ground_truth_dict = dict(sorted(customer_east_ground_truth_dict.items(), key=lambda x: x[0]))

    customer_west_ground_truth_dict = {}
    for f in customer_west_df_list:
        gt_dict = get_text_dict(f, turn='시민')

        for k, v in gt_dict.items():
            customer_west_ground_truth_dict[k]=v
    customer_west_ground_truth_dict = dict(sorted(customer_west_ground_truth_dict.items(), key=lambda x: x[0]))

    agent_ground_truth_dict = {}
    for f in agent_df_list:
        gt_dict = get_text_dict(f, turn='상담사')

        for k, v in gt_dict.items():
            agent_ground_truth_dict[k]=v
    agent_ground_truth_dict = dict(sorted(agent_ground_truth_dict.items(), key=lambda x: x[0]))

    customer_whisper_standard_stt_df = get_wer_cer_scores(customer_whisper_standard_dict, customer_standard_ground_truth_dict)
    customer_whisper_east_stt_df = get_wer_cer_scores(customer_whisper_east_dict, customer_east_ground_truth_dict)
    customer_whisper_west_stt_df = get_wer_cer_scores(customer_whisper_west_dict, customer_west_ground_truth_dict)

    agent_whisper_stt_df = get_wer_cer_scores(agent_whisper_result_dict, agent_ground_truth_dict)

    customer_whisper_standard_stt_df.to_csv("../results/stt_results/customer_whisper_stt_eval_result_standard.csv", encoding='euc-kr', index=False)
    customer_whisper_standard_stt_df = pd.read_csv("../results/stt_results/customer_whisper_stt_eval_result_standard.csv", encoding='euc-kr')
    customer_whisper_standard_stt_df.to_excel("../results/stt_results/customer_whisper_stt_eval_result_standard.xlsx", index=False)

    customer_whisper_east_stt_df.to_csv("../results/stt_results/customer_whisper_stt_eval_result_east.csv", encoding='euc-kr', index=False)
    customer_whisper_east_stt_df = pd.read_csv("../results/stt_results/customer_whisper_stt_eval_result_east.csv", encoding='euc-kr')
    customer_whisper_east_stt_df.to_excel("../results/stt_results/customer_whisper_stt_eval_result_east.xlsx", index=False)

    customer_whisper_west_stt_df.to_csv("../results/stt_results/customer_whisper_stt_eval_result_west.csv", encoding='euc-kr', index=False)
    customer_whisper_west_stt_df = pd.read_csv("../results/stt_results/customer_whisper_stt_eval_result_west.csv", encoding='euc-kr')
    customer_whisper_west_stt_df.to_excel("../results/stt_results/customer_whisper_stt_eval_result_west.xlsx", index=False)

    agent_whisper_stt_df.to_csv("../results/stt_results/agent_whisper_stt_eval_result.csv", encoding='euc-kr', index=False)
    agent_whisper_stt_df = pd.read_csv("../results/stt_results/agent_whisper_stt_eval_result.csv", encoding='euc-kr')
    agent_whisper_stt_df.to_excel("../results/stt_results/agent_whisper_stt_eval_result.xlsx", index=False)

if __name__ == '__main__':
    main()