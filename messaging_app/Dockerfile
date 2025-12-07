FROM python:3.10

WORKDIR /usr/src/app

COPY requirements.txt ./

# This line is bulletproof – fast mirror + long timeout + retries
RUN pip install --no-cache-dir \
    --timeout=1000 \
    --retries=20 \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn \
    -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]