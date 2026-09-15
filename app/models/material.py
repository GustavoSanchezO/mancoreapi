from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Material(Base):
    __tablename__ = "materiales"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    nombre: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    unidad: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    codigo: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )