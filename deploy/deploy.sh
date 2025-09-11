#!/bin/bash
# Survey Dashboard - One-click Deployment Script
# Usage: curl -sSL https://raw.githubusercontent.com/your-repo/main/deploy/deploy.sh | bash

set -e

echo "🚀 Survey Dashboard - Automated Deployment"
echo "=========================================="

# Configuration
REPO_URL="https://github.com/your-username/survey-dashboard.git"
INSTALL_DIR="/opt/survey-dashboard"
SERVICE_USER="survey"
DOMAIN=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --domain)
            DOMAIN="$2"
            shift 2
            ;;
        --install-dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Function to detect OS
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
    else
        echo "❌ Unsupported operating system"
        exit 1
    fi
}

# Function to install dependencies
install_dependencies() {
    echo "📦 Installing system dependencies..."
    
    case $OS in
        "Ubuntu"*|"Debian"*)
            apt-get update
            apt-get install -y python3 python3-pip python3-venv git nginx supervisor curl
            ;;
        "CentOS"*|"Red Hat"*|"Fedora"*)
            yum update -y
            yum install -y python3 python3-pip git nginx supervisor curl
            ;;
        *)
            echo "❌ Unsupported OS: $OS"
            exit 1
            ;;
    esac
}

# Function to create service user
create_user() {
    echo "👤 Creating service user..."
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd --system --home-dir "$INSTALL_DIR" --shell /bin/bash --create-home "$SERVICE_USER"
    fi
}

# Function to clone repository
clone_repo() {
    echo "📥 Cloning repository..."
    if [[ -d "$INSTALL_DIR" ]]; then
        echo "⚠️  Installation directory exists. Backing up..."
        mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%Y%m%d%H%M%S)"
    fi
    
    git clone "$REPO_URL" "$INSTALL_DIR"
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
}

# Function to setup Python environment
setup_python() {
    echo "🐍 Setting up Python environment..."
    
    cd "$INSTALL_DIR"
    sudo -u "$SERVICE_USER" python3 -m venv venv
    sudo -u "$SERVICE_USER" ./venv/bin/pip install --upgrade pip
    sudo -u "$SERVICE_USER" ./venv/bin/pip install -r backend/requirements.txt
    sudo -u "$SERVICE_USER" ./venv/bin/python -m spacy download en_core_web_sm
}

# Function to configure supervisor
configure_supervisor() {
    echo "⚙️  Configuring supervisor..."
    
    cat > /etc/supervisor/conf.d/survey-dashboard.conf << EOF
[program:survey-dashboard]
command=$INSTALL_DIR/venv/bin/python app.py
directory=$INSTALL_DIR/backend
user=$SERVICE_USER
autostart=true
autorestart=true
stdout_logfile=/var/log/survey-dashboard.log
stderr_logfile=/var/log/survey-dashboard-error.log
environment=FLASK_ENV="production"
EOF

    supervisorctl reread
    supervisorctl update
    supervisorctl start survey-dashboard
}

# Function to configure nginx
configure_nginx() {
    echo "🌐 Configuring nginx..."
    
    if [[ -n "$DOMAIN" ]]; then
        SERVER_NAME="server_name $DOMAIN;"
    else
        SERVER_NAME="server_name _;"
    fi
    
    cat > /etc/nginx/sites-available/survey-dashboard << EOF
server {
    listen 80;
    $SERVER_NAME
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
    }
}
EOF

    ln -sf /etc/nginx/sites-available/survey-dashboard /etc/nginx/sites-enabled/
    nginx -t && systemctl restart nginx
}

# Function to setup SSL (optional)
setup_ssl() {
    if [[ -n "$DOMAIN" ]]; then
        echo "🔒 Setting up SSL certificate..."
        apt-get install -y certbot python3-certbot-nginx
        certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email admin@"$DOMAIN"
    fi
}

# Function to create backup script
create_backup() {
    echo "💾 Setting up backup system..."
    
    cat > "$INSTALL_DIR/backup.sh" << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/survey-dashboard"
DATE=$(date +%Y%m%d)

mkdir -p "$BACKUP_DIR"
cp -r /opt/survey-dashboard/backend/data "$BACKUP_DIR/data_$DATE"
tar -czf "$BACKUP_DIR/app_$DATE.tar.gz" /opt/survey-dashboard

# Keep only last 30 days
find "$BACKUP_DIR" -name "data_*" -mtime +30 -exec rm -rf {} +
find "$BACKUP_DIR" -name "app_*.tar.gz" -mtime +30 -delete
EOF

    chmod +x "$INSTALL_DIR/backup.sh"
    
    # Add to crontab for daily backup
    (crontab -l 2>/dev/null; echo "0 2 * * * $INSTALL_DIR/backup.sh") | crontab -
}

# Function to print completion message
print_completion() {
    echo ""
    echo "🎉 Survey Dashboard Deployment Complete!"
    echo "========================================"
    echo ""
    echo "📊 Dashboard URL: http://$(curl -s ifconfig.me || echo 'localhost'):80"
    if [[ -n "$DOMAIN" ]]; then
        echo "📊 Custom Domain: https://$DOMAIN"
    fi
    echo "🔐 Login: admin / surveydash2024"
    echo "📁 Installation: $INSTALL_DIR"
    echo "📋 Logs: /var/log/survey-dashboard.log"
    echo ""
    echo "Management Commands:"
    echo "  Status:  supervisorctl status survey-dashboard"
    echo "  Restart: supervisorctl restart survey-dashboard"
    echo "  Logs:    tail -f /var/log/survey-dashboard.log"
    echo "  Backup:  $INSTALL_DIR/backup.sh"
    echo ""
    echo "✅ Your survey dashboard is ready for production use!"
}

# Main deployment process
main() {
    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        echo "❌ This script must be run as root (use sudo)"
        exit 1
    fi
    
    detect_os
    install_dependencies
    create_user
    clone_repo
    setup_python
    configure_supervisor
    configure_nginx
    
    if [[ -n "$DOMAIN" ]]; then
        setup_ssl
    fi
    
    create_backup
    print_completion
}

# Run main function
main "$@"