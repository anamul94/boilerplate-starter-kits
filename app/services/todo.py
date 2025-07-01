from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List, Optional
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate
from app.core.logging import logger

class TodoServiceError(Exception):
    """Base exception for todo service errors"""
    pass

def get_todo(db: Session, todo_id: int) -> Optional[Todo]:
    try:
        return db.query(Todo).filter(Todo.id == todo_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching todo by ID {todo_id}: {str(e)}")
        raise TodoServiceError(f"Error retrieving todo: {str(e)}")

def get_todos(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Todo]:
    try:
        return db.query(Todo).filter(Todo.user_id == user_id).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching todos for user {user_id}: {str(e)}")
        raise TodoServiceError(f"Error retrieving todos: {str(e)}")

def create_todo(db: Session, todo_in: TodoCreate, user_id: int) -> Todo:
    try:
        db_todo = Todo(**todo_in.dict(), user_id=user_id)
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        logger.info(f"New todo created: '{db_todo.title}' for user_id: {user_id}")
        return db_todo
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error when creating todo for user {user_id}: {str(e)}")
        raise TodoServiceError(f"Database integrity error: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error when creating todo for user {user_id}: {str(e)}")
        raise TodoServiceError(f"Error creating todo: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error when creating todo for user {user_id}: {str(e)}")
        raise TodoServiceError(f"Unexpected error: {str(e)}")

def update_todo(db: Session, todo: Todo, todo_in: TodoUpdate) -> Todo:
    try:
        update_data = todo_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(todo, field, value)
        
        db.add(todo)
        db.commit()
        db.refresh(todo)
        logger.info(f"Todo updated: id={todo.id}, title='{todo.title}', user_id={todo.user_id}")
        return todo
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error when updating todo {todo.id}: {str(e)}")
        raise TodoServiceError(f"Database integrity error: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error when updating todo {todo.id}: {str(e)}")
        raise TodoServiceError(f"Error updating todo: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error when updating todo {todo.id}: {str(e)}")
        raise TodoServiceError(f"Unexpected error: {str(e)}")

def delete_todo(db: Session, todo: Todo) -> None:
    try:
        todo_id = todo.id
        user_id = todo.user_id
        db.delete(todo)
        db.commit()
        logger.info(f"Todo deleted: id={todo_id}, user_id={user_id}")
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error when deleting todo {todo.id}: {str(e)}")
        raise TodoServiceError(f"Database integrity error: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error when deleting todo {todo.id}: {str(e)}")
        raise TodoServiceError(f"Error deleting todo: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error when deleting todo {todo.id}: {str(e)}")
        raise TodoServiceError(f"Unexpected error: {str(e)}")