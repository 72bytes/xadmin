-- ============================================================================
-- Test Plan Database - Sample Data (50+ Records)
-- ============================================================================
-- 基于 output.json 中的真实设备数据生成
-- 生成时间: 2025-11-11
-- 说明: 包含测试设备、操作系统、测试类型、测试组件、测试用例和测试计划的完整数据

-- 清空现有数据（可选，谨慎使用）
-- TRUNCATE TABLE test_plan_cases, test_plans, test_cases, test_components, test_types, os_supported_kernels, os_configs, sut_devices RESTART IDENTITY CASCADE;

-- ============================================================================
-- 1. 测试设备数据 (SUT Devices) - 10条
-- ============================================================================
INSERT INTO sut_devices (hostname, asic_name, ip_address, device_id, rev_id, gpu_series, gpu_model, created_at, updated_at)
VALUES
-- APU设备 (基于output.json)
('aerith-0', 'VGH 163F_REV_AE', '10.67.78.176', '163f', 'ae', 'AMD APU', 'AMD Custom GPU 0405', NOW(), NOW()),
('aerith-1', 'VGH 163F_REV_AE', '10.67.78.177', '163f', 'ae', 'AMD APU', 'AMD Custom GPU 0405', NOW(), NOW()),
('aerith-2', 'VGH 163F_REV_AE', '10.67.78.178', '163f', 'ae', 'AMD APU', 'AMD Custom GPU 0405', NOW(), NOW()),

-- Navi 31 设备 (RX 7900 系列)
('navi31-test-01', 'Navi 31 GFX1100', '10.67.80.101', '744c', 'c8', 'Radeon RX 7000', 'RX 7900 XTX', NOW(), NOW()),
('navi31-test-02', 'Navi 31 GFX1100', '10.67.80.102', '744c', 'c8', 'Radeon RX 7000', 'RX 7900 XTX', NOW(), NOW()),
('navi31-test-03', 'Navi 31 GFX1100', '10.67.80.103', '744c', 'c8', 'Radeon RX 7000', 'RX 7900 XT', NOW(), NOW()),

-- Navi 32 设备 (RX 7800/7700 系列)
('navi32-test-01', 'Navi 32 GFX1101', '10.67.81.101', '747e', 'd0', 'Radeon RX 7000', 'RX 7800 XT', NOW(), NOW()),
('navi32-test-02', 'Navi 32 GFX1101', '10.67.81.102', '747e', 'd0', 'Radeon RX 7000', 'RX 7700 XT', NOW(), NOW()),

-- Navi 33 设备 (RX 7600 系列)
('navi33-test-01', 'Navi 33 GFX1102', '10.67.82.101', '743f', 'c8', 'Radeon RX 7000', 'RX 7600', NOW(), NOW()),
('navi33-test-02', 'Navi 33 GFX1102', '10.67.82.102', '743f', 'c8', 'Radeon RX 7000', 'RX 7600 XT', NOW(), NOW());

-- ============================================================================
-- 2. 操作系统配置数据 (OS Configs) - 8条
-- ============================================================================
INSERT INTO os_configs (os_family, version, download_url, created_at, updated_at)
VALUES
-- Ubuntu LTS 版本
('Ubuntu', '20.04', 'https://releases.ubuntu.com/20.04/ubuntu-20.04.6-desktop-amd64.iso', NOW(), NOW()),
('Ubuntu', '22.04', 'https://releases.ubuntu.com/22.04/ubuntu-22.04.3-desktop-amd64.iso', NOW(), NOW()),
('Ubuntu', '24.04', 'https://releases.ubuntu.com/24.04/ubuntu-24.04-desktop-amd64.iso', NOW(), NOW()),

-- RHEL/CentOS
('RHEL', '8.8', 'https://access.redhat.com/downloads/rhel/', NOW(), NOW()),
('RHEL', '9.2', 'https://access.redhat.com/downloads/rhel/', NOW(), NOW()),

-- Fedora
('Fedora', '38', 'https://download.fedoraproject.org/pub/fedora/linux/releases/38/', NOW(), NOW()),
('Fedora', '39', 'https://download.fedoraproject.org/pub/fedora/linux/releases/39/', NOW(), NOW()),

-- openSUSE
('openSUSE', '15.5', 'https://get.opensuse.org/leap/15.5/', NOW(), NOW());

-- ============================================================================
-- 3. 操作系统支持的内核版本 (OS Supported Kernels) - 12条
-- ============================================================================
INSERT INTO os_supported_kernels (os_config_id, kernel_version)
VALUES
-- Ubuntu 20.04
(1, '5.4.0-150-generic'),
(1, '5.15.0-78-generic'),

