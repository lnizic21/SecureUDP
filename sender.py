import socket
import time
import random

# Konfiguracija
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
PACKET_SIZE = 1024
TIMEOUT = 2
WINDOW_SIZE = 4
FEC_GROUP_SIZE = 4  # Broj paketa na koje primjenjujemo FEC

# Funkcija za generiranje FEC paketa (XOR svih paketa u grupi)
def generate_fec_packet(packets):
    # Filtriraj None pakete (ako su neki paketi izgubljeni)
    valid_packets = [packet for packet in packets if packet is not None]
    
    # Ako nema valjanih paketa, ne možemo generirati FEC
    if not valid_packets:
        return None
    
    # Inicijaliziraj FEC paket s prvim validnim paketom
    fec_packet = valid_packets[0]
    for packet in valid_packets[1:]:
        fec_packet = bytes(a ^ b for a, b in zip(fec_packet, packet))
    return fec_packet

# Simulacija gubitka paketa i oštećenja
def simulate_packet_loss_and_corruption(packets, loss_probability=0.1, corruption_probability=0.1):
    for i in range(len(packets)):
        if random.random() < loss_probability:
            print(f"Simuliran gubitak paketa {i}")
            packets[i] = None  # Paket se "gubi"
        elif random.random() < corruption_probability:
            print(f"Simulirano oštećenje paketa {i}")
            packets[i] = bytes([random.randint(0, 255) for _ in range(PACKET_SIZE)])  # Paket se "oštećuje"
    return packets

# Pouzdano slanje s FEC-om
def reliable_send_with_fec(data, dest_ip, dest_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)
    
    packets = [data[i:i + PACKET_SIZE] for i in range(0, len(data), PACKET_SIZE)]
    packets += [b"" * PACKET_SIZE] * ((FEC_GROUP_SIZE - len(packets) % FEC_GROUP_SIZE) % FEC_GROUP_SIZE)
    acks = [False] * len(packets)
    base = 0
    
    while base < len(packets):
        # Slanje paketa i FEC-a unutar prozora
        for i in range(base, min(base + WINDOW_SIZE, len(packets)), FEC_GROUP_SIZE):
            group = packets[i:i + FEC_GROUP_SIZE]
            group = simulate_packet_loss_and_corruption(group)  # Simulacija gubitka i oštećenja paketa
            fec_packet = generate_fec_packet(group)
            if fec_packet is not None:
                sock.sendto(f"FEC|{i}|".encode() + fec_packet, (dest_ip, dest_port))
                print(f"Poslan FEC za grupu {i}-{i + FEC_GROUP_SIZE - 1}")
            
            for j, packet in enumerate(group):
                if packet is not None and not acks[i + j]:
                    numbered_packet = f"{i + j}|".encode() + packet
                    sock.sendto(numbered_packet, (dest_ip, dest_port))
                    print(f"Poslan paket {i + j}")

        # Čekanje potvrda
        start_time = time.time()
        while time.time() - start_time < TIMEOUT:
            try:
                ack_data, _ = sock.recvfrom(1024)
                ack_num = int(ack_data.decode())
                print(f"Primljen ACK za paket {ack_num}")
                acks[ack_num] = True
                
                # Pomiče bazu ako su svi prethodni paketi potvrđeni
                while base < len(acks) and acks[base]:
                    base += 1
            except socket.timeout:
                print("Timeout pri čekanju na ACK.")
                break

    # Slanje signala za završetak
    sock.sendto(b"0|END", (dest_ip, dest_port))
    print("Poslan signal za završetak (END).")
    sock.close()

def main():
    print("Pokreće se klijent...")
    
    # Učitaj datoteku koju želiš poslati
    with open("file_to_send.jpg", "rb") as f:
        data = f.read()
    
    reliable_send_with_fec(data, SERVER_IP, SERVER_PORT)

if __name__ == "__main__":
    main()
