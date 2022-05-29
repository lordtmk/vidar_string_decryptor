from arc4 import ARC4
import argparse
import re

def get_rc4_key():
    with open(dll, 'rb') as f:
        f.seek(4494)
        data = f.read(4)
        data = (['{:02X}'.format(b) for b in data][::-1])
        f.seek(4502)
        add_value = f.read(1)
        add_value = ((['{:02X}'.format(b) for b in add_value]))
        key = (hex(int(''.join(data),16) + int(add_value[0],16))[2:])
        #Reverse the key
        key = [key[i:i+2] for i in range(0, len(key), 2)]
        key.reverse()
        
    return ' '.join(key)


def get_data_chunk():
    with open(dll, 'rb') as f:
        f.seek(95808)
        data = bytes.fromhex(str(f.read(622742), 'ascii'))
    
    return data


def decrypt(key, data):
    key = bytes.fromhex(key)
    arc4 = ARC4(key)
    dec =  bytearray(arc4.decrypt(data))
    
    for x in range(len(dec) - 1):
        dec[x] = ((dec[x] ^ key[x % len(key)]) - dec[x + 1]) & 0xff
        
    return dec


def extract_data_chunk(e_dll):
    
    with open(e_dll, 'rb') as f:
        f.seek(12800)
        data = f.read(128)
        data = (['{:02X}'.format(b) for b in data][::-1])
        #Reverse bytes
        data.reverse()

        encoded_url = data[(len(data)//2):]
        xor_bytes = data[:(len(data)//2)]

        clear_url = [chr(int(j, 16) ^ int(xor_bytes[i], 16)) for i, j in enumerate(encoded_url)]

        return "".join(clear_url)

    
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dll", help="Path to IcedID dll", required=True, dest="dll")
args = parser.parse_args()
dll = args.dll


def main():
    dec = (decrypt(get_rc4_key(), get_data_chunk())).split(b'|SPL|')[2]

    with open(f"{dll}_unpacked.dll", 'wb') as fp:
        fp.write(dec)
        print("Done unpacking IcedID!")
        print("Try to extract C2...")
        
        match = re.search("((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*", extract_data_chunk(f"{dll}_unpacked.dll"))
        print(f"Decoded URL: {match[0]}")
        
if __name__ == '__main__':
    main()