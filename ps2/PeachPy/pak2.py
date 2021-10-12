import struct, sys, os
from collections import namedtuple

# pak_chunks = namedtuple("pak_chunks", "theirsce lipsync image_unk1 image_unk2 image_blobs")


def get_file_name_noext(path):
    return os.path.splitext(os.path.basename(path))[0]


def get_parent_folder(path):
    return os.path.normpath(os.path.join(path, os.pardir))


def insert_padded_chunk(file: bytes, chunk: bytes, alignment: int = 4):
    file.write(chunk)
    pad = (alignment - (file.tell() % alignment)) % alignment
    output.write(b"\x00" * pad)
    return file.tell()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("pak2.py [pak2_path] [theirsce_path]")
        sys.exit()

    with open(sys.argv[1], "rb") as input:
        pak2 = input.read()

    # Extract individual chunks:
    offsets = []
    offsets = struct.unpack("<6I", pak2[:24])
    char_count, = struct.unpack("<H", pak2[0x18:0x1A])
    slots_count, = struct.unpack("<H", pak2[0x1A:0x1C])  # 0x20 always
    image_count, = struct.unpack("<H", pak2[0x1C:0x1E])

    print("PAK2 size: %d" % len(pak2))
    print("char_count: %d" % char_count)
    print("slots_count: %d" % slots_count)
    print("images_count: %d" % image_count)
    print()

    theirsce = pak2[offsets[0] : offsets[1]]

    size = struct.unpack("<I", pak2[offsets[1] : offsets[1] + 4])[0] + 0x10
    lipsync = pak2[offsets[1] : offsets[1] + size]

    unused = pak2[offsets[2] : offsets[2] + (char_count * 4)]
    image_unk1 = pak2[offsets[3] : offsets[3] + (slots_count * 4)]
    image_unk2 = pak2[offsets[4] : offsets[4] + (image_count * 2)]
    # image_data = bytearray(pak2[offsets[5]:len(pak2)])

    image_blobs = []
    blob_offsets = list(
        struct.unpack(
            "<%dI" % (image_count * 2), pak2[offsets[5] : offsets[5] + image_count * 8]
        )
    )
    del blob_offsets[1::2] #Yeet all the odd offset, they be useless

    for blob in blob_offsets:
        blob_size = struct.unpack("<I", pak2[blob : blob + 4])[0]
        if blob_size == 0:
            blob_size = 0x400
        image_blobs.append(pak2[blob : blob + blob_size])

    # base_addr, = struct.unpack("<I", image_data[0:4])
    # for ofs in range(image_count):
    #    relative_offset = struct.unpack("<I", image_data[ofs*4:(ofs*4)+4])[0] - base_addr
    #    image_data[ofs*4:(ofs*4)+4] = struct.pack("<I", relative_offset)

    # image_data = bytes(image_data)

    # Get new Theirsce, if there's no second arg just reinsert original
    if len(sys.argv) > 2:
        with open(sys.argv[2], "rb+") as f:
            theirsce = f.read()

    with open(sys.argv[1] + ".new", "wb+") as output:
        output.write(b"\x00" * 0x20)
        offsets_new = []
        offsets_new.append(output.tell())

        # theirsce
        offsets_new.append(insert_padded_chunk(output, theirsce))

        # lipsync
        offsets_new.append(insert_padded_chunk(output, lipsync))

        # unused
        offsets_new.append(insert_padded_chunk(output, unused))

        # unk1
        offsets_new.append(insert_padded_chunk(output, image_unk1))

        # unk2
        offsets_new.append(insert_padded_chunk(output, image_unk2))

        # images
        # Create image chunk
        image_chunk = b"\x00" * (image_count * 8)  # minimum size
        insert_padded_chunk(output, image_chunk, 128)
        image_offsets = []

        image_offsets.append(output.tell())

        for blob in image_blobs:
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
        output.write(struct.pack("<H", char_count))
        output.write(struct.pack("<H", slots_count))
        output.write(struct.pack("<H", image_count))

    print("Done!")