-- Ubuntu 22.04
(2, '5.15.0-78-generic'),
(2, '6.2.0-39-generic'),
(2, '6.5.0-14-generic'),

-- Ubuntu 24.04
(3, '6.5.0-14-generic'),
(3, '6.8.0-31-generic'),

-- RHEL 8.8
(4, '4.18.0-477.el8'),

-- RHEL 9.2
(5, '5.14.0-284.el9'),

-- Fedora 38
(6, '6.2.15-300.fc38'),

-- Fedora 39
(7, '6.5.6-300.fc39'),

-- openSUSE 15.5
(8, '5.14.21-150500.55.12');

-- ============================================================================
-- 4. 测试类型数据 (Test Types) - 6条
-- ============================================================================
INSERT INTO test_types (type_name, created_at, updated_at)
VALUES
('Benchmark', NOW(), NOW()),
('Functional', NOW(), NOW()),
('Performance', NOW(), NOW()),
('Stress', NOW(), NOW()),
('Stability', NOW(), NOW()),
('Compatibility', NOW(), NOW());

-- ============================================================================
-- 5. 测试组件数据 (Test Components) - 15条
-- ============================================================================
INSERT INTO test_components (test_type_id, component_category, component_name)
VALUES
-- Benchmark 测试组件
(1, 'Media', 'ffmpeg'),
(1, 'Media', 'gstreamer'),
(1, 'Compute', 'clpeak'),
(1, 'Compute', 'rocm-bandwidth'),
(1, 'Graphics', 'glmark2'),
(1, 'Graphics', 'unigine-heaven'),

-- Functional 测试组件
(2, 'Media', 'vainfo'),
(2, 'Graphics', 'glxgears'),
(2, 'Graphics', 'vkcube'),
(2, 'Compute', 'rocminfo'),

-- Performance 测试组件
(3, 'Gaming', 'unigine-superposition'),
(3, 'Compute', 'hip-samples'),

-- Stress 测试组件
(4, 'Compute', 'stress-ng'),
(4, 'Memory', 'memtester'),

-- Stability 测试组件
(5, 'System', 'stability-test');

-- ============================================================================
-- 6. 测试用例数据 (Test Cases) - 30条
-- ============================================================================
INSERT INTO test_cases (test_component_id, case_name, case_config, created_at, updated_at)
VALUES
-- ffmpeg 测试用例 (组件ID: 1)
(1, 'H.264 4K Encoding', '{"resolution": "3840x2160", "codec": "h264", "bitrate": "20M", "preset": "medium", "iterations": 100}', NOW(), NOW()),
(1, 'H.265 4K Encoding', '{"resolution": "3840x2160", "codec": "hevc", "bitrate": "15M", "preset": "medium", "iterations": 50}', NOW(), NOW()),
(1, 'H.264 1080p Encoding', '{"resolution": "1920x1080", "codec": "h264", "bitrate": "8M", "preset": "fast", "iterations": 200}', NOW(), NOW()),
(1, 'VP9 4K Encoding', '{"resolution": "3840x2160", "codec": "vp9", "bitrate": "18M", "iterations": 50}', NOW(), NOW()),

-- gstreamer 测试用例 (组件ID: 2)
(2, 'H.264 Decode Pipeline', '{"pipeline": "vaapih264dec", "resolution": "3840x2160", "iterations": 100}', NOW(), NOW()),
(2, 'H.265 Decode Pipeline', '{"pipeline": "vaapih265dec", "resolution": "3840x2160", "iterations": 50}', NOW(), NOW()),

-- clpeak 测试用例 (组件ID: 3)
(3, 'OpenCL Compute SP', '{"test_types": ["compute_sp", "global_bandwidth"], "iterations": 10}', NOW(), NOW()),
(3, 'OpenCL Compute DP', '{"test_types": ["compute_dp", "global_bandwidth"], "iterations": 10}', NOW(), NOW()),
(3, 'OpenCL Transfer Bandwidth', '{"test_types": ["transfer_bandwidth"], "iterations": 20}', NOW(), NOW()),

-- rocm-bandwidth 测试用例 (组件ID: 4)
(4, 'ROCm Memory Bandwidth', '{"test_type": "memory", "iterations": 10}', NOW(), NOW()),
(4, 'ROCm PCIe Bandwidth', '{"test_type": "pcie", "iterations": 10}', NOW(), NOW()),

-- glmark2 测试用例 (组件ID: 5)
(5, 'OpenGL Benchmark Full', '{"preset": "full", "resolution": "1920x1080"}', NOW(), NOW()),
(5, 'OpenGL Benchmark Medium', '{"preset": "medium", "resolution": "2560x1440"}', NOW(), NOW()),

