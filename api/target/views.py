from typing import List

from fastapi import APIRouter, FastAPI, Depends, Request, HTTPException
from pydantic import BaseModel
from sqlalchemy import and_
from sqlalchemy.orm import Session

from models import Target, Diary
from datetime import datetime, timedelta
import json

from dependency import get_db, get_messages_from_kakaotalk_export, get_next_target_chat

from scheduler import scheduler

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


class GetTargetModel(BaseModel):
    seq: int
    targetName: str
    targetLostDate: str
    targetRelation: str


@router.get("/list", response_model=List[GetTargetModel])
async def get_target_list(db: Session = Depends(get_db)):
    """
    유저의 target 리스트를 가져온다.
    """

    # 로그인 구현 이후 사용자 target만 가져오게 수정 필요
    return [{"seq": x.seq, "targetName": x.target_name, "targetLostDate": x.target_lost_date.strftime("%Y%m%d"),
             "targetRelation": x.target_relation} for x in db.query(Target).all()]


class AddTargetModel(BaseModel):
    targetKakaoChat: str
    targetName: str
    targetLostDate: str
    targetRelation: str


class AddTargetModelResponse(BaseModel):
    message: str
    seq: int


@router.post("/", response_model=AddTargetModelResponse)
async def add_target(payload: AddTargetModel, db: Session = Depends(get_db)):
    """
    user의 target을 추가한다.
    """

    print(payload)

    target_kakao_chat = payload.targetKakaoChat
    target_name = payload.targetName
    target_chat_data = json.dumps(get_messages_from_kakaotalk_export(target_kakao_chat, target_name))
    target_lost_date = datetime(int(payload.targetLostDate[:4]), int(payload.targetLostDate[4:6]),
                                int(payload.targetLostDate[6:8]))

    target_relation = payload.targetRelation

    target_row = Target(
        target_name=payload.targetName,
        target_kakao_chat=target_kakao_chat,
        target_lost_date=target_lost_date,
        target_relation=target_relation,
        target_history=target_chat_data,
        target_add_datetime=datetime.now()
    )

    db.add(target_row)
    db.commit()

    return {
        "message": "success",
        "seq": target_row.seq
    }


class AddChatModel(BaseModel):
    seq: int
    dday : int
    chat: str


class AddChatModelResponse(BaseModel):
    message: str
    receivedChat: str


@router.post("/chat", response_model=AddChatModelResponse)
async def add_chat(payload: AddChatModel, db: Session = Depends(get_db)):
    """
    target에 chat을 추가하고 AI에게 chat을 receive받는다
    """

    print(payload)

    target_row = db.query(Target).filter(Target.seq == payload.seq).first()
    target_chat_data = json.loads(target_row.target_history.encode("utf-8"))

    target_chat_data.append({"role": "user", "content": payload.chat})

    mode = "timetogo" if payload.dday >= 15 else "normal"
    received_chat = get_next_target_chat(target_chat_data, payload.chat, target_row.target_name, mode)
    print(received_chat)
    target_chat_data.append({"role": "assistant", "content": received_chat})

    target_row.target_history = json.dumps(target_chat_data)

    # db.commit()

    return {
        "message": "success",
        "receivedChat": received_chat
    }


class AddDiaryModel(BaseModel):
    targetSeq: int
    diaryContent: str


class AddDiaryModelResponse(BaseModel):
    seq: int


@router.post("/diary", response_model=AddDiaryModelResponse)
async def add_diary(payload: AddDiaryModel, db: Session = Depends(get_db)):
    """
        diary를 추가한다.
    """

    print(payload)

    target_row = db.query(Target).filter(Target.seq == payload["targetSeq"]).first()
    target_lost_date = target_row.target_lost_date

    # get dday from targetListDate
    dday = (datetime.now() - target_lost_date).days

    diary_row = Diary(
        target_seq=payload["targetSeq"],
        diary_dday=dday,
        diary_content=payload["diaryContent"],
        diary_add_datetime=datetime.now()
    )

    db.add(diary_row)
    db.commit()

    return {
        "message": "success",
        "seq": diary_row.seq
    }


class GetDiaryListModel(BaseModel):
    targetSeq: int


class GetDiaryListModelResponse(BaseModel):
    seq: int
    targetSeq: int
    diaryDday: int
    diaryContent: str
    diaryAddDatetime: str


@router.get("/diary/list", response_model=List[GetDiaryListModelResponse])
async def get_diary_list(payload: GetDiaryListModel, db: Session = Depends(get_db)):
    """
        target에 대한 diary 리스트를 가져온다.
    """

    return [{"seq": x.seq, "targetSeq": x.target_seq, "diaryDday": x.diary_dday,
             "diaryContent": x.diary_content, "diaryAddDatetime": x.diary_add_datetime.strftime("%Y%m%d")} for x in
            db.query(Diary).filter(Diary.target_seq == payload.targetSeq).all()]


class GetDiaryModel(BaseModel):
    targetSeq: int
    diaryDday: int


class GetDiaryModelResponse(BaseModel):
    seq: int
    targetSeq: int
    diaryDday: int
    diaryContent: str
    diaryAddDatetime: str


@router.get("/diary", response_model=GetDiaryModelResponse)
async def get_diary(payload: GetDiaryModel, db: Session = Depends(get_db)):
    """
        특정 target과 dday에 대한 diary를 가져온다.
    """

    result = db.query(Diary).filter(
        and_(Diary.target_seq == payload.targetSeq, Diary.diary_dday == payload.diaryDday)).first()

    if result is None:
        # 404
        raise HTTPException(status_code=404, detail="Item not found")

    return GetDiaryModelResponse(seq=result.seq, targetSeq=result.target_seq, diaryDday=result.diary_dday,
                                 diaryContent=result.diary_content,
                                 diaryAddDatetime=result.diary_add_datetime.strftime("%Y%m%d"))


class GetGuideModel(BaseModel):
    targetSeq: int
    diaryDday: int

class GetGuideModelResponse(BaseModel):
    guide: str

@router.get("/guide")
async def get_guide(payload: GetGuideModel, db: Session = Depends(get_db)):
    """
    특정 target과 dday에 대한 guide를 제공.
    """


    target_row = db.query(Target).filter(Target.seq == payload.targetSeq).first()
    dday = payload.diaryDday


    return {
        "guide" : "guide"
    }

