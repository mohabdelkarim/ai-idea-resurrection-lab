import socket
import struct
import argparse

def send_redis_command(host, port, command):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.sendall(command.encode("utf-8"))
    response = b"".join(iter(lambda: sock.recv(4096), b""))
    sock.close()
    return response

def xtrim_option(host, port, stream_name, group_names):
    # XINFO STREAM to get the last id
    command = f"XINFO STREAM {stream_name}".encode("utf-8")
    response = send_redis_command(host, port, command)
    last_id = response.decode("utf-8").split(" ")[-1].strip()

    # Get the acknowledged ids for each group
    acknowledged_ids = {}
    for group_name in group_names:
        command = f"XINFO GROUP {stream_name} {group_name}".encode("utf-8")
        response = send_redis_command(host, port, command)
        lines = response.decode("utf-8").split("\n")
        for line in lines:
            if "Pending" in line:
                pending_ids = line.split(" ")[-1].strip().split("-")
                acknowledged_ids[group_name] = pending_ids[0]
                break

    # Find the minimum acknowledged id across all groups
    min_ack_id = last_id
    for group_name, ack_id in acknowledged_ids.items():
        if ack_id < min_ack_id:
            min_ack_id = ack_id

    # XTRIM to delete messages before the minimum acknowledged id
    command = f"XTRIM {stream_name} MAXID {min_ack_id}".encode("utf-8")
    response = send_redis_command(host, port, command)
    return response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="XTRIM option")
    parser.add_argument("--host", default="localhost", help="Redis host")
    parser.add_argument("--port", type=int, default=6379, help="Redis port")
    parser.add_argument("--stream_name", required=True, help="Stream name")
    parser.add_argument("--group_names", nargs="+", required=True, help="Consumer group names")
    args = parser.parse_args()

    try:
        response = xtrim_option(args.host, args.port, args.stream_name, args.group_names)
        print(response.decode("utf-8"))
    except Exception as e:
        print(f"Error: {e}")