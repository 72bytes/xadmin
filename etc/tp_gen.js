// Mock data for test machines
const mockMachines = [
    { id: 1, name: "Machine A", motherboard: "ASUS Pro WS X570-ACE", gpu: "Radeon RX 7900 Series", cpu: "Ryzen Threadripper", status: "Available" },
    { id: 2, name: "Machine B", motherboard: "Gigabyte B550 AORUS", gpu: "Radeon RX 7900 Series", cpu: "Ryzen Threadripper", status: "Available" },
    { id: 3, name: "Machine C", motherboard: "ASRock X570 Taichi", gpu: "Radeon RX 6800 Series", cpu: "Ryzen 7", status: "Available" },
    { id: 4, name: "Machine D", motherboard: "MSI MEG X570 GODLIKE", gpu: "Radeon Pro W7800", cpu: "EPYC", status: "Available" },
    { id: 5, name: "Machine E", motherboard: "ASUS Pro WS X570-ACE", gpu: "Radeon Pro W6800", cpu: "Ryzen Threadripper", status: "Available" },
    { id: 6, name: "Machine F", motherboard: "Gigabyte B550 AORUS", gpu: "Radeon RX 6800 Series", cpu: "Ryzen 9", status: "Available" },
    { id: 7, name: "Machine G", motherboard: "ASRock X570 Taichi", gpu: "Radeon RX 7900 Series", cpu: "EPYC", status: "Available" },
    { id: 8, name: "Machine H", motherboard: "MSI MEG X570 GODLIKE", gpu: "Radeon Pro W6800", cpu: "Ryzen 7", status: "Available" },
    { id: 9, name: "Machine I", motherboard: "ASUS Pro WS X570-ACE", gpu: "Radeon RX 6800 Series", cpu: "Ryzen Threadripper", status: "Available" },
    { id: 10, name: "Machine J", motherboard: "Gigabyte B550 AORUS", gpu: "Radeon Pro W7800", cpu: "Ryzen 9", status: "Available" },
    { id: 11, name: "Machine K", motherboard: "ASRock X570 Taichi", gpu: "Radeon RX 7900 Series", cpu: "Ryzen Threadripper", status: "Available" },
    { id: 12, name: "Machine L", motherboard: "MSI MEG X570 GODLIKE", gpu: "Radeon RX 7900 Series", cpu: "EPYC", status: "Available" },
    { id: 13, name: "Machine M", motherboard: "ASUS Pro WS X570-ACE", gpu: "Radeon RX 7900 Series", cpu: "Ryzen 9", status: "Available" },
    { id: 14, name: "Machine N", motherboard: "Gigabyte B550 AORUS", gpu: "Radeon RX 7900 Series", cpu: "Ryzen 7", status: "Available" },
    { id: 15, name: "Machine O", motherboard: "ASRock X570 Taichi", gpu: "Radeon RX 7900 Series", cpu: "EPYC", status: "Available" }
];

// Test case groups organized by test type
const testCaseGroups = {
    "Benchmark": {
        "ffmpeg": [
            { id: 101, name: "H.264 Encoding", description: "Benchmark H.264 video encoding performance" },
            { id: 102, name: "H.265 Decoding", description: "Benchmark H.265 video decoding performance" },
            { id: 103, name: "AV1 Transcoding", description: "Benchmark AV1 video transcoding performance" }
        ],
        "clpeak": [
            { id: 104, name: "Global Memory Bandwidth", description: "Measure global memory bandwidth" },
            { id: 105, name: "Single-Precision Compute", description: "Measure single-precision compute performance" },
            { id: 106, name: "Double-Precision Compute", description: "Measure double-precision compute performance" }
        ]
    },
    "Functional": {
        "Compute": [
            { id: 201, name: "OpenCL Basic Operations", description: "Test basic OpenCL operations" },
            { id: 202, name: "Vulkan Compute Shaders", description: "Test Vulkan compute shaders" }
        ],
        "Media": [
            { id: 203, name: "Video Playback", description: "Test video playback functionality" },
            { id: 204, name: "Image Processing", description: "Test image processing capabilities" }
        ]
    },
    "Performance": {
        "Gaming": [
            { id: 301, name: "3D Gaming Benchmark", description: "Measure 3D gaming performance" },
            { id: 302, name: "VR Performance Test", description: "Test VR performance" }
        ],
        "Rendering": [
            { id: 303, name: "3D Model Rendering", description: "Measure 3D model rendering performance" },
            { id: 304, name: "Ray Tracing Performance", description: "Test ray tracing performance" }
        ]
    },
    "Stress": {
        "Memory": [
            { id: 401, name: "Memory Stress Test", description: "Stress test system memory" },
            { id: 402, name: "VRAM Stress Test", description: "Stress test GPU memory" }
        ],
        "Compute": [
            { id: 403, name: "Compute Stress Test", description: "Stress test compute capabilities" },
            { id: 404, name: "Thermal Stress Test", description: "Stress test thermal management" }
        ]
    }
};

// DOM elements
const form = document.getElementById('tpgen-form');
const progressBar = document.getElementById('progress-bar');
const progressText = document.getElementById('progress-text');
const machineList = document.getElementById('machine-list');
const cpuSelect = document.getElementById('cpu');
const gpuSelect = document.getElementById('gpu');
const sameOsConfig = document.getElementById('same-os-config');
const individualOsConfig = document.getElementById('individual-os-config');
const sameKernelConfig = document.getElementById('same-kernel-config');
const individualKernelConfig = document.getElementById('individual-kernel-config');
const testTypeGroups = document.getElementById('test-type-groups');
const testCaseContainer = document.getElementById('test-case-container');
const testCaseSearch = document.getElementById('test-case-search');
const searchResults = document.getElementById('search-results');
const addCustomGroupBtn = document.getElementById('add-custom-group');
const customGroupModal = document.getElementById('custom-group-modal');
const customGroupName = document.getElementById('custom-group-name');
const existingCaseSearch = document.getElementById('existing-case-search');
const existingCasesList = document.getElementById('existing-cases-list');
const customTestCaseName = document.getElementById('custom-test-case-name');
const customTestCaseDesc = document.getElementById('custom-test-case-desc');
const addTestCaseBtn = document.getElementById('add-test-case');
const saveCustomGroupBtn = document.getElementById('save-custom-group');
const cancelCustomGroupBtn = document.getElementById('cancel-custom-group');
const customTestCasesList = document.getElementById('custom-test-cases-list');
const closeModalBtn = document.querySelector('.close-modal');
const generateBtn = document.getElementById('generate-btn');
const resetBtn = document.getElementById('reset-btn');
const yamlOutput = document.getElementById('yaml-output');
const yamlContent = document.getElementById('yaml-content');
const yamlLineNumbers = document.getElementById('yaml-line-numbers');
const copyBtn = document.getElementById('copy-btn');
const downloadBtn = document.getElementById('download-btn');
const notification = document.getElementById('notification');

// New DOM elements for hardware configuration enhancements
const filterSummary = document.getElementById('filter-summary');
const filterValue = document.getElementById('filter-value');
const clearFilterBtn = document.getElementById('clear-filter-btn');
const totalMachinesEl = document.getElementById('total-machines');
const matchedMachinesEl = document.getElementById('matched-machines');
const selectedMachinesEl = document.getElementById('selected-machines');
const selectAllBtn = document.getElementById('select-all-btn');
const invertSelectionBtn = document.getElementById('invert-selection-btn');
const clearSelectionBtn = document.getElementById('clear-selection-btn');
const invalidSelectionWarning = document.getElementById('invalid-selection-warning');
const invalidCountEl = document.getElementById('invalid-count');
const clearInvalidBtn = document.getElementById('clear-invalid-btn');

// Sync scroll between line numbers and code content
yamlContent.addEventListener('scroll', function() {
    yamlLineNumbers.scrollTop = yamlContent.scrollTop;
});

// Upload tab elements
const tabs = document.querySelectorAll('.tab');
const tabContents = document.querySelectorAll('.tab-content');
const uploadArea = document.getElementById('upload-area');
const yamlUpload = document.getElementById('yaml-upload');
const analyzeBtn = document.getElementById('analyze-btn');
const validationResults = document.getElementById('validation-results');
const yamlAnalysisOutput = document.getElementById('yaml-analysis-output');
const analysisContent = document.getElementById('analysis-content');

// State
let selectedMachines = [];
let selectedTestCases = [];
let filteredMachines = [...mockMachines];
let customGroups = {};
let currentCustomGroup = {
    name: '',
    testCases: [],
    selectedExistingCases: []
};
let nextCustomId = 1000;
let uploadedYamlData = null;

// Initialize the application
function init() {
    // Set default CPU and GPU selections
    cpuSelect.value = "Ryzen Threadripper";
    gpuSelect.value = "Radeon RX 7900 Series";
    
    filterMachines();
    renderTestTypeGroups();
    renderTestCases();
    setupEventListeners();
    updateProgress();
    
    // Initialize statistics display
    updateMachineStats();
    
    // Load saved data from localStorage if available
    loadFromStorage();
}

// Tab switching functionality
function setupTabs() {
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabId = tab.getAttribute('data-tab');
            
            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Update active content
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === tabId) {
                    content.classList.add('active');
                }
            });
        });
    });
}

// Upload functionality
function setupUpload() {
    // Click on upload area to trigger file input
    uploadArea.addEventListener('click', () => {
        yamlUpload.click();
    });
    
    // Handle file selection
    yamlUpload.addEventListener('change', handleFileUpload);
    
    // Drag and drop functionality
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        if (e.dataTransfer.files.length) {
            yamlUpload.files = e.dataTransfer.files;
            handleFileUpload();
        }
    });
}

