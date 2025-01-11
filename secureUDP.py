import socket
import threading
import time
import itertools

# Konfiguracija
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
CLIENT_PORT = 12346
PACKET_SIZE = 1024
TIMEOUT = 2
WINDOW_SIZE = 4
FEC_GROUP_SIZE = 4  # Broj paketa na koje primjenjujemo FEC

# Funkcija za generiranje FEC paketa (XOR svih paketa u grupi)
def generate_fec_packet(packets):
    fec_packet = packets[0]
    for packet in packets[1:]:
        fec_packet = bytes(a ^ b for a, b in zip(fec_packet, packet))
    return fec_packet

# Funkcija za rekonstrukciju izgubljenog paketa pomoću FEC-a
def reconstruct_packet(fec_packet, packets):
    missing_packet = fec_packet
    for packet in packets:
        missing_packet = bytes(a ^ b for a, b in zip(missing_packet, packet))
    return missing_packet

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
            fec_packet = generate_fec_packet(group)
            for j, packet in enumerate(group):
                if not acks[i + j]:
                    numbered_packet = f"{i + j}|".encode() + packet
                    sock.sendto(numbered_packet, (dest_ip, dest_port))
                    print(f"Poslan paket {i + j}")
            sock.sendto(f"FEC|{i}|".encode() + fec_packet, (dest_ip, dest_port))
            print(f"Poslan FEC za grupu {i}-{i + FEC_GROUP_SIZE - 1}")

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
                break
    
    sock.close()

# Pouzdano primanje s FEC-om
def reliable_receive_with_fec(listen_ip, listen_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((listen_ip, listen_port))
    
    received_data = {}
    expected_seq = 0
    fec_buffer = {}

    while True:
        data, addr = sock.recvfrom(2048)
        if data.startswith(b"FEC|"):
            _, base_seq, fec_packet = data.split(b"|", 2)
            base_seq = int(base_seq)
            fec_buffer[base_seq] = fec_packet
            print(f"Primljen FEC za grupu {base_seq}-{base_seq + FEC_GROUP_SIZE - 1}")
            continue
        
        seq_num, packet_data = data.split(b"|", 1)
        seq_num = int(seq_num)
        
        # Provjera redoslijeda i slanje ACK-a
        if seq_num == expected_seq:
            print(f"Primljen paket {seq_num}, očekivano {expected_seq}")
            received_data[seq_num] = packet_data
            expected_seq += 1
            sock.sendto(str(seq_num).encode(), addr)
        elif seq_num > expected_seq:
            print(f"Primljen paket {seq_num}, ne očekivan!")
            received_data[seq_num] = packet_data
            sock.sendto(str(seq_num).encode(), addr)

        # Provjera FEC-a za rekonstrukciju
        group_base = (seq_num // FEC_GROUP_SIZE) * FEC_GROUP_SIZE
        if group_base in fec_buffer:
            group = [received_data.get(i, None) for i in range(group_base, group_base + FEC_GROUP_SIZE)]
            if group.count(None) == 1:  # Ako je samo jedan paket izgubljen
                missing_index = group.index(None)
                reconstructed = reconstruct_packet(fec_buffer[group_base], [p for p in group if p])
                received_data[group_base + missing_index] = reconstructed
                print(f"Rekonstruiran paket {group_base + missing_index} pomoću FEC-a")
        
        # Prekid ako nema više podataka
        if packet_data == b"END":
            break
    
    sock.close()
    # Spajanje primljenih podataka
    return b"".join([received_data[i] for i in sorted(received_data)])

# Glavna funkcija za testiranje
def main():
    # Pokretanje servera i klijenta u odvojenim nitima
    def server():
        print("Pokreće se server...")
        received = reliable_receive_with_fec(SERVER_IP, SERVER_PORT)
        print("Primljeni podaci:", received.decode())
    
    def client():
        time.sleep(1)  # Daje serveru vremena za pokretanje
        print("Pokreće se klijent...")
        data = b"Ovo su podaci koji se šalju preko UDP-a. END"
        reliable_send_with_fec(data, SERVER_IP, SERVER_PORT)
    
    threading.Thread(target=server, daemon=True).start()
    threading.Thread(target=client, daemon=True).start()

    time.sleep(10)  # Čekanje završetka

if __name__ == "__main__":
    main()
