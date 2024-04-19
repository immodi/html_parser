import sys
from pathlib import Path
lib_dir = Path("../").__str__()
sys.path.insert(0, str(lib_dir))

from fastapi import FastAPI
from pydantic import BaseModel
from lib.htm_parser import parser, data_object_maker
import json

app = FastAPI()
class Novel(BaseModel):
    title: str
    author: str
    summary: str
    jsonBinary: str

@app.get("/")
async def root():
    print(parser)
    return {"message": "Hello World"}

@app.post("/upload-json/")
async def compile_pdf(novel_data: Novel):
    with open("s.json", "wb") as file_r:
        file_r.write(novel_data.jsonBinary.encode())
    
    with open('s.json', 'r') as openfile:
        json_object = json.load(openfile)

    data = data_object_maker(novel_data.title, novel_data.author, novel_data.summary, json_object.get("titles"), json_object.get("content"))
    parser(data, 'testing')
    return {"status": True}


