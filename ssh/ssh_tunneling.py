from time import sleep
from sshtunnel import SSHTunnelForwarder

PKEY_FILE = '/home/owenchew/.ssh/id_rsa'
FIRST_JUMP_SSH_ADDRESS = "sunfire.comp.nus.edu.sg"
FIRST_JUMP_USERNAME = "e0406642"

SECOND_JUMP_ADDRESS ="137.132.86.227"
SECOND_JUMP_USERNAME = "xilinx"
SECOND_JUMP_PASSWORD = "xnilix_toor"

TARGET_ADDRESS = "137.132.86.227"
TARGET_PORT = 15001

"""Creates the tunnel to the target IP and port, using several bastions."""
class TunnelNetwork(object):
    def __init__(self, tunnel_info, target_ip, target_port):
        self.tunnel_info = tunnel_info
        self.target_ip = target_ip
        self.target_port = target_port


    def start_tunnels(self):
        self.tunnels = []
        for idx, info in enumerate(self.tunnel_info):
            # if we're not the first element, set the bastion to the local port of the previous tunnel
            if idx > 0:
                info['ssh_address_or_host'] = ('127.0.0.1', self.tunnels[-1].local_bind_port)
            # if we are the last element, the target is the real target
            if idx == len(self.tunnel_info) - 1:
                target = (self.target_ip, self.target_port)
            # else, the target is the next bastion
            else:
                if isinstance(self.tunnel_info[idx+1]['ssh_address_or_host'], tuple):
                    target = self.tunnel_info[idx+1]['ssh_address_or_host']
                else:
                    target = (self.tunnel_info[idx+1]['ssh_address_or_host'], 22)
            
            self.tunnels.append(SSHTunnelForwarder(remote_bind_address=target, **info))
            
            try:
                print("connecting")

                self.tunnels[idx].start()
                print("connected")
                print(self.tunnels[0].local_bind_port)
            except Exception as e:
                print(e)
                return False

        return True

    def stop_tunnels(self):
        for tunnel in reversed(self.tunnels):
            tunnel.stop()    


    def are_tunnels_active(self):
        return self.tunnels and all([t.is_active for t in self.tunnels])

    """Gets the local port at which the tunnel to the target is connected to"""
    def get_local_connect_port(self):
        if self.tunnels:
            return self.tunnels[-1].local_bind_port
        else:
            return None


"""If class is used on its own"""
if __name__ == '__main__':
        
    tunnel_i = [
        {"ssh_address_or_host": FIRST_JUMP_SSH_ADDRESS,
        "ssh_username": FIRST_JUMP_USERNAME,
        "ssh_pkey": PKEY_FILE,

        },
        {"ssh_address_or_host": SECOND_JUMP_ADDRESS,
        "ssh_username": SECOND_JUMP_USERNAME,
        "ssh_password": SECOND_JUMP_PASSWORD,
        }
    ]

    tn = TunnelNetwork(tunnel_i, TARGET_ADDRESS, TARGET_PORT)
    
    tn.start_tunnels()
    print("niggs")
    print(tn.get_local_connect_port())
    
    print("hi")
    while True:
        sleep(2)

