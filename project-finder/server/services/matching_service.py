from typing import List, Tuple, Dict, Optional, Any
from sqlalchemy.orm import Session
from models.project import Project
from models.user import User
from services.semantic_search import semantic_search
from services.profile_search import profile_search
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class MatchingService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.min_compatibility_score = 0.3  # Минимальный порог совместимости
    
    def _prepare_project_text(self, project: Project) -> str:
        """Подготовка текста проекта для сопоставления"""
        return f"""
        Название проекта: {project.title}
        Описание: {project.description or ''}
        Требуемые технологии: {', '.join(project.technologies or [])}
        Требуемые роли: {', '.join(project.roles or [])}
        Статус проекта: {project.status}
        """
    
    def _prepare_profile_text(self, user: User) -> str:
        """Подготовка текста анкеты для сопоставления"""
        return f"""
        Имя: {user.full_name}
        Био: {user.bio or ''}
        Навыки: {', '.join(user.skills or [])}
        Опыт: {user.experience or ''}
        Образование: {user.education or ''}
        Технологии: {', '.join(user.technologies or [])}
        Роли: {user.role}
        Языки: {', '.join(user.languages or [])}
        """
    
    def find_matching_profiles(
        self,
        project: Project,
        top_k: int = 10,
        min_score: Optional[float] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Поиск подходящих участников для проекта"""
        try:
            # Подготавливаем текст проекта
            project_text = self._prepare_project_text(project)
            
            # Ищем подходящие анкеты
            results = profile_search.search(project_text, top_k)
            
            # Фильтруем по минимальному порогу совместимости
            min_score = min_score or self.min_compatibility_score
            filtered_results = [
                (profile, score) for profile, score in results
                if score >= min_score
            ]
            
            logger.info(f"Найдено {len(filtered_results)} подходящих участников для проекта {project.title}")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Ошибка при поиске подходящих участников: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при поиске подходящих участников"
            )
    
    def find_matching_projects(
        self,
        user: User,
        top_k: int = 10,
        min_score: Optional[float] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Поиск подходящих проектов для участника"""
        try:
            # Подготавливаем текст анкеты
            profile_text = self._prepare_profile_text(user)
            
            # Ищем подходящие проекты
            results = semantic_search.search(profile_text, top_k)
            
            # Фильтруем по минимальному порогу совместимости
            min_score = min_score or self.min_compatibility_score
            filtered_results = [
                (project, score) for project, score in results
                if score >= min_score
            ]
            
            logger.info(f"Найдено {len(filtered_results)} подходящих проектов для участника {user.full_name}")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Ошибка при поиске подходящих проектов: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при поиске подходящих проектов"
            )
    
    def calculate_compatibility(
        self,
        project: Project,
        user: User
    ) -> float:
        """Оценка совместимости проекта и участника"""
        try:
            # Подготавливаем тексты
            project_text = self._prepare_project_text(project)
            profile_text = self._prepare_profile_text(user)
            
            # Векторизуем тексты
            project_vector = semantic_search._vectorize_text(project_text)
            profile_vector = profile_search._vectorize_text(profile_text)
            
            # Вычисляем сходство
            similarity = semantic_search._compute_similarity(project_vector, profile_vector)
            
            logger.info(f"Совместимость проекта {project.title} и участника {user.full_name}: {similarity:.2f}")
            return similarity
            
        except Exception as e:
            logger.error(f"Ошибка при расчете совместимости: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при расчете совместимости"
            )
    
    def get_recommendations(
        self,
        user: User,
        top_k: int = 5
    ) -> Dict[str, List[Tuple[Dict[str, Any], float]]]:
        """Получение рекомендаций для участника"""
        try:
            # Находим подходящие проекты
            matching_projects = self.find_matching_projects(user, top_k)
            
            # Находим похожих участников
            profile_text = self._prepare_profile_text(user)
            similar_profiles = profile_search.search(profile_text, top_k)
            
            # Фильтруем похожих участников (исключаем самого пользователя)
            similar_profiles = [
                (profile, score) for profile, score in similar_profiles
                if profile['id'] != user.id
            ]
            
            return {
                'matching_projects': matching_projects,
                'similar_profiles': similar_profiles
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении рекомендаций: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при получении рекомендаций"
            )

# Создаем глобальный экземпляр сервиса
matching_service = MatchingService() 