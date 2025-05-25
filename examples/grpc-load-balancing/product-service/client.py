import os
import time
import grpc
import logging
import argparse
from collections import Counter

import product_pb2
import product_pb2_grpc

# Configure logging
logging.basicConfig(level=logging.INFO)

def run_client(target, num_requests=100, interval=0.1):
    """Run the gRPC client."""
    # Create a gRPC channel
    channel = grpc.insecure_channel(target)
    
    # Create a stub (client)
    stub = product_pb2_grpc.ProductServiceStub(channel)
    
    # Track which servers respond
    server_responses = Counter()
    
    logging.info(f"Client starting, connecting to {target}")
    logging.info(f"Will send {num_requests} requests with {interval}s interval")
    
    # Send requests
    for i in range(num_requests):
        try:
            # Alternate between GetProduct and ListProducts
            if i % 2 == 0:
                # Get a specific product
                product_id = f"p{(i % 5) + 1}"  # Cycle through p1 to p5
                response = stub.GetProduct(product_pb2.ProductRequest(product_id=product_id))
                logging.info(f"Request {i+1}: GetProduct({product_id}) -> Server: {response.server_id}")
                server_responses[response.server_id] += 1
            else:
                # List products
                response = stub.ListProducts(product_pb2.ListProductsRequest(page_size=2, page_number=1))
                logging.info(f"Request {i+1}: ListProducts() -> Server: {response.server_id}")
                server_responses[response.server_id] += 1
            
            # Wait between requests
            time.sleep(interval)
            
        except grpc.RpcError as e:
            logging.error(f"RPC error: {e.code()}: {e.details()}")
    
    # Print summary
    logging.info("\n--- Request Distribution Summary ---")
    total = sum(server_responses.values())
    for server, count in server_responses.items():
        percentage = (count / total) * 100
        logging.info(f"Server {server}: {count} requests ({percentage:.1f}%)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='gRPC Product Service Client')
    parser.add_argument('--target', default='localhost:50051', help='Target server address')
    parser.add_argument('--requests', type=int, default=100, help='Number of requests to send')
    parser.add_argument('--interval', type=float, default=0.1, help='Interval between requests in seconds')
    
    args = parser.parse_args()
    run_client(args.target, args.requests, args.interval)
