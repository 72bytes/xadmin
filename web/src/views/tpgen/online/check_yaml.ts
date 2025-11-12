// ============================================================================
// Compatibility Analysis Functions (TypeScript Version)
// ============================================================================

/**
 * Types and Interfaces
 */

type ValueType = 'string' | 'int' | 'number' | 'boolean' | 'array' | 'object' | 'null'

interface ValidationResult {
  valid: boolean
  errorCode: string
  errorMessage: string
}

interface YamlData {
  [key: string]: any
}

interface ValueTypeConfig {
  [key: string]: ValueType
}

interface ValueRangeConfig {
  [key: string]: string[]
}

/**
 * Configuration Rules (from backend/config/*.yaml)
 */

// Required Root Keys (E001)
const REQUIRED_ROOT_KEYS: string[] = ['hardware.cpu', 'hardware.gpu']

// Mandatory Non-Empty Keys (E002)
const MANDATORY_NON_EMPTY_KEYS: string[] = ['hardware.machines', 'test_suites']

// Value Type Configuration (E101)
const VALUE_TYPE_CONFIG: ValueTypeConfig = {
  'hardware.cpu': 'string',
}

// Value Range Configuration (E102)
const VALUE_RANGE_CONFIG: ValueRangeConfig = {
  'hardware.cpu': ['Ryzen Threadripper', 'Ryzen 7', 'Ryzen 9', 'EPYC'],
}

/**
 * Helper Functions
 */

// Check if a value is empty
function isEmpty(value: any): boolean {
  if (value === null || value === undefined) return true
  if (typeof value === 'string' && value.trim() === '') return true
  if (Array.isArray(value) && value.length === 0) return true
  if (typeof value === 'object' && Object.keys(value).length === 0) return true
  return false
}

// Get nested value from object using dot notation path
function getNestedValue(obj: YamlData, path: string): any {
  return path.split('.').reduce((current: any, key: string) => {
    return current && current[key] !== undefined ? current[key] : undefined
  }, obj)
}

// Check if key exists in object (at any depth)
function hasKey(obj: YamlData, key: string): boolean {
  if (!obj || typeof obj !== 'object') return false
  if (obj.hasOwnProperty(key)) return true

  for (const k in obj) {
    if (obj.hasOwnProperty(k) && typeof obj[k] === 'object') {
      if (hasKey(obj[k], key)) return true
    }
  }
  return false
}

// Get value type as string
function getValueType(value: any): string {
  if (value === null) return 'null'
  if (Array.isArray(value)) return 'array'
  return typeof value
}

/**
 * Validation Functions
 */

// Validate E001: Check for missing mandatory root keys
function validateRequiredRootKeys(yamlData: YamlData): ValidationResult {
  for (const key of REQUIRED_ROOT_KEYS) {
    // Support both dot notation (e.g., 'hardware.cpu') and simple keys (e.g., 'cpu')
    let exists = false
    if (key.includes('.')) {
      // For dot notation, use getNestedValue
      const value = getNestedValue(yamlData, key)
      exists = value !== undefined
    } else {
      // For simple keys, use hasKey
      exists = hasKey(yamlData, key)
    }

    if (!exists) {
      return {
        valid: false,
        errorCode: `E001 Unsupported: missing mandatory key [${key}]`,
        errorMessage: `E001 Unsupported: missing mandatory key [${key}]`,
      }
    }
  }
  return { valid: true, errorCode: '0', errorMessage: 'OK' }
}

// Validate E002: Check for empty mandatory keys
function validateMandatoryNonEmptyKeys(yamlData: YamlData): ValidationResult {
  for (const key of MANDATORY_NON_EMPTY_KEYS) {
    // Support both dot notation (e.g., 'hardware.machines') and simple keys (e.g., 'machines')
    let value: any
    if (key.includes('.')) {
      // For dot notation, use getNestedValue
      value = getNestedValue(yamlData, key)
    } else {
      // For simple keys, try multiple fallbacks
      value = getNestedValue(yamlData, key)
      || (yamlData.hardware && yamlData.hardware[key])
      || yamlData[key]
    }

    if (value === undefined) {
      return {
        valid: false,
        errorCode: `E002 Unsupported: empty value for [${key}]`,
        errorMessage: `E002 Unsupported: empty value for [${key}]`,
      }
    }

    if (isEmpty(value)) {
      return {
        valid: false,
        errorCode: `E002 Unsupported: empty value for [${key}]`,
        errorMessage: `E002 Unsupported: empty value for [${key}]`,
      }
    }
  }
  return { valid: true, errorCode: '0', errorMessage: 'OK' }
}

