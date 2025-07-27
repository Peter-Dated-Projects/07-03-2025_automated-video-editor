"""
main.py

The backend fastapi backend server


"""


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from dotenv import load_dotenv
import os


# Load environment variables
load_dotenv()
root_dir = Path(__file__).resolve().parent.parent
os.chdir(root_dir)
print("Working in directory:", os.getcwd())

# -------------------------------------------------- #
# Initialize FastAPI app

app = FastAPI()

# CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Serve static files from the 'assets' directory
app.mount("/static", StaticFiles(directory="assets"), name="static")


# ------------------------------------------------------ #
# Basic Web Routes

@app.get("/hello_world")
async def hello_world():
    return {"message": "Hello, World!", "status": "success"}


# ------------------------------------------------------ #
# Include other routers or endpoints here



# ------------------------------------------------------- #
# Run the app with: uvicorn backend.main:app --reload
# This will start the FastAPI server with live reloading enabled
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=os.environ.get("BACKEND_SERVER_HOST"), 
        port=int(os.environ.get("BACKEND_SERVER_PORT")), 
        log_level="info",
    )