# FoMo4AICC
This repository contains the code for the paper "Exploring the Potential of Foundation Models as Reliable AI Contact Centers".

## Dataset
### Audio data
Please refer this repository for download the audio data: https://drive.google.com/drive/folders/15HPIDhIwHi6-eEz3yK5DkFeBviAnZy2m?usp=drive_link
### Script data
```
./data/script
```
There are scripts for customers in regional dialects and separate scripts for agents. Each script is organized by topic.

## Run FOMO4AICC
### Speech to Text
```
cd run_aiagent
python run_stt.py --mode stt --name large-v3 --stt_all --lang_ko --w_wt --show
```

### Response generation
```
cd run_aiagent
python run_llm.py --title "title" --case 0 --API_ENGINE gpt-4-1106-preview --accent standard --gender female --age over50
```

``title`` is one of the following topic titles:
> 문화체육관광_한강공원시민행사_눈썰매장스케이트장 \
> 문화체육관광_한강시민공원행사_한강공원수영장 \
> 문화체육관광_청계천행사_서울빛초롱(서울라이트) \
> 서비스와생활_일반보건 \
> 자연과환경_청소재활용_폐기물(대형,소형등) \
> 자연과환경_쓰레기(생활,재활용쓰레기) \
> 세금과재정_재산세 \
> 개인과가정_여권 \
> 상하수도_이사정산자동이체 \
> 경제산업_재래시장_한강달빛야시장(밤도깨비야시장) \
> 도시환경_공원안내_서울페스타 \
> 교통_불법주정차 \
> (추가)발화의도파악을위한추가작성본

``case`` is the case number of the script.

## Evaluation
### Evaluation of transripted text
```
cd eval_aiagent
python eval_stt.py
```

### Automatic hierarchical evaluation metric
#### Stage 1
```
cd eval_aiagent
python eval_response.py --API_ENGINE gpt-4-0125-preview --ai_agent gpt --stage dialog --lang eng
```
#### Stage 2
```
cd eval_aiagent
python eval_response.py --API_ENGINE gpt-4-0125-preview --ai_agent gpt --stage fact --lang eng
```

