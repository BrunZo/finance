from typing import Any, Callable
from fastapi import HTTPException


def try_run(fn: Callable[..., Any], *args, **kwargs) -> Any:
    try:
        return fn(*args, **kwargs)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))