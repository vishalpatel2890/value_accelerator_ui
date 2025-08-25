from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn
import sys
import os
import time
import json

# Add the server directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routers import td_mcp, github, deployment, simple_github

app = FastAPI(
    title="TD Value Accelerator API",
    description="Backend API for TD Value Accelerator deployment tool",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log HTTP requests for debugging"""
    start_time = time.time()
    
    # Log all API requests
    if request.url.path.startswith('/api/'):
        print(f"\n🌐 API REQUEST: {request.method} {request.url.path}")
        if request.method == "POST":
            try:
                body = await request.body()
                if body:
                    json_body = json.loads(body.decode())
                    print(f"   Data: {list(json_body.keys())}")
            except Exception as e:
                print(f"   Could not parse request: {e}")
    
    # Process the request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log API responses
    if request.url.path.startswith('/api/'):
        print(f"✅ API RESPONSE: {response.status_code} ({process_time:.1f}s)")
    
    return response

app.include_router(td_mcp.router, prefix="/api/td", tags=["TD MCP"])
app.include_router(github.router, prefix="/api/github", tags=["GitHub"])
app.include_router(simple_github.router, prefix="/api/simple", tags=["Simple Deploy"])
app.include_router(deployment.router, prefix="/api/deployment", tags=["Deployment"])

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed logging"""
    print(f"=== VALIDATION ERROR ===")
    print(f"Request URL: {request.url}")
    print(f"Request method: {request.method}")
    
    try:
        body = await request.body()
        print(f"Request body: {body.decode()}")
    except:
        print("Could not read request body")
    
    print(f"Validation errors: {exc.errors()}")
    print(f"========================")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": f"Validation error: {exc.errors()}", 
            "errors": exc.errors()
        }
    )

@app.get("/")
async def root():
    return {"message": "TD Value Accelerator API", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)