from fastapi import FastAPI
from .simulator import generate

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
