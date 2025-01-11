# SecureUDP

SecureUDP is a Python project that implements reliable data transmission over UDP using Forward Error Correction (FEC). It ensures data integrity and reliability by generating FEC packets and reconstructing lost packets.

## Configuration

The configuration parameters are defined at the beginning of the `secureUDP.py` file:

- `SERVER_IP`: IP address of the server.
- `SERVER_PORT`: Port number of the server.
- `CLIENT_PORT`: Port number of the client.
- `PACKET_SIZE`: Size of each packet in bytes.
- `TIMEOUT`: Timeout duration for waiting for acknowledgments.
- `WINDOW_SIZE`: Size of the sliding window for packet transmission.
- `FEC_GROUP_SIZE`: Number of packets in a group for applying FEC.

## Functions

### `generate_fec_packet(packets)`

Generates an FEC packet by performing XOR on all packets in the group.

### `reconstruct_packet(fec_packet, packets)`

Reconstructs a lost packet using the FEC packet and the received packets.

### `reliable_send_with_fec(data, dest_ip, dest_port)`

Sends data reliably using FEC. It splits the data into packets, generates FEC packets, and sends them to the destination. It also handles acknowledgments and retransmissions.

### `reliable_receive_with_fec(listen_ip, listen_port)`

Receives data reliably using FEC. It listens for incoming packets, handles FEC packets, and reconstructs lost packets. It also sends acknowledgments for received packets.

## Usage

To test the SecureUDP implementation, run the `main` function. It starts the server and client in separate threads and sends a sample message from the client to the server.

```python
if __name__ == "__main__":
    main()
```

## Example

1. Configure the parameters in `secureUDP.py` as needed.
2. Run the script:

```sh
python secureUDP.py
```

3. The server will start and wait for incoming data. The client will send a sample message to the server.
4. The server will receive the data, including any reconstructed packets, and print the received message.

## License

This project is licensed under the GNU General Public License (GPL).
