import grpc
import greter_pb2
import greter_pb2_grpc

def run():
    channel = grpc.insecure_channel("localhost:50051")
    stub = greter_pb2_grpc.GreeterStub(channel)
    response = stub.SayHello(greter_pb2.HelloRequest(name="Sakshi"))
    print("Client received:", response.message)

if __name__ == "__main__":
    run()
