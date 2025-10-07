from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)


class CRMException(Exception):
    """Base exception for CRM application"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(CRMException):
    """Resource not found error"""
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, 404)


class ValidationError(CRMException):
    """Validation error"""
    def __init__(self, message: str):
        super().__init__(message, 400)


class AuthenticationError(CRMException):
    """Authentication error"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401)


class AuthorizationError(CRMException):
    """Authorization error"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, 403)


class DuplicateError(CRMException):
    """Duplicate resource error"""
    def __init__(self, resource: str, field: str = None):
        message = f"Duplicate {resource}"
        if field:
            message = f"Duplicate {resource}: {field} already exists"
        super().__init__(message, 409)


async def crm_exception_handler(request: Request, exc: CRMException):
    """Handle CRM exceptions"""
    logger.error(f"CRM Exception: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "type": exc.__class__.__name__}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation exceptions"""
    logger.error(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"error": "Validation failed", "details": exc.errors()}
    )


async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """Handle database integrity exceptions"""
    logger.error(f"Database Integrity Error: {str(exc)}")

    # Check for common constraint violations
    error_message = str(exc.orig) if hasattr(exc, 'orig') else str(exc)

    if "unique constraint" in error_message.lower():
        return JSONResponse(
            status_code=409,
            content={"error": "Resource already exists", "type": "DuplicateError"}
        )
    elif "foreign key constraint" in error_message.lower():
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid reference", "type": "ForeignKeyError"}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"error": "Database error", "type": "DatabaseError"}
        )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle generic exceptions"""
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "type": "InternalError"}
    )


def setup_exception_handlers(app: FastAPI):
    """Setup exception handlers for the FastAPI app"""
    app.add_exception_handler(CRMException, crm_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)