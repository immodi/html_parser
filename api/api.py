import sys
from pathlib import Path
from typing import List

lib_dir = Path("../").__str__()
sys.path.insert(0, str(lib_dir))

from fastapi import FastAPI, Form, File, UploadFile, Request
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    FileResponse,
    StreamingResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from lib.htm_parser import parser, data_object_maker
import json

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class Novel(BaseModel):
    title: str
    author: str
    summary: str
    jsonFile: str  # This will hold the filename


class NovelJson(BaseModel):
    titles: List[str]
    content: List[List[str]]


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/spinner", response_class=HTMLResponse)
async def get_spinner():
    html_content = """
        <div class="spinner-container">
            <span class="loader"></span>
        </div>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/")
async def handle_form(
    title: str = Form(...),
    author: str = Form(...),
    summary: str = Form(...),
    jsonFile: UploadFile = File(...),
):
    # Process the form data
    try:
        content = {
            "title": title,
            "author": author,
            "summary": summary,
            "json_file": jsonFile.filename,
        }

        # Read the JSON file content asynchronously
        json_content = await jsonFile.read()

        # Load JSON from the content
        json_object = json.loads(json_content)

        # Assuming data_object_maker is a synchronous function, you can call it directly
        data = data_object_maker(
            content["title"],
            content["author"],
            content["summary"],
            json_object.get("titles"),
            json_object.get("content"),
        )

        # Assuming parser is also a synchronous function
        parser(data, "file")

        filename = "file.html"
        response = StreamingResponse(
            open(filename, "rb"), media_type="application/octet-stream"
        )

        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response

    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)}, status_code=400
        )
