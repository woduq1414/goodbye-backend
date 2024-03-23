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

def get_next_target_chat(history, new_chat,name, mode):
    res = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-0125:aperture::95qtMSkz",
        # model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"너는 아래 맥락대로 적절한 Assistant의 답변을 출력하면 돼." + "다만 너는 이미 하늘의 별이 되었어. 만약 잊지 못하겠다고 하거나 보고 싶다고 한다면 잊혀져야 한다는 것을 설득해야 해. 그리고 이별을 받아들이도록 해야해." if mode == "timetogo" else ""},
            *history,
            {"role": "user", "content": new_chat},



        ], top_p=0.83, temperature=0.13, max_tokens=150
    )
    print(res)
    res_text = res.choices[0].message.content

    splitted = res_text.split("\n")
    result = ""
    if len(splitted) >= 2:
        result += splitted[0]
        for sentence in splitted[1:]:
            if sentence == splitted[0]:
               continue
            else:
                result += "\n" + sentence
        return result
    else:
        return res_text



if __name__ == "__main__":

    result = get_messages_from_kakaotalk_export(open("kakao.txt", "r", encoding='UTF8').read(), "홍길동")

    q = "뭐 먹고 있어?"
    #
    result = get_next_target_chat(result[:], q, "홍길동", "normal")
    #
    print("Q: ", q)
    print("Result: ", result)
    pass