// Handle file upload
function handleFileUpload() {
    const file = yamlUpload.files[0];
    if (!file) return;
    
    // Check file extension
    const fileName = file.name.toLowerCase();
    const isYamlFile = fileName.endsWith('.yaml') || fileName.endsWith('.yml');
    
    if (!isYamlFile) {
        validationResults.innerHTML = `
            <div class="validation-item error">
                <i class="fas fa-exclamation-circle"></i>
                <div>
                    <strong>Invalid file format</strong>
                    <p>Please upload a valid YAML file (.yaml or .yml extension). The uploaded file "${file.name}" is not a YAML file.</p>
                </div>
            </div>
        `;
        analyzeBtn.disabled = true;
        // Hide Analysis Results section when file format is invalid
        yamlAnalysisOutput.style.display = 'none';
        return;
    }
    
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            // Parse YAML content
            const yamlContent = e.target.result;
            const parseResult = validateYamlSyntax(yamlContent);
            
            if (parseResult.hasErrors) {
                // Show syntax errors with highlighted content
                displayYamlSyntaxErrors(yamlContent, parseResult.errors, file.name);
                analyzeBtn.disabled = true;
            } else {
                uploadedYamlData = parseYaml(yamlContent);
                
                // Enable analyze button
                analyzeBtn.disabled = false;
                
                // Hide previous Analysis Results until user clicks Analyze button
                yamlAnalysisOutput.style.display = 'none';
                
                // Show success message
                validationResults.innerHTML = `
                    <div class="validation-item success">
                        <i class="fas fa-check-circle"></i>
                        <div>
                            <strong>${file.name} Uploaded Successfully!</strong>
                            <p>Click "Analyze Test Plan" to validate the configuration.</p>
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            validationResults.innerHTML = `
                <div class="validation-item error">
                    <i class="fas fa-exclamation-circle"></i>
                    <div>
                        <strong>Error parsing YAML file</strong>
                        <p>${error.message}</p>
                    </div>
                </div>
            `;
            analyzeBtn.disabled = true;
            // Hide Analysis Results section when there's a parsing error
            yamlAnalysisOutput.style.display = 'none';
        }
    };
    reader.readAsText(file);
}

// Validate YAML syntax and detect errors
function validateYamlSyntax(yamlContent) {
    const lines = yamlContent.split('\n');
    const errors = [];
    const indentLevels = []; // Track indentation levels
    let expectedIndentSize = null; // Expected indent size (2 or 4 spaces)
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const lineNum = i + 1;
        const trimmed = line.trim();
        
        // Skip empty lines and pure comments
        if (!trimmed || trimmed.startsWith('#')) continue;
        
        // Calculate indentation
        const indent = line.search(/\S/);
        if (indent === -1) continue;
        
        // Check for tab characters (not allowed in YAML)
        const leadingSpaces = line.substring(0, indent);
        if (leadingSpaces.includes('\t')) {
            errors.push({
                line: lineNum,
                message: 'Tab character detected in indentation. YAML requires spaces only for indentation.',
                severity: 'error'
            });
            // Continue checking other errors even if tab is found
        }
        
        // Check for mixed tabs and spaces
        if (line.match(/^[ \t]+/) && line.match(/^\s*\t/) && line.match(/^\s* /)) {
            errors.push({
                line: lineNum,
                message: 'Mixed tabs and spaces in indentation. Use spaces only.',
                severity: 'error'
            });
        }
        
        // Determine expected indent size from first indented line
        if (expectedIndentSize === null && indent > 0) {
            if (indent === 2 || indent === 4) {
                expectedIndentSize = indent;
            }
        }
        
        // Check for consistent indentation
        if (indent > 0 && expectedIndentSize !== null) {
            // Check if indentation is multiple of expected size
            if (indent % expectedIndentSize !== 0) {
                errors.push({
                    line: lineNum,
                    message: `Inconsistent indentation. Expected multiples of ${expectedIndentSize} spaces, but found ${indent} spaces.`,
                    severity: 'error'
                });
            }
        }
        
        // Check for unusual indentation jumps
        if (indentLevels.length > 0) {
            const lastIndent = indentLevels[indentLevels.length - 1];
            const indentDiff = indent - lastIndent;
            
            // If indent increases, it should be by standard amount (2 or 4)
            if (indentDiff > 0 && indentDiff !== 2 && indentDiff !== 4) {
                errors.push({
                    line: lineNum,
                    message: `Unusual indentation increase. Indent changed by ${indentDiff} spaces. Standard is 2 or 4 spaces per level.`,
                    severity: 'warning'
                });
            }
        }
        
        // Store current indent level
        if (indent >= 0) {
            indentLevels.push(indent);
        }
        
        // Check for lines starting with dash (list items)
        if (trimmed.startsWith('-')) {
            // Critical: Check for missing space after dash
            if (trimmed.length > 1 && trimmed[1] !== ' ') {
                errors.push({
                    line: lineNum,
                    message: 'Missing space after dash "-". YAML list items must have format "- item", not "-item".',
                    severity: 'error'
                });
            }
            // 1737 -- 1751 : 2025.10.29 14:17 annotation
            // // Check for invalid list item used as implicit map key
            // // Pattern: "- key:" which tries to use a list item as a map key
            // const afterDash = trimmed.substring(1).trim();
            // if (afterDash.includes(':') && afterDash.endsWith(':')) {
            //    // Extract the key name for better error message
            //    const keyName = afterDash.substring(0, afterDash.length - 1).trim();
            //    // This is "- something:" which is invalid in most contexts
            //    // A list item should contain either a scalar value or start a nested structure
            //    // But "- key:" tries to make the list item itself a key, which is not allowed
            //    errors.push({
            //        line: lineNum,
            //        message: `Invalid YAML syntax: "- ${keyName}:" uses a list item as an implicit map key, which is not allowed. Fix: Change "- ${keyName}:" to "${keyName}:" (remove the dash) to make it a regular key-value pair.`,
            //        severity: 'error'
            //    });
            //}
        }
        
        // Check lines with colons (key-value pairs or section headers)
        if (trimmed.includes(':')) {
            const colonIndex = trimmed.indexOf(':');
            const key = trimmed.substring(0, colonIndex);
            const afterColon = trimmed.substring(colonIndex + 1);
            
            // Check for invalid characters in keys
            if (key.includes('[') || key.includes(']') || key.includes('{') || key.includes('}')) {
                errors.push({
                    line: lineNum,
                    message: `Invalid character in key "${key}". Keys should not contain brackets.`,
                    severity: 'error'
                });
            }
            
            // Check for missing space after colon (if there's a value)
            if (afterColon && afterColon[0] !== ' ' && afterColon.trim() !== '') {
                errors.push({
                    line: lineNum,
                    message: 'Missing space after colon. YAML requires "key: value" format, not "key:value".',
                    severity: 'error'
                });
            }
            
            // Check for trailing spaces before colon
            if (key !== key.trim() && key.trim() !== '') {
                errors.push({
                    line: lineNum,
                    message: 'Unnecessary spaces before colon in key.',
                    severity: 'warning'
                });
            }
            
            // Check for potential unquoted special characters in values
            const value = afterColon.trim();
            if (value && !value.startsWith('"') && !value.startsWith("'") && !value.startsWith('[') && !value.startsWith('{')) {
                if (value.includes('#')) {
                    errors.push({
                        line: lineNum,
                        message: 'Unquoted "#" character in value may be interpreted as a comment. Consider quoting the value.',
                        severity: 'warning'
                    });
                }
                if (value.includes(':') && !trimmed.endsWith(':')) {
                    errors.push({
                        line: lineNum,
                        message: 'Unquoted colon in value. Consider quoting the value to avoid parsing issues.',
                        severity: 'warning'
                    });
                }
            }
        } else if (trimmed && !trimmed.startsWith('-') && !trimmed.startsWith('#')) {
            // Line doesn't contain colon and is not a list item or comment
            errors.push({
                line: lineNum,
                message: 'Invalid YAML syntax. Expected key-value pair (key: value) or list item (- item).',
                severity: 'error'
            });
        }
    }
    
    return {
        errors: errors,
        hasErrors: errors.some(e => e.severity === 'error')
    };
}

// Display YAML syntax errors with file content
function displayYamlSyntaxErrors(yamlContent, errors, fileName) {
    const lines = yamlContent.split('\n');
    const errorLineNums = new Set(errors.filter(e => e.severity === 'error').map(e => e.line));
    const warningLineNums = new Set(errors.filter(e => e.severity === 'warning').map(e => e.line));
    
    const errorCount = errors.filter(e => e.severity === 'error').length;
    const warningCount = errors.filter(e => e.severity === 'warning').length;
    
    let htmlContent = `
        <div class="validation-item error">
            <i class="fas fa-exclamation-circle"></i>
            <div>
                <strong>YAML Syntax Errors Found in ${fileName}</strong>
                <p>${errorCount} error(s) and ${warningCount} warning(s) detected. Please fix the errors before analyzing.</p>
            </div>
        </div>
    `;
    
    // Display error and warning list
    htmlContent += '<div class="error-list">';
    errors.forEach(error => {
        const icon = error.severity === 'error' ? 
            '<i class="fas fa-times-circle"></i>' : 
            '<i class="fas fa-exclamation-triangle"></i>';
        const className = error.severity === 'error' ? 'error-item' : 'warning-item';
        htmlContent += `
            <div class="${className}">
                ${icon}
                <div>
                    <strong>Line ${error.line}</strong> [${error.severity.toUpperCase()}]
                    <div>${error.message}</div>
                </div>
            </div>
        `;
    });
    htmlContent += '</div>';
    
    // Display file content with highlighted error lines
    htmlContent += '<div class="yaml-content-display">';
    htmlContent += '<div class="yaml-header"><i class="fas fa-file-code"></i> File Content (errors highlighted in red):</div>';
    htmlContent += '<pre class="yaml-code">';
    
    lines.forEach((line, index) => {
        const lineNum = index + 1;
        const hasError = errorLineNums.has(lineNum);
        const hasWarning = warningLineNums.has(lineNum);
        const lineClass = hasError ? 'error-line' : (hasWarning ? 'warning-line' : '');
        
        // Escape HTML characters and preserve spaces
        const escapedLine = line
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;')
            .replace(/ /g, '&nbsp;'); // Preserve all spaces
        
        // Format line number
        const lineNumStr = lineNum.toString().padStart(4, ' ').replace(/ /g, '&nbsp;');
        
        // Use separate spans for line number and content to avoid display issues
        htmlContent += `<div class="code-line"><span class="line-number ${lineClass}">${lineNumStr}</span><span class="line-content ${lineClass}">${escapedLine || '&nbsp;'}</span></div>`;
    });
    
    htmlContent += '</pre></div>';
    
    validationResults.innerHTML = htmlContent;
    
    // Hide Analysis Results section when there are syntax errors
    yamlAnalysisOutput.style.display = 'none';
}

// Simple YAML parser (for demonstration)
function parseYaml(yamlContent) {
    // This is a simplified YAML parser for demonstration
    // In a real application, you would use a proper YAML parser library
    
    const lines = yamlContent.split('\n');
    const result = {};
    let currentSection = null;
    
    for (const line of lines) {
        const trimmed = line.trim();
        
        // Skip empty lines and comments
        if (!trimmed || trimmed.startsWith('#')) continue;
        
        // Section headers
        if (trimmed.endsWith(':')) {
            currentSection = trimmed.slice(0, -1).trim();
            result[currentSection] = {};
        } 
        // Key-value pairs
        else if (trimmed.includes(':')) {
            const [key, value] = trimmed.split(':').map(s => s.trim());
            if (currentSection) {
                result[currentSection][key] = value;
            } else {
                result[key] = value;
            }
        }
    }
    
    return result;
}

// Analyze uploaded YAML
function analyzeYaml() {
    if (!uploadedYamlData) return;
    
    const analysis = validateYamlConfig(uploadedYamlData);
    displayAnalysisResults(analysis);
}

// Validate YAML configuration against available machines
function validateYamlConfig(yamlData) {
    const results = {
        compatibleMachines: [],
        incompatibleMachines: [],
        missingConfigurations: [],
        warnings: []
    };
    
    // Extract hardware requirements from YAML
    const requiredCPU = yamlData.hardware?.cpu;
    const requiredGPU = yamlData.hardware?.gpu;
    
    if (!requiredCPU || !requiredGPU) {
        results.missingConfigurations.push('Hardware configuration (CPU/GPU) is missing in the YAML file');
    }
    
    // Check each machine for compatibility
    mockMachines.forEach(machine => {
        const cpuMatch = !requiredCPU || machine.cpu === requiredCPU;
        const gpuMatch = !requiredGPU || machine.gpu === requiredGPU;
        
        if (cpuMatch && gpuMatch) {
            results.compatibleMachines.push(machine);
        } else {
            results.incompatibleMachines.push({
                machine,
                reasons: [
                    ...(cpuMatch ? [] : [`CPU mismatch: required ${requiredCPU}, found ${machine.cpu}`]),
                    ...(gpuMatch ? [] : [`GPU mismatch: required ${requiredGPU}, found ${machine.gpu}`])
                ]
            });
        }
    });
    
    // Check for other configuration issues
    if (!yamlData.environment?.os) {
        results.warnings.push('OS configuration is not specified');
    }
    
    if (!yamlData.environment?.kernel) {
        results.warnings.push('Kernel configuration is not specified');
    }
    
    if (!yamlData.firmware?.gpu_version) {
        results.warnings.push('GPU firmware version is not specified');
    }
    
    if (!yamlData.test_suites || yamlData.test_suites.length === 0) {
        results.warnings.push('No test suites defined');
    }
    
    return results;
}

// Display analysis results
function displayAnalysisResults(analysis) {
    let html = '';
    
    // Compatible machines
    if (analysis.compatibleMachines.length > 0) {
        html += `
            <div class="validation-item success">
                <i class="fas fa-check-circle"></i>
                <div>
                    <strong>Compatible Machines (${analysis.compatibleMachines.length})</strong>
                    <p>The following machines match your test plan requirements:</p>
                    <div class="machine-list">
        `;
        
        analysis.compatibleMachines.forEach(machine => {
            html += `
                <div class="machine-card">
                    <h3>${machine.name}</h3>
                    <p><strong>Motherboard:</strong> ${machine.motherboard}</p>
                    <p><strong>GPU:</strong> ${machine.gpu}</p>
                    <p><strong>CPU:</strong> ${machine.cpu}</p>
                    <p><span class="status">Compatible</span></p>
                </div>
            `;
        });
        
        html += `</div></div></div>`;
    }
    
    // Incompatible machines section
    if (analysis.incompatibleMachines.length > 0) {
        // When compatible machines exist, show collapsible section
        if (analysis.compatibleMachines.length > 0) {
            html += `
                <div class="validation-item" style="background: #fff3e0; border-left-color: #ff9800; cursor: pointer;" onclick="toggleIncompatibleMachines()">
                    <i class="fas fa-info-circle" style="color: #ff9800;"></i>
                    <div style="flex: 1;">
                        <strong>Incompatible Machines (${analysis.incompatibleMachines.length})</strong>
                        <p style="margin: 5px 0 0 0;">${analysis.incompatibleMachines.length} machine(s) do not match requirements. Click to view details.</p>
                    </div>
                    <i id="incompatible-toggle-icon" class="fas fa-chevron-down" style="color: #ff9800; font-size: 1.2rem; transition: transform 0.3s;"></i>
                </div>
                <div id="incompatible-machines-content" style="display: none; margin-top: 10px;">
                    <div class="validation-item warning">
                        <i class="fas fa-exclamation-triangle"></i>
                        <div>
                            <strong>Incompatible Machines Details</strong>
                            <p>The following machines do not match your test plan requirements:</p>
                            <div class="machine-list">
            `;
            
            analysis.incompatibleMachines.forEach(item => {
                html += `
                    <div class="machine-card unavailable">
                        <h3>${item.machine.name}</h3>
                        <p><strong>Motherboard:</strong> ${item.machine.motherboard}</p>
                        <p><strong>GPU:</strong> ${item.machine.gpu}</p>
                        <p><strong>CPU:</strong> ${item.machine.cpu}</p>
                        <p><span class="status unavailable">Incompatible</span></p>
                        <ul style="margin-top: 10px; padding-left: 20px;">
                            ${item.reasons.map(reason => `<li style="font-size: 0.9rem; color: #666;">${reason}</li>`).join('')}
                        </ul>
                    </div>
                `;
            });
            
            html += `
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            // When NO compatible machines exist, show directly (not collapsible)
            html += `
                <div class="validation-item warning">
                    <i class="fas fa-exclamation-triangle"></i>
                    <div>
                        <strong>Incompatible Machines (${analysis.incompatibleMachines.length})</strong>
                        <p>The following machines do not match your test plan requirements:</p>
                        <div class="machine-list">
            `;
            
            analysis.incompatibleMachines.forEach(item => {
                html += `
                    <div class="machine-card unavailable">
                        <h3>${item.machine.name}</h3>
                        <p><strong>Motherboard:</strong> ${item.machine.motherboard}</p>
                        <p><strong>GPU:</strong> ${item.machine.gpu}</p>
                        <p><strong>CPU:</strong> ${item.machine.cpu}</p>
                        <p><span class="status unavailable">Incompatible</span></p>
                        <ul style="margin-top: 10px; padding-left: 20px;">
                            ${item.reasons.map(reason => `<li style="font-size: 0.9rem; color: #666;">${reason}</li>`).join('')}
                        </ul>
                    </div>
                `;
            });
            
            html += `</div></div></div>`;
        }
    }
    
    // Missing configurations
    if (analysis.missingConfigurations.length > 0) {
        html += `
            <div class="validation-item error">
                <i class="fas fa-times-circle"></i>
                <div>
                    <strong>Missing Configurations</strong>
                    <ul>
                        ${analysis.missingConfigurations.map(config => `<li>${config}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    }
    
    // Warnings
    if (analysis.warnings.length > 0) {
        html += `
            <div class="validation-item warning">
                <i class="fas fa-exclamation-triangle"></i>
                <div>
                    <strong>Configuration Warnings</strong>
                    <ul>
                        ${analysis.warnings.map(warning => `<li>${warning}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    }
    
    analysisContent.innerHTML = html;
    yamlAnalysisOutput.style.display = 'block';
    
    // Scroll to analysis results
    yamlAnalysisOutput.scrollIntoView({ behavior: 'smooth' });
}

