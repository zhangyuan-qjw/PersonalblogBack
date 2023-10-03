# 使用官方 Python 镜像
FROM python:3.10.7

# 设置工作目录
WORKDIR /app

## 复制项目文件到容器中
#COPY . /app

# 安装项目依赖项
RUN pip install -r requirements.txt

# 执行 Django 数据库迁移
RUN python manage.py migrate

# 启动 Django 项目
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]