#!/bin/bash
# infra/setup.sh
# Run once on a fresh EC2 Ubuntu 22.04 t2.micro instance
# Usage: bash setup.sh

set -e

echo "──────────────────────────────────────────────"
echo "  CodeJudge EC2 Bootstrap"
echo "──────────────────────────────────────────────"

# ── 1. System update ──────────────────────────────
apt-get update -y
apt-get upgrade -y

# ── 2. Install Docker ─────────────────────────────
apt-get install -y ca-certificates curl gnupg lsb-release git

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  > /etc/apt/sources.list.d/docker.list

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

systemctl enable docker
systemctl start docker

# Allow ubuntu user to use docker
usermod -aG docker ubuntu

# ── 3. Install Docker Compose standalone ─────────
COMPOSE_VERSION="v2.27.0"
curl -SL "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-linux-x86_64" \
    -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# ── 4. Configure swap (needed on t2.micro 1GB RAM) ─
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# ── 5. Clone repo ─────────────────────────────────
# Replace with your actual repo URL
REPO_URL=${REPO_URL:-"https://github.com/YOUR_USERNAME/codejudge.git"}
git clone "$REPO_URL" /opt/codejudge

cd /opt/codejudge

# ── 6. Setup .env ─────────────────────────────────
cp .env.example .env
echo ""
echo "⚠️  Edit /opt/codejudge/.env with your secrets before continuing!"
echo ""

# ── 7. Build sandbox images ───────────────────────
echo "Building sandbox images..."
docker build -t codejudge-cpp    ./sandbox/cpp
docker build -t codejudge-python ./sandbox/python
docker build -t codejudge-java   ./sandbox/java

# ── 8. Pull base images ───────────────────────────
docker pull postgres:15-alpine
docker pull redis:7-alpine
docker pull nginx:alpine

echo ""
echo "──────────────────────────────────────────────"
echo "  Setup complete!"
echo "  Next steps:"
echo "  1. Edit /opt/codejudge/.env"
echo "  2. cd /opt/codejudge && docker-compose up -d"
echo "──────────────────────────────────────────────"