-- unigine-heaven 测试用例 (组件ID: 6)
(6, '3D Graphics Ultra', '{"preset": "ultra", "resolution": "2560x1440", "fullscreen": true, "duration": 300}', NOW(), NOW()),
(6, '3D Graphics High', '{"preset": "high", "resolution": "1920x1080", "fullscreen": true, "duration": 300}', NOW(), NOW()),

-- vainfo 测试用例 (组件ID: 7)
(7, 'VA-API Profile Check', '{"check_profiles": ["VAProfileH264Main", "VAProfileH264High", "VAProfileHEVCMain"]}', NOW(), NOW()),

-- glxgears 测试用例 (组件ID: 8)
(8, 'OpenGL Basic Test', '{"duration": 30, "resolution": "1920x1080", "fullscreen": false}', NOW(), NOW()),
(8, 'OpenGL Fullscreen Test', '{"duration": 60, "resolution": "2560x1440", "fullscreen": true}', NOW(), NOW()),

-- vkcube 测试用例 (组件ID: 9)
(9, 'Vulkan Basic Test', '{"duration": 30}', NOW(), NOW()),

-- rocminfo 测试用例 (组件ID: 10)
(10, 'ROCm Platform Info', '{}', NOW(), NOW()),

-- unigine-superposition 测试用例 (组件ID: 11)
(11, 'Superposition 4K Optimized', '{"preset": "4K Optimized", "duration": 300}', NOW(), NOW()),
(11, 'Superposition 1080p Extreme', '{"preset": "1080p Extreme", "duration": 300}', NOW(), NOW()),

-- hip-samples 测试用例 (组件ID: 12)
(12, 'HIP Matrix Multiply', '{"matrix_size": 4096, "iterations": 100}', NOW(), NOW()),
(12, 'HIP Vector Add', '{"vector_size": 1048576, "iterations": 1000}', NOW(), NOW()),

-- stress-ng 测试用例 (组件ID: 13)
(13, 'GPU Memory Stress', '{"duration": 3600, "workers": 4, "memory_percentage": 90}', NOW(), NOW()),
(13, 'GPU Load Stress', '{"duration": 7200, "workers": 8, "test_methods": ["gpu-load", "gpu-mem"]}', NOW(), NOW()),

-- memtester 测试用例 (组件ID: 14)
(14, 'Memory Test 8GB', '{"size": "8G", "iterations": 10}', NOW(), NOW()),

-- stability-test 测试用例 (组件ID: 15)
(15, '24h Stability Test', '{"duration": 86400, "mixed_workload": true}', NOW(), NOW()),
(15, '48h Stability Test', '{"duration": 172800, "mixed_workload": true}', NOW(), NOW()),
(15, '72h Stability Test', '{"duration": 259200, "mixed_workload": true}', NOW(), NOW());

-- ============================================================================
-- 7. 测试计划数据 (Test Plans) - 20条
-- ============================================================================
INSERT INTO test_plans (plan_name, plan_description, sut_device_id, os_config_id, created_by, created_at, updated_at)
VALUES
-- APU 测试计划
('APU Aerith-0 Ubuntu 20.04 Benchmark', 'APU设备基准性能测试', 1, 1, 'qa_team', NOW(), NOW()),
('APU Aerith-1 Ubuntu 22.04 Full Test', 'APU设备完整功能测试', 2, 2, 'qa_team', NOW(), NOW()),
('APU Aerith-2 Ubuntu 24.04 Compatibility', 'APU新系统兼容性测试', 3, 3, 'qa_team', NOW(), NOW()),

-- Navi 31 测试计划
('RX 7900 XTX Media Benchmark', 'RX 7900 XTX 媒体编码性能测试', 4, 2, 'media_team', NOW(), NOW()),
('RX 7900 XTX Compute Performance', 'RX 7900 XTX 计算性能测试', 4, 2, 'compute_team', NOW(), NOW()),
('RX 7900 XTX Gaming Benchmark', 'RX 7900 XTX 游戏性能测试', 4, 2, 'gaming_team', NOW(), NOW()),
('RX 7900 XTX Stress Test', 'RX 7900 XTX 压力稳定性测试', 5, 2, 'stability_team', NOW(), NOW()),
('RX 7900 XT Full Validation', 'RX 7900 XT 完整验证测试', 6, 2, 'qa_team', NOW(), NOW()),
('RX 7900 XTX Multi-OS Test', 'RX 7900 XTX 多操作系统测试', 4, 4, 'qa_team', NOW(), NOW()),
('RX 7900 XTX Fedora Test', 'RX 7900 XTX Fedora系统测试', 5, 6, 'qa_team', NOW(), NOW()),

-- Navi 32 测试计划
('RX 7800 XT Benchmark Suite', 'RX 7800 XT 基准测试套件', 7, 2, 'qa_team', NOW(), NOW()),
('RX 7800 XT OpenCL Test', 'RX 7800 XT OpenCL性能测试', 7, 2, 'compute_team', NOW(), NOW()),
('RX 7700 XT Media Test', 'RX 7700 XT 媒体处理测试', 8, 2, 'media_team', NOW(), NOW()),
('RX 7700 XT Graphics Test', 'RX 7700 XT 图形渲染测试', 8, 3, 'gaming_team', NOW(), NOW()),

-- Navi 33 测试计划
('RX 7600 Entry Level Test', 'RX 7600 入门级性能测试', 9, 2, 'qa_team', NOW(), NOW()),
('RX 7600 XT Gaming Test', 'RX 7600 XT 游戏性能测试', 10, 2, 'gaming_team', NOW(), NOW()),
('RX 7600 Compute Test', 'RX 7600 计算性能测试', 9, 2, 'compute_team', NOW(), NOW()),

-- 混合测试计划
('Multi-GPU Comparison Test', '多GPU对比测试', 4, 2, 'benchmark_team', NOW(), NOW()),
('Cross-Platform Validation', '跨平台验证测试', 4, 5, 'qa_team', NOW(), NOW()),
('Long-term Stability Test', '长期稳定性测试', 5, 2, 'stability_team', NOW(), NOW());

-- ============================================================================
-- 8. 测试计划与用例关联数据 (Test Plan Cases) - 100+条
-- ============================================================================

-- 计划1: APU Aerith-0 Benchmark (基础媒体测试)
INSERT INTO test_plan_cases (test_plan_id, test_case_id, timeout)
VALUES
(1, 1, 300),  -- H.264 4K Encoding
(1, 3, 200),  -- H.264 1080p Encoding
(1, 7, 180),  -- OpenCL Compute SP
(1, 12, 120), -- OpenGL Benchmark Full
(1, 18, 60);  -- OpenGL Basic Test

-- 计划2: APU Aerith-1 Full Test (完整功能测试)
INSERT INTO test_plan_cases (test_plan_id, test_case_id, timeout)
VALUES
(2, 1, 300),
(2, 2, 600),
(2, 5, 300),
(2, 7, 180),
(2, 8, 180),
(2, 12, 120),
(2, 16, 30),
(2, 18, 60),
(2, 20, 30);

-- 计划3: APU Compatibility (兼容性测试)
INSERT INTO test_plan_cases (test_plan_id, test_case_id, timeout)
VALUES
(3, 16, 30),
(3, 18, 60),
(3, 20, 30),
(3, 21, 30);

-- 计划4: RX 7900 XTX Media Benchmark (媒体编码性能)
INSERT INTO test_plan_cases (test_plan_id, test_case_id, timeout)
VALUES
(4, 1, 300),
(4, 2, 600),
(4, 3, 200),
(4, 4, 600),
(4, 5, 300),
(4, 6, 300);

-- 计划5: RX 7900 XTX Compute Performance (计算性能)
INSERT INTO test_plan_cases (test_plan_id, test_case_id, timeout)
VALUES
(5, 7, 180),
(5, 8, 180),
(5, 9, 240),
(5, 10, 120),
(5, 11, 120),
(5, 23, 300),
(5, 24, 300);

-- 计划6: RX 7900 XTX Gaming Benchmark (游戏性能)
INSERT INTO test_plan_cases (test_plan_id, test_case_id, timeout)
VALUES
(6, 12, 120),
(6, 13, 120),
(6, 14, 600),
(6, 15, 600),
(6, 22, 600),
(6, 23, 600);

-- 计划7: RX 7900 XTX Stress Test (压力测试)
INSERT INTO test_plan_cases (test_plan_id, test_case_id, timeout)
VALUES
(7, 25, 3600),
(7, 26, 7200),
(7, 27, 1200),
(7, 28, 86400);

-- 计划8: RX 7900 XT Full Validation (完整验证)
INSERT INTO test_plan_cases (test_plan_id, test_case_id, timeout)
VALUES
(8, 1, 300),
(8, 2, 600),
(8, 7, 180),
(8, 8, 180),
(8, 12, 120),
(8, 14, 600),
(8, 16, 30),
(8, 18, 60),
(8, 21, 30),
(8, 25, 3600);

