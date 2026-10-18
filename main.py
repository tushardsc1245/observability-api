import time, json, uuid
from collections import deque
from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

EMAIL = "25f1002656@ds.study.iitm.ac.in"   # <-- change this

app = FastAPI()
START = time.time()
LOGS = deque(maxlen=1000)
REQS = Counter("http_requests", "Total HTTP requests")  # exposed as http_requests_total

@app.middleware("http")
async def mw(request: Request, call_next):
    REQS.inc()
    rid = str(uuid.uuid4())
    entry = {"level": "INFO", "ts": time.time(), "path": request.url.path,
             "request_id": rid, "method": request.method}
    LOGS.append(entry)
    print(json.dumps(entry), flush=True)
    resp = await call_next(request)
    resp.headers["X-Request-ID"] = rid
    return resp

@app.get("/work")
def work(n: int = 1):
    s = 0
    for i in range(n):
        s += i
    return {"email": EMAIL, "done": n}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/healthz")
def healthz():
    return {"status": "ok", "uptime_s": float(time.time() - START)}

@app.get("/logs/tail")
def tail(limit: int = 10):
    return list(LOGS)[-limit:] if limit > 0 else []
