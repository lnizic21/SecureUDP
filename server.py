### Server (salje.py)
import socket

# Konfiguracija
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
PACKET_SIZE = 1024
FEC_GROUP_SIZE = 4  # Broj paketa na koje primjenjujemo FEC

# Funkcija za rekonstrukciju izgubljenog paketa pomoću FEC-a
def reconstruct_packet(fec_packet, packets):
    missing_packet = fec_packet
    for packet in packets:
        missing_packet = bytes(a ^ b for a, b in zip(missing_packet, packet))
    return missing_packet

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
            print("Primljen signal za završetak. Gasi se server.")
            break
    
    sock.close()
    # Spajanje primljenih podataka
    return b"".join([received_data[i] for i in sorted(received_data)])

def main():
    print("Pokreće se server...")
    received = reliable_receive_with_fec(SERVER_IP, SERVER_PORT)
    print("Primljeni podaci:", received.decode())

if __name__ == "__main__":
    main()