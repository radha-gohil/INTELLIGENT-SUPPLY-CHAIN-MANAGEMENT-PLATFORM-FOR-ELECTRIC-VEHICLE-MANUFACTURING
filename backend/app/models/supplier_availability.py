from sqlalchemy import Column, Integer, DateTime, ForeignKey
from datetime import datetime

from backend.app.database.connection import Base


class SupplierAvailability(Base):

    __tablename__ = "supplier_availability"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    supplier_id = Column(
        Integer,
        ForeignKey("suppliers.id"),
        nullable=False,
        index=True
    )

    component_id = Column(
        Integer,
        ForeignKey("components.id"),
        nullable=False,
        index=True
    )

    available_quantity = Column(
        Integer,
        nullable=False,
        default=0
    )

    committed_quantity = Column(
        Integer,
        nullable=False,
        default=0
    )

    available_to_promise = Column(
        Integer,
        nullable=False,
        default=0
    )

    expected_replenishment_quantity = Column(
        Integer,
        nullable=False,
        default=0
    )

    expected_replenishment_date = Column(
        DateTime,
        nullable=True
    )

    last_updated = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )