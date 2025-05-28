import os
import time
import uuid
import random
import socket
import grpc
import logging
import argparse
from concurrent import futures

import product_pb2
import product_pb2_grpc

# Configure logging
logging.basicConfig(level=logging.INFO)

# Generate a unique server ID
SERVER_ID = str(uuid.uuid4())[:8]

# Get hostname
HOSTNAME = socket.gethostname()

# Sample product data
PRODUCTS = [
    {"product_id": "p1", "name": "Smartphone", "description": "Latest model", "price": 999.99},
    {"product_id": "p2", "name": "Laptop", "description": "High performance", "price": 1299.99},
    {"product_id": "p3", "name": "Headphones", "description": "Noise cancelling", "price": 299.99},
    {"product_id": "p4", "name": "Smartwatch", "description": "Fitness tracker", "price": 199.99},
    {"product_id": "p5", "name": "Tablet", "description": "10-inch screen", "price": 499.99},
]

class ProductServiceServicer(product_pb2_grpc.ProductServiceServicer):
    """Implementation of ProductService service."""

    def __init__(self):
        self.request_count = 0
        logging.info(f"Server starting with ID: {SERVER_ID} on host: {HOSTNAME}")

    def GetProduct(self, request, context):
        """Return product details."""
        self.request_count += 1
        
        # Log the request for monitoring
        logging.info(f"GetProduct request #{self.request_count} received on server {SERVER_ID}")
        
        # Simulate some processing time (variable to demonstrate load)
        time.sleep(random.uniform(0.01, 0.1))
        
        # Find the product
        product = next((p for p in PRODUCTS if p["product_id"] == request.product_id), None)
        
        if not product:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Product {request.product_id} not found")
            return product_pb2.ProductResponse()
        
        # Return the product with server ID to identify which instance responded
        return product_pb2.ProductResponse(
            product_id=product["product_id"],
            name=product["name"],
            description=product["description"],
            price=product["price"],
            server_id=f"{SERVER_ID} ({HOSTNAME})"
        )

    def ListProducts(self, request, context):
        """Return a list of products."""
        self.request_count += 1
        
        # Log the request for monitoring
        logging.info(f"ListProducts request #{self.request_count} received on server {SERVER_ID}")
        
        # Simulate some processing time (variable to demonstrate load)
        time.sleep(random.uniform(0.05, 0.2))
        
        # Paginate products
        page_size = request.page_size if request.page_size > 0 else len(PRODUCTS)
        page_number = request.page_number if request.page_number > 0 else 1
        
        start_idx = (page_number - 1) * page_size
        end_idx = start_idx + page_size
        
        page_products = PRODUCTS[start_idx:end_idx]
        
        # Convert to response objects
        product_responses = [
            product_pb2.ProductResponse(
                product_id=p["product_id"],
                name=p["name"],
                description=p["description"],
                price=p["price"],
                server_id=f"{SERVER_ID} ({HOSTNAME})"
            )
            for p in page_products
        ]
        
        return product_pb2.ListProductsResponse(
            products=product_responses,
            server_id=f"{SERVER_ID} ({HOSTNAME})"
        )

def serve(port=50051):
    """Start the gRPC server."""
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add the servicer to the server
    product_pb2_grpc.add_ProductServiceServicer_to_server(
        ProductServiceServicer(), server)
    
    # Listen on specified port
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    
    logging.info(f"Server started, listening on port {port}")
    logging.info(f"Server ID: {SERVER_ID}, Hostname: {HOSTNAME}")
    
    # Keep thread alive
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='gRPC Product Service Server')
    parser.add_argument('--port', type=int, default=50051, help='Port to listen on')
    args = parser.parse_args()
    
    # Start server with specified port
    serve(args.port)
