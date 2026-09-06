ALTER TABLE suppliers
ADD COLUMN IF NOT EXISTS component_category VARCHAR(100);

ALTER TABLE suppliers
ADD COLUMN IF NOT EXISTS master_lead_time_days INTEGER;

ALTER TABLE suppliers
ADD COLUMN IF NOT EXISTS master_unit_cost DOUBLE PRECISION;

ALTER TABLE suppliers
ADD COLUMN IF NOT EXISTS master_monthly_capacity INTEGER;

ALTER TABLE suppliers
ADD COLUMN IF NOT EXISTS quality_rating DOUBLE PRECISION;

ALTER TABLE suppliers
ADD COLUMN IF NOT EXISTS baseline_reliability_score DOUBLE PRECISION;


CREATE INDEX IF NOT EXISTS ix_suppliers_component_category
ON suppliers(component_category);