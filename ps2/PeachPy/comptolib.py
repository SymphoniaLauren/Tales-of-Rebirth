import ctypes, os, struct

# Error codes
SUCCESS               =  0
ERROR_FILE_IN         = -1
ERROR_FILE_OUT        = -2
ERROR_MALLOC          = -3
ERROR_BAD_INPUT       = -4
ERROR_UNKNOWN_VERSION = -5
ERROR_FILES_MISMATCH  = -6

class ComptoFileInputError(Exception):
    pass

class ComptoFileOutputError(Exception):
    pass

class ComptoMemoryAllocationError(Exception):
    pass

class ComptoBadInputError(Exception):
    pass

class ComptoUnknownVersionError(Exception):
    pass

class ComptoMismatchedFilesError(Exception):
    pass

class ComptoUnknownError(Exception):
    pass

def RaiseError(error: int):
    if error == SUCCESS:
        return
    elif error == ERROR_FILE_IN:
        raise ComptoFileInputError("Error with input file")
    elif error == ERROR_FILE_OUT:
        raise ComptoFileOutputError("Error with output file")
    elif error == ERROR_MALLOC:
        raise ComptoMemoryAllocationError("Malloc failure")
    elif error == ERROR_BAD_INPUT:
        raise ComptoBadInputError("Bad Input")
    elif error == ERROR_UNKNOWN_VERSION:
        raise ComptoUnknownVersionError("Unknown version")
    elif error == ERROR_FILES_MISMATCH:
        raise ComptoMismatchedFilesError("Mismatch")
    else:
        raise ComptoUnknownError("Unknown error")

comptolib_path = os.path.dirname(os.path.abspath(__file__)) + "/comptolib.dll"

comptolib = ctypes.cdll.LoadLibrary(comptolib_path)
compto_decode = comptolib.Decode
compto_decode.argtypes = ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint)
compto_decode.restype = ctypes.c_int

compto_encode = comptolib.Encode
compto_encode.argtypes = ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint)
compto_encode.restype = ctypes.c_int

compto_fdecode = comptolib.DecodeFile
compto_fdecode.argtypes = ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int
compto_fdecode.restype = ctypes.c_int

compto_fencode = comptolib.EncodeFile
compto_fencode.argtypes = ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int
compto_fencode.restype = ctypes.c_int

def compress_data(input: bytes, raw: bool=False, version: int=3):
    input_size = len(input)
    output_size = ((input_size * 9) // 8) + 10
    output = b"\x00" * output_size
    output_size = ctypes.c_uint(output_size)
    error = compto_encode(version, input, input_size, output, ctypes.byref(output_size))
    RaiseError(error)
    
    if not raw:
        output = struct.pack("<b", version) + struct.pack("<2L", *(input_size, output_size.value)) + output[:output_size.value]
    
    return output

def decompress_data(input: bytes, raw: bool=False, version: int=3)->bytes:
    if raw:
        input_size = len(input)
        output_size = input_size * 10
    else:
        version ,= struct.unpack("<b", input[:1])
        input_size, output_size = struct.unpack("<2L", input[1:9])
        
    output = b"\x00" * output_size
    input = input[9:]
    
    error = compto_decode(version, input, input_size, output, ctypes.byref(ctypes.c_uint(output_size)))
    RaiseError(error)
    return output

def compress_file(input: str, output: str, raw: bool=False, version: int=3):
    error = compto_fencode(input.encode("utf-8"), output.encode("utf-8"), raw, version)
    RaiseError(error)

def decompress_file(input: str, output: str, raw: bool=False, version: int=3):
    error = compto_fdecode(input.encode("utf-8"), output.encode("utf-8"), raw, version)
    RaiseError(error)