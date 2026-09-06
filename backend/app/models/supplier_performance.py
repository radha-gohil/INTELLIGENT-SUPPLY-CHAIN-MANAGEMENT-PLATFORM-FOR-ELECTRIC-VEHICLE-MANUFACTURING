from sqlalchemy import (
    Column,
    Integer,
    Float,
    Date,
    ForeignKey
)

from backend.app.database.connection import Base


class SupplierPerformance(Base):

    __tablename__ = "supplier_performance"

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

    performance_date = Column(
        Date,
        nullable=False
    )

    total_orders = Column(
        Integer,
        nullable=False,
        default=0
    )

    on_time_orders = Column(
        Integer,
        nullable=False,
        default=0
    )

    late_orders = Column(
        Integer,
        nullable=False,
        default=0
    )

    ordered_quantity = Column(
        Integer,
        nullable=False,
        default=0
    )

    received_quantity = Column(
        Integer,
        nullable=False,
        default=0
    )

    defective_quantity = Column(
        Integer,
        nullable=False,
        default=0
    )

    average_delay_days = Column(
        Float,
        nullable=False,
        default=0
    )