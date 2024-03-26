from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse
import PIL.Image as Image
import io
from img2multion import img2text, to_multion

app = FastAPI()

# Mount the static directory to be served at '/static'
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...), input_text: str = Form(...)):

    try:
        image_bytes = await file.read()
        
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')

        caption, ocr_text = img2text(image)
        to_multion(caption=caption, input_text=input_text, ocr_text=ocr_text)

        # sanity check- return size of image
        width, height = image.size
        return JSONResponse(content={"filename": file.filename, "width": width, "height": height, "response": "On it! Should be done shortly :)"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})