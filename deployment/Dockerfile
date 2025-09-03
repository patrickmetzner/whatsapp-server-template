FROM python:3.8-slim

ENV PIP_ROOT_USER_ACTION=ignore

ENV TASK_ROOT=/var/task

RUN pip install --upgrade pip==24.2

COPY . /whatsapp-server-template

RUN  pip3 install -r /whatsapp-server-template/deployment/requirements.txt --upgrade

WORKDIR /whatsapp-server-template

ENV PYTHONPATH=/whatsapp-server-template

EXPOSE 5000

ENTRYPOINT ["python", "-m", "uvicorn"]
CMD ["app.main:app", "--host", "0.0.0.0", "--port", "5000"]
