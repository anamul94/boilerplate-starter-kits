from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.todo import Todo
from app.schemas.todo import Todo as TodoSchema, TodoCreate, TodoUpdate
from app.services.todo import create_todo, get_todo, get_todos, update_todo, delete_todo, TodoServiceError
from app.core.logging import logger

router = APIRouter()

@router.get("/", response_model=List[TodoSchema])
def read_todos(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve todos for current user
    """
    try:
        todos = get_todos(db, user_id=current_user.id, skip=skip, limit=limit)
        logger.info(
            f"User retrieved todos list",
            extra={
                "user_id": current_user.id,
                "count": len(todos),
                "skip": skip,
                "limit": limit,
                "client_ip": request.client.host if request.client else None,
            }
        )
        return todos
    except TodoServiceError as e:
        logger.error(f"Error retrieving todos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving todos",
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving todos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

@router.post("/", response_model=TodoSchema, status_code=status.HTTP_201_CREATED)
def create_new_todo(
    todo_in: TodoCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create new todo for current user
    """
    try:
        todo = create_todo(db=db, todo_in=todo_in, user_id=current_user.id)
        logger.info(
            f"User created new todo",
            extra={
                "user_id": current_user.id,
                "todo_id": todo.id,
                "todo_title": todo.title,
                "client_ip": request.client.host if request.client else None,
            }
        )
        return todo
    except TodoServiceError as e:
        logger.error(f"Error creating todo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating todo",
        )
    except Exception as e:
        logger.error(f"Unexpected error creating todo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

@router.get("/{todo_id}", response_model=TodoSchema)
def read_todo(
    todo_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get todo by ID
    """
    try:
        todo = get_todo(db=db, todo_id=todo_id)
        if not todo:
            logger.warning(
                f"Todo not found",
                extra={
                    "user_id": current_user.id,
                    "todo_id": todo_id,
                    "client_ip": request.client.host if request.client else None,
                }
            )
            raise HTTPException(status_code=404, detail="Todo not found")
            
        if todo.user_id != current_user.id:
            logger.warning(
                f"Unauthorized todo access attempt",
                extra={
                    "user_id": current_user.id,
                    "todo_id": todo_id,
                    "todo_owner_id": todo.user_id,
                    "client_ip": request.client.host if request.client else None,
                }
            )
            raise HTTPException(status_code=403, detail="Not enough permissions")
            
        logger.info(
            f"User retrieved todo",
            extra={
                "user_id": current_user.id,
                "todo_id": todo_id,
                "client_ip": request.client.host if request.client else None,
            }
        )
        return todo
    except TodoServiceError as e:
        logger.error(f"Error retrieving todo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving todo",
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving todo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

@router.put("/{todo_id}", response_model=TodoSchema)
def update_todo_item(
    todo_id: int,
    todo_in: TodoUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a todo
    """
    try:
        todo = get_todo(db=db, todo_id=todo_id)
        if not todo:
            logger.warning(
                f"Todo not found for update",
                extra={
                    "user_id": current_user.id,
                    "todo_id": todo_id,
                    "client_ip": request.client.host if request.client else None,
                }
            )
            raise HTTPException(status_code=404, detail="Todo not found")
            
        if todo.user_id != current_user.id:
            logger.warning(
                f"Unauthorized todo update attempt",
                extra={
                    "user_id": current_user.id,
                    "todo_id": todo_id,
                    "todo_owner_id": todo.user_id,
                    "client_ip": request.client.host if request.client else None,
                }
            )
            raise HTTPException(status_code=403, detail="Not enough permissions")
            
        updated_todo = update_todo(db=db, todo=todo, todo_in=todo_in)
        logger.info(
            f"User updated todo",
            extra={
                "user_id": current_user.id,
                "todo_id": todo_id,
                "fields_updated": list(todo_in.dict(exclude_unset=True).keys()),
                "client_ip": request.client.host if request.client else None,
            }
        )
        return updated_todo
    except TodoServiceError as e:
        logger.error(f"Error updating todo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating todo",
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating todo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo_item(
    todo_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a todo
    """
    try:
        todo = get_todo(db=db, todo_id=todo_id)
        if not todo:
            logger.warning(
                f"Todo not found for deletion",
                extra={
                    "user_id": current_user.id,
                    "todo_id": todo_id,
                    "client_ip": request.client.host if request.client else None,
                }
            )
            raise HTTPException(status_code=404, detail="Todo not found")
            
        if todo.user_id != current_user.id:
            logger.warning(
                f"Unauthorized todo deletion attempt",
                extra={
                    "user_id": current_user.id,
                    "todo_id": todo_id,
                    "todo_owner_id": todo.user_id,
                    "client_ip": request.client.host if request.client else None,
                }
            )
            raise HTTPException(status_code=403, detail="Not enough permissions")
            
        delete_todo(db=db, todo=todo)
        logger.info(
            f"User deleted todo",
            extra={
                "user_id": current_user.id,
                "todo_id": todo_id,
                "client_ip": request.client.host if request.client else None,
            }
        )
    except TodoServiceError as e:
        logger.error(f"Error deleting todo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting todo",
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting todo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )