# 后端启动脚本
cd /app/backend
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
uvicorn main:app --host 0.0.0.0 --port 8000
