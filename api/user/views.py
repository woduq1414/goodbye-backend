from fastapi import APIRouter, FastAPI, Depends, Request
from sqlalchemy.orm import Session



from datetime import datetime, timedelta

from scheduler import scheduler

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


# @router.get("/")
# async def get_reservation_list(db: Session = Depends(get_db)):
#     now = datetime.now()
#     return now
#
#
# @router.post("/")
# async def make_reservation(payload: Request, db: Session = Depends(get_db)):
#     payload = await payload.json()
#     print(payload)
#
#     reservation_row = Reservation(
#         departure=payload["departure"],
#         departure_time=payload["departure_time"],
#         arrival_time=payload["arrival_time"],
#         shuttle_date=datetime(int(payload["shuttle_date"][:4]), int(payload["shuttle_date"][4:6]),
#                               int(payload["shuttle_date"][6:8])),
#         add_datetime=datetime.now()
#     )
#     db.add(reservation_row)
#     db.commit()
#
#     init_schedule()
#
#     return "success"


# @router.delete("/")
# async def delete_reservation(seq: int, db: Session = Depends(get_db)):
#     print(seq)
#     target_row = db.query(Reservation).filter(Reservation.seq == seq).first()
#
#     sched_id = get_schedule_id(target_row)
#     try:
#         scheduler.remove_job(sched_id)
#     except:
#         pass
#     db.delete(target_row)
#     db.commit()
#
#     return "success"