// Toggle incompatible machines display
function toggleIncompatibleMachines() {
    const content = document.getElementById('incompatible-machines-content');
    const icon = document.getElementById('incompatible-toggle-icon');
    
    if (content && icon) {
        if (content.style.display === 'none') {
            // Show content
            content.style.display = 'block';
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-up');
            icon.style.transform = 'rotate(180deg)';
        } else {
            // Hide content
            content.style.display = 'none';
            icon.classList.remove('fa-chevron-up');
            icon.classList.add('fa-chevron-down');
            icon.style.transform = 'rotate(0deg)';
        }
    }
}

// Filter machines based on selected CPU and GPU (Enhanced)
function filterMachines() {
    const selectedCPU = cpuSelect.value;
    const selectedGPU = gpuSelect.value;
    
    // Support single-item filtering - improved logic
    filteredMachines = mockMachines.filter(machine => {
        const cpuMatch = !selectedCPU || machine.cpu === selectedCPU;
        const gpuMatch = !selectedGPU || machine.gpu === selectedGPU;
        return cpuMatch && gpuMatch;
    });
    
    // Update filter summary display
    updateFilterSummary(selectedCPU, selectedGPU);
    
    // Update statistics
    updateMachineStats();
    
    // Validate current selection
    validateSelection();
    
    renderMachines();
}

// Update filter summary display
function updateFilterSummary(cpu, gpu) {
    let filterText = '';
    const filters = [];
    
    if (cpu) filters.push(`CPU: ${cpu}`);
    if (gpu) filters.push(`GPU: ${gpu}`);
    
    if (filters.length === 0) {
        filterText = 'None (Showing all machines)';
        clearFilterBtn.classList.add('hidden');
    } else {
        filterText = filters.join(' • ');
        clearFilterBtn.classList.remove('hidden');
    }
    
    filterValue.textContent = filterText;
}

// Update machine statistics
function updateMachineStats() {
    totalMachinesEl.textContent = mockMachines.length;
    matchedMachinesEl.textContent = filteredMachines.length;
    
    // Count selected machines that are in filtered results
    const validSelectedCount = selectedMachines.filter(id => 
        filteredMachines.some(m => m.id === id)
    ).length;
    
    selectedMachinesEl.textContent = validSelectedCount;
}

// Clear all filters
function clearFilter() {
    cpuSelect.value = '';
    gpuSelect.value = '';
    filterMachines();
}

