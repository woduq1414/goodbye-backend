from datetime import timedelta, datetime

from db import SessionLocal

import json

import requests
from urllib import parse

from bs4 import BeautifulSoup  # parser

from jsbn import RSAKey
from openai import OpenAI, BadRequestError


from scheduler import scheduler
import re

from config import OPEN_AI_KEY
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_messages_from_kakaotalk_export(export_data, target_name):
    my_katalk_data = list()
    katalk_msg_pattern = "[0-9]{4}[년.] [0-9]{1,2}[월.] [0-9]{1,2}[일.] 오\S [0-9]{1,2}:[0-9]{1,2},.*:"
    date_info = "[0-9]{4}년 [0-9]{1,2}월 [0-9]{1,2}일 \S요일"
    in_out_info = "[0-9]{4}[년.] [0-9]{1,2}[월.] [0-9]{1,2}[일.] 오\S [0-9]{1,2}:[0-9]{1,2}:.*"

    for line in export_data.split("\n"):
        if re.match(date_info, line) or re.match(in_out_info, line):
            continue
        elif line == '\n':
            continue
        elif ',' not in line:
            continue
        elif re.match(katalk_msg_pattern, line):
            line = line.split(",")
            date_time = line[0]
            user_text = line[1].split(" : ", maxsplit=1)
            user_name = user_text[0].strip()
            text = user_text[1].strip()

            if text != "이모티콘":
                # my_katalk_data.append({'date_time': date_time,
                #                        'user_name': user_name,
                #                        'text': text
                #                        })
                # my_katalk_data.append(f"{'상대' if user_name == target_name else '나'} : {text}")
                if user_name == target_name:
                    if len(my_katalk_data) == 0 or my_katalk_data[-1]['role'] == "user":
                        my_katalk_data.append({"role": "assistant", "content": f"{text}"})
                    else:
                        my_katalk_data[-1]['content'] += "\n" + text
                else:
                    if len(my_katalk_data) == 0 or my_katalk_data[-1]['role'] == "assistant":
                        my_katalk_data.append({"role": "user", "content": f"{text}"})
                    else:
                        my_katalk_data[-1]['content'] += "\n" + text
        else:
            if len(my_katalk_data) > 0:
                my_katalk_data[-1]['text'] += "\n" + line.strip()





    return my_katalk_data


client = OpenAI(api_key=OPEN_AI_KEY)


def summarize_text(text):

    summ_res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "아래 글을 한 문단으로 요약해줘. \n\n" + text},
        ]
    )

    summed_text = summ_res.choices[0].message.content
    return summed_text

def get_next_target_chat(history, new_chat):
    res = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-0125:aperture::95qtMSkz",
        messages=[
            {"role": "system", "content": "말투를 흉내내서 대화를 이어나가"},
            *history,
            {"role": "user", "content": new_chat}
        ], top_p=0.9, temperature=0.1, max_tokens=45
    )
    print(res)
    res_text = res.choices[0].message.content
    return res_text



if __name__ == "__main__":

    result = get_messages_from_kakaotalk_export(open("kakao.txt", "r", encoding='UTF8').read(), "강우진")
    print(result[-100:])


    q = "코딩 어떻게 배워?"
    #
    result = mimic_target_chat(result[-100:], q)
    #
    print("Q: ", q)
    print("Result: ", result)
    pass
