from fastapi import APIRouter, Depends
from app.application.use_cases import HelloUseCase
from app.infrastructure.dependencies import get_hello_use_case

router = APIRouter()

@router.get("/hello")
def hello(use_case: HelloUseCase = Depends(get_hello_use_case)):
    return {"message": use_case.execute()}
