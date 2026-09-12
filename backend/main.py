from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.upload import router as upload_router
from routes.chat import router as chat_router
from routes.quiz import router as quiz_router 

# 1. DEFINE APP FIRST
app = FastAPI(
    title="AI Student Assistant API",
    description="Backend API for AI Student Assistant",
    version="1.0.0"
)

# 2. ADD MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. ATTACH ROUTERS AFTER APP IS DEFINED
app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(quiz_router) 

@app.get("/")
def root():
    return {"message": "AI Student Assistant API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}