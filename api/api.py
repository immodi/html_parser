import json
from lib.html_parser import data_object_maker, parser
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    FileResponse,
)
from glob import glob
from fastapi import FastAPI, Form, File, UploadFile, Request, BackgroundTasks
from pathlib import Path
from typing import List
import pdfkit
from os import remove
import asyncio


app = FastAPI()
config = pdfkit.configuration(wkhtmltopdf="./wkhtmltopdf")

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


@app.get("/pdf-form", response_class=HTMLResponse)
async def get_main(request: Request):
    return templates.TemplateResponse("pdf_form.html", {"request": request})


@app.post("/pdf")
async def handle_form(
    background_tasks: BackgroundTasks,
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
        base_filename = f"output/{title}"
        parser(data, base_filename)

        html_filename = f"{base_filename}.html"
        filename = f"{base_filename}.pdf"

        pdfkit.from_file(html_filename, filename, configuration=config)

        response = FileResponse(filename)

        response.headers["Content-Disposition"] = (
            f"attachment; filename={
            filename}"
        )

        background_tasks.add_task(delete_file, base_filename)
        return response

    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)}, status_code=400
        )


def delete_file(file_name: str):
    all_files = glob(f"./{file_name}.*")

    for file in all_files:
        try:
            remove(file)
            print(f"{file} has been deleted.")
        except FileNotFoundError:
            print(f"{file} does not exist.")
        except Exception as e:
            print(e)
