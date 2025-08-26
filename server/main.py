from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn
import sys
import os
import time
import json
import uuid
import builtins

# Add the server directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logging_config import logger

# Route all print statements through the configured logger
builtins.print = lambda *args, **kwargs: logger.info(" ".join(str(a) for a in args))

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
    """Log HTTP requests with timing and client details"""
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    if request.url.path.startswith('/api/'):
        client_host = request.client.host if request.client else "unknown"
        logger.info(f"[{request_id}] {request.method} {request.url.path} from {client_host}")
        if request.method == "POST":
            try:
                body = await request.body()
                if body:
                    json_body = json.loads(body.decode())
                    logger.debug(f"[{request_id}] Body keys: {list(json_body.keys())}")
            except Exception as e:
                logger.warning(f"[{request_id}] Could not parse request body: {e}")

    response = await call_next(request)
    process_time = time.time() - start_time

    if request.url.path.startswith('/api/'):
        logger.info(
            f"[{request_id}] {response.status_code} completed in {process_time:.2f}s"
        )

    return response

app.include_router(td_mcp.router, prefix="/api/td", tags=["TD MCP"])
app.include_router(github.router, prefix="/api/github", tags=["GitHub"])
app.include_router(simple_github.router, prefix="/api/simple", tags=["Simple Deploy"])
app.include_router(deployment.router, prefix="/api/deployment", tags=["Deployment"])

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with structured logging"""
    request_id = str(uuid.uuid4())[:8]
    logger.error(f"[{request_id}] Validation error on {request.method} {request.url}")

    try:
        body = await request.body()
        logger.error(f"[{request_id}] Request body: {body.decode()}")
    except Exception:
        logger.error(f"[{request_id}] Could not read request body")

    logger.error(f"[{request_id}] Errors: {exc.errors()}")

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
