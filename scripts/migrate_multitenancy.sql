-- Multi-tenant migration for existing databases (MySQL)
-- Run once: mysql -u root aviacion < backend/scripts/migrate_multitenancy.sql

CREATE TABLE IF NOT EXISTS organizations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(80) NOT NULL UNIQUE,
    is_active TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS organization_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    organization_id INT NOT NULL,
    user_id INT NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'member',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_org_user (organization_id, user_id),
    CONSTRAINT fk_org_member_org FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    CONSTRAINT fk_org_member_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

INSERT INTO organizations (name, slug, is_active)
SELECT 'Cliente Demo', 'demo', 1
WHERE NOT EXISTS (SELECT 1 FROM organizations WHERE slug = 'demo');

SET @org_id := (SELECT id FROM organizations WHERE slug = 'demo' LIMIT 1);

INSERT INTO organization_members (organization_id, user_id, role)
SELECT @org_id, u.id, 'admin'
FROM users u
WHERE u.username = 'admin'
  AND NOT EXISTS (
    SELECT 1 FROM organization_members om
    WHERE om.organization_id = @org_id AND om.user_id = u.id
  );

ALTER TABLE inspections
    ADD COLUMN IF NOT EXISTS organization_id INT NULL AFTER id;

UPDATE inspections
SET organization_id = @org_id
WHERE organization_id IS NULL;

ALTER TABLE inspections
    MODIFY organization_id INT NOT NULL,
    ADD INDEX idx_inspections_org (organization_id),
    ADD CONSTRAINT fk_inspections_org FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE;

ALTER TABLE aircraft_models
    ADD COLUMN IF NOT EXISTS organization_id INT NULL AFTER id;

UPDATE aircraft_models
SET organization_id = @org_id
WHERE organization_id IS NULL;

ALTER TABLE aircraft_models
    MODIFY organization_id INT NOT NULL,
    ADD INDEX idx_aircraft_models_org (organization_id),
    ADD CONSTRAINT fk_aircraft_models_org FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE;
