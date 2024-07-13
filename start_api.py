from fastapi import FastAPI
from api.insert_thread import InsertThread

app = FastAPI()


#------------------------------------ENDPOINTS------------------------------------
insert_thread = InsertThread()
insert_thread.create_endpoint(app)
#------------------------------------ENDPOINTS------------------------------------


@app.get("/")
async def root():
    return {"Message":"Online"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host = "127.0.0.1",port=8000)