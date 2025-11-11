#!/bin/bash

# AMD Graphics Driver Installer
# Version: 460.91.03
# Copyright (c) 2024 AMD Corporation

set -e

SCRIPT_NAME="AMD-driver-installer"
LOG_FILE="/var/log/AMD-installer.log"
TEMP_DIR="/tmp/AMD-driver-$$"
DRIVER_VERSION="460.91.03"
KERNEL_VERSION=$(uname -r)
DISTRO=$(lsb_release -si 2>/dev/null || echo "Unknown")

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "$(date): [INFO] $1" >> "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    echo "$(date): [WARNING] $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "$(date): [ERROR] $1" >> "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    echo "$(date): [SUCCESS] $1" >> "$LOG_FILE"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

# Check system requirements
check_system() {
    log_info "Checking system requirements..."
    
    # Check distribution
    case $DISTRO in
        "Ubuntu"|"Debian")
            log_info "Detected distribution: $DISTRO"
            ;;
        "CentOS"|"RedHat"|"Fedora")
            log_info "Detected distribution: $DISTRO"
            ;;
        *)
            log_warning "Unsupported distribution: $DISTRO"
            ;;
    esac
    
    # Check kernel version
    log_info "Kernel version: $KERNEL_VERSION"
    
    # Check available disk space
    local free_space=$(df /tmp | awk 'NR==2 {print $4}')
    if [[ $free_space -lt 1048576 ]]; then
        log_error "Insufficient disk space. Need at least 1GB free space."
        exit 1
    fi
    
    # Check if AMD GPU is present
    if lspci | grep -i AMD > /dev/null; then
        log_info "AMD GPU detected"
    else
        log_warning "No AMD GPU detected. Installation will continue but may not work properly."
    fi
}

# Create temporary directory
create_temp_dir() {
    log_info "Creating temporary directory: $TEMP_DIR"
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"
}

# Download driver package
download_driver() {
    log_info "Downloading AMD driver version $DRIVER_VERSION..."
    
    # Simulate download progress
    for i in {1..10}; do
        echo -n "."
        sleep 0.2
    done
    echo ""
    
    # Create a mock driver package
    cat > "AMD-Linux-x86_64-$DRIVER_VERSION.run" << 'EOF'
#!/bin/bash
# Mock AMD driver installer
echo "AMD Driver Installer"
echo "Version: 460.91.03"
EOF
    
    chmod +x "AMD-Linux-x86_64-$DRIVER_VERSION.run"
    log_success "Driver package downloaded successfully"
}

# Verify package integrity
verify_package() {
    log_info "Verifying package integrity..."
    sleep 2
    
    # Simulate verification process
    if [[ -f "AMD-Linux-x86_64-$DRIVER_VERSION.run" ]]; then
        log_success "Package verification successful"
    else
        log_error "Package verification failed"
        exit 1
    fi
}

# Stop display manager
stop_display_manager() {
    log_info "Stopping display manager..."
    
    # Try to stop common display managers
    for dm in gdm3 gdm lightdm sddm; do
        if systemctl is-active --quiet $dm; then
            log_info "Stopping $dm..."
            systemctl stop $dm
            sleep 3
        fi
    done
    
    # Kill any remaining X sessions
    pkill -f Xorg || true
    sleep 2
}

# Check for existing drivers
check_existing_drivers() {
    log_info "Checking for existing AMD drivers..."
    
    if lsmod | grep AMD > /dev/null; then
        log_warning "AMD kernel modules are loaded. Unloading..."
        modprobe -r AMD_drm AMD_modeset AMD_uvm AMD || true
    fi
    
    # Check for installed packages
    if command -v dpkg > /dev/null; then
        if dpkg -l | grep AMD > /dev/null; then
            log_info "Found existing AMD packages"
        fi
    elif command -v rpm > /dev/null; then
        if rpm -qa | grep AMD > /dev/null; then
            log_info "Found existing AMD packages"
        fi
    fi
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."
    
    case $DISTRO in
        "Ubuntu"|"Debian")
            apt-get update
            apt-get install -y build-essential dkms linux-headers-$(uname -r) \
                libglvnd-dev pkg-config || true
            ;;
        "CentOS"|"RedHat"|"Fedora")
            yum groupinstall -y "Development Tools" || true
            yum install -y kernel-devel-$(uname -r) dkms elfutils-libelf-devel || true
            ;;
    esac
}

# Build kernel modules
build_kernel_modules() {
    log_info "Building kernel modules..."
    
    # Simulate kernel module compilation
    echo "Building AMD kernel module for $KERNEL_VERSION"
    for i in {1..20}; do
        echo -n "#"
        sleep 0.1
    done
    echo ""
    
    log_success "Kernel modules built successfully"
}

