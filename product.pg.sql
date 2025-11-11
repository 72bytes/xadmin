-- comment 产品信息表初始化
-- 初始化产品数据
INSERT INTO product
(id, product_type, product_name, sku, asic_family, status, create_user, create_time, update_user, update_time)
VALUES
-- Radeon 系列
(1, 'Radeon', 'Navi31', 'Navi31 XT-W', 'Navi31', 1, 1, NOW(), NULL, NULL),
(2, 'Radeon', 'Navi31', 'Navi31 XLW-AI', 'Navi31', 1, 1, NOW(), NULL, NULL),
(3, 'Radeon', 'Navi31', 'Navi31 XTW-AI', 'Navi31', 1, 1, NOW(), NULL, NULL),
(4, 'Radeon', 'Navi31', 'Navi31 XTX', 'Navi31', 1, 1, NOW(), NULL, NULL),
(5, 'Radeon', 'Navi31', 'Navi31 XT', 'Navi31', 1, 1, NOW(), NULL, NULL),
(6, 'Radeon', 'Navi31', 'Navi31 XL', 'Navi31', 1, 1, NOW(), NULL, NULL),
(7, 'Radeon', 'Navi31', 'Navi31 XL-W', 'Navi31', 1, 1, NOW(), NULL, NULL),
(8, 'Radeon', 'Navi32', 'Navi32 GL-XL', 'Navi32', 1, 1, NOW(), NULL, NULL),
(9, 'Radeon', 'Navi32', 'Navi32 XL-W', 'Navi32', 1, 1, NOW(), NULL, NULL),
(10, 'Radeon', 'Navi32', 'Navi32 XTX', 'Navi32', 1, 1, NOW(), NULL, NULL),
(11, 'Radeon', 'Navi32', 'NAVI32 XE', 'Navi32', 1, 1, NOW(), NULL, NULL),
(12, 'Radeon', 'Navi32', 'Navi32 XL', 'Navi32', 1, 1, NOW(), NULL, NULL),

-- Instinct 系列
(13, 'Instinct', 'MI300', 'MI300A', 'MI300', 1, 1, NOW(), NULL, NULL),
(14, 'Instinct', 'MI300', 'MI300X-O', 'MI300', 1, 1, NOW(), NULL, NULL),
(15, 'Instinct', 'MI308', 'MI308X', 'MI308', 1, 1, NOW(), NULL, NULL),

-- Ryzen 系列
(16, 'Ryzen', 'Ryzen 7000', 'RYZEN7_7800X', 'Zen4', 1, 1, NOW(), NULL, NULL),
(17, 'Ryzen', 'Ryzen 7000', 'RYZEN9_7950X', 'Zen4', 1, 1, NOW(), NULL, NULL),

-- Embedded 系列
(18, 'Embedded', 'Embedded V2000', 'V2000_EMB', 'Navi2', 1, 1, NOW(), NULL, NULL);