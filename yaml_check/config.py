"""
YAML 验证规则配置
"""
REQUIRED_ROOT_KEYS = [
    # ========== Metadata（元数据） ==========
    'metadata.generated',           # 生成时间戳
    'metadata.version',             # 配置版本号
    'metadata.description',         # 配置描述信息

    
    # ========== Hardware（硬件配置） ==========
    'hardware.machines',            # 机器列表（数组）
    # hardware.machines 数组中每项的必需字段：
    'hardware.machines[].id',       # 机器ID
    'hardware.machines[].hostname', # 主机名
    'hardware.machines[].productName', # 产品名称
    'hardware.machines[].asicName', # ASIC名称
    'hardware.machines[].ipAddress', # IP地址（如果是可选的，可以移除）
    'hardware.machines[].gpuModel', # GPU型号（如果是可选的，可以移除）
    
    # ========== Environment（环境配置） ==========
    'environment.machines',         # 机器环境配置（对象）
    # environment.machines 下每个机器的必需字段：
    # 注意：机器名是动态的（如 navi10-test-01），所以需要用通配符或特殊处理
    'environment.machines.*.configurations', # 配置列表（数组）
    
    # configurations 数组中每项的必需字段：
    'environment.machines.*.configurations[].config_id',          # 配置ID
    'environment.machines.*.configurations[].os',                 # 操作系统对象
    'environment.machines.*.configurations[].os.id',              # OS ID
    'environment.machines.*.configurations[].os.family',          # OS系列
    'environment.machines.*.configurations[].os.version',         # OS版本
    'environment.machines.*.configurations[].deployment_method',  # 部署方法
    'environment.machines.*.configurations[].kernel',             # 内核对象
    'environment.machines.*.configurations[].kernel.kernel_version', # 内核版本
    'environment.machines.*.configurations[].test_type',          # 测试类型
    'environment.machines.*.configurations[].execution_case_list', # 执行用例列表（数组）
]

# E002: 
#1 不能为空的键
#无需配置 逻辑已写在函数中，即yaml转为的json再转为jsonl后，每条jsonl都要有值，如果有值为空，则验证不通过

#2 可以为空的键
CAN_BE_EMPTY_KEYS = [
    'description',
]

# E101: 值类型配置 
VALUE_TYPE_CONFIG = {
    'id': 'int',
    'ipAddress': 'IPv4',
    # 'ipAddress': 'int',
}

# E102: 值范围配置（白名单） 预留接口，短期内不需要使能这个功能
VALUE_RANGE_CONFIG = {
    # 'hardware.cpu': [],
}