// Validate E101: Check value types
function validateValueTypes(yamlData: YamlData): ValidationResult {
  for (const [key, expectedType] of Object.entries(VALUE_TYPE_CONFIG)) {
    // Support both dot notation and simple keys
    let value: any
    if (key.includes('.')) {
      value = getNestedValue(yamlData, key)
    } else {
      value = getNestedValue(yamlData, key)
      || (yamlData.hardware && yamlData.hardware[key])
      || yamlData[key]
    }

    if (value === undefined) continue

    const actualType = getValueType(value)
    const typeMap: Record<string, string[]> = {
      string: ['string'],
      int: ['number'],
      number: ['number'],
      boolean: ['boolean'],
      array: ['array'],
      object: ['object'],
    }

    const validTypes = typeMap[expectedType] || [expectedType]

    if (!validTypes.includes(actualType)) {
      return {
        valid: false,
        errorCode: `E101 Unsupported: value type error for [${key}]. Expected ${expectedType}, got ${actualType}`,
        errorMessage: `E101 Unsupported: value type error for [${key}]. Expected ${expectedType}, got ${actualType}`,
      }
    }
  }
  return { valid: true, errorCode: '0', errorMessage: 'OK' }
}

// Validate E102: Check value ranges (whitelist)
function validateValueRanges(yamlData: YamlData): ValidationResult {
  for (const [key, allowedValues] of Object.entries(VALUE_RANGE_CONFIG)) {
    // Support both dot notation and simple keys
    let value: any
    if (key.includes('.')) {
      value = getNestedValue(yamlData, key)
    } else {
      value = getNestedValue(yamlData, key)
      || (yamlData.hardware && yamlData.hardware[key])
      || yamlData[key]
    }

    if (value === undefined) continue

    if (!allowedValues.includes(value)) {
      return {
        valid: false,
        errorCode: `E102 Unsupported: invalid value range for [${key}]. Value "${value}" is not in whitelist [${allowedValues.join(', ')}]`,
        errorMessage: `E102 Unsupported: invalid value range for [${key}]. Value "${value}" is not in whitelist [${allowedValues.join(', ')}]`,
      }
    }
  }
  return { valid: true, errorCode: '0', errorMessage: 'OK' }
}

/**
 * Main Compatibility Analysis Function
 *
 * @param yamlData - Parsed YAML object to validate
 * @returns Result in format "bool:errorCode"
 *          - Success: "True:0"
 *          - Failure: "False:E001", "False:E002", "False:E101", "False:E102", "False:E300"
 */
function compatibility_analysis(yamlData: YamlData): string {
  try {
    // Input validation
    if (!yamlData || typeof yamlData !== 'object') {
      return 'False:E000'
    }

    // Step 1: Validate required root keys (E001)
    const rootKeysResult = validateRequiredRootKeys(yamlData)
    if (!rootKeysResult.valid) {
      console.error(`[${rootKeysResult.errorCode}] ${rootKeysResult.errorMessage}`)
      return `False:${rootKeysResult.errorCode}`
    }

    // Step 2: Validate mandatory non-empty keys (E002)
    const nonEmptyKeysResult = validateMandatoryNonEmptyKeys(yamlData)
    if (!nonEmptyKeysResult.valid) {
      console.error(`[${nonEmptyKeysResult.errorCode}] ${nonEmptyKeysResult.errorMessage}`)
      return `False:${nonEmptyKeysResult.errorCode}`
    }

    // Step 3: Validate value types (E101)
    const valueTypesResult = validateValueTypes(yamlData)
    if (!valueTypesResult.valid) {
      console.error(`[${valueTypesResult.errorCode}] ${valueTypesResult.errorMessage}`)
      return `False:${valueTypesResult.errorCode}`
    }

    // Step 4: Validate value ranges (E102)
    const valueRangesResult = validateValueRanges(yamlData)
    if (!valueRangesResult.valid) {
      console.error(`[${valueRangesResult.errorCode}] ${valueRangesResult.errorMessage}`)
      return `False:${valueRangesResult.errorCode}`
    }

    // All validations passed
    console.log('[SUCCESS] Compatibility analysis passed')
    return 'True:0'
  } catch (error) {
    console.error('[ERROR] Compatibility analysis failed with exception:', error)
    return 'False:E999'
  }
}

