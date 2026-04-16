import inspect
from typing import Type, Generic, TypeVar, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

T = TypeVar("T", bound=SQLModel)


from core.standard_response_route import StandardResponseRoute
from repositories.base import BaseRepository
from schemas.pagination import PaginatedResponse


class GenericCRUDRouter(Generic[T], APIRouter):
    def __init__(
        self,
        model: Type[T],
        get_session,
        schema_create: Optional[Type[Any]] = None,
        schema_read: Optional[Type[Any]] = None,
        *args,
        **kwargs,
    ):
        kwargs.setdefault("route_class", StandardResponseRoute)
        super().__init__(*args, **kwargs)
        self.model = model
        self.get_session = get_session
        self.schema_create = schema_create or model
        self.schema_read = schema_read or model
        self.repository = BaseRepository(self.model)

        self.add_api_route(
            "/",
            self._make_endpoint(self.get_all),
            methods=["GET"],
            response_model=PaginatedResponse[self.schema_read],
        )

        self.add_api_route(
            "/{id}",
            self._make_endpoint(self.get_one),
            methods=["GET"],
            response_model=self.schema_read,
        )

        self.add_api_route(
            "/",
            self._make_endpoint(self.create),
            methods=["POST"],
            response_model=self.schema_read,
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
            db_session: AsyncSession = Depends(self.get_session),
            **kwargs,
        ):
            kwargs["session"] = db_session
            return await method(**kwargs)

        sig = inspect.signature(method)
        parameters = []
        for p in sig.parameters.values():
            if p.name in ["self", "session"]:
                continue
            if p.name == "obj":
                parameters.append(p.replace(annotation=self.schema_create))
            else:
                parameters.append(p)
        parameters.append(
            inspect.Parameter(
                "db_session",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(self.get_session),
                annotation=AsyncSession,
            )
        )
        endpoint.__signature__ = sig.replace(parameters=parameters)
        return endpoint

    async def get_all(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        filter_by: Optional[str] = None,
        filter_value: Optional[str] = None,
    ):
        data, total = await self.repository.get_all(
            session,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            filter_by=filter_by,
            filter_value=filter_value,
        )
        return {"data": data, "total": total, "skip": skip, "limit": limit}

    async def get_one(self, session: AsyncSession, id: UUID):
        db_obj = await self.repository.get_by_id(session, id)
        if not db_obj:
            raise HTTPException(
                status_code=404, detail=f"{self.model.__name__} no encontrado"
            )
        return db_obj

    async def create(self, session: AsyncSession, obj: Any):
        return await self.repository.create(session, obj)

    async def delete(self, session: AsyncSession, id: UUID):
        db_obj = await self.repository.get_by_id(session, id)

        if not db_obj or getattr(db_obj, "is_deleted", False):
            raise HTTPException(status_code=404, detail="Registro no encontrado")

        await self.repository.delete(session, db_obj)

        return {
            "ok": True,
            "message": f"{self.model.__name__} Eliminado correctamente",
        }