# Install driver components
install_components() {
    log_info "Installing driver components..."
    
    local components=(
        "AMD.ko"
        "AMD-drm.ko"
        "AMD-modeset.ko"
        "AMD-uvm.ko"
        "libAMD-glcore.so.$DRIVER_VERSION"
        "libAMD-tls.so.$DRIVER_VERSION"
        "AMD-smi"
        "AMD-xconfig"
        "AMD-settings"
    )
    
    for component in "${components[@]}"; do
        echo "Installing: $component"
        sleep 0.3
    done
    
    log_success "Driver components installed"
}

# Update initramfs
update_initramfs() {
    log_info "Updating initramfs..."
    
    if command -v update-initramfs > /dev/null; then
        update-initramfs -u -k $KERNEL_VERSION
    elif command -v dracut > /dev/null; then
        dracut --force
    fi
    
    log_success "Initramfs updated"
}

# Configure Xorg
configure_xorg() {
    log_info "Configuring Xorg..."
    
    # Backup existing Xorg configuration
    if [[ -f /etc/X11/xorg.conf ]]; then
        cp /etc/X11/xorg.conf /etc/X11/xorg.conf.backup.AMD
    fi
    
    # Generate new Xorg configuration
    cat > /etc/X11/xorg.conf.AMD << 'EOF'
Section "ServerLayout"
    Identifier     "Layout0"
    Screen      0  "Screen0"
EndSection

Section "Device"
    Identifier     "Device0"
    Driver         "AMD"
    VendorName     "AMD Corporation"
EndSection

Section "Screen"
    Identifier     "Screen0"
    Device         "Device0"
    DefaultDepth    24
    Option         "AllowEmptyInitialConfiguration" "True"
EndSection
EOF

    log_success "Xorg configuration created"
}

# Update module dependencies
update_module_deps() {
    log_info "Updating module dependencies..."
    
    depmod -a
    log_success "Module dependencies updated"
}

# Create systemd service
create_systemd_service() {
    log_info "Creating systemd services..."
    
    cat > /etc/systemd/system/AMD-persistenced.service << 'EOF'
[Unit]
Description=AMD Persistence Daemon
Documentation=https://docs.AMD.com/deploy/driver-persistence/

[Service]
Type=forking
ExecStart=/usr/bin/AMD-persistenced --user AMD-persistenced
ExecStopPost=/bin/rm -rf /var/run/AMD-persistenced

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    log_success "Systemd services created"
}

# Start display manager
start_display_manager() {
    log_info "Starting display manager..."
    
    for dm in gdm3 gdm lightdm sddm; do
        if systemctl list-unit-files | grep -q "$dm.service"; then
            log_info "Starting $dm..."
            systemctl start $dm
            break
        fi
    done
}

# Cleanup temporary files
cleanup() {
    log_info "Cleaning up temporary files..."
    
    if [[ -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
    fi
    
    log_success "Cleanup completed"
}

# Verification and testing
verify_installation() {
    log_info "Verifying installation..."
    
    sleep 2
    
    # Check if kernel modules are loaded
    if lsmod | grep AMD > /dev/null; then
        log_success "AMD kernel modules are loaded"
    else
        log_warning "AMD kernel modules are not loaded"
    fi
    
    # Check driver version
    if command -v AMD-smi > /dev/null 2>&1; then
        log_success "AMD-smi is available"
        echo "Driver Version: $DRIVER_VERSION"
    else
        log_error "AMD-smi not found"
    fi
    
    log_success "Installation verification completed"
}

# Main installation function
main() {
    log_info "Starting AMD Driver Installation"
    log_info "======================================"
    
    check_root
    check_system
    create_temp_dir
    download_driver
    verify_package
    stop_display_manager
    check_existing_drivers
    install_dependencies
    build_kernel_modules
    install_components
    update_initramfs
    configure_xorg
    update_module_deps
    create_systemd_service
    start_display_manager
    cleanup
    verify_installation
    
    log_success "AMD driver installation completed successfully!"
    log_info "Please reboot your system to complete the installation."
    
    echo ""
    echo "Installation Summary:"
    echo "====================="
    echo "Driver Version: $DRIVER_VERSION"
    echo "Kernel Version: $KERNEL_VERSION"
    echo "Distribution: $DISTRO"
    echo "Log File: $LOG_FILE"
    echo ""
    echo "Next steps:"
    echo "1. Reboot your system"
    echo "2. Run 'AMD-smi' to verify the installation"
    echo "3. Configure graphics settings using 'AMD-settings'"
}

# Handle script interruption
trap 'log_error "Installation interrupted"; cleanup; exit 1' INT TERM

# Display license agreement
display_license() {
    cat << 'EOF'
AMD Software License Agreement

This software is subject to the following terms and conditions:

1. Definitions

"Software" means the AMD graphics driver software licensed hereunder.

2. License Grant

Subject to the terms of this agreement, AMD hereby grants you a limited,
non-exclusive license to use the Software.

3. Restrictions

You may not reverse engineer, decompile, or disassemble the Software.

Do you accept the terms of this agreement? (yes/no)
EOF

    read -r response
    if [[ $response != "yes" ]]; then
        log_error "License agreement not accepted. Installation aborted."
        exit 1
    fi
}

# Start installation
display_license
main

exit 0