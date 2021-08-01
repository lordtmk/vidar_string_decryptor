from idautils import XrefsTo
import idautils
import idc
import idaapi
import ida_bytes


def decrypt(str, key):
    """Aims to decrypt VIDAR's XOR encryption

    Args:
        str (list): list containing string to decrypt in hex form
        key (list): list containing key to decrypt in hex form

    Returns:
        str: returns decrypted value in a readable way
    """
    buf = []
    i = 0
    result = ""
    while i <= (len(str) - 1):
        str[i] = convert_to_ord(str[i])
        key[i] = convert_to_ord(key[i])
        decrypted_char = (str[i] ^ key[i])
        buf.append(chr(decrypted_char))
        i += 1 
    result = result.join(buf) 
    return result

def get_current_address():
    """Get the cursor address of a call to the decryption routine, if the cursor is not on this function, it prints an error and exits 

    Returns:
        ea: current screen address
    """
    ca = idc.get_screen_ea()
    
    if idc.print_insn_mnem(ca) == "call":
       addr = idc.get_operand_value(ca, 0)
    else:
        print("Please place your cursor on the decryption function call !")
        exit(0)
    
    return addr
    
    
def get_xrefs_addr(addr):
    """Gets all xrefs of a function

    Args:
        addr (ea): address of the function to get xrefs

    Returns:
        list: xrefs addresses
    """
    xrefs = []
    for xref in idautils.XrefsTo(addr):
        xrefs.append(xref.frm)
    return xrefs
    
def get_key(addr,size):
    """Gather the XOR key value

    Args:
        addr (ea): address of value
        size (ea): size of bytes to capture

    Returns:
        list: key in list of hex bytes
    """
    key = idaapi.get_bytes(addr, size)
    key = slice_val(key.hex())
    return key
    
def get_value(addr,icsize):
    """Gather the encrypted data 

    Args:
        addr (ea): address of value
        icsize (int): size arg of function, in case of all values are "unk" in ida

    Returns:
        list: value in list of hex bytes 
        int: size of bytes to capture
        int: return size of data if value was "unk"
    """
    size = get_size(addr) - 1
    if size > 0:
        value = idaapi.get_bytes(addr, size)
        value = slice_val(value.hex())
        return value, size;
    else:
        value = idaapi.get_bytes(addr, icsize)
        value = slice_val(value.hex())
        return value, icsize;
    
def get_size(addr):
    """Get the bytes size of an value  

    Args:
        addr (ea): adress of value 
    """
    size = ida_bytes.get_item_size(addr)
    return(size)

def scan_args(func_addr):
    """Get all args of a function

    Args:
        func_addr (ea): address of call to decryption routine

    Returns:
        ea: address of encrypted string arg
        ea: address of key arg
        int: size arg
    """
    args = []
    i = 0
    
    while i < 3:
        func_addr = idc.prev_head(func_addr)
        mnem = idc.print_insn_mnem(func_addr)        
        if mnem == "push" and i < 3:
            args.append(idc.get_operand_value(func_addr, 0))
            i += 1
    icsize = args[2] #! In case of unk for value data, try to take size arg (which can be a register)
    encrypted = args[1]
    key = args[0]
    return encrypted, key, icsize;

def convert_to_ord(value):
    """Convert an hex value to decimal 

    Args:
        value (hex): hex byte to convert

    Returns:
        int: decimal byte
    """
    value = str('0x') + str(value) # Converted to hex string
    value = int(value, 16) # Convert to ord
    return value
    
def slice_val(str):
    """Slice value into hex bytes of 2

    Args:
        str (hex): hex string

    Returns:
        list : list of 2 digit hex values
    """
    sliced = []
    while str:
        sliced.append(str[:2])
        str = str[2:]
    return sliced

def comment_result(addr, comm):
    """Comment addresses where the dwords are referenced

    Args:
        addr (ea): address of call function
        comm (str): decrypted value to comment
    """
    addr = idc.next_head(addr)
    while idc.print_insn_mnem(addr) != "call":
        if idc.print_insn_mnem(addr) == "mov" and idc.get_operand_value(addr,0) > 10:
            dword_address = idc.get_operand_value(addr,0)
            xrefs = get_xrefs_addr(dword_address)
            for xref in xrefs:
                idc.set_cmt(xref, comm, 0)
        addr = idc.next_head(addr)
    
def main():
    """Main function of program
        1. Get address of decryption function
        2. Check xrefs
        3. Gather all args of each function
        4. Gather key and encrypted string values
        5. Decrypt values
        6. Comment decrypted string on each reference
        7. Write strings in a txt file for other purposes  
    """
    num_str = 0
    ca = get_current_address()
    xrefs = get_xrefs_addr(ca)
    str_list = []
    breakpoint()
    
    for addr in xrefs:
        val_addr, key_addr, icsize = scan_args(addr)
        val, size = get_value(val_addr,icsize)
        key = get_key(key_addr,size)
        result = decrypt(val,key)
        if result:
            comment_result(addr, result)
            str_list.append(result)
            num_str += 1
        

    print("Work done !")
    print(str(num_str) + " strings were decrypted")
    write_to_log_file(str_list)

        
def test_single_function(addr):
    """If you figure out that an xref if causing an error, you can test the script with this address only
    
    #! FOR DEBUG ONLY
    
    Args:
        addr (ea): address of call
    """
    
    val_addr, key_addr, icsize = scan_args(addr)
    val, size = get_value(val_addr, icsize)
    key = get_key(key_addr,size)
    result = decrypt(val,key)
    comment_result(addr, result)
    print(result)

def write_to_log_file(vals):
    """Write all decrypted strings in a file

    Args:
        vals (list): list of decrypted values
    """
    file = open("VSD_log.txt", 'w') #* Change the w value to a if u want to decrypt multiple samples in the same file
    for val in vals:
        file.write(val + "\n")
    file.close()
    
    print("Done writing to " + file.name)
    
    
main()