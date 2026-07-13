-- Run if inspections table already exists without aircraft_model_id
ALTER TABLE inspections
  ADD COLUMN aircraft_model_id INT NULL,
  ADD INDEX ix_inspections_aircraft_model_id (aircraft_model_id),
  ADD CONSTRAINT fk_inspections_aircraft_model_id
    FOREIGN KEY (aircraft_model_id) REFERENCES aircraft_models(id) ON DELETE SET NULL;
