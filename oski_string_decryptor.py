import idautils
import idc
from qiling import *
from qiling import Qiling
from qiling.const import QL_ARCH, QL_VERBOSE
from qiling.exception import *
from qiling.os.const import *
from qiling.os.windows import structs
from qiling.os.windows.api import *
from qiling.os.windows.const import *
from qiling.os.windows.fncc import *
from qiling.os.windows.handle import *
from qiling.os.windows.thread import *
from qiling.os.windows.utils import *

global xrefs_addr

def watcher(ql, addr, size):
    if addr in xrefs_addr:
        idc.set_cmt(addr, ql.mem.string(ql.reg.eax), 0)
        print(f"Comment set on address: {hex(addr)}")
        
def getXrefsAddr(addr):
    """Gets all xrefs of a function
    Args:
        addr (ea): address of the function to get xrefs
    Returns:
        list: xrefs addresses
    """
    return [xref.frm + 0x8 for xref in idautils.XrefsTo(addr)]

def getCurrentAddress():
    """Get the cursor address of a call to the decryption routine, if the cursor is not on this function, it prints an error and exits 
    Returns:
        ea: current screen address
    """
    ca = idc.get_screen_ea()

    if idc.print_insn_mnem(ca) == "call":
        return idc.get_operand_value(ca, 0)

    print("Please place your cursor on the decryption function call !")
    return 0

ql = Qiling(["dotu.exe"], "x86_windows", verbose=QL_VERBOSE.OFF)
xrefs_addr = getXrefsAddr(getCurrentAddress())

ql.hook_code(watcher)

ql.run()