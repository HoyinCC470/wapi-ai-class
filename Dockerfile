FROM python:3.9
WORKDIR /app
COPY . .
# 这一行加了清华源，下载速度快10倍，且不容易断
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