// Render available test machines
function renderMachines() {
    machineList.innerHTML = '';
    
    if (filteredMachines.length === 0) {
        machineList.innerHTML = '<p>No machines match the selected criteria.</p>';
        return;
    }
    
    filteredMachines.forEach(machine => {
        const isSelected = selectedMachines.includes(machine.id);
        const machineCard = document.createElement('div');
        machineCard.className = `machine-card ${isSelected ? 'selected' : ''}`;
        machineCard.innerHTML = `
            <h3>${machine.name}</h3>
            <p><strong>Motherboard:</strong> ${machine.motherboard}</p>
            <p><strong>GPU:</strong> ${machine.gpu}</p>
            <p><strong>CPU:</strong> ${machine.cpu}</p>
            <p><span class="status">${machine.status}</span></p>
        `;
        machineCard.addEventListener('click', () => toggleMachineSelection(machine.id));
        machineList.appendChild(machineCard);
    });
}

// Toggle machine selection
function toggleMachineSelection(machineId) {
    const index = selectedMachines.indexOf(machineId);
    if (index === -1) {
        selectedMachines.push(machineId);
    } else {
        selectedMachines.splice(index, 1);
    }
    renderMachines();
    updateIndividualConfigs();
    updateMachineStats();
    validateSelection();
    saveToStorage();
    updateProgress();
}

// Batch operation: Select all filtered machines
function selectAllMachines() {
    const filteredIds = filteredMachines.map(m => m.id);
    // Add all filtered machines that aren't already selected
    filteredIds.forEach(id => {
        if (!selectedMachines.includes(id)) {
            selectedMachines.push(id);
        }
    });
    renderMachines();
    updateIndividualConfigs();
    updateMachineStats();
    validateSelection();
    saveToStorage();
    updateProgress();
    showNotification('All filtered machines selected!');
}

// Batch operation: Invert selection of filtered machines
function invertSelection() {
    const filteredIds = new Set(filteredMachines.map(m => m.id));
    const newSelection = [];
    
    // Keep selections that are not in filtered results
    selectedMachines.forEach(id => {
        if (!filteredIds.has(id)) {
            newSelection.push(id);
        }
    });
    
    // Add filtered machines that were not selected
    filteredMachines.forEach(machine => {
        if (!selectedMachines.includes(machine.id)) {
            newSelection.push(machine.id);
        }
    });
    
    selectedMachines = newSelection;
    renderMachines();
    updateIndividualConfigs();
    updateMachineStats();
    validateSelection();
    saveToStorage();
    updateProgress();
    showNotification('Selection inverted!');
}

// Batch operation: Clear all selections
function clearAllSelections() {
    if (selectedMachines.length === 0) {
        showNotification('No machines selected');
        return;
    }
    
    selectedMachines = [];
    renderMachines();
    updateIndividualConfigs();
    updateMachineStats();
    validateSelection();
    saveToStorage();
    updateProgress();
    showNotification('All selections cleared!');
}

// Validate selection and show warnings
function validateSelection() {
    const filteredIds = new Set(filteredMachines.map(m => m.id));
    const invalidIds = selectedMachines.filter(id => !filteredIds.has(id));
    
    if (invalidIds.length > 0) {
        // Show warning
        invalidCountEl.textContent = invalidIds.length;
        invalidSelectionWarning.classList.remove('hidden');
    } else {
        // Hide warning
        invalidSelectionWarning.classList.add('hidden');
    }
    
    return {
        valid: selectedMachines.filter(id => filteredIds.has(id)),
        invalid: invalidIds
    };
}

// Clear invalid selections
function clearInvalidSelections() {
    const filteredIds = new Set(filteredMachines.map(m => m.id));
    const beforeCount = selectedMachines.length;
    
    selectedMachines = selectedMachines.filter(id => filteredIds.has(id));
    
    const removedCount = beforeCount - selectedMachines.length;
    
    renderMachines();
    updateIndividualConfigs();
    updateMachineStats();
    validateSelection();
    saveToStorage();
    updateProgress();
    
    showNotification(`Removed ${removedCount} invalid selection(s)`);
}

// Update individual OS and kernel configurations based on selected machines
function updateIndividualConfigs() {
    // Update individual OS configurations
    individualOsConfig.innerHTML = '';
    selectedMachines.forEach(machineId => {
        const machine = mockMachines.find(m => m.id === machineId);
        if (machine) {
            const machineConfig = document.createElement('div');
            machineConfig.className = 'machine-config';
            machineConfig.innerHTML = `
                <h4><i class="fas fa-server"></i> ${machine.name}</h4>
                <div class="form-group">
                    <label for="os-${machineId}">OS Distribution</label>
                    <select id="os-${machineId}" name="os-${machineId}">
                        <option value="">Select an OS</option>
                        <option value="Ubuntu 22.04">Ubuntu 22.04</option>
                        <option value="Ubuntu 20.04">Ubuntu 20.04</option>
                        <option value="RHEL 9">RHEL 9</option>
                        <option value="RHEL 8">RHEL 8</option>
                        <option value="RHEL 7">RHEL 7</option>
                        <option value="CentOS Stream">CentOS Stream</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Deployment Method</label>
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="radio" id="bare-metal-${machineId}" name="deployment-${machineId}" value="Bare Metal">
                            <label for="bare-metal-${machineId}">Bare Metal</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="radio" id="virtual-machine-${machineId}" name="deployment-${machineId}" value="Virtual Machine">
                            <label for="virtual-machine-${machineId}">Virtual Machine</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="radio" id="container-${machineId}" name="deployment-${machineId}" value="Container">
                            <label for="container-${machineId}">Container</label>
                        </div>
                    </div>
                </div>
            `;
            individualOsConfig.appendChild(machineConfig);
        }
    });
    
    // Update individual kernel configurations
    individualKernelConfig.innerHTML = '';
    selectedMachines.forEach(machineId => {
        const machine = mockMachines.find(m => m.id === machineId);
        if (machine) {
            const machineConfig = document.createElement('div');
            machineConfig.className = 'machine-config';
            machineConfig.innerHTML = `
                <h4><i class="fas fa-server"></i> ${machine.name}</h4>
                <div class="form-group">
                    <label for="kernel-type-${machineId}">Kernel Type</label>
                    <select id="kernel-type-${machineId}" name="kernel-type-${machineId}">
                        <option value="">Select kernel type</option>
                        <option value="DKMS">DKMS</option>
                        <option value="Mainline">Mainline</option>
                        <option value="Custom Build">Custom Build</option>
                        <option value="LTS">LTS</option>

                    </select>
                </div>
                <div class="form-group">
                    <label for="kernel-version-${machineId}">Kernel Version</label>
                    <select id="kernel-version-${machineId}" name="kernel-version-${machineId}">
                        <option value="">Select kernel version</option>
                        <option value="6.2">6.2</option>
                        <option value="6.1">6.1</option>
                        <option value="6.0">6.0</option>
                        <option value="5.15">5.15</option>
                        <option value="5.10">5.10</option>
                    </select>
                </div>
            `;
            individualKernelConfig.appendChild(machineConfig);
        }
    });
}

// Render test type groups
function renderTestTypeGroups() {
    testTypeGroups.innerHTML = '';
    
    // Render predefined test groups
    Object.entries(testCaseGroups).forEach(([testType, subgroups]) => {
        const testTypeGroup = document.createElement('div');
        testTypeGroup.className = 'test-type-group';
        testTypeGroup.innerHTML = `
            <h4><i class="fas fa-layer-group"></i> ${testType}</h4>
        `;
        
        Object.entries(subgroups).forEach(([subgroupName, testCases]) => {
            const subgroupDiv = document.createElement('div');
            subgroupDiv.className = 'test-case-subgroup';
            subgroupDiv.innerHTML = `
                <h5>${subgroupName}</h5>
            `;
            
            testCases.forEach(testCase => {
                const checkboxItem = document.createElement('div');
                checkboxItem.className = 'checkbox-item';
                checkboxItem.innerHTML = `
                    <input type="checkbox" id="test-case-${testCase.id}" name="test-case" value="${testCase.id}" data-test-type="${testType}" data-subgroup="${subgroupName}">
                    <label for="test-case-${testCase.id}">${testCase.name}</label>
                `;
                subgroupDiv.appendChild(checkboxItem);
            });
            
            testTypeGroup.appendChild(subgroupDiv);
        });
        
        testTypeGroups.appendChild(testTypeGroup);
    });
    
    // Render custom test groups
    Object.entries(customGroups).forEach(([groupName, testCases]) => {
        const testTypeGroup = document.createElement('div');
        testTypeGroup.className = 'test-type-group';
        testTypeGroup.innerHTML = `
            <h4><i class="fas fa-star"></i> ${groupName} <span class="badge badge-custom">Custom</span></h4>
        `;
        
        const subgroupDiv = document.createElement('div');
        subgroupDiv.className = 'test-case-subgroup';
        
        testCases.forEach(testCase => {
            const checkboxItem = document.createElement('div');
            checkboxItem.className = 'checkbox-item';
            checkboxItem.innerHTML = `
                <input type="checkbox" id="test-case-${testCase.id}" name="test-case" value="${testCase.id}" data-test-type="Custom" data-subgroup="${groupName}" data-custom-group="${groupName}">
                <label for="test-case-${testCase.id}">${testCase.name}</label>
            `;
            subgroupDiv.appendChild(checkboxItem);
        });
        
        testTypeGroup.appendChild(subgroupDiv);
        testTypeGroups.appendChild(testTypeGroup);
    });
}

// Render selected test cases
function renderTestCases() {
    testCaseContainer.innerHTML = '';
    
    if (selectedTestCases.length === 0) {
        testCaseContainer.innerHTML = '<p>No test cases selected. Select test cases from the groups above.</p>';
        return;
    }
    
    selectedTestCases.forEach(testCase => {
        const testCaseItem = document.createElement('div');
        testCaseItem.className = 'test-case-item';
        testCaseItem.setAttribute('data-id', testCase.id);
        testCaseItem.setAttribute('draggable', 'true');
        testCaseItem.innerHTML = `
            <div>
                <strong>${testCase.name}</strong>
                <div>${testCase.description}</div>
            </div>
            <div>${testCase.testType} - ${testCase.subgroup} 
                ${testCase.testType === 'Custom' ? '<span class="badge badge-custom">Custom</span>' : '<span class="badge badge-primary">Standard</span>'}
            </div>
        `;
        
        testCaseItem.addEventListener('dragstart', handleDragStart);
        testCaseItem.addEventListener('dragover', handleDragOver);
        testCaseItem.addEventListener('drop', handleDrop);
        testCaseItem.addEventListener('dragend', handleDragEnd);
        
        testCaseContainer.appendChild(testCaseItem);
    });
}

