/**
 * 将 JavaScript 对象转换为 YAML 字符串
 * @param obj 要转换的对象
 * @param indent 缩进级别（默认为 0）
 * @returns YAML 格式的字符串
 */
export function jsToYaml(obj: any, indent = 0): string {
  let yaml = ''
  const spaces = '  '.repeat(indent)
  const entries = Object.entries(obj)

  entries.forEach(([key, value], index) => {
    if (Array.isArray(value)) {
      yaml += `${spaces}${key}:\n`
      value.forEach((item) => {
        if (typeof item === 'object' && item !== null) {
          // 为数组项生成 YAML，使用 indent + 2 来确保正确的缩进
          const itemYaml = jsToYaml(item, indent + 2)
          const lines = itemYaml.split('\n').filter(l => l.length > 0)
          
          // 第一行前面加 "- "
          if (lines.length > 0) {
            // 移除第一行原有的缩进，因为我们要加 "- "
            const firstLine = lines[0].substring((indent + 2) * 2)
            yaml += `${spaces}  - ${firstLine}\n`
            
            // 后续行保持原有缩进
            for (let i = 1; i < lines.length; i++) {
              yaml += `${lines[i]}\n`
            }
          }
        }
        else {
          yaml += `${spaces}  - ${item}\n`
        }
      })
    }
    else if (typeof value === 'object' && value !== null) {
      yaml += `${spaces}${key}:\n${jsToYaml(value, indent + 1)}`
    }
    else {
      yaml += `${spaces}${key}: ${value}\n`
    }

    // 在顶层（indent = 0）的各部分之间添加空行，使 YAML 更易读
    if (indent === 0 && index < entries.length - 1) {
      yaml += '\n'
    }
  })

  return yaml
}

