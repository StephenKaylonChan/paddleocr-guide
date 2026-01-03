# 部署指南

> PaddleOCR 应用的生产环境部署方案

本指南提供从开发到生产的完整部署方案，包括 Docker、云平台和性能优化。

---

## 目录

- [一、Docker 部署](#一docker-部署)
- [二、生产环境配置](#二生产环境配置)
- [三、云平台部署](#三云平台部署)
- [四、监控和运维](#四监控和运维)

---

## 一、Docker 部署

### 1.1 基础 Dockerfile

**文件**: `Dockerfile`

```dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 安装项目
RUN pip install -e .

# 暴露端口（如果需要 API 服务）
EXPOSE 8000

# 启动命令
CMD ["python", "app.py"]
```

---

### 1.2 优化的 Dockerfile（多阶段构建）

```dockerfile
# ============= 构建阶段 =============
FROM python:3.11-slim AS builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装依赖到临时目录
RUN pip install --no-cache-dir --user -r requirements.txt

# ============= 运行阶段 =============
FROM python:3.11-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制依赖
COPY --from=builder /root/.local /root/.local

# 复制项目代码
COPY . .

# 安装项目
RUN pip install --no-cache-dir -e .

# 设置环境变量
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# 创建非 root 用户
RUN useradd -m -u 1000 ocruser && \
    chown -R ocruser:ocruser /app

USER ocruser

EXPOSE 8000

CMD ["python", "app.py"]
```

**优势**:
- 镜像体积更小（减少 30%+）
- 构建速度更快（利用缓存）
- 更安全（非 root 用户运行）

---

### 1.3 构建和运行

```bash
# 构建镜像
docker build -t paddleocr-app:latest .

# 运行容器
docker run -d \
  --name paddleocr \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  --memory=4g \
  --cpus=2 \
  paddleocr-app:latest

# 查看日志
docker logs -f paddleocr

# 进入容器
docker exec -it paddleocr bash
```

---

### 1.4 Docker Compose

**文件**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  paddleocr-api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: paddleocr-api
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./output:/app/output
      - ./logs:/app/logs
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=INFO
      - MAX_WORKERS=4
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Redis 缓存（可选）
  redis:
    image: redis:7-alpine
    container_name: paddleocr-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  redis-data:
```

**使用**:

```bash
# 启动所有服务
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f paddleocr-api

# 停止服务
docker-compose down

# 重启服务
docker-compose restart paddleocr-api
```

---

### 1.5 GPU 支持（可选）

**Dockerfile.gpu**:

```dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Python 安装
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir paddlepaddle-gpu -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .

CMD ["python3", "app.py"]
```

**docker-compose.gpu.yml**:

```yaml
version: '3.8'

services:
  paddleocr-gpu:
    build:
      context: .
      dockerfile: Dockerfile.gpu
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

**运行**:

```bash
docker-compose -f docker-compose.gpu.yml up -d
```

---

## 二、生产环境配置

### 2.1 API 服务示例（FastAPI）

**文件**: `app.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PaddleOCR API 服务
Production-Ready OCR API
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from examples._common import (
    OCRContextManager,
    OCRException,
    setup_logging,
    resize_image_for_ocr,
)

# 配置日志
setup_logging(level='INFO')
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="PaddleOCR API",
    description="生产级 OCR 识别服务",
    version="1.0.0",
)

# 全局 OCR 实例（启动时初始化）
ocr_instance = None


@app.on_event("startup")
async def startup_event():
    """启动时初始化 OCR 引擎"""
    global ocr_instance
    logger.info("初始化 OCR 引擎...")
    from paddleocr import PaddleOCR

    ocr_instance = PaddleOCR(
        lang='ch',
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )
    logger.info("✓ OCR 引擎初始化完成")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "paddleocr-api"}


@app.post("/ocr")
async def ocr_endpoint(
    file: UploadFile = File(...),
    max_size: int = 1200,
) -> JSONResponse:
    """
    OCR 识别接口

    Args:
        file: 上传的图片文件
        max_size: 最大边长（用于缩小大图片）

    Returns:
        JSONResponse: 识别结果
    """
    try:
        # 保存上传文件
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # 预处理大图片
        processed_path = resize_image_for_ocr(temp_path, max_size=max_size)

        # 识别
        result = ocr_instance.predict(processed_path)

        # 提取文本
        texts = []
        scores = []
        for res in result:
            data = res.json
            if 'rec_texts' in data:
                texts.extend(data['rec_texts'])
            if 'rec_scores' in data:
                scores.extend(data['rec_scores'])

        # 清理临时文件
        Path(temp_path).unlink(missing_ok=True)
        if processed_path != temp_path:
            Path(processed_path).unlink(missing_ok=True)

        return JSONResponse({
            "success": True,
            "data": {
                "texts": texts,
                "scores": scores,
                "count": len(texts),
            }
        })

    except OCRException as e:
        logger.error(f"OCR 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        logger.error(f"未知错误: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


if __name__ == "__main__":
    # 启动服务
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        workers=4,           # 工作进程数
        log_level="info",
        access_log=True,
    )
```

**使用**:

```bash
# 安装依赖
pip install fastapi uvicorn python-multipart

# 启动服务
python app.py

# 测试 API
curl -X POST "http://localhost:8000/ocr" \
  -F "file=@test.png"
```

---

### 2.2 环境变量配置

**文件**: `.env`

```bash
# 应用配置
APP_NAME=paddleocr-api
APP_ENV=production
APP_DEBUG=false

# OCR 配置
OCR_LANG=ch
OCR_MAX_SIZE=1200
OCR_USE_GPU=false
OCR_GPU_MEM=8000

# 服务配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_WORKERS=4

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log

# 资源限制
MAX_MEMORY_MB=4000
MAX_FILE_SIZE_MB=10
MAX_CONCURRENT_REQUESTS=10

# Redis 配置（如果使用缓存）
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_TTL=3600
```

**加载配置**:

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    """应用配置"""

    app_name: str = "paddleocr-api"
    app_env: str = "production"

    ocr_lang: str = "ch"
    ocr_max_size: int = 1200
    ocr_use_gpu: bool = False

    server_host: str = "0.0.0.0"
    server_port: int = 8000
    server_workers: int = 4

    log_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

### 2.3 Nginx 反向代理

**文件**: `nginx.conf`

```nginx
upstream paddleocr_api {
    # 负载均衡（如果有多个实例）
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name ocr.example.com;

    # 客户端最大上传大小
    client_max_body_size 10M;

    # 请求超时
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    location / {
        proxy_pass http://paddleocr_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 健康检查
    location /health {
        access_log off;
        proxy_pass http://paddleocr_api/health;
    }

    # 静态文件（如果有）
    location /static {
        alias /var/www/static;
        expires 7d;
    }

    # 日志
    access_log /var/log/nginx/paddleocr-access.log;
    error_log /var/log/nginx/paddleocr-error.log;
}
```

---

### 2.4 Systemd 服务

**文件**: `/etc/systemd/system/paddleocr.service`

```ini
[Unit]
Description=PaddleOCR API Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/paddleocr-api
Environment="PATH=/opt/paddleocr-api/venv/bin"
ExecStart=/opt/paddleocr-api/venv/bin/python app.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/paddleocr/app.log
StandardError=append:/var/log/paddleocr/error.log

# 资源限制
LimitNOFILE=65536
MemoryLimit=4G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

**使用**:

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start paddleocr

# 开机自启
sudo systemctl enable paddleocr

# 查看状态
sudo systemctl status paddleocr

# 查看日志
sudo journalctl -u paddleocr -f
```

---

## 三、云平台部署

### 3.1 阿里云 ECS

#### 环境准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com | bash
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 部署步骤

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/paddleocr-api.git
cd paddleocr-api

# 2. 配置环境变量
cp .env.example .env
vim .env

# 3. 构建镜像
docker-compose build

# 4. 启动服务
docker-compose up -d

# 5. 配置防火墙
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 6. 配置 Nginx（可选）
sudo apt install nginx
sudo cp nginx.conf /etc/nginx/sites-available/paddleocr
sudo ln -s /etc/nginx/sites-available/paddleocr /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

### 3.2 腾讯云 CVM

**使用腾讯云 COS 存储结果**:

```python
from qcloud_cos import CosConfig, CosS3Client
import logging

# 配置
secret_id = 'your-secret-id'
secret_key = 'your-secret-key'
region = 'ap-guangzhou'
bucket = 'paddleocr-results-1234567890'

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
client = CosS3Client(config)

# 上传结果
def upload_to_cos(local_file: str, cos_key: str) -> str:
    """上传文件到 COS"""
    response = client.upload_file(
        Bucket=bucket,
        LocalFilePath=local_file,
        Key=cos_key,
    )
    return f"https://{bucket}.cos.{region}.myqcloud.com/{cos_key}"

# 使用
url = upload_to_cos('result.json', 'results/2024/01/result.json')
print(f"结果已上传: {url}")
```

---

### 3.3 AWS EC2

**使用 S3 存储**:

```python
import boto3

s3 = boto3.client('s3')

def upload_to_s3(file_path: str, bucket: str, key: str) -> str:
    """上传文件到 S3"""
    s3.upload_file(file_path, bucket, key)
    return f"s3://{bucket}/{key}"

# 使用
url = upload_to_s3('result.json', 'paddleocr-results', '2024/01/result.json')
```

---

## 四、监控和运维

### 4.1 健康检查

```python
from fastapi import FastAPI
import psutil

app = FastAPI()

@app.get("/health")
async def health_check():
    """详细的健康检查"""
    # 检查内存
    mem = psutil.virtual_memory()
    mem_percent = mem.percent

    # 检查 CPU
    cpu_percent = psutil.cpu_percent(interval=1)

    # 检查磁盘
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent

    status = "healthy"
    if mem_percent > 90 or cpu_percent > 90 or disk_percent > 90:
        status = "unhealthy"

    return {
        "status": status,
        "memory_percent": mem_percent,
        "cpu_percent": cpu_percent,
        "disk_percent": disk_percent,
    }
```

---

### 4.2 日志管理

**使用 Python logging + Logrotate**:

```python
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
handler = RotatingFileHandler(
    'app.log',
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,               # 保留 5 个备份
)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

**Logrotate 配置** (`/etc/logrotate.d/paddleocr`):

```
/var/log/paddleocr/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload paddleocr
    endscript
}
```

---

### 4.3 性能监控

**使用 Prometheus + Grafana**:

```python
from prometheus_client import Counter, Histogram, generate_latest

# 定义指标
ocr_requests_total = Counter('ocr_requests_total', 'Total OCR requests')
ocr_duration_seconds = Histogram('ocr_duration_seconds', 'OCR processing duration')

@app.post("/ocr")
async def ocr_endpoint(file: UploadFile):
    ocr_requests_total.inc()  # 计数器 +1

    with ocr_duration_seconds.time():  # 记录处理时间
        # OCR 处理...
        result = process_image(file)

    return result

@app.get("/metrics")
async def metrics():
    """Prometheus 指标接口"""
    return Response(generate_latest(), media_type="text/plain")
```

---

### 4.4 告警配置

**使用钉钉/企业微信告警**:

```python
import requests

def send_alert(message: str, webhook_url: str):
    """发送告警消息"""
    data = {
        "msgtype": "text",
        "text": {
            "content": f"[PaddleOCR 告警] {message}"
        }
    }
    requests.post(webhook_url, json=data)

# 监控内存使用
mem_percent = psutil.virtual_memory().percent
if mem_percent > 90:
    send_alert(f"内存使用率过高: {mem_percent}%", webhook_url)
```

---

## 总结：部署检查清单

### ✅ Docker 部署

- [ ] Dockerfile 优化（多阶段构建）
- [ ] docker-compose.yml 配置
- [ ] 资源限制（CPU、内存）
- [ ] 健康检查配置
- [ ] 日志卷挂载

### ✅ 生产环境

- [ ] API 服务（FastAPI/Flask）
- [ ] 环境变量配置（.env）
- [ ] Nginx 反向代理
- [ ] Systemd 服务自启
- [ ] HTTPS 证书配置

### ✅ 云平台

- [ ] 云服务器配置
- [ ] 对象存储集成（COS/S3）
- [ ] 防火墙规则
- [ ] 域名解析
- [ ] 负载均衡（可选）

### ✅ 监控运维

- [ ] 健康检查接口
- [ ] 日志轮转配置
- [ ] 性能监控（Prometheus）
- [ ] 告警通知配置
- [ ] 备份策略

---

## 参考资源

- [Docker 官方文档](https://docs.docker.com/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Nginx 文档](https://nginx.org/en/docs/)
- [性能优化](performance.md)
- [最佳实践](best_practices.md)

---

**上次更新**: 2026-01-03
**版本**: v0.3.0
