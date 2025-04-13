from typing import List, Tuple, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from models.user import User
from sqlalchemy.orm import Session
import faiss
import pickle
import os
from datetime import datetime
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class ProfileSearch:
    def __init__(self) -> None:
        """Инициализация сервиса поиска профилей"""
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.dimension = self.model.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatL2(self.dimension)
            self.profiles: List[User] = []
            logger.info("Сервис поиска профилей успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка при инициализации сервиса: {str(e)}")
            raise

    def _vectorize_text(self, text: str) -> np.ndarray:
        """Векторизация текста"""
        try:
            return self.model.encode([text])[0]
        except Exception as e:
            logger.error(f"Ошибка при векторизации текста: {str(e)}")
            raise

    def _compute_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Вычисление косинусного сходства между векторами"""
        try:
            return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
        except Exception as e:
            logger.error(f"Ошибка при вычислении сходства: {str(e)}")
            raise

    def index_profiles(self, profiles: List[User]) -> None:
        """Индексация профилей"""
        try:
            if not profiles:
                return

            # Очищаем предыдущий индекс
            self.index = faiss.IndexFlatL2(self.dimension)
            self.profiles = []

            # Подготавливаем тексты профилей
            texts = []
            for profile in profiles:
                text = f"""
                {profile.full_name}
                {profile.bio or ''}
                {' '.join(profile.skills or [])}
                {profile.experience or ''}
                {profile.education or ''}
                {' '.join(profile.technologies or [])}
                {profile.role}
                {' '.join(profile.languages or [])}
                """
                texts.append(text)

            # Векторизуем тексты
            vectors = self.model.encode(texts)

            # Добавляем векторы в индекс
            self.index.add(np.array(vectors).astype('float32'))
            self.profiles = profiles

            logger.info(f"Успешно проиндексировано {len(profiles)} профилей")
        except Exception as e:
            logger.error(f"Ошибка при индексации профилей: {str(e)}")
            raise

    def search(self, query: str, top_k: int = 10) -> List[Tuple[Dict[str, Any], float]]:
        """Поиск профилей по запросу"""
        try:
            if not self.profiles:
                return []

            # Векторизуем запрос
            query_vector = self._vectorize_text(query)

            # Ищем ближайшие векторы
            distances, indices = self.index.search(
                np.array([query_vector]).astype('float32'),
                min(top_k, len(self.profiles))
            )

            # Формируем результаты
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.profiles):
                    profile = self.profiles[idx]
                    similarity = 1 / (1 + distance)  # Преобразуем расстояние в сходство
                    results.append((profile.dict(), similarity))

            return results
        except Exception as e:
            logger.error(f"Ошибка при поиске профилей: {str(e)}")
            raise

# Создаем глобальный экземпляр сервиса
profile_search = ProfileSearch() 