import zmq
import time

# the room pulls messages from the clients

def main():
    context = zmq.Context()
    pull_socket = context.socket(zmq.PULL)
    pull_socket.bind("ipc://room.sock")

    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind("ipc://room_pub.sock")
    
    room_messages = []
    
    while True:
        zr,zw,zx = zmq.select([pull_socket], [pub_socket],[], timeout = 0.0)
        if pull_socket in zr:
            message = pull_socket.recv_json()
            print "got message: {}".format(message)
            room_messages.append(message)
        
        if pub_socket in zw and room_messages:
            print 'publishing message'
            pub_socket.send_json(room_messages.pop(0))

        print 'sleeping .. Zzzzz'
        time.sleep(0.01)

if __name__ == '__main__':
    main()