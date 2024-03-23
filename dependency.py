from datetime import timedelta, datetime

from db import SessionLocal

import json

import requests
from urllib import parse

from bs4 import BeautifulSoup  # parser

from jsbn import RSAKey


from scheduler import scheduler
import re


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

            if user_name == target_name:
                # my_katalk_data.append({'date_time': date_time,
                #                        'user_name': user_name,
                #                        'text': text
                #                        })
                my_katalk_data.append(text)

        else:
            if len(my_katalk_data) > 0:
                my_katalk_data[-1]['text'] += "\n" + line.strip()


    return my_katalk_data





if __name__ == "__main__":

    result = get_messages_from_kakaotalk_export(open("kakao.txt", "r", encoding='UTF8').read(), "조영민")
    print(result)
    pass
