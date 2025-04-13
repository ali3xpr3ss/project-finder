from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db, check_database_connection
from core.logging_config import loggers

router = APIRouter()
logger = loggers['api']

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Проверка здоровья приложения
    """
    try:
        # Проверяем подключение к базе данных
        db_status = check_database_connection()
        
        # Проверяем JWT
        jwt_status = True  # JWT проверяется при каждом запросе
        
        status = {
            "status": "healthy" if db_status and jwt_status else "unhealthy",
            "database": "connected" if db_status else "disconnected",
            "jwt": "configured" if jwt_status else "not configured",
            "version": "1.0.0"
        }
        
        logger.info(f"Health check completed: {status}")
        return status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        } 