FROM python:3.10-slim
COPY chatbot.py .
COPY requirements.txt .
COPY config.ini .
ENV ACCESS_TOKEN = 5881114142:AAG2uG1SsE81QUj7GRGKI9I20-eUAZRNbT4
ENV HOST = comp7940group15.redis.cache.windows.net
ENV PASSWORD = Qsl1JnRd5qKJgQdb7I2X57QwONOhKnkRkAzCaJ7yd9Q=
ENV REDISPORT = 6380
RUN pip install -r requirements.txt
CMD python chatbot.py