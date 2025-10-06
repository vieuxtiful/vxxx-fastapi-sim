"""
Data Models for FastAPI Analysis Boilerplate
============================================

Pydantic models for request/response validation and data serialization.
These models define the structure of data flowing through the API.

Author: vieuxtiful
License: MIT
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
import uuid

# Enums
class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TermClassification(str, Enum):
    VALID = "valid"
    REVIEW = "review"
    CRITICAL = "critical"
    SPELLING = "spelling"
    GRAMMAR = "grammar"

class ReportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    HTML = "html"
    PDF = "pdf"
    XLSX = "xlsx"

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

# Base Models
class BaseResponse(BaseModel):
    """Base response model"""
    success: bool
    message: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])

class APIResponse(BaseResponse):
    """Standard API response"""
    data: Optional[Any] = None
    error_code: Optional[str] = None

class ErrorResponse(BaseResponse):
    """Error response model"""
    error_code: str
    details: Optional[Dict[str, Any]] = None

# Analysis Models
class AnalyzedTerm(BaseModel):
    """Individual analyzed term"""
    text: str = Field(..., description="The analyzed text")
    start_position: int = Field(..., description="Start position in the original text")
    end_position: int = Field(..., description="End position in the original text")
    classification: TermClassification = Field(..., description="Term classification")
    score: float = Field(..., ge=0.0, le=1.0, description="Quality score (0-1)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level (0-1)")
    frequency: int = Field(..., ge=0, description="Frequency in the text")
    context: str = Field(..., description="Surrounding context")
    rationale: str = Field(..., description="Explanation for the classification")
    suggestions: Optional[List[str]] = Field(default=None, description="Improvement suggestions")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class AnalysisStatistics(BaseModel):
    """Analysis statistics"""
    total_terms: int = Field(..., ge=0, description="Total number of terms analyzed")
    valid_terms: int = Field(..., ge=0, description="Number of valid terms")
    review_terms: int = Field(..., ge=0, description="Number of terms needing review")
    critical_terms: int = Field(..., ge=0, description="Number of critical terms")
    spelling_errors: int = Field(default=0, ge=0, description="Number of spelling errors")
    grammar_errors: int = Field(default=0, ge=0, description="Number of grammar errors")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Overall quality score")
    confidence_min: float = Field(..., ge=0.0, le=1.0, description="Minimum confidence")
    confidence_max: float = Field(..., ge=0.0, le=1.0, description="Maximum confidence")
    confidence_avg: float = Field(..., ge=0.0, le=1.0, description="Average confidence")
    coverage: float = Field(..., ge=0.0, le=1.0, description="Analysis coverage")
    processing_time: float = Field(..., ge=0.0, description="Processing time in seconds")

class AnalysisOptions(BaseModel):
    """Analysis configuration options"""
    include_spelling_check: bool = Field(default=True, description="Enable spelling check")
    include_grammar_check: bool = Field(default=False, description="Enable grammar check")
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence threshold")
    max_suggestions: int = Field(default=3, ge=0, le=10, description="Maximum suggestions per term")
    include_context: bool = Field(default=True, description="Include context information")
    detailed_rationale: bool = Field(default=True, description="Include detailed rationale")
    custom_rules: Optional[Dict[str, Any]] = Field(default=None, description="Custom analysis rules")

class AnalysisRequest(BaseModel):
    """Analysis request model"""
    content: str = Field(..., min_length=1, max_length=100000, description="Text content to analyze")
    language: str = Field(default="en", description="Language code (e.g., 'en', 'es', 'fr')")
    domain: str = Field(default="general", description="Domain/context (e.g., 'medical', 'legal', 'technical')")
    options: Optional[AnalysisOptions] = Field(default=None, description="Analysis options")
    reference_text: Optional[str] = Field(default=None, description="Reference text for comparison")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()

    @validator('language')
    def validate_language(cls, v):
        # Add language validation logic here
        allowed_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ja', 'zh', 'ko']
        if v not in allowed_languages:
            raise ValueError(f'Language must be one of: {", ".join(allowed_languages)}')
        return v

class AnalysisResponse(BaseModel):
    """Analysis response model"""
    terms: List[AnalyzedTerm] = Field(..., description="List of analyzed terms")
    statistics: AnalysisStatistics = Field(..., description="Analysis statistics")
    status: AnalysisStatus = Field(default=AnalysisStatus.COMPLETED, description="Analysis status")
    request_id: str = Field(..., description="Request identifier")
    language: str = Field(..., description="Analysis language")
    domain: str = Field(..., description="Analysis domain")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

# User and Session Models
class UserProfile(BaseModel):
    """User profile model"""
    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., description="User email address")
    full_name: Optional[str] = Field(default=None, description="Full name")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    preferences: Optional[Dict[str, Any]] = Field(default=None, description="User preferences")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation date")
    last_login: Optional[datetime] = Field(default=None, description="Last login timestamp")
    is_active: bool = Field(default=True, description="Account status")

class UserSession(BaseModel):
    """User session model"""
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")
    language: str = Field(default="en", description="Session language")
    domain: str = Field(default="general", description="Session domain")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation time")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity time")
    preferences: Optional[Dict[str, Any]] = Field(default=None, description="Session preferences")
    project_id: Optional[str] = Field(default=None, description="Current project ID")
    expires_at: datetime = Field(..., description="Session expiration time")

# Project Models
class ProjectData(BaseModel):
    """Project data model"""
    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    description: Optional[str] = Field(default=None, max_length=500, description="Project description")
    language: str = Field(default="en", description="Project language")
    domain: str = Field(default="general", description="Project domain")
    settings: Optional[Dict[str, Any]] = Field(default=None, description="Project settings")
    tags: Optional[List[str]] = Field(default=None, description="Project tags")
    is_public: bool = Field(default=False, description="Public visibility")

class Project(ProjectData):
    """Complete project model"""
    project_id: str = Field(..., description="Project identifier")
    user_id: str = Field(..., description="Owner user ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    analysis_count: int = Field(default=0, ge=0, description="Number of analyses")
    file_count: int = Field(default=0, ge=0, description="Number of files")
    status: str = Field(default="active", description="Project status")

# File Models
class FileMetadata(BaseModel):
    """File metadata model"""
    file_id: str = Field(..., description="File identifier")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type/extension")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    checksum: str = Field(..., description="File checksum")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, description="Upload timestamp")
    user_id: str = Field(..., description="Uploader user ID")
    project_id: Optional[str] = Field(default=None, description="Associated project ID")

class ProcessedFile(FileMetadata):
    """Processed file model"""
    content: Optional[str] = Field(default=None, description="Extracted text content")
    character_count: int = Field(default=0, ge=0, description="Character count")
    word_count: int = Field(default=0, ge=0, description="Word count")
    line_count: int = Field(default=0, ge=0, description="Line count")
    language_detected: Optional[str] = Field(default=None, description="Detected language")
    processing_status: str = Field(default="completed", description="Processing status")
    processing_time: float = Field(default=0.0, ge=0.0, description="Processing time in seconds")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

# Configuration Models
class ConfigurationData(BaseModel):
    """User configuration model"""
    language: str = Field(default="en", description="Default language")
    domain: str = Field(default="general", description="Default domain")
    analysis_options: Optional[AnalysisOptions] = Field(default=None, description="Default analysis options")
    ui_preferences: Optional[Dict[str, Any]] = Field(default=None, description="UI preferences")
    notification_settings: Optional[Dict[str, Any]] = Field(default=None, description="Notification settings")
    api_settings: Optional[Dict[str, Any]] = Field(default=None, description="API settings")

# Feedback Models
class FeedbackData(BaseModel):
    """User feedback model"""
    feedback_type: str = Field(..., description="Type of feedback")
    content: str = Field(..., min_length=1, max_length=1000, description="Feedback content")
    rating: Optional[int] = Field(default=None, ge=1, le=5, description="Rating (1-5)")
    category: Optional[str] = Field(default=None, description="Feedback category")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Context information")
    anonymous: bool = Field(default=False, description="Anonymous feedback")

class Feedback(FeedbackData):
    """Complete feedback model"""
    feedback_id: str = Field(..., description="Feedback identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    status: str = Field(default="pending", description="Feedback status")
    response: Optional[str] = Field(default=None, description="Admin response")

# Report Models
class ReportConfig(BaseModel):
    """Report configuration model"""
    format: ReportFormat = Field(..., description="Report format")
    title: str = Field(..., description="Report title")
    description: Optional[str] = Field(default=None, description="Report description")
    include_statistics: bool = Field(default=True, description="Include statistics")
    include_terms: bool = Field(default=True, description="Include analyzed terms")
    include_charts: bool = Field(default=False, description="Include charts")
    date_range: Optional[Dict[str, datetime]] = Field(default=None, description="Date range filter")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Additional filters")

class GeneratedReport(BaseModel):
    """Generated report model"""
    report_id: str = Field(..., description="Report identifier")
    user_id: str = Field(..., description="User identifier")
    config: ReportConfig = Field(..., description="Report configuration")
    file_path: str = Field(..., description="Generated file path")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: Optional[datetime] = Field(default=None, description="Expiration timestamp")
    download_count: int = Field(default=0, ge=0, description="Download count")

# WebSocket Models
class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    type: str = Field(..., description="Message type")
    data: Any = Field(..., description="Message data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    request_id: Optional[str] = Field(default=None, description="Request identifier")

class WebSocketResponse(BaseModel):
    """WebSocket response model"""
    type: str = Field(..., description="Response type")
    data: Any = Field(..., description="Response data")
    success: bool = Field(default=True, description="Success status")
    error: Optional[str] = Field(default=None, description="Error message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(default=None, description="Request identifier")
