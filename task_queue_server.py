from fastapi import FastAPI
import redis
import uuid
from pydantic import BaseModel

app = FastAPI()
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

class TaskRequest(BaseModel):
    pipelineId: str
    ocrResult: str

@app.post("/enque")
def enque_first_step(request: TaskRequest):
    step_id = str(uuid.uuid4())

    task_key = f"task:{step_id}"
    r.hset(task_key, mapping={
        "pipelineId": request.pipelineId,
        "stepId": step_id,
        "status": "queued",
        "order": 1,
        "payload": request.ocrResult
    })

    # 3. 작업 큐에 step_id 넣기 (예: Redis list 사용)
    r.lpush("task_queue", step_id)

    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$ response 구조체 도입 필요 $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    return {
        "message": "Task enqueued successfully",
        "stepId": step_id
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)