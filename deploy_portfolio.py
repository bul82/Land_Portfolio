#!/usr/bin/env python3
import os
import sys
import datetime
import paramiko

# Configuration
HOST = "138.16.225.102"
USER = "root"
KEY_FILE = "/Users/bul82/.ssh/catalog_zoj_vps"
PROJECT_NAME = "land-portfolio"
LOCAL_DIR = "/Users/bul82/Documents/Land_Portfolio"

def run_command_over_ssh(ssh_client, cmd):
    print(f"Running remote command: {cmd}")
    stdin, stdout, stderr = ssh_client.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    out_text = stdout.read().decode().strip()
    err_text = stderr.read().decode().strip()
    if exit_status != 0:
        print(f"Command failed with exit code {exit_status}")
        if err_text:
            print(f"Error output:\n{err_text}")
    return exit_status, out_text, err_text

def deploy():
    print("=== Land Portfolio VPS Deployment ===")
    
    # 1. Establish SSH connection bypassing the VPN
    print("\nConnecting to VPS using physical interface en0 routing bypass...")
    try:
        proxy = paramiko.ProxyCommand(f'nc -b en0 {HOST} 22')
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Load the private key
        pkey = paramiko.Ed25519Key.from_private_key_file(KEY_FILE)
        
        ssh.connect(
            hostname=HOST,
            username=USER,
            pkey=pkey,
            sock=proxy,
            timeout=15
        )
        print("Successfully connected to VPS SSH server!")
    except Exception as e:
        print(f"SSH connection failed: {e}")
        sys.exit(1)
        
    # 2. Create release directories
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    remote_base_dir = f"/var/www/landings/{PROJECT_NAME}"
    remote_release_dir = f"{remote_base_dir}/releases/{timestamp}"
    
    print(f"\nCreating release directory on server: {remote_release_dir}")
    run_command_over_ssh(ssh, f"mkdir -p {remote_release_dir}/assets/generated")
    run_command_over_ssh(ssh, f"mkdir -p {remote_release_dir}/assets/portfolio")
    run_command_over_ssh(ssh, f"mkdir -p {remote_release_dir}/assets/fonts")
    
    # 3. Upload files via SFTP
    print("\nUploading project code and assets via SFTP...")
    try:
        sftp = ssh.open_sftp()
        
        # Upload main HTML & CSS & JS and backend server files
        files_to_upload = ["index.html",
    "privacy.html", "styles.css", "script.js", "server.py", ".env"]
        for f in files_to_upload:
            local_path = os.path.join(LOCAL_DIR, f)
            remote_path = f"{remote_release_dir}/{f}"
            print(f"Uploading: {f} -> {remote_path}")
            sftp.put(local_path, remote_path)
            
        # Upload assets/generated
        local_generated = os.path.join(LOCAL_DIR, "assets", "generated")
        if os.path.exists(local_generated):
            for f in os.listdir(local_generated):
                if f.endswith((".jpg", ".png")):
                    local_path = os.path.join(local_generated, f)
                    remote_path = f"{remote_release_dir}/assets/generated/{f}"
                    print(f"Uploading generated asset: assets/generated/{f}")
                    sftp.put(local_path, remote_path)
                    
        # Upload assets/portfolio
        local_portfolio = os.path.join(LOCAL_DIR, "assets", "portfolio")
        if os.path.exists(local_portfolio):
            for f in os.listdir(local_portfolio):
                if f.endswith((".jpg", ".png", ".webm", ".mp4")):
                    local_path = os.path.join(local_portfolio, f)
                    remote_path = f"{remote_release_dir}/assets/portfolio/{f}"
                    print(f"Uploading portfolio asset: assets/portfolio/{f}")
                    sftp.put(local_path, remote_path)
                    
        # Upload assets/fonts
        local_fonts = os.path.join(LOCAL_DIR, "assets", "fonts")
        if os.path.exists(local_fonts):
            for f in os.listdir(local_fonts):
                if f.endswith((".woff2", ".css")):
                    local_path = os.path.join(local_fonts, f)
                    remote_path = f"{remote_release_dir}/assets/fonts/{f}"
                    print(f"Uploading font asset: assets/fonts/{f}")
                    sftp.put(local_path, remote_path)
            
        sftp.close()
        print("All assets uploaded successfully!")
    except Exception as e:
        print(f"SFTP upload failed: {e}")
        ssh.close()
        sys.exit(1)
        
    # 4. Update symlink to point to the new release
    print("\nUpdating symlinks...")
    current_symlink = f"{remote_base_dir}/current"
    symlink_cmd = f"ln -sfn releases/{timestamp} {current_symlink}"
    exit_status, _, _ = run_command_over_ssh(ssh, symlink_cmd)
    
    if exit_status == 0:
        print(f"Deployment successful! Symlink updated: {current_symlink} -> releases/{timestamp}")
    else:
        print("Failed to update symlink on remote VPS.")
        ssh.close()
        sys.exit(1)
        
    # 5. Fix permissions for www-data
    print("\nSetting ownership permissions on remote server...")
    run_command_over_ssh(ssh, f"chown -R www-data:www-data {remote_base_dir}")
    
    # 6. Reload systemd, enable and restart portfolio-feedback service
    print("\nEnabling and restarting portfolio-feedback systemd service...")
    run_command_over_ssh(ssh, "systemctl daemon-reload")
    run_command_over_ssh(ssh, "systemctl enable portfolio-feedback.service")
    run_command_over_ssh(ssh, "systemctl restart portfolio-feedback.service")
        
    ssh.close()
    print("\n=== Land Portfolio VPS Deployment Completed Successfully! ===")
    print(f"Live URL: https://{HOST}/")
    print(f"Domain URL: https://bul82info.ru/")

if __name__ == "__main__":
    deploy()