// Update selected test cases based on checkbox selections
function updateSelectedTestCases() {
    selectedTestCases = [];
    
    // Get all test cases from predefined groups
    const allPredefinedTestCases = [];
    Object.entries(testCaseGroups).forEach(([testType, subgroups]) => {
        Object.entries(subgroups).forEach(([subgroupName, testCases]) => {
            testCases.forEach(testCase => {
                allPredefinedTestCases.push({
                    ...testCase,
                    testType: testType,
                    subgroup: subgroupName
                });
            });
        });
    });
    
    // Get all test cases from custom groups
    const allCustomTestCases = [];
    Object.entries(customGroups).forEach(([groupName, testCases]) => {
        testCases.forEach(testCase => {
            allCustomTestCases.push({
                ...testCase,
                testType: "Custom",
                subgroup: groupName,
                customGroup: groupName
            });
        });
    });
    
    // Get selected test case IDs and their custom group info
    const selectedIds = [];
    const selectedCustomGroups = {};
    
    document.querySelectorAll('input[name="test-case"]:checked').forEach(checkbox => {
        const id = parseInt(checkbox.value);
        const customGroup = checkbox.getAttribute('data-custom-group');
        selectedIds.push(id);
        
        if (customGroup) {
            selectedCustomGroups[id] = customGroup;
        }
    });
    
    // Filter test cases by selected IDs, considering custom groups
    selectedTestCases = [
        ...allPredefinedTestCases.filter(testCase => 
            selectedIds.includes(testCase.id) && !selectedCustomGroups[testCase.id]
        ),
        ...allCustomTestCases.filter(testCase => 
            selectedIds.includes(testCase.id) && selectedCustomGroups[testCase.id] === testCase.customGroup
        )
    ];
    
    renderTestCases();
    saveToStorage();
}

// Show custom group modal
function showCustomGroupModal() {
    customGroupModal.classList.remove('hidden');
    currentCustomGroup = {
        name: '',
        testCases: [],
        selectedExistingCases: []
    };
    customGroupName.value = '';
    existingCaseSearch.value = '';
    customTestCaseName.value = '';
    customTestCaseDesc.value = '';
    customTestCasesList.innerHTML = '';
    renderExistingCasesList();
}

// Hide custom group modal
function hideCustomGroupModal() {
    customGroupModal.classList.add('hidden');
}

// Render existing test cases for selection
function renderExistingCasesList() {
    existingCasesList.innerHTML = '';
    
    // Get all test cases
    const allTestCases = getAllTestCases();
    
    allTestCases.forEach(testCase => {
        const caseItem = document.createElement('div');
        caseItem.className = 'existing-case-item';
        caseItem.innerHTML = `
            <div>
                <strong>${testCase.name}</strong>
                <div>${testCase.description}</div>
                <small>${testCase.testType} - ${testCase.subgroup} 
                    ${testCase.testType === 'Custom' ? '<span class="badge badge-custom">Custom</span>' : '<span class="badge badge-primary">Standard</span>'}
                </small>
            </div>
        `;
        caseItem.addEventListener('click', () => toggleExistingCaseSelection(testCase.id, caseItem));
        existingCasesList.appendChild(caseItem);
    });
}

// Get all test cases (predefined + custom)
function getAllTestCases() {
    const allTestCases = [];
    
    // Add predefined test cases
    Object.entries(testCaseGroups).forEach(([testType, subgroups]) => {
        Object.entries(subgroups).forEach(([subgroupName, testCases]) => {
            testCases.forEach(testCase => {
                allTestCases.push({
                    ...testCase,
                    testType: testType,
                    subgroup: subgroupName
                });
            });
        });
    });
    
    // Add custom test cases
    Object.entries(customGroups).forEach(([groupName, testCases]) => {
        testCases.forEach(testCase => {
            allTestCases.push({
                ...testCase,
                testType: "Custom",
                subgroup: groupName
            });
        });
    });
    
    return allTestCases;
}

// Toggle existing case selection
function toggleExistingCaseSelection(caseId, caseItem) {
    const index = currentCustomGroup.selectedExistingCases.indexOf(caseId);
    
    if (index === -1) {
        currentCustomGroup.selectedExistingCases.push(caseId);
        caseItem.classList.add('selected');
    } else {
        currentCustomGroup.selectedExistingCases.splice(index, 1);
        caseItem.classList.remove('selected');
    }
    
    renderCustomTestCasesList();
}

// Add test case to current custom group
function addTestCaseToCustomGroup() {
    const name = customTestCaseName.value.trim();
    const desc = customTestCaseDesc.value.trim();
    
    if (!name) {
        alert('Please enter a test case name');
        return;
    }
    
    const testCase = {
        id: nextCustomId++,
        name: name,
        description: desc
    };
    
    currentCustomGroup.testCases.push(testCase);
    renderCustomTestCasesList();
    
    // Clear input fields
    customTestCaseName.value = '';
    customTestCaseDesc.value = '';
}

// Render custom test cases list in modal
function renderCustomTestCasesList() {
    customTestCasesList.innerHTML = '';
    
    // Add existing cases
    const allTestCases = getAllTestCases();
    currentCustomGroup.selectedExistingCases.forEach(caseId => {
        const testCase = allTestCases.find(tc => tc.id === caseId);
        if (testCase) {
            const testCaseItem = document.createElement('div');
            testCaseItem.className = 'existing-case-item';
            testCaseItem.innerHTML = `
                <div>
                    <strong>${testCase.name}</strong>
                    <div>${testCase.description}</div>
                    <small>${testCase.testType} - ${testCase.subgroup} 
                        ${testCase.testType === 'Custom' ? '<span class="badge badge-custom">Custom</span>' : '<span class="badge badge-primary">Standard</span>'}
                    </small>
                </div>
                <button type="button" class="btn-secondary remove-test-case" data-id="${testCase.id}">
                    <i class="fas fa-times"></i> Remove
                </button>
            `;
            customTestCasesList.appendChild(testCaseItem);
            
            // Add event listener for remove button
            testCaseItem.querySelector('.remove-test-case').addEventListener('click', function() {
                const id = parseInt(this.getAttribute('data-id'));
                currentCustomGroup.selectedExistingCases = currentCustomGroup.selectedExistingCases.filter(cid => cid !== id);
                renderCustomTestCasesList();
            });
        }
    });
    
    // Add new custom cases
    currentCustomGroup.testCases.forEach(testCase => {
        const testCaseItem = document.createElement('div');
        testCaseItem.className = 'existing-case-item';
        testCaseItem.innerHTML = `
            <div>
                <strong>${testCase.name}</strong>
                <div>${testCase.description}</div>
                <small><span class="badge badge-custom">New Custom</span></small>
            </div>
            <button type="button" class="btn-secondary remove-test-case" data-id="${testCase.id}">
                <i class="fas fa-times"></i> Remove
            </button>
        `;
        customTestCasesList.appendChild(testCaseItem);
        
        // Add event listener for remove button
        testCaseItem.querySelector('.remove-test-case').addEventListener('click', function() {
            const id = parseInt(this.getAttribute('data-id'));
            currentCustomGroup.testCases = currentCustomGroup.testCases.filter(tc => tc.id !== id);
            renderCustomTestCasesList();
        });
    });
}

// Save custom group
function saveCustomGroup() {
    const groupName = customGroupName.value.trim();
    
    if (!groupName) {
        alert('Please enter a group name');
        return;
    }
    
    if (currentCustomGroup.selectedExistingCases.length === 0 && currentCustomGroup.testCases.length === 0) {
        alert('Please add at least one test case to the group');
        return;
    }
    
    // Get all selected existing cases
    const allTestCases = getAllTestCases();
    const selectedCases = currentCustomGroup.selectedExistingCases.map(id => {
        const originalCase = allTestCases.find(tc => tc.id === id);
        // Create a copy to avoid reference issues
        return originalCase ? {
            id: originalCase.id,
            name: originalCase.name,
            description: originalCase.description
        } : null;
    }).filter(tc => tc !== null);
    
    // Combine with new custom cases
    customGroups[groupName] = [...selectedCases, ...currentCustomGroup.testCases];
    
    hideCustomGroupModal();
    renderTestTypeGroups();
    saveToStorage();
}

// Search test cases in main form
function searchTestCases(searchTerm) {
    searchResults.innerHTML = '';
    
    if (!searchTerm) {
        searchResults.classList.add('hidden');
        return;
    }
    
    const allTestCases = getAllTestCases();
    const filteredCases = allTestCases.filter(testCase => 
        testCase.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        testCase.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        testCase.testType.toLowerCase().includes(searchTerm.toLowerCase()) ||
        testCase.subgroup.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    if (filteredCases.length === 0) {
        searchResults.innerHTML = '<p>No test cases found.</p>';
    } else {
        filteredCases.forEach(testCase => {
            const resultItem = document.createElement('div');
            resultItem.className = 'search-result-item';
            resultItem.innerHTML = `
                <div>
                    <strong>${testCase.name}</strong>
                    <div>${testCase.description}</div>
                    <small>${testCase.testType} - ${testCase.subgroup} 
                        ${testCase.testType === 'Custom' ? '<span class="badge badge-custom">Custom</span>' : '<span class="badge badge-primary">Standard</span>'}
                    </small>
                </div>
            `;
            resultItem.addEventListener('click', () => {
                // Check the corresponding checkbox
                const checkbox = document.getElementById(`test-case-${testCase.id}`);
                if (checkbox) {
                    checkbox.checked = true;
                    updateSelectedTestCases();
                }
            });
            searchResults.appendChild(resultItem);
        });
    }
    
    searchResults.classList.remove('hidden');
}

// Drag and drop functionality for test cases
let draggedItem = null;

function handleDragStart(e) {
    draggedItem = this;
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
    this.classList.add('dragging');
}

function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    return false;
}

