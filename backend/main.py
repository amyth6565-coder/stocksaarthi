from dotenv import load_dotenv
load_dotenv(override=False)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from collections import defaultdict
import time
import logging
from routers import stock, chat, ipo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="StockSaarthi API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RATE_LIMITS = {
    "default": {"requests": 30, "window": 60},
    "ai": {"requests": 5, "window": 60},
}
AI_PATHS = ["/api/chat", "/api/ipo/verdict", "/api/analyse"]
_request_log = defaultdict(lambda: defaultdict(list))

def _is_rate_limited(ip, path):
    now = time.time()
    path_type = "ai" if any(path.startswith(p) for p in AI_PATHS) else "default"
    limit = RATE_LIMITS[path_type]
    window = limit["window"]
    max_requests = limit["requests"]
    _request_log[ip][path_type] = [t for t in _request_log[ip][path_type] if now - t < window]
    count = len(_request_log[ip][path_type])
    if count >= max_requests:
        oldest = _request_log[ip][path_type][0]
        return True, int(window - (now - oldest)) + 1
    _request_log[ip][path_type].append(now)
    return False, 0

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    ip = request.headers.get("X-Forwarded-For", request.client.host).split(",")[0].strip()
    path = request.url.path
    if path in ["/", "/docs", "/openapi.json", "/health"]:
        return await call_next(request)
    is_limited, retry_after = _is_rate_limited(ip, path)
    if is_limited:
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded.", "retry_after_seconds": retry_after},
            headers={"Retry-After": str(retry_after)},
        )
    return await call_next(request)

@app.get("/health")
def health():
    return {"status": "ok", "service": "StockSaarthi API v2"}

app.include_router(stock.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(ipo.router)
