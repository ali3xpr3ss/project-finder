from typing import List, Tuple, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from models.project import Project
from sqlalchemy.orm import Session
import faiss
import pickle
import os
from datetime import datetime
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class SemanticSearch:
    def __init__(self) -> None:
        """Инициализация сервиса семантического поиска"""
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.dimension = self.model.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatL2(self.dimension)
            self.projects: List[Project] = []
            logger.info("Сервис семантического поиска успешно инициализирован")
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

    def index_projects(self, projects: List[Project]) -> None:
        """Индексация проектов"""
        try:
            if not projects:
                return

            # Очищаем предыдущий индекс
            self.index = faiss.IndexFlatL2(self.dimension)
            self.projects = []

            # Подготавливаем тексты проектов
            texts = []
            for project in projects:
                text = f"{project.title} {project.description} {' '.join(project.technologies or [])} {' '.join(project.roles or [])}"
                texts.append(text)

            # Векторизуем тексты
            vectors = self.model.encode(texts)

            # Добавляем векторы в индекс
            self.index.add(np.array(vectors).astype('float32'))
            self.projects = projects

            logger.info(f"Успешно проиндексировано {len(projects)} проектов")
        except Exception as e:
            logger.error(f"Ошибка при индексации проектов: {str(e)}")
            raise

    def search(self, query: str, top_k: int = 10) -> List[Tuple[Dict[str, Any], float]]:
        """Поиск проектов по запросу"""
        try:
            if not self.projects:
                return []

            # Векторизуем запрос
            query_vector = self._vectorize_text(query)

            # Ищем ближайшие векторы
            distances, indices = self.index.search(
                np.array([query_vector]).astype('float32'),
                min(top_k, len(self.projects))
            )

            # Формируем результаты
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.projects):
                    project = self.projects[idx]
                    similarity = 1 / (1 + distance)  # Преобразуем расстояние в сходство
                    results.append((project.dict(), similarity))

            return results
        except Exception as e:
            logger.error(f"Ошибка при поиске проектов: {str(e)}")
            raise

# Создаем глобальный экземпляр сервиса
semantic_search = SemanticSearch() 