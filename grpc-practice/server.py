import grpc
from concurrent import futures
import greter_pb2
import greter_pb2_grpc

class GreeterServicer(greter_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        return greter_pb2.HelloReply(message=f"Hello, {request.name}!")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    greter_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)
    server.add_insecure_port('[::]:50051')  # gRPC runs on port 50051 by default
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
