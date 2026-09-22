from sqlalchemy import (
    Boolean,
    Column,
    Float,
    Integer,
    String
)

from backend.app.database.connection import Base


# ============================================================
# SUPPLIER MODEL
# ============================================================

class Supplier(Base):

    __tablename__ = "suppliers"

    # ========================================================
    # PRIMARY KEY
    # ========================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ========================================================
    # BASIC SUPPLIER MASTER DATA
    # ========================================================

    supplier_code = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )

    supplier_name = Column(
        String(150),
        nullable=False
    )

    location = Column(
        String(150),
        nullable=True
    )

    component_category = Column(
        String(100),
        nullable=True,
        index=True
    )

    # ========================================================
    # MASTER / DEFAULT COMMERCIAL INFORMATION
    #
    # Component-specific commercial information belongs
    # inside SupplierComponent.
    #
    # These values come from supplier_master.csv and represent
    # general/default supplier characteristics.
    # ========================================================

    master_lead_time_days = Column(
        Integer,
        nullable=True
    )

    master_unit_cost = Column(
        Float,
        nullable=True
    )

    master_monthly_capacity = Column(
        Integer,
        nullable=True
    )

    # ========================================================
    # MASTER QUALITY / RELIABILITY
    #
    # quality_rating:
    #     Supplier master quality rating.
    #
    # baseline_reliability_score:
    #     Supplier-master reliability rating.
    #
    # Operational reliability can be calculated separately
    # from historical supplier performance.
    # ========================================================

    quality_rating = Column(
        Float,
        nullable=True
    )

    baseline_reliability_score = Column(
        Float,
        nullable=True
    )

    # ========================================================
    # CONTACT INFORMATION
    # ========================================================

    contact_email = Column(
        String(150),
        nullable=True
    )

    contact_phone = Column(
        String(30),
        nullable=True
    )

    # ========================================================
    # STATUS
    # ========================================================

    status = Column(
        String(30),
        nullable=False,
        default="ACTIVE"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )