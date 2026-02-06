from fastapi import APIRouter
from datetime import datetime
from zoneinfo import ZoneInfo # for timezone awareness

router = APIRouter()

@router.get("/healthz")
def health_check():
    eastern_time = datetime.now(ZoneInfo("America/New_York"))
    
    formatted_time = eastern_time.strftime("%Y-%m-%d %I:%M:%S %p %Z")
    
    return {
        "status": "ok",
        "service": "stock-watch-api",
        "timestamp": formatted_time,
        "timezone": "America/New_York"
    }