-- 计划9: RX 7900 XTX Multi-OS Test
INSERT INTO test_plan_cases (test_plan_id, test_case_id, timeout)
VALUES
(9, 1, 300),
(9, 7, 180),
(9, 18, 60),
(9, 21, 30);

-- 计划10: RX 7900 XTX Fedora Test
INSERT INTO test_plan_cases (test_plan_id, test_case_id, timeout)
VALUES
(10, 1, 300),
(10, 7, 180),
(10, 12, 120),
(10, 18, 60);

-- 计划11: RX 7800 XT Benchmark Suite
INSERT INTO test_plan_cases (test_plan_id, test_case_id, timeout)
VALUES
(11, 1, 300),
(11, 2, 600),
(11, 7, 180),
(11, 12, 120),
(11, 14, 600);

-- 计划12: RX 7800 XT OpenCL Test
INSERT INTO test_plan_cases (test_plan_id, test_case_id, timeout)
VALUES
(12, 7, 180),
(12, 8, 180),
(12, 9, 240),
(12, 21, 30);

-- 计划13: RX 7700 XT Media Test
INSERT INTO test_plan_cases (test_plan_id, test_case_id, timeout)
VALUES
(13, 1, 300),
(13, 2, 600),
(13, 3, 200),
(13, 5, 300);

-- 计划14: RX 7700 XT Graphics Test
INSERT INTO test_plan_cases (test_plan_id, test_case_id, timeout)
VALUES
(14, 12, 120),
(14, 13, 120),
(14, 18, 60),
(14, 19, 120),
(14, 20, 30);

-- 计划15: RX 7600 Entry Level Test
INSERT INTO test_plan_cases (test_plan_id, test_case_id, timeout)
VALUES
(15, 3, 200),
(15, 7, 180),
(15, 12, 120),
(15, 18, 60);

-- 计划16: RX 7600 XT Gaming Test
INSERT INTO test_plan_cases (test_plan_id, test_case_id, timeout)
VALUES
(16, 12, 120),
(16, 13, 120),
(16, 14, 600),
(16, 18, 60);

-- 计划17: RX 7600 Compute Test
INSERT INTO test_plan_cases (test_plan_id, test_case_id, timeout)
VALUES
(17, 7, 180),
(17, 8, 180),
(17, 10, 120),
(17, 21, 30);

-- 计划18: Multi-GPU Comparison Test
INSERT INTO test_plan_cases (test_plan_id, test_case_id, timeout)
VALUES
(18, 1, 300),
(18, 7, 180),
(18, 12, 120),
(18, 14, 600);

-- 计划19: Cross-Platform Validation
INSERT INTO test_plan_cases (test_plan_id, test_case_id, timeout)
VALUES
(19, 1, 300),
(19, 7, 180),
(19, 16, 30),
(19, 18, 60),
(19, 21, 30);

-- 计划20: Long-term Stability Test
INSERT INTO test_plan_cases (test_plan_id, test_case_id, timeout)
VALUES
(20, 28, 86400),
(20, 29, 172800),
(20, 30, 259200);

-- ============================================================================
-- 数据统计
-- ============================================================================
-- 测试设备:        10 条
-- 操作系统配置:    8 条
-- 内核版本:        12 条
-- 测试类型:        6 条
-- 测试组件:        15 条
-- 测试用例:        30 条
-- 测试计划:        20 条
-- 计划-用例关联:   100+ 条
-- ============================================================================
-- 总计:            约 200+ 条数据记录
-- ============================================================================

-- 查询示例
-- 查看所有测试计划及其用例数量
-- SELECT tp.id, tp.plan_name, sd.hostname, oc.os_family, oc.version, COUNT(tpc.id) as case_count
-- FROM test_plans tp
-- JOIN sut_devices sd ON tp.sut_device_id = sd.id
-- JOIN os_configs oc ON tp.os_config_id = oc.id
-- LEFT JOIN test_plan_cases tpc ON tp.id = tpc.test_plan_id
-- GROUP BY tp.id, tp.plan_name, sd.hostname, oc.os_family, oc.version
-- ORDER BY tp.id;

-- 查看特定设备的所有测试计划
-- SELECT * FROM test_plans WHERE sut_device_id = 4;

-- 查看特定测试计划的所有用例
-- SELECT tc.case_name, tcom.component_name, tt.type_name, tpc.timeout
-- FROM test_plan_cases tpc
-- JOIN test_cases tc ON tpc.test_case_id = tc.id
-- JOIN test_components tcom ON tc.test_component_id = tcom.id
-- JOIN test_types tt ON tcom.test_type_id = tt.id
-- WHERE tpc.test_plan_id = 4;

