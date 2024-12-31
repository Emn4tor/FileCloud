from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import FileResponse, StreamingResponse
from pathlib import Path
import os
import shutil
import uvicorn
from fastapi.middleware.cors import CORSMiddleware




# Initialize
app = FastAPI()

# Root dir
drive_root = Path("W:/")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to your frontend's origin
    allow_methods=["*"],
    allow_headers=["*"],
)

if not drive_root.exists():
    raise RuntimeError(f"Drive {drive_root} does not exist.")


# Helper
def list_directory(path: Path):
    if not path.exists():
        raise HTTPException(status_code=404, detail="Path not found")

    if not path.is_dir():
        raise HTTPException(status_code=400, detail="Not a directory")

    contents = []
    for item in path.iterdir():
        contents.append({
            "name": item.name,
            "is_dir": item.is_dir(),
            "path": str(item.relative_to(drive_root))
        })
    return contents


@app.get("/files")
def get_files(path: str = ""):
    """Fetch contents of dir."""
    target_path = drive_root / path
    return list_directory(target_path)


@app.get("/file/{file_path:path}")
def get_file(file_path: str):
    """Stream or download file."""
    target_file = drive_root / file_path
    if not target_file.exists() or not target_file.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(target_file, media_type="application/octet-stream", filename=target_file.name)


@app.post("/file/upload")
def upload_file(file: UploadFile, target_dir: str = Form("")):
    """Upload"""
    target_path = drive_root / target_dir / file.filename

    if not target_path.parent.exists():
        raise HTTPException(status_code=400, detail="Target directory does not exist")

    with target_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": "File uploaded successfully", "path": str(target_path.relative_to(drive_root))}


@app.delete("/file/{file_path:path}")
def delete_file(file_path: str):
    """Delete"""
    target_path = drive_root / file_path

    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Path not found")

    if target_path.is_dir():
        shutil.rmtree(target_path)
    else:
        target_path.unlink()

    return {"message": "Deleted successfully", "path": file_path}


@app.get("/file/stream/{file_path:path}")
def stream_file(file_path: str):
    """Stream video or audio."""
    target_file = drive_root / file_path
    if not target_file.exists() or not target_file.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    def file_iterator():
        with target_file.open("rb") as f:
            yield from f

    return StreamingResponse(file_iterator(), media_type="application/octet-stream")

if __name__ == "__main__":
    print("Starting FastAPI server on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
