/**
 * Mock data for kernel, OS, and deployment configurations
 */

export interface SelectOption {
  label: string
  value: string
}

// Operating System options
export const osOptions: SelectOption[] = [
  { label: 'Ubuntu 20.04', value: 'ubuntu-20.04' },
  { label: 'Ubuntu 22.04', value: 'ubuntu-22.04' },
  { label: 'Ubuntu 24.04', value: 'ubuntu-24.04' },
  { label: 'RHEL 8', value: 'rhel-8' },
  { label: 'RHEL 9', value: 'rhel-9' },
  { label: 'CentOS 7', value: 'centos-7' },
  { label: 'CentOS 8', value: 'centos-8' },
  { label: 'Debian 11', value: 'debian-11' },
  { label: 'Debian 12', value: 'debian-12' },
]

// Deployment options
export const deploymentOptions: SelectOption[] = [
  { label: 'Bare Metal', value: 'bare-metal' },
  { label: 'Virtual Machine', value: 'vm' },
  { label: 'Docker Container', value: 'docker' },
  { label: 'Kubernetes Pod', value: 'k8s' },
]

// Kernel type options
export const kernelTypeOptions: SelectOption[] = [
  { label: 'Default Kernel', value: 'default' },
  { label: 'Real-time Kernel', value: 'realtime' },
  { label: 'Low-latency Kernel', value: 'lowlatency' },
  { label: 'Custom Kernel', value: 'custom' },
]

// Kernel version options
export const kernelVersionOptions: SelectOption[] = [
  { label: '5.15.0', value: '5.15.0' },
  { label: '5.19.0', value: '5.19.0' },
  { label: '6.1.0', value: '6.1.0' },
  { label: '6.2.0', value: '6.2.0' },
  { label: '6.5.0', value: '6.5.0' },
]