function handleDrop(e) {
    e.stopPropagation();
    if (draggedItem !== this) {
        const draggedIndex = Array.from(testCaseContainer.children).indexOf(draggedItem);
        const dropIndex = Array.from(testCaseContainer.children).indexOf(this);
        
        // Reorder the test cases array
        const [movedItem] = selectedTestCases.splice(draggedIndex, 1);
        selectedTestCases.splice(dropIndex, 0, movedItem);
        
        renderTestCases();
        saveToStorage();
    }
    return false;
}

function handleDragEnd(e) {
    this.classList.remove('dragging');
}

// Update progress bar
function updateProgress() {
    const formElements = form.elements;
    let filledFields = 0;
    let totalFields = 0;
    
    for (let i = 0; i < formElements.length; i++) {
        const element = formElements[i];
        
        // Skip buttons and non-required fields for progress calculation
        if (element.type === 'button' || element.type === 'submit') continue;
        
        totalFields++;
        
        if (element.type === 'checkbox' || element.type === 'radio') {
            if (element.checked) filledFields++;
        } else if (element.type === 'select-one') {
            if (element.value) filledFields++;
        }
    }
    
    // Add machine selection to progress
    totalFields++;
    if (selectedMachines.length > 0) filledFields++;
    
    // Add test case selection to progress
    totalFields++;
    if (selectedTestCases.length > 0) filledFields++;
    
    const progress = Math.round((filledFields / totalFields) * 100);
    progressBar.style.width = `${progress}%`;
    progressText.textContent = `Progress: ${progress}%`;
}

// Generate YAML test plan
function generateYAML() {
    const formData = new FormData(form);
    
    // Get OS configuration
    const osConfigMethod = formData.get('os-config-method');
    let osConfig = {};
    
    if (osConfigMethod === 'same') {
        osConfig = {
            method: 'same',
            os: formData.get('os'),
            deployment: formData.get('deployment')
        };
    } else {
        osConfig = {
            method: 'individual',
            machines: {}
        };
        
        selectedMachines.forEach(machineId => {
            osConfig.machines[machineId] = {
                os: formData.get(`os-${machineId}`),
                deployment: formData.get(`deployment-${machineId}`)
            };
        });
    }
    
    // Get kernel configuration
    const kernelConfigMethod = formData.get('kernel-config-method');
    let kernelConfig = {};
    
    if (kernelConfigMethod === 'same') {
        kernelConfig = {
            method: 'same',
            type: formData.get('kernel-type'),
            version: formData.get('kernel-version')
        };
    } else {
        kernelConfig = {
            method: 'individual',
            machines: {}
        };
        
        selectedMachines.forEach(machineId => {
            kernelConfig.machines[machineId] = {
                type: formData.get(`kernel-type-${machineId}`),
                version: formData.get(`kernel-version-${machineId}`)
            };
        });
    }
    
    // Build test suites
    const testSuites = selectedTestCases.map((testCase, index) => ({
        id: testCase.id,
        name: testCase.name,
        description: testCase.description,
        type: testCase.testType,
        subgroup: testCase.subgroup,
        order: index + 1
    }));
    
    // Build YAML structure
    const yamlData = {
        metadata: {
            generated: new Date().toISOString(),
            version: "1.0"
        },
        hardware: {
            cpu: formData.get('cpu'),
            gpu: formData.get('gpu'),
            machines: selectedMachines.map(id => {
                const machine = mockMachines.find(m => m.id === id);
                return {
                    id: machine.id,
                    name: machine.name,
                    specs: {
                        motherboard: machine.motherboard,
                        gpu: machine.gpu,
                        cpu: machine.cpu
                    }
                };
            })
        },
        environment: {
            os: osConfig,
            kernel: kernelConfig
        },
        firmware: {
            gpu_version: formData.get('firmware-version'),
            comparison: formData.get('version-comparison') === 'on'
        },
        test_suites: testSuites
    };
    
    // Convert to YAML string (simplified)
    const yamlString = jsToYaml(yamlData);
    yamlContent.textContent = yamlString;
    
    // Generate line numbers
    const lines = yamlString.split('\n');
    const lineNumbers = lines.map((_, i) => i + 1).join('\n');
    document.getElementById('yaml-line-numbers').textContent = lineNumbers;
    
    yamlOutput.style.display = 'block';
    
    // Scroll to YAML output
    yamlOutput.scrollIntoView({ behavior: 'smooth' });
}

// Simplified JavaScript to YAML converter
function jsToYaml(obj, indent = 0) {
    let yaml = '';
    const spaces = '  '.repeat(indent);
    
    for (const [key, value] of Object.entries(obj)) {
        if (Array.isArray(value)) {
            yaml += `${spaces}${key}:\n`;
            value.forEach((item, index) => {
                if (typeof item === 'object' && item !== null) {
                    // Handle objects in arrays
                    const itemEntries = Object.entries(item);
                    itemEntries.forEach(([itemKey, itemValue], i) => {
                        if (i === 0) {
                            // First property uses the list marker
                            if (typeof itemValue === 'object' && itemValue !== null && !Array.isArray(itemValue)) {
                                yaml += `${spaces}  - ${itemKey}:\n`;
                                yaml += jsToYaml(itemValue, indent + 2);
                            } else if (Array.isArray(itemValue)) {
                                yaml += `${spaces}  - ${itemKey}:\n`;
                                itemValue.forEach(subItem => {
                                    if (typeof subItem === 'object') {
                                        yaml += `${spaces}      - ${jsToYaml(subItem, indent + 3).trim()}\n`;
                                    } else {
                                        yaml += `${spaces}      - ${subItem}\n`;
                                    }
                                });
                            } else {
                                yaml += `${spaces}  - ${itemKey}: ${itemValue}\n`;
                            }
                        } else {
                            // Subsequent properties are indented
                            if (typeof itemValue === 'object' && itemValue !== null && !Array.isArray(itemValue)) {
                                yaml += `${spaces}    ${itemKey}:\n`;
                                yaml += jsToYaml(itemValue, indent + 2);
                            } else if (Array.isArray(itemValue)) {
                                yaml += `${spaces}    ${itemKey}:\n`;
                                itemValue.forEach(subItem => {
                                    if (typeof subItem === 'object') {
                                        yaml += `${spaces}      - ${jsToYaml(subItem, indent + 3).trim()}\n`;
                                    } else {
                                        yaml += `${spaces}      - ${subItem}\n`;
                                    }
                                });
                            } else {
                                yaml += `${spaces}    ${itemKey}: ${itemValue}\n`;
                            }
                        }
                    });
                } else {
                    yaml += `${spaces}  - ${item}\n`;
                }
            });
        } else if (typeof value === 'object' && value !== null) {
            yaml += `${spaces}${key}:\n${jsToYaml(value, indent + 1)}`;
        } else {
            yaml += `${spaces}${key}: ${value}\n`;
        }
    }
    
    return yaml;
}

// Copy YAML to clipboard
function copyToClipboard() {
    try {
        const yamlText = yamlContent.textContent;
        // let yamlText = '';
        // let yamlText = 'key:\n\tbad_tab: value';  // Tab字符（YAML不允许）


        // Check if YAML content is empty
        if (!yamlText || yamlText.trim().length === 0) {
            showNotification('Test plan copy failed!\nContent Empty!', 'error');
            return;
        }
        
        // Check for format errors using isValidYAML function
        const validationResult = isValidYAML(yamlText);
        if (!validationResult.valid) {
            const lineInfo = validationResult.lineNumber ? `line ${validationResult.lineNumber}\n` : '';
            showNotification(`Test plan copy failed!\n${lineInfo}Invalid format!`, 'error');
            return;
        }
        
        // Check if Clipboard API is supported (Browser compatibility)
        if (!navigator.clipboard) {
            showNotification('Test plan copy failed!\nBrowser not supported!', 'error');
            return;
        }
        
        // Check if running in secure context (HTTPS or localhost)
        if (!window.isSecureContext) {
            showNotification('Test plan copy failed!\nHTTPS required for clipboard access!', 'error');
            return;
        }
        
        // Parse YAML text back to object for compatibility analysis
        let yamlDataObject = null;
        try {
            if (typeof jsyaml !== 'undefined') {
                yamlDataObject = jsyaml.load(yamlText);
            }
        } catch (parseError) {
            console.error('YAML parse error for compatibility check:', parseError);
            // If parsing fails, continue with copy (format already validated above)
        }
        
        // Perform compatibility analysis if parsing succeeded
        if (yamlDataObject) {
            const compatResult = compatibility_analysis(yamlDataObject);
            // Split only at the first colon to preserve complete error message
            const colonIndex = compatResult.indexOf(':');
            const isValid = compatResult.substring(0, colonIndex);
            const errorCode = compatResult.substring(colonIndex + 1);
            
            if (isValid === 'False') {
                console.error(`Compatibility check failed: ${errorCode}`);
                const lineNumber = findLineNumberInYAML(yamlText, errorCode);
                const lineInfo = lineNumber ? `line ${lineNumber}\n` : '';
                showNotification(`Test plan copy failed!\n${lineInfo}Compatibility error!\n${errorCode}`, 'error');
                return;
            }
        }
        
        // Attempt to copy to clipboard
        navigator.clipboard.writeText(yamlText).then(() => {
            showNotification('Test plan copied to clipboard!');
        }).catch((error) => {
            console.error('Clipboard copy error:', error);
            showNotification('Test plan copy failed!\nUnknown error occurred!', 'error');
        });
    } catch (error) {
        console.error('Copy function error:', error);
        showNotification('Test plan copy failed!\nUnknown error occurred!', 'error');
    }
}

function isValidYAML(yamlText) {
    try {
        // js-yaml 库加载后，全局对象是 jsyaml
        if (typeof jsyaml !== 'undefined') {
            jsyaml.load(yamlText);
        } else if (typeof window.jsyaml !== 'undefined') {
            window.jsyaml.load(yamlText);
        } else {
            // 如果库未加载，进行简单验证
            console.warn('js-yaml library not loaded, using basic validation');
            return { valid: !yamlText.includes('Error:') && !yamlText.includes('error:') };
        }
        return { valid: true };
    } catch (e) {
        console.error('YAML validation error:', e);
        // Try to extract line number from error message
        let lineNumber = null;
        if (e.mark && e.mark.line !== undefined) {
            lineNumber = e.mark.line + 1; // js-yaml uses 0-based line numbers
        }
        return { valid: false, lineNumber: lineNumber };
    }
}

