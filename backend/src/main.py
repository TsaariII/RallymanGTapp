from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Rallyman GT app API",
    description="API Rallyman GT app",
    version="1.0.0"
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# root for backend in port 3000
@app.get("/")
async def root():
	return {"message": "Backend OK!"}

# health check for the backend
@app.get("/health")
async def health():
	return {"status": "healthy", "service": "meeting-room-api"}


if __name__ == "__main__":
	uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=3000,
        reload=True # Change for deployment 
	)