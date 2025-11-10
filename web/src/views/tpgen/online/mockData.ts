import type { Machine, TestCaseGroup } from './types'

// Mock 机器数据
export const mockMachines: Machine[] = [
  { id: 1, name: 'Machine A', motherboard: 'ASUS Pro WS X570-ACE', gpu: 'Radeon RX 7900 Series', cpu: 'Ryzen Threadripper', status: 'Available' },
  { id: 2, name: 'Machine B', motherboard: 'Gigabyte B550 AORUS', gpu: 'Radeon RX 7900 Series', cpu: 'Ryzen Threadripper', status: 'Available' },
  { id: 3, name: 'Machine C', motherboard: 'ASRock X570 Taichi', gpu: 'Radeon RX 6800 Series', cpu: 'Ryzen 7', status: 'Available' },
  { id: 4, name: 'Machine D', motherboard: 'MSI MEG X570 GODLIKE', gpu: 'Radeon Pro W7800', cpu: 'EPYC', status: 'Available' },
  { id: 5, name: 'Machine E', motherboard: 'ASUS Pro WS X570-ACE', gpu: 'Radeon Pro W6800', cpu: 'Ryzen Threadripper', status: 'Available' },
  { id: 6, name: 'Machine F', motherboard: 'Gigabyte B550 AORUS', gpu: 'Radeon RX 6800 Series', cpu: 'Ryzen 9', status: 'Available' },
  { id: 7, name: 'Machine G', motherboard: 'ASRock X570 Taichi', gpu: 'Radeon RX 7900 Series', cpu: 'EPYC', status: 'Available' },
  { id: 8, name: 'Machine H', motherboard: 'MSI MEG X570 GODLIKE', gpu: 'Radeon Pro W6800', cpu: 'Ryzen 7', status: 'Available' },
  { id: 9, name: 'Machine I', motherboard: 'ASUS Pro WS X570-ACE', gpu: 'Radeon RX 6800 Series', cpu: 'Ryzen Threadripper', status: 'Available' },
  { id: 10, name: 'Machine J', motherboard: 'Gigabyte B550 AORUS', gpu: 'Radeon Pro W7800', cpu: 'Ryzen 9', status: 'Available' },
]

// 测试用例组数据
export const testCaseGroups: TestCaseGroup = {
  Benchmark: {
    ffmpeg: [
      { id: 101, name: 'H.264 Encoding', description: 'Benchmark H.264 video encoding performance' },
      { id: 102, name: 'H.265 Decoding', description: 'Benchmark H.265 video decoding performance' },
      { id: 103, name: 'AV1 Transcoding', description: 'Benchmark AV1 video transcoding performance' },
    ],
    clpeak: [
      { id: 104, name: 'Global Memory Bandwidth', description: 'Measure global memory bandwidth' },
      { id: 105, name: 'Single-Precision Compute', description: 'Measure single-precision compute performance' },
      { id: 106, name: 'Double-Precision Compute', description: 'Measure double-precision compute performance' },
    ],
  },
  Functional: {
    Compute: [
      { id: 201, name: 'OpenCL Basic Operations', description: 'Test basic OpenCL operations' },
      { id: 202, name: 'Vulkan Compute Shaders', description: 'Test Vulkan compute shaders' },
    ],
    Media: [
      { id: 203, name: 'Video Playback', description: 'Test video playback functionality' },
      { id: 204, name: 'Image Processing', description: 'Test image processing capabilities' },
    ],
  },
  Performance: {
    Gaming: [
      { id: 301, name: '3D Gaming Benchmark', description: 'Measure 3D gaming performance' },
      { id: 302, name: 'VR Performance Test', description: 'Test VR performance' },
    ],
    Rendering: [
      { id: 303, name: '3D Model Rendering', description: 'Measure 3D model rendering performance' },
      { id: 304, name: 'Ray Tracing Performance', description: 'Test ray tracing performance' },
    ],
  },
  Stress: {
    Memory: [
      { id: 401, name: 'Memory Stress Test', description: 'Stress test system memory' },
      { id: 402, name: 'VRAM Stress Test', description: 'Stress test GPU memory' },
    ],
    Compute: [
      { id: 403, name: 'Compute Stress Test', description: 'Stress test compute capabilities' },
      { id: 404, name: 'Thermal Stress Test', description: 'Stress test thermal management' },
    ],
  },
}

// CPU 选项
export const cpuOptions = [
  { label: 'Ryzen Threadripper', value: 'Ryzen Threadripper' },
  { label: 'EPYC', value: 'EPYC' },
  { label: 'Ryzen 9', value: 'Ryzen 9' },
  { label: 'Ryzen 7', value: 'Ryzen 7' },
]

// GPU 选项
export const gpuOptions = [
  { label: 'Radeon RX 7900 Series', value: 'Radeon RX 7900 Series' },
  { label: 'Radeon Pro W7800', value: 'Radeon Pro W7800' },
  { label: 'Radeon RX 6800 Series', value: 'Radeon RX 6800 Series' },
  { label: 'Radeon Pro W6800', value: 'Radeon Pro W6800' },
]

// OS 选项
export const osOptions = [
  { label: 'Ubuntu 22.04', value: 'Ubuntu 22.04' },
  { label: 'Ubuntu 20.04', value: 'Ubuntu 20.04' },
  { label: 'RHEL 9', value: 'RHEL 9' },
  { label: 'RHEL 8', value: 'RHEL 8' },
  { label: 'CentOS Stream', value: 'CentOS Stream' },
]

// 部署方式选项
export const deploymentOptions = [
  { label: 'Bare Metal', value: 'Bare Metal' },
  { label: 'Virtual Machine', value: 'Virtual Machine' },
  { label: 'Container', value: 'Container' },
]

// 内核类型选项
export const kernelTypeOptions = [
  { label: 'DKMS', value: 'DKMS' },
  { label: 'Mainline', value: 'Mainline' },
  { label: 'Custom Build', value: 'Custom Build' },
  { label: 'LTS', value: 'LTS' },
]

// 内核版本选项
export const kernelVersionOptions = [
  { label: '6.1', value: '6.1' },
  { label: '6.0', value: '6.0' },
  { label: '5.15', value: '5.15' },
  { label: '5.10', value: '5.10' },
]

// 固件版本选项
export const firmwareVersionOptions = [
  { label: '2023.07', value: '2023.07' },
  { label: '2023.05', value: '2023.05' },
  { label: '2023.03', value: '2023.03' },
  { label: '2022.12', value: '2022.12' },
]