// Helper function to find line number of a key in YAML text
function findLineNumberInYAML(yamlText, errorCode) {
    if (!yamlText) return null;
    
    const lines = yamlText.split('\n');
    
    // Extract key path from error code
    // E.g., "E001 Unsupported: missing mandatory key [cpu]" -> "cpu"
    // E.g., "E300 Unsupported: invalid combination detected [environment.os.os]" -> "environment.os.os"
    let searchKey = null;
    const bracketMatch = errorCode.match(/\[([^\]]+)\]/);
    if (bracketMatch) {
        searchKey = bracketMatch[1];
    }
    
    if (!searchKey) return null;
    
    // Split nested key path (e.g., "environment.os.os" -> ["environment", "os", "os"])
    const keyParts = searchKey.split('.');
    const lastKey = keyParts[keyParts.length - 1];
    
    // Search for the key in YAML text
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        // Match patterns like "  key:" or "  key: value"
        const keyPattern = new RegExp(`^\\s*${lastKey}\\s*:`);
        if (keyPattern.test(line)) {
            return i + 1; // Return 1-based line number
        }
    }
    
    // If specific key not found, try to find any key in the path
    for (const key of keyParts.reverse()) {
        for (let i = 0; i < lines.length; i++) {
            const keyPattern = new RegExp(`^\\s*${key}\\s*:`);
            if (keyPattern.test(lines[i])) {
                return i + 1;
            }
        }
    }
    
    return null;
}

// ============================================================================
// Compatibility Analysis Functions (from compatibility_analysis.js)
// ============================================================================

/**
 * Configuration Rules (from backend/config/*.yaml)
 */

// Required Root Keys (E001)
const REQUIRED_ROOT_KEYS = ['hardware.cpu', 'hardware.gpu',"test_key"];

// Mandatory Non-Empty Keys (E002)
const MANDATORY_NON_EMPTY_KEYS = ['hardware.machines', 'test_suites'];

// Value Type Configuration (E101)
const VALUE_TYPE_CONFIG = {
    'hardware.cpu': 'string'
};

// Value Range Configuration (E102)
const VALUE_RANGE_CONFIG = {
    'hardware.cpu': ['Ryzen Threadripper', 'Ryzen 7', 'Ryzen 9', 'EPYC']
};

// Invalid Combination Configuration (E300)
const INVALID_COMBO_CONFIG = [
    {
        name: "RHEL7 官方内核≤3.10，≥5.0 无法启动",
        when: {
            "environment.os.os": "RHEL 7",
            "environment.kernel.type": "LTS",
            "environment.kernel.version": "6.1"
        },
        action: "report_error"
    }
];

/**
 * Helper Functions
 */

// Check if a value is empty
function isEmpty(value) {
    if (value === null || value === undefined) return true;
    if (typeof value === 'string' && value.trim() === '') return true;
    if (Array.isArray(value) && value.length === 0) return true;
    if (typeof value === 'object' && Object.keys(value).length === 0) return true;
    return false;
}

// Get nested value from object using dot notation path
function getNestedValue(obj, path) {
    return path.split('.').reduce((current, key) => {
        return current && current[key] !== undefined ? current[key] : undefined;
    }, obj);
}

// Check if key exists in object (at any depth)
function hasKey(obj, key) {
    if (!obj || typeof obj !== 'object') return false;
    if (obj.hasOwnProperty(key)) return true;
    
    for (let k in obj) {
        if (obj.hasOwnProperty(k) && typeof obj[k] === 'object') {
            if (hasKey(obj[k], key)) return true;
        }
    }
    return false;
}

// Get value type as string
function getValueType(value) {
    if (value === null) return 'null';
    if (Array.isArray(value)) return 'array';
    return typeof value;
}

/**
 * Validation Functions
 */

// Validate E001: Check for missing mandatory root keys
function validateRequiredRootKeys(yamlData) {
    for (const key of REQUIRED_ROOT_KEYS) {
        // Support both dot notation (e.g., 'hardware.cpu') and simple keys (e.g., 'cpu')
        let exists = false;
        if (key.includes('.')) {
            // For dot notation, use getNestedValue
            const value = getNestedValue(yamlData, key);
            exists = value !== undefined;
        } else {
            // For simple keys, use hasKey
            exists = hasKey(yamlData, key);
        }
        
        if (!exists) {
            return {
                valid: false,
                errorCode: `E001 Unsupported: missing mandatory key [${key}]`,
                errorMessage: `E001 Unsupported: missing mandatory key [${key}]`
            };
        }
    }
    return { valid: true, errorCode: '0', errorMessage: 'OK' };
}

// Validate E002: Check for empty mandatory keys
function validateMandatoryNonEmptyKeys(yamlData) {
    for (const key of MANDATORY_NON_EMPTY_KEYS) {
        // Support both dot notation (e.g., 'hardware.machines') and simple keys (e.g., 'machines')
        let value;
        if (key.includes('.')) {
            // For dot notation, use getNestedValue
            value = getNestedValue(yamlData, key);
        } else {
            // For simple keys, try multiple fallbacks
            value = getNestedValue(yamlData, key) || 
                   (yamlData.hardware && yamlData.hardware[key]) ||
                   yamlData[key];
        }
        
        if (value === undefined) {
            return {
                valid: false,
                errorCode: `E002 Unsupported: empty value for [${key}]`,
                errorMessage: `E002 Unsupported: empty value for [${key}]`
            };
        }
        
        if (isEmpty(value)) {
            return {
                valid: false,
                errorCode: `E002 Unsupported: empty value for [${key}]`,
                errorMessage: `E002 Unsupported: empty value for [${key}]`
            };
        }
    }
    return { valid: true, errorCode: '0', errorMessage: 'OK' };
}

// Validate E101: Check value types
function validateValueTypes(yamlData) {
    for (const [key, expectedType] of Object.entries(VALUE_TYPE_CONFIG)) {
        // Support both dot notation and simple keys
        let value;
        if (key.includes('.')) {
            value = getNestedValue(yamlData, key);
        } else {
            value = getNestedValue(yamlData, key) || 
                   (yamlData.hardware && yamlData.hardware[key]) ||
                   yamlData[key];
        }
        
        if (value === undefined) continue;
        
        const actualType = getValueType(value);
        const typeMap = {
            'string': ['string'],
            'int': ['number'],
            'number': ['number'],
            'boolean': ['boolean'],
            'array': ['array'],
            'object': ['object']
        };
        
        const validTypes = typeMap[expectedType] || [expectedType];
        
        if (!validTypes.includes(actualType)) {
            return {
                valid: false,
                errorCode: `E101 Unsupported: value type error for [${key}]. Expected ${expectedType}, got ${actualType}`,
                errorMessage: `E101 Unsupported: value type error for [${key}]. Expected ${expectedType}, got ${actualType}`
            };
        }
    }
    return { valid: true, errorCode: '0', errorMessage: 'OK' };
}

// Validate E102: Check value ranges (whitelist)
function validateValueRanges(yamlData) {
    for (const [key, allowedValues] of Object.entries(VALUE_RANGE_CONFIG)) {
        // Support both dot notation and simple keys
        let value;
        if (key.includes('.')) {
            value = getNestedValue(yamlData, key);
        } else {
            value = getNestedValue(yamlData, key) || 
                   (yamlData.hardware && yamlData.hardware[key]) ||
                   yamlData[key];
        }
        
        if (value === undefined) continue;
        
        if (!allowedValues.includes(value)) {
            return {
                valid: false,
                errorCode: `E102 Unsupported: invalid value range for [${key}]. Value "${value}" is not in whitelist [${allowedValues.join(', ')}]`,
                errorMessage: `E102 Unsupported: invalid value range for [${key}]. Value "${value}" is not in whitelist [${allowedValues.join(', ')}]`
            };
        }
    }
    return { valid: true, errorCode: '0', errorMessage: 'OK' };
}

// Validate E300: Check for invalid combinations
function validate_combo(yamlData) {
    console.log('[validate_combo] Checking invalid combinations...');
    for (const combo of INVALID_COMBO_CONFIG) {
        console.log(`[validate_combo]`);
        // Check if all conditions in "when" are met
        let allConditionsMet = true;
        const matchedConditions = [];
        
        for (const [keyPath, expectedValue] of Object.entries(combo.when)) {
            const actualValue = getNestedValue(yamlData, keyPath);
            console.log(`[validate_combo]   ${keyPath}: expected="${expectedValue}" (type: ${typeof expectedValue}), actual="${actualValue}" (type: ${typeof actualValue})`);
            
            // If expected value is an array, check if actual value is in the array
            if (Array.isArray(expectedValue)) {
                // Use loose comparison to handle number vs string
                const found = expectedValue.some(exp => exp == actualValue);
                if (!found) {
                    allConditionsMet = false;
                    break;
                }
                matchedConditions.push(`[${keyPath}]="${actualValue}"`);
            } else {
                // Use loose comparison (==) to match number vs string (e.g., 6.1 == "6.1")
                if (actualValue != expectedValue) {
                    allConditionsMet = false;
                    break;
                }
                matchedConditions.push(`[${keyPath}]="${actualValue}"`);
            }
        }
        
        // If all conditions are met, report the invalid combination error
        if (allConditionsMet && combo.action === "report_error") {
            console.log(`[validate_combo] INVALID COMBO DETECTED!`);
            return {
                valid: false,
                errorCode: `E300 Unsupported: invalid combination detected ${matchedConditions.join(' with ')}`,
                errorMessage: `E300 Unsupported: invalid combination detected ${matchedConditions.join(' with ')}`
            };
        }
    }
    console.log('[validate_combo] No invalid combinations found');
    return { valid: true, errorCode: '0', errorMessage: 'OK' };
}


/**
 * Main Compatibility Analysis Function
 * 
 * @param {Object} yamlData - Parsed YAML object to validate
 * @returns {string} Result in format "bool:errorCode"
 *                   - Success: "True:0"
 *                   - Failure: "False:E001", "False:E002", "False:E101", "False:E102", "False:E300"
 */
