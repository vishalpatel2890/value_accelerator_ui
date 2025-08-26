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

from routers import td_mcp, github, deployment

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
    """Log ALL HTTP requests with detailed timing and error capture"""
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    # Log ALL requests, not just /api/
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"[{request_id}] {request.method} {request.url.path} from {client_host}")
    
    # Note: We can't safely read request body in middleware without consuming it
    # The request body will be logged in the endpoint functions instead

    # Process the request and capture any errors
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"[{request_id}] Unhandled exception during request processing: {e}")
        logger.error(f"[{request_id}] Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"[{request_id}] Traceback: {traceback.format_exc()}")
        raise
    
    process_time = time.time() - start_time

    # Log ALL responses with detailed status information
    status_level = "ERROR" if response.status_code >= 400 else "INFO"
    log_func = logger.error if response.status_code >= 400 else logger.info
    
    log_func(f"[{request_id}] {response.status_code} {request.method} {request.url.path} completed in {process_time:.3f}s")
    
    # For error responses, try to log the response body
    if response.status_code >= 400:
        try:
            # This is tricky because response body can only be read once
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            # Try to decode and log error response
            try:
                error_content = json.loads(response_body.decode())
                logger.error(f"[{request_id}] Error response: {error_content}")
            except:
                logger.error(f"[{request_id}] Error response (raw): {response_body.decode()[:500]}")
            
            # Recreate the response since we consumed the body
            from fastapi.responses import Response
            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        except Exception as e:
            logger.error(f"[{request_id}] Could not log error response body: {e}")

    return response

app.include_router(td_mcp.router, prefix="/api/td", tags=["TD MCP"])
app.include_router(github.router, prefix="/api/github", tags=["GitHub"])
app.include_router(deployment.router, prefix="/api/deploy", tags=["Deployment"])

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
