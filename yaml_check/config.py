"""
YAML 验证规则配置
"""

# E001: 必需的根键
REQUIRED_ROOT_KEYS = [
    'metadata.generated'
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
    'order': 'int',
    'ipAddress': 'IPv4',
}


# E102: 值范围配置（白名单） 依赖yaml确定后再来改
VALUE_RANGE_CONFIG = {
    # 'hardware.cpu': ['Ryzen Threadripper', 'Ryzen 7', 'Ryzen 9', 'EPYC'],
}

