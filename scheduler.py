from apscheduler.schedulers.background import BackgroundScheduler
from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite
from datetime import date
from fastapi_scheduler import SchedulerAdmin


site = AdminSite(settings=Settings(database_url_async='sqlite+aiosqlite:///amisadmin.db'))

# # Custom timed task scheduler
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.jobstores.redis import RedisJobStore
# # Use `RedisJobStore` to create a job store
# scheduler = AsyncIOScheduler(jobstores={'default':RedisJobStore(db=2,host="127.0.0.1",port=6379,password="test")})
# scheduler = SchedulerAdmin.bind(site,scheduler=scheduler)

# Create an instance of the scheduled task scheduler `SchedulerAdmin`
scheduler = SchedulerAdmin.bind(site, scheduler=BackgroundScheduler(timezone="Asia/Seoul"))