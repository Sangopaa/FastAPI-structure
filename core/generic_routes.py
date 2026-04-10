import inspect
from typing import Type, List, Generic, TypeVar, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import SQLModel, Session
from uuid import UUID

T = TypeVar("T", bound=SQLModel)


from core.standard_response_route import StandardResponseRoute
from repositories.base import BaseRepository


class GenericCRUDRouter(Generic[T], APIRouter):
    def __init__(self, model: Type[T], get_session, *args, **kwargs):
        kwargs.setdefault("route_class", StandardResponseRoute)
        super().__init__(*args, **kwargs)
        self.model = model
        self.get_session = get_session
        self.repository = BaseRepository(self.model)

        self.add_api_route(
            "/",
            self._make_endpoint(self.get_all),
            methods=["GET"],
            response_model=List[self.model],
        )

        self.add_api_route(
            "/{id}",
            self._make_endpoint(self.get_one),
            methods=["GET"],
            response_model=self.model,
        )

        self.add_api_route(
            "/",
            self._make_endpoint(self.create),
            methods=["POST"],
            response_model=self.model,
            status_code=status.HTTP_201_CREATED,
        )

        self.add_api_route(
            "/{id}",
            self._make_endpoint(self.delete),
            methods=["DELETE"],
            status_code=status.HTTP_200_OK,
        )

    def _make_endpoint(self, method):
        async def endpoint(
            db_session: Session = Depends(self.get_session),
            **kwargs,
        ):
            kwargs["session"] = db_session
            return await method(**kwargs)

        sig = inspect.signature(method)
        parameters = [
            p for p in sig.parameters.values() if p.name not in ["self", "session"]
        ]
        parameters.append(
            inspect.Parameter(
                "db_session",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(self.get_session),
                annotation=Session,
            )
        )
        endpoint.__signature__ = sig.replace(parameters=parameters)
        return endpoint

    async def get_all(self, session: Session):
        return self.repository.get_all(session)

    async def get_one(self, session: Session, id: UUID):
        db_obj = self.repository.get_by_id(session, id)
        if not db_obj:
            raise HTTPException(
                status_code=404, detail=f"{self.model.__name__} no encontrado"
            )
        return db_obj

    async def create(self, session: Session, obj: Any):
        return self.repository.create(session, obj)

    async def delete(self, session: Session, id: UUID):
        db_obj = self.repository.get_by_id(session, id)

        if not db_obj or getattr(db_obj, "is_deleted", False):
            raise HTTPException(status_code=404, detail="Registro no encontrado")

        self.repository.delete(session, db_obj)

        return {
            "ok": True,
            "message": f"{self.model.__name__} Eliminado correctamente",
        }
