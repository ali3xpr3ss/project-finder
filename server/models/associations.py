from sqlalchemy import Column, Integer, ForeignKey, Table
from core.database import Base

# Таблица для связи many-to-many между проектами и пользователями (участники)
project_members = Table(
    'project_members',
    Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id', ondelete='CASCADE')),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'))
)

# Таблица для связи many-to-many между проектами и пользователями (лайки)
project_likes = Table(
    'project_likes',
    Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id', ondelete='CASCADE')),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'))
) 