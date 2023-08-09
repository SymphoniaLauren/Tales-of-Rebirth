import struct, sys, os, io
from dataclasses import dataclass, field
@dataclass
class pak2_chunks:
    theirsce: bytes = b""
    lipsync: bytes = b""
    unused: bytes = b""
    image_unk1: bytes = b""
    image_unk2: bytes = b""
    image_blobs: list = field(default_factory=list)

@dataclass
class pak2_file:
    #offsets: list
    char_count: int = 0
    slot_count: int = 0
    image_count: int = 0
    chunks: pak2_chunks = pak2_chunks()

def get_file_name_noext(path):
    return os.path.splitext(os.path.basename(path))[0]


def get_parent_folder(path):
    return os.path.normpath(os.path.join(path, os.pardir))


def insert_padded_chunk(file: bytes, chunk: bytes, alignment: int = 4):
    file.write(chunk)
    pad = (alignment - (file.tell() % alignment)) % alignment
    file.write(b"\x00" * pad)
    return file.tell()


def get_theirsce_from_pak2(file: bytes)->bytes:
    offsets = struct.unpack("<3I", file[:12])

    # Handle null 2nd offset because of course that's a thing
    if offsets[1] == 0:
        return file[offsets[0] : offsets[2]]
    else:
        return file[offsets[0] : offsets[1]]


def get_data(file: bytes)->pak2_file:
    offsets = struct.unpack("<6I", file[:24])
    data = pak2_file()
    data.char_count = struct.unpack("<H", file[0x18:0x1A])[0]
    data.slot_count = struct.unpack("<H", file[0x1A:0x1C])[0]  # 0x20 always
    data.image_count = struct.unpack("<H", file[0x1C:0x1E])[0]

    # Handle null 2nd offset because of course that's a thing
    if offsets[1] == 0:
        data.chunks.theirsce = file[offsets[0] : offsets[2]]
    else:
        data.chunks.theirsce = file[offsets[0] : offsets[1]]
        size = struct.unpack("<I", file[offsets[1] : offsets[1] + 4])[0] + 0x10
        data.chunks.lipsync = file[offsets[1] : offsets[1] + size]

    data.chunks.unused = file[offsets[2] : offsets[2] + (data.char_count * 4)]
    data.chunks.image_unk1 = file[offsets[3] : offsets[3] + (data.slot_count * 4)]
    data.chunks.image_unk2 = file[offsets[4] : offsets[4] + (data.image_count * 2)]
    # image_data = bytearray(file[offsets[5]:len(file)])

    blob_offsets = list(
        struct.unpack(
            "<%dI" % (data.image_count * 2), file[offsets[5] : offsets[5] + data.image_count * 8]
        )
    )
    del blob_offsets[1::2] #Yeet all the odd offset, they be useless

    for blob in blob_offsets:
        blob_size = struct.unpack("<I", file[blob : blob + 4])[0]
        if blob_size == 0:
            blob_size = 0x400
        data.chunks.image_blobs.append(file[blob : blob + blob_size])
    
    return data


def create_pak2(data: pak2_file)->bytes:
    output = io.BytesIO()
    output.seek(0)
    output.write(b"\x00" * 0x20)
    offsets_new = []
    offsets_new.append(output.tell())

    # theirsce
    offsets_new.append(insert_padded_chunk(output, data.chunks.theirsce))

    # lipsync
    offsets_new.append(insert_padded_chunk(output, data.chunks.lipsync))

    # unused
    offsets_new.append(insert_padded_chunk(output, data.chunks.unused))

    # unk1
    offsets_new.append(insert_padded_chunk(output, data.chunks.image_unk1))

    # unk2
    offsets_new.append(insert_padded_chunk(output, data.chunks.image_unk2))

    # images
    # Create image chunk
    image_chunk = b"\x00" * (data.image_count * 8)  # minimum size
    insert_padded_chunk(output, image_chunk, 128)
    image_offsets = []

    image_offsets.append(output.tell())

    for blob in data.chunks.image_blobs:
        image_offsets.append(insert_padded_chunk(output, blob, 128))

    image_offsets = image_offsets[:-1]
    image_offsets = [
        val for val in image_offsets for _ in (0, 1)
    ]  # image data offsets are duplicated

    # Write image data offsets
    output.seek(offsets_new[5])
    output.write(struct.pack("<%dI" % len(image_offsets), *image_offsets))

    # Write chunk offsets
    output.seek(0)
    output.write(struct.pack("<%dI" % len(offsets_new), *offsets_new))

    # Write metadata
    output.write(struct.pack("<H", data.char_count))
    output.write(struct.pack("<H", data.slot_count))
    output.write(struct.pack("<H", data.image_count))

    end = output.getvalue()

    return end


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("pak2.py [pak2_path] [theirsce_path]")
        sys.exit()

    with open(sys.argv[1], "rb") as input:
        file = input.read()

    pak2 = get_data(file)

    print("file size: %d" % len(file))
    print("char_count: %d" % pak2.char_count)
    print("slot_count: %d" % pak2.slot_count)
    print("image_count: %d" % pak2.image_count)
    print()

    # Get new Theirsce, if there's no second arg just reinsert original
    if len(sys.argv) > 2:
        with open(sys.argv[2], "rb+") as f:
            theirsce = f.read()

    with open(sys.argv[2] + ".new", "wb+") as output:
        output.write(create_pak2(pak2))

    print("Done!")
