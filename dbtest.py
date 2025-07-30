from dotenv import load_dotenv
import os
from db.pipeline_crud import PipelineCRUD
from constants.configs.configs import PipelineConfig

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def main():
    crud = PipelineCRUD(DATABASE_URL)

    # 1. 파이프라인 실행 생성
    pipeline_id = "pipeline1"
    execution = crud.create_pipeline_execution(pipeline_id, PipelineConfig)
    print(f"Created PipelineExecution: {execution.pipeline_id}, status: {execution.status}")

    # 2. 파이프라인 실행 조회
    exec_fetched = crud.get_pipeline_execution(pipeline_id)
    print(f"Fetched PipelineExecution status: {exec_fetched.status}")

    # 3. 파이프라인 실행 업데이트
    crud.update_pipeline_execution(pipeline_id, status="COMPLETED", total_time=12.34, error_message=None)
    updated_exec = crud.get_pipeline_execution(pipeline_id)
    print(f"Updated PipelineExecution: status={updated_exec.status}, total_processing_time={updated_exec.total_processing_time}")

if __name__ == "__main__":
    main()