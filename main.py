"""
FastAPI Analysis Boilerplate
============================

A production-ready FastAPI boilerplate for building text analysis and processing APIs.
Includes authentication, WebSocket support, file handling, and comprehensive error handling.

Features:
- RESTful API endpoints
- WebSocket real-time communication
- File upload and processing
- Authentication and session management
- Database integration ready
- Comprehensive error handling
- API documentation with OpenAPI/Swagger
- Rate limiting and security
- Monitoring and logging

Author: LexiQ Team
License: MIT
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

from .models import (
    AnalysisRequest, AnalysisResponse, AnalyzedTerm, AnalysisStatistics,
    UserSession, ProjectData, ConfigurationData, FeedbackData,
    APIResponse, ErrorResponse
)
from .services import (
    AnalysisService, FileProcessingService, SessionManager,
    ConfigurationService, DatabaseService
)
from .auth import AuthService, get_current_user
from .websocket import ConnectionManager
from .utils import setup_logging, create_response, handle_errors
from .config import get_settings

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Get application settings
settings = get_settings()

# Global services
analysis_service = AnalysisService()
file_service = FileProcessingService()
session_manager = SessionManager()
config_service = ConfigurationService()
auth_service = AuthService()
connection_manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting FastAPI Analysis Application")
    await analysis_service.initialize()
    await file_service.initialize()
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI Analysis Application")
    await analysis_service.cleanup()
    await file_service.cleanup()

# Create FastAPI application
app = FastAPI(
    title="Analysis API",
    description="A comprehensive API for text analysis and processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security
security = HTTPBearer()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Static files (for serving frontend if needed)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "analysis": await analysis_service.health_check(),
            "file_processing": await file_service.health_check(),
            "database": await DatabaseService.health_check()
        }
    }

# Authentication endpoints
@app.post("/auth/login", response_model=APIResponse, tags=["Authentication"])
async def login(credentials: dict):
    """User login endpoint"""
    try:
        token = await auth_service.authenticate(
            credentials.get("username"),
            credentials.get("password")
        )
        
        if token:
            return create_response(
                success=True,
                data={"token": token, "expires_in": 3600},
                message="Login successful"
            )
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
    except Exception as e:
        return handle_errors(e, "Login failed")

@app.post("/auth/logout", tags=["Authentication"])
async def logout(current_user: dict = Depends(get_current_user)):
    """User logout endpoint"""
    try:
        await auth_service.revoke_token(current_user.get("token"))
        return create_response(success=True, message="Logout successful")
    except Exception as e:
        return handle_errors(e, "Logout failed")

# Analysis endpoints
@app.post("/api/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_text(
    request: AnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze text content with comprehensive linguistic analysis
    
    This endpoint processes text content and returns detailed analysis including:
    - Term classification and scoring
    - Statistical metrics
    - Quality assessment
    - Suggestions for improvement
    """
    try:
        # Validate request
        if not request.content or len(request.content.strip()) == 0:
            raise HTTPException(status_code=400, detail="Content cannot be empty")
        
        # Perform analysis
        result = await analysis_service.analyze_text(
            content=request.content,
            language=request.language,
            domain=request.domain,
            options=request.options
        )
        
        # Log analysis for monitoring
        logger.info(f"Analysis completed for user {current_user.get('user_id')}: "
                   f"{len(result.terms)} terms analyzed")
        
        return result
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        return handle_errors(e, "Analysis failed")

@app.post("/api/analyze/batch", response_model=List[AnalysisResponse], tags=["Analysis"])
async def analyze_batch(
    requests: List[AnalysisRequest],
    current_user: dict = Depends(get_current_user)
):
    """Batch analysis of multiple text contents"""
    try:
        if len(requests) > settings.MAX_BATCH_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"Batch size cannot exceed {settings.MAX_BATCH_SIZE}"
            )
        
        results = []
        for request in requests:
            result = await analysis_service.analyze_text(
                content=request.content,
                language=request.language,
                domain=request.domain,
                options=request.options
            )
            results.append(result)
        
        return results
        
    except Exception as e:
        return handle_errors(e, "Batch analysis failed")

@app.get("/api/analyze/status/{request_id}", tags=["Analysis"])
async def get_analysis_status(
    request_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the status of a long-running analysis request"""
    try:
        status = await analysis_service.get_analysis_status(request_id)
        return create_response(success=True, data=status)
    except Exception as e:
        return handle_errors(e, "Failed to get analysis status")

# File processing endpoints
@app.post("/api/files/upload", tags=["Files"])
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = "document",
    current_user: dict = Depends(get_current_user)
):
    """Upload and process a file"""
    try:
        # Validate file
        if file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Process file
        result = await file_service.process_file(
            file=file,
            file_type=file_type,
            user_id=current_user.get("user_id")
        )
        
        return create_response(
            success=True,
            data=result,
            message="File uploaded and processed successfully"
        )
        
    except Exception as e:
        return handle_errors(e, "File upload failed")

@app.get("/api/files/{file_id}", tags=["Files"])
async def get_file(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get file information and content"""
    try:
        file_data = await file_service.get_file(file_id, current_user.get("user_id"))
        return create_response(success=True, data=file_data)
    except Exception as e:
        return handle_errors(e, "Failed to retrieve file")

@app.delete("/api/files/{file_id}", tags=["Files"])
async def delete_file(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a file"""
    try:
        await file_service.delete_file(file_id, current_user.get("user_id"))
        return create_response(success=True, message="File deleted successfully")
    except Exception as e:
        return handle_errors(e, "Failed to delete file")

# Project management endpoints
@app.post("/api/projects", tags=["Projects"])
async def create_project(
    project_data: ProjectData,
    current_user: dict = Depends(get_current_user)
):
    """Create a new project"""
    try:
        project = await session_manager.create_project(
            user_id=current_user.get("user_id"),
            project_data=project_data
        )
        return create_response(
            success=True,
            data=project,
            message="Project created successfully"
        )
    except Exception as e:
        return handle_errors(e, "Failed to create project")

@app.get("/api/projects", tags=["Projects"])
async def get_projects(
    current_user: dict = Depends(get_current_user)
):
    """Get user's projects"""
    try:
        projects = await session_manager.get_user_projects(current_user.get("user_id"))
        return create_response(success=True, data=projects)
    except Exception as e:
        return handle_errors(e, "Failed to retrieve projects")

@app.get("/api/projects/{project_id}", tags=["Projects"])
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific project details"""
    try:
        project = await session_manager.get_project(project_id, current_user.get("user_id"))
        return create_response(success=True, data=project)
    except Exception as e:
        return handle_errors(e, "Failed to retrieve project")

# Statistics and reporting endpoints
@app.get("/api/statistics", tags=["Statistics"])
async def get_statistics(
    current_user: dict = Depends(get_current_user)
):
    """Get analysis statistics"""
    try:
        stats = await analysis_service.get_user_statistics(current_user.get("user_id"))
        return create_response(success=True, data=stats)
    except Exception as e:
        return handle_errors(e, "Failed to retrieve statistics")

@app.post("/api/reports/generate", tags=["Reports"])
async def generate_report(
    report_config: dict,
    current_user: dict = Depends(get_current_user)
):
    """Generate a custom report"""
    try:
        report = await analysis_service.generate_report(
            user_id=current_user.get("user_id"),
            config=report_config
        )
        return create_response(
            success=True,
            data=report,
            message="Report generated successfully"
        )
    except Exception as e:
        return handle_errors(e, "Failed to generate report")

# Configuration endpoints
@app.get("/api/config", tags=["Configuration"])
async def get_configuration(
    current_user: dict = Depends(get_current_user)
):
    """Get user configuration"""
    try:
        config = await config_service.get_user_config(current_user.get("user_id"))
        return create_response(success=True, data=config)
    except Exception as e:
        return handle_errors(e, "Failed to retrieve configuration")

@app.put("/api/config", tags=["Configuration"])
async def update_configuration(
    config_data: ConfigurationData,
    current_user: dict = Depends(get_current_user)
):
    """Update user configuration"""
    try:
        updated_config = await config_service.update_user_config(
            user_id=current_user.get("user_id"),
            config_data=config_data
        )
        return create_response(
            success=True,
            data=updated_config,
            message="Configuration updated successfully"
        )
    except Exception as e:
        return handle_errors(e, "Failed to update configuration")

# Feedback endpoints
@app.post("/api/feedback", tags=["Feedback"])
async def submit_feedback(
    feedback: FeedbackData,
    current_user: dict = Depends(get_current_user)
):
    """Submit user feedback"""
    try:
        result = await analysis_service.submit_feedback(
            user_id=current_user.get("user_id"),
            feedback=feedback
        )
        return create_response(
            success=True,
            data=result,
            message="Feedback submitted successfully"
        )
    except Exception as e:
        return handle_errors(e, "Failed to submit feedback")

# WebSocket endpoint for real-time analysis
@app.websocket("/ws/analysis")
async def websocket_analysis(websocket: WebSocket):
    """WebSocket endpoint for real-time analysis"""
    await connection_manager.connect(websocket)
    try:
        while True:
            # Receive data from client
            data = await websocket.receive_text()
            request_data = json.loads(data)
            
            # Perform real-time analysis
            result = await analysis_service.analyze_text_realtime(
                content=request_data.get("content", ""),
                language=request_data.get("language", "en"),
                domain=request_data.get("domain", "general")
            )
            
            # Send result back to client
            await connection_manager.send_personal_message(
                json.dumps(result, default=str),
                websocket
            )
            
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await connection_manager.send_personal_message(
            json.dumps({"error": str(e)}),
            websocket
        )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