// ============================================================================
// End of Compatibility Analysis Functions
// ============================================================================

/**
 * Browser-specific functions (require DOM and external dependencies)
 * Note: These need to be adapted for use in a TypeScript/Vue environment
 */

interface YamlValidationResult {
  valid: boolean
  lineNumber?: number
}

/**
 * Show notification message
 * @param message - The message to display
 * @param type - Notification type: 'success' or 'error'
 */
function showNotification(message: string, type: 'success' | 'error' = 'success'): void {
  // Get or create notification element
  let notification = document.getElementById('yaml-notification') as HTMLDivElement | null

  if (!notification) {
    // Create notification element if it doesn't exist
    notification = document.createElement('div')
    notification.id = 'yaml-notification'
    notification.className = 'notification'

    // Add styles
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 15px 25px;
      border-radius: 8px;
      background-color: #52c41a;
      color: white;
      font-size: 14px;
      font-weight: 500;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      z-index: 9999;
      display: none;
      animation: slideInRight 0.3s ease-out;
      max-width: 400px;
      word-wrap: break-word;
    `

    document.body.appendChild(notification)
  }

  // Set message
  notification.textContent = message

  // Reset classes
  notification.className = 'notification'

  // Apply error style if needed
  if (type === 'error') {
    notification.classList.add('error')
    notification.style.backgroundColor = '#ff4d4f'
  } else {
    notification.style.backgroundColor = '#52c41a'
  }

  // Show notification
  notification.style.display = 'block'

  // Hide after 3 seconds
  setTimeout(() => {
    if (notification) {
      notification.style.display = 'none'
    }
  }, 3000)
}

// Type declarations for external libraries (should be installed separately)
declare const jsyaml: any
declare function isValidYAML(text: string): YamlValidationResult
declare function findLineNumberInYAML(text: string, errorCode: string): number | null
declare const yamlContent: HTMLElement

// Download YAML file
function downloadYAML(): void {
  try {
    const yamlText = yamlContent.textContent || ''

    // 测试1：空内容
    // let yamlText = '';

    // 测试2：错误格式 - 选择以下任意一个测试
    // let yamlText = 'key: value\n  bad indent: value';  // 缩进错误
    // let yamlText = 'key: "unclosed string';  // 未闭合引号
    // let yamlText = 'key: value\n:\ninvalid';  // 无效键
    // let yamlText = 'key: [1, 2, 3';  // 未闭合数组
    // let yamlText = 'key:\n\tbad_tab: value';  // Tab字符（YAML不允许）

    // 调试信息
    console.log('yamlText length:', yamlText ? yamlText.length : 'null/undefined')
    console.log('yamlText content:', yamlText)

    // Check if YAML content is empty
    if (!yamlText || yamlText.trim().length === 0) {
      showNotification('Test plan download failed!\nContent empty!', 'error')
      return
    }

    // Check for format errors (basic validation)
    // Check if content contains "Error:" which indicates generation error
    const validationResult = isValidYAML(yamlText)
    if (!validationResult.valid) {
      const lineInfo = validationResult.lineNumber ? `line ${validationResult.lineNumber}\n` : ''
      showNotification(`Test plan download failed!\n${lineInfo}Invalid yaml format!`, 'error')
      return
    }

    // Perform compatibility analysis if parsing succeeded
    if (yamlText) {
      // Parse YAML text to object first
      let yamlDataObject: YamlData | null = null
      try {
        if (typeof jsyaml !== 'undefined') {
          yamlDataObject = jsyaml.load(yamlText)
        } else {
          console.warn('js-yaml library not loaded, skipping compatibility check')
        }
      } catch (parseError) {
        console.error('YAML parse error for compatibility check:', parseError)
        showNotification('Test plan download failed!\nYAML parse error!', 'error')
        return
      }

      // Run compatibility analysis on parsed object
      if (yamlDataObject) {
        const compatResult = compatibility_analysis(yamlDataObject)
        // Split only at the first colon to preserve complete error message
        const colonIndex = compatResult.indexOf(':')
        const isValid = compatResult.substring(0, colonIndex)
        const errorCode = compatResult.substring(colonIndex + 1)

        if (isValid === 'False') {
          console.error(`Compatibility check failed: ${errorCode}`)
          const lineNumber = findLineNumberInYAML(yamlText, errorCode)
          const lineInfo = lineNumber ? `line ${lineNumber}\n` : ''
          showNotification(`Test plan download failed!\n${lineInfo}Compatibility error!\n${errorCode}`, 'error')
          return
        }
      }
    }

    // Generate filename with current date and time
    const now = new Date()
    const year = now.getFullYear()
    const month = String(now.getMonth() + 1).padStart(2, '0')
    const day = String(now.getDate()).padStart(2, '0')
    const hours = String(now.getHours()).padStart(2, '0')
    const minutes = String(now.getMinutes()).padStart(2, '0')
    const seconds = String(now.getSeconds()).padStart(2, '0')
    const filename = `test_plan_${year}-${month}-${day}_${hours}${minutes}${seconds}.yaml`

    const blob = new Blob([yamlText], { type: 'text/yaml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    showNotification('Test plan download success!')
  } catch (error) {
    console.error('Download error:', error)
    showNotification('Test plan download failed!\nPlease try later!', 'error')
  }
}

// Copy YAML to clipboard
function copyToClipboard(): void {
  try {
    const yamlText = yamlContent.textContent || ''
    // let yamlText = '';
    // let yamlText = 'key:\n\tbad_tab: value';  // Tab字符（YAML不允许）

    // Check if YAML content is empty
    if (!yamlText || yamlText.trim().length === 0) {
      showNotification('Test plan copy failed!\nContent Empty!', 'error')
      return
    }

    // Check for format errors using isValidYAML function
    const validationResult = isValidYAML(yamlText)
    if (!validationResult.valid) {
      const lineInfo = validationResult.lineNumber ? `line ${validationResult.lineNumber}\n` : ''
      showNotification(`Test plan copy failed!\n${lineInfo}Invalid format!`, 'error')
      return
    }

    // Check if Clipboard API is supported (Browser compatibility)
    if (!navigator.clipboard) {
      showNotification('Test plan copy failed!\nBrowser not supported!', 'error')
      return
    }

    // Check if running in secure context (HTTPS or localhost)
    if (!window.isSecureContext) {
      showNotification('Test plan copy failed!\nHTTPS required for clipboard access!', 'error')
      return
    }

    // Parse YAML text back to object for compatibility analysis
    let yamlDataObject: YamlData | null = null
    try {
      if (typeof jsyaml !== 'undefined') {
        yamlDataObject = jsyaml.load(yamlText)
      }
    } catch (parseError) {
      console.error('YAML parse error for compatibility check:', parseError)
      // If parsing fails, continue with copy (format already validated above)
    }

    // Perform compatibility analysis if parsing succeeded
    if (yamlDataObject) {
      const compatResult = compatibility_analysis(yamlDataObject)
      // Split only at the first colon to preserve complete error message
      const colonIndex = compatResult.indexOf(':')
      const isValid = compatResult.substring(0, colonIndex)
      const errorCode = compatResult.substring(colonIndex + 1)

      if (isValid === 'False') {
        console.error(`Compatibility check failed: ${errorCode}`)
        const lineNumber = findLineNumberInYAML(yamlText, errorCode)
        const lineInfo = lineNumber ? `line ${lineNumber}\n` : ''
        showNotification(`Test plan copy failed!\n${lineInfo}Compatibility error!\n${errorCode}`, 'error')
        return
      }
    }

    // Attempt to copy to clipboard
    navigator.clipboard.writeText(yamlText).then(() => {
      showNotification('Test plan copied to clipboard!')
    }).catch((error) => {
      console.error('Clipboard copy error:', error)
      showNotification('Test plan copy failed!\nUnknown error occurred!', 'error')
    })
  } catch (error) {
    console.error('Copy function error:', error)
    showNotification('Test plan copy failed!\nUnknown error occurred!', 'error')
  }
}

// Export functions for use in modules
export {
  compatibility_analysis,
  downloadYAML,
  copyToClipboard,
  showNotification,
  validateRequiredRootKeys,
  validateMandatoryNonEmptyKeys,
  validateValueTypes,
  validateValueRanges,
  isEmpty,
  getNestedValue,
  hasKey,
  getValueType,
}

// For non-module usage
export type {
  ValidationResult,
  YamlData,
  ValueTypeConfig,
  ValueRangeConfig,
  YamlValidationResult,
}
