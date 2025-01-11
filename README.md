### **Opis koda**

#### **1. Server (`server.py`)**
Ovaj dio programa predstavlja UDP server koji prima podatke od klijenta uz implementaciju mehanizama za pouzdano primanje koristeći Forward Error Correction (FEC). 

- **Glavne komponente:**
  - `reliable_receive_with_fec`: Funkcija za primanje podataka.
    - **FEC podrška:** Ako se paket izgubi, FEC omogućuje rekonstrukciju izgubljenog paketa.
    - **ACK:** Server šalje potvrdu (ACK) za ispravno primljene pakete.
    - **END signal:** Kada primi paket s oznakom "END", server završava rad.
  - `reconstruct_packet`: Pomoćna funkcija za rekonstrukciju izgubljenog paketa koristeći XOR svih paketa u grupi.
  - **Radni tok**:
    - Prima pakete i provjerava redoslijed.
    - Provjerava je li potrebno rekonstruirati paket pomoću FEC-a.
    - Po završetku vraća sve primljene podatke spojene u cjelinu.

---

#### **2. Klijent (`sender.py`)**
Ovaj dio programa šalje podatke serveru koristeći UDP protokol s implementacijom pouzdanog prijenosa koristeći prozore i FEC.

- **Glavne komponente:**
  - `reliable_send_with_fec`: Funkcija za slanje podataka.
    - **FEC generacija:** Generira FEC paket za svaku grupu paketa kako bi omogućila rekonstrukciju izgubljenih paketa na strani servera.
    - **Prozor za slanje:** Koristi veličinu prozora (WINDOW_SIZE) kako bi ograničio broj paketa koji se šalju istovremeno.
    - **Timeout:** Čeka potvrde (ACK) i ponovo šalje pakete koji nisu potvrđeni.
    - **END signal:** Na kraju šalje poseban paket "END" kako bi obavijestio server o završetku.
  - `generate_fec_packet`: Funkcija za generiranje FEC paketa koristeći XOR svih paketa u grupi.
  - **Radni tok**:
    - Dijeli podatke na manje pakete (ako je potrebno) i šalje ih serveru.
    - Provjerava odgovore servera i ponovno šalje nepotvrđene pakete.
    - Na kraju šalje signal za završetak.

---

### **Kako funkcioniraju FEC i ACK mehanizmi**
1. **FEC (Forward Error Correction)**:
   - Grupira određeni broj paketa (FEC_GROUP_SIZE).
   - Generira FEC paket kao XOR svih paketa u grupi.
   - Ako jedan paket u grupi nedostaje, server koristi FEC paket za rekonstrukciju.

2. **ACK (Acknowledgment)**:
   - Server šalje ACK za svaki uspješno primljeni paket.
   - Klijent ponovno šalje pakete za koje nije primio ACK.

3. **END signal**:
   - Klijent šalje poseban paket `END`, koji server prepoznaje kao signal za završetak.

---

### **Kako koristiti kod**
1. Pokrenite server:
   ```bash
   python server.py
   ```
2. Pokrenite klijent:
   ```bash
   python sender.py
   ```
3. Server će prikazivati dolazne pakete, rekonstruirati izgubljene pakete ako je moguće, i završiti rad nakon što primi `END`.


## License

This project is licensed under the GNU General Public License (GPL).
