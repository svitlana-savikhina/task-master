from fastapi import FastAPI

from task_info import routers_ as task_info_router

app = FastAPI()

app.include_router(task_info_router.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
