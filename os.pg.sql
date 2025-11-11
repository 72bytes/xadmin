-- 插入数据
INSERT INTO os (distro_name, version, variant, is_active) VALUES

-- Ubuntu 系列
VALUES
('Ubuntu', '22.04', 'Standard', TRUE),
('Ubuntu', '22.04', 'HWE', TRUE),
('Ubuntu', '22.04', 'Edge', TRUE),
('Ubuntu', '22.04', 'Generic', TRUE),
('Ubuntu', '24.04', 'Generic', TRUE),

-- RHEL 系列
('RHEL', '9.6', 'Standard', TRUE),
('RHEL', '9.7', 'Standard', TRUE),
('RHEL', '10.1', 'Standard', TRUE);