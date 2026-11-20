
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .simulator import generate, evolve, snapshot


# FastAPI 서버 생성
app = FastAPI(title="P1 Election Data Server")

# 교육용 가상 개표 데이터 생성
districts = generate()


# 서버 작동 확인
@app.get("/health")
def health():
    return {
        "status": "ok",
        "simulation": True
    }


# 모의 개표 데이터 제공
@app.get("/api/districts")
def get_districts():
    return {
        "simulation": True,
        "district_count": len(districts),
        "districts": districts
    }

# 교육용 모의 개표 WebSocket
@app.websocket("/ws/counting")
async def stream_counting(websocket: WebSocket):
    await websocket.accept()

    seed = 20261111
    step = 0
    live_districts = generate(seed)

    try:
        while True:
            if step > 0:
                evolve(live_districts, seed, step)

            data = snapshot(live_districts, step, seed)

            await websocket.send_json(data)

            step += 1
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        pass