function compatibility_analysis(yamlData) {
    try {
        // Input validation
        if (!yamlData || typeof yamlData !== 'object') {
            return 'False:E000';
        }
        
        // Step 1: Validate required root keys (E001)
        const rootKeysResult = validateRequiredRootKeys(yamlData);
        if (!rootKeysResult.valid) {
            console.error(`[${rootKeysResult.errorCode}] ${rootKeysResult.errorMessage}`);
            return `False:${rootKeysResult.errorCode}`;
        }
        
        // Step 2: Validate mandatory non-empty keys (E002)
        const nonEmptyKeysResult = validateMandatoryNonEmptyKeys(yamlData);
        if (!nonEmptyKeysResult.valid) {
            console.error(`[${nonEmptyKeysResult.errorCode}] ${nonEmptyKeysResult.errorMessage}`);
            return `False:${nonEmptyKeysResult.errorCode}`;
        }
        
        // Step 3: Validate value types (E101)
        const valueTypesResult = validateValueTypes(yamlData);
        if (!valueTypesResult.valid) {
            console.error(`[${valueTypesResult.errorCode}] ${valueTypesResult.errorMessage}`);
            return `False:${valueTypesResult.errorCode}`;
        }
        
        // Step 4: Validate value ranges (E102)
        const valueRangesResult = validateValueRanges(yamlData);
        if (!valueRangesResult.valid) {
            console.error(`[${valueRangesResult.errorCode}] ${valueRangesResult.errorMessage}`);
            return `False:${valueRangesResult.errorCode}`;
        }
        
        // Step 5: Validate invalid combinations (E300)
        const comboResult = validate_combo(yamlData);
        if (!comboResult.valid) {
            console.error(`[${comboResult.errorCode}] ${comboResult.errorMessage}`);
            return `False:${comboResult.errorCode}`;
        }
        
        // All validations passed
        console.log('[SUCCESS] Compatibility analysis passed');
        return 'True:0';
        
    } catch (error) {
        console.error('[ERROR] Compatibility analysis failed with exception:', error);
        return 'False:E999';
    }
}

// ============================================================================
// End of Compatibility Analysis Functions
// ============================================================================

// Download YAML file
function downloadYAML() {
    try {
        const yamlText = yamlContent.textContent;
        
        // 测试1：空内容
        // let yamlText = '';
        
        // 测试2：错误格式 - 选择以下任意一个测试
        // let yamlText = 'key: value\n  bad indent: value';  // 缩进错误
        // let yamlText = 'key: "unclosed string';  // 未闭合引号
        // let yamlText = 'key: value\n:\ninvalid';  // 无效键
        // let yamlText = 'key: [1, 2, 3';  // 未闭合数组
        // let yamlText = 'key:\n\tbad_tab: value';  // Tab字符（YAML不允许）

        // 调试信息
        console.log('yamlText length:', yamlText ? yamlText.length : 'null/undefined');
        console.log('yamlText content:', yamlText);
        
        // Check if YAML content is empty
        if (!yamlText || yamlText.trim().length === 0) {
            showNotification('Test plan download failed!\nContent empty!', 'error');
            return;
        }
        
        // Check for format errors (basic validation)
        // Check if content contains "Error:" which indicates generation error
        const validationResult = isValidYAML(yamlText);
        if (!validationResult.valid) {
            const lineInfo = validationResult.lineNumber ? `line ${validationResult.lineNumber}\n` : '';
            showNotification(`Test plan download failed!\n${lineInfo}Invalid yaml format!`, 'error');
            return;
        }
        
         // Perform compatibility analysis if parsing succeeded
        if (yamlText) {
            // Parse YAML text to object first
            let yamlDataObject = null;
            try {
                if (typeof jsyaml !== 'undefined') {
                    yamlDataObject = jsyaml.load(yamlText);
                } else {
                    console.warn('js-yaml library not loaded, skipping compatibility check');
                }
            } catch (parseError) {
                console.error('YAML parse error for compatibility check:', parseError);
                showNotification('Test plan download failed!\nYAML parse error!', 'error');
                return;
            }
            
            // Run compatibility analysis on parsed object
            if (yamlDataObject) {
                const compatResult = compatibility_analysis(yamlDataObject);
                // Split only at the first colon to preserve complete error message
                const colonIndex = compatResult.indexOf(':');
                const isValid = compatResult.substring(0, colonIndex);
                const errorCode = compatResult.substring(colonIndex + 1);
                
                if (isValid === 'False') {
                    console.error(`Compatibility check failed: ${errorCode}`);
                    const lineNumber = findLineNumberInYAML(yamlText, errorCode);
                    const lineInfo = lineNumber ? `line ${lineNumber}\n` : '';
                    showNotification(`Test plan download failed!\n${lineInfo}Compatibility error!\n${errorCode}`, 'error');
                    return;
                }
            }
        }

        // Generate filename with current date and time
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        const filename = `test_plan_${year}-${month}-${day}_${hours}${minutes}${seconds}.yaml`;
        
        const blob = new Blob([yamlText], { type: 'text/yaml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showNotification('Test plan download success!');
    } catch (error) {
        console.error('Download error:', error);
        showNotification('Test plan download failed!\nPlease try later!', 'error');
    }
}

// Show notification
function showNotification(message, type = 'success') {
    notification.textContent = message;
    notification.className = 'notification';
    if (type === 'error') {
        notification.classList.add('error');
    }
    notification.style.display = 'block';
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// Reset form
function resetForm() {
    form.reset();
    // Reset to default values
    cpuSelect.value = "Ryzen Threadripper";
    gpuSelect.value = "Radeon RX 7900 Series";
    
    selectedMachines = [];
    selectedTestCases = [];
    filteredMachines = [...mockMachines];
    customGroups = {};
    renderMachines();
    renderTestTypeGroups();
    renderTestCases();
    hideCustomGroupModal();
    searchResults.classList.add('hidden');
    yamlOutput.style.display = 'none';
    updateProgress();
    localStorage.removeItem('tpgen-data');
}

// Save form data to localStorage
function saveToStorage() {
    const formData = new FormData(form);
    const data = {
        formData: Object.fromEntries(formData),
        selectedMachines,
        selectedTestCases,
        customGroups,
        nextCustomId
    };
    localStorage.setItem('tpgen-data', JSON.stringify(data));
}

// Load form data from localStorage
function loadFromStorage() {
    const savedData = localStorage.getItem('tpgen-data');
    if (savedData) {
        const data = JSON.parse(savedData);
        
        // Restore form fields
        for (const [key, value] of Object.entries(data.formData)) {
            const element = form.elements[key];
            if (element) {
                if (element.type === 'checkbox' || element.type === 'radio') {
                    element.checked = value;
                } else {
                    element.value = value;
                }
            }
        }
        
        // Restore selected machines and test cases
        selectedMachines = data.selectedMachines || [];
        selectedTestCases = data.selectedTestCases || [];
        customGroups = data.customGroups || {};
        nextCustomId = data.nextCustomId || 1000;
        
        // Filter machines based on restored selections
        filterMachines();
        renderMachines();
        updateIndividualConfigs();
        renderTestTypeGroups();
        renderTestCases();
        updateProgress();
        
        // Update test case checkboxes
        selectedTestCases.forEach(testCase => {
            const checkbox = document.getElementById(`test-case-${testCase.id}`);
            if (checkbox) {
                checkbox.checked = true;
            }
        });
    }
}

// Set up event listeners
function setupEventListeners() {
    // Tab functionality
    setupTabs();
    
    // Upload functionality
    setupUpload();
    
    // Analyze button
    analyzeBtn.addEventListener('click', analyzeYaml);
    
    // Filter machines when CPU or GPU selection changes
    cpuSelect.addEventListener('change', filterMachines);
    gpuSelect.addEventListener('change', filterMachines);
    
    // Clear filter button
    clearFilterBtn.addEventListener('click', clearFilter);
    
    // Batch operation buttons
    selectAllBtn.addEventListener('click', selectAllMachines);
    invertSelectionBtn.addEventListener('click', invertSelection);
    clearSelectionBtn.addEventListener('click', clearAllSelections);
    
    // Clear invalid selections button
    clearInvalidBtn.addEventListener('click', clearInvalidSelections);
    
    // Toggle between same and individual OS configuration
    document.getElementById('same-os').addEventListener('change', function() {
        if (this.checked) {
            sameOsConfig.classList.remove('hidden');
            individualOsConfig.classList.add('hidden');
        }
    });
    
    document.getElementById('individual-os').addEventListener('change', function() {
        if (this.checked) {
            sameOsConfig.classList.add('hidden');
            individualOsConfig.classList.remove('hidden');
        }
    });
    
    // Toggle between same and individual kernel configuration
    document.getElementById('same-kernel').addEventListener('change', function() {
        if (this.checked) {
            sameKernelConfig.classList.remove('hidden');
            individualKernelConfig.classList.add('hidden');
        }
    });
    
    document.getElementById('individual-kernel').addEventListener('change', function() {
        if (this.checked) {
            sameKernelConfig.classList.add('hidden');
            individualKernelConfig.classList.remove('hidden');
        }
    });
    
    // Update selected test cases when checkboxes change
    document.addEventListener('change', function(e) {
        if (e.target.name === 'test-case') {
            updateSelectedTestCases();
            updateProgress();
        }
    });
    
    // Search functionality
    testCaseSearch.addEventListener('input', function() {
        searchTestCases(this.value);
    });
    
    existingCaseSearch.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const items = existingCasesList.querySelectorAll('.existing-case-item');
        
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    });
    
    // Custom group functionality
    addCustomGroupBtn.addEventListener('click', showCustomGroupModal);
    addTestCaseBtn.addEventListener('click', addTestCaseToCustomGroup);
    saveCustomGroupBtn.addEventListener('click', saveCustomGroup);
    cancelCustomGroupBtn.addEventListener('click', hideCustomGroupModal);
    closeModalBtn.addEventListener('click', hideCustomGroupModal);
    
    // Close modal when clicking outside
    customGroupModal.addEventListener('click', function(e) {
        if (e.target === this) {
            hideCustomGroupModal();
        }
    });
    
    // Form change events
    form.addEventListener('change', () => {
        saveToStorage();
        updateProgress();
    });
    
    // Generate button
    generateBtn.addEventListener('click', generateYAML);
    
    // Reset button
    resetBtn.addEventListener('click', resetForm);
    
    // Copy button
    copyBtn.addEventListener('click', copyToClipboard);
    
    // Download button
    downloadBtn.addEventListener('click', downloadYAML);
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', init);