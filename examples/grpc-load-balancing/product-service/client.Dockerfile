FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY product.proto .

# Generate gRPC code
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. product.proto

COPY client.py .

ENTRYPOINT ["python", "client.py"]
