import ipywidgets as widgets
import zmq
import threading
import time
import ipythonchat_state

def get_chat_window(my_nickname,socket_address):
    def handle_input(sender):
        context = zmq.Context()
        push_socket = context.socket(zmq.PUSH)
        push_socket.connect(socket_address)

        push_socket.send_json({'nickname':my_nickname,'message':sender.value})
        sender.value = ''

    console_container = widgets.VBox(visible=False)
    console_container.padding = '10px'

    output_box = widgets.Textarea()
    output_box.height = '400px'
    output_box.font_family = 'monospace'
    output_box.color = '#AAAAAA'
    output_box.background_color = 'black'
    output_box.width = '800px'

    input_box = widgets.Text()
    input_box.font_family = 'monospace'
    input_box.color = '#AAAAAA'
    input_box.background_color = 'black'
    input_box.width = '800px'

    console_container.children = [output_box, input_box]
    console_container.visible = True

    input_box.on_submit(handle_input)
    return output_box,console_container


def chat_room(kernel,output_box,socket_address):
    context = zmq.Context()
    subscribe_socket = context.socket(zmq.SUB)
    subscribe_socket.connect(socket_address)
    subscribe_socket.setsockopt(zmq.SUBSCRIBE, '')
    print '>>> welcome to the zmq chatroom'
    while True:
        # print 'loop'
        zr,zw,zx = zmq.select([subscribe_socket],[],[],timeout = 0.0)
        if subscribe_socket in zr:
            # print 'ok got message'
            message = subscribe_socket.recv_json()
            output_box.value += '{}: {}\n'.format(message['nickname'],message['message'])
            # print 'aqcuiring lock on shared state'
            ipythonchat_state.shared_state_lock.acquire()
            #ok now we no, nobody else is manipulating the shared_state object
            ipythonchat_state.shared_state = {'last message':message['message']}
            ipythonchat_state.shared_state_lock.release()
            # print 'released lock, shared state is: ', ipythonchat_state.shared_state
            kernel.do_one_iteration()
        time.sleep(0.01)

def copy_state():
    ipythonchat_state.shared_state_lock.acquire()
    #ok now we no, nobody else is manipulating the shared_state object
    copied = dict(**ipythonchat_state.shared_state) if ipythonchat_state.shared_state else None
    ipythonchat_state.shared_state_lock.release()
    return copied
    
def start_chat(kernel,output_box,socket_addess):
    p = threading.Thread(target = chat_room, args = (kernel,output_box,socket_addess))
    p.start()

def bootstrap(nickname, write_to, read_from):
    output_box,console_container = get_chat_window(nickname,write_to)
    start_chat(get_ipython().kernel,output_box,read_from)
    return console_container