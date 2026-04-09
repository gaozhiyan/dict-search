from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import scraper
import os
import sys
import re

app = FastAPI()

base_path = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_path, "static")

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open(os.path.join(static_dir, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/upload")
@app.post("/.netlify/functions/api/upload")
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are allowed")
    
    content = await file.read()
    text = content.decode("utf-8")
    
    # Extract words (simple splitting by whitespace)
    words = re.findall(r'\b[a-zA-Z-]+\b', text)
    
    # Remove duplicates and keep order
    seen = set()
    unique_words = []
    for w in words:
        w_lower = w.lower()
        if w_lower not in seen:
            seen.add(w_lower)
            unique_words.append(w_lower)
            
    # Process words sequentially to avoid overwhelming the server
    results = []
    for word in unique_words:
        info = scraper.get_word_info(word)
        results.append(info)
        
    return {"results": results}

