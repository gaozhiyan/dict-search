from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import scraper
import os
import sys
import re

app = FastAPI()

@app.get("/test")
@app.get("/api/test")
@app.get("/.netlify/functions/api/test")
async def test_route():
    return {"message": "Hello from FastAPI!"}


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

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(path_name: str):
    return {"message": f"Caught path: {path_name}"}

