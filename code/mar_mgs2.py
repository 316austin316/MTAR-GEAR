import struct
import os

class MarHeader:
    def __init__(self, data):
        self.magic = struct.unpack_from('<I', data, 0)[0]
        self.maxJoint = struct.unpack_from('<I', data, 4)[0]
        self.numMotion = struct.unpack_from('<I', data, 8)[0]
        self.mtcmOffset = struct.unpack_from('<I', data, 12)[0]




def read_mar(file_path):
    with open(file_path, 'rb') as file:
        data = file.read(16)  # MAR header is 16 bytes
        return MarHeader(data)

def extract_blocks(file_path, header):
    blocks = []
    with open(file_path, 'rb') as file:
        # Start reading from right after the header
        file.seek(16)  # MAR header size is 16 bytes

        while file.tell() < header.mtcmOffset:
            entry_data = file.read(16)
            if not entry_data or len(entry_data) != 16:
                break

            # Unpack the entry data using little-endian format
            data_offset, _, data_size, _ = struct.unpack('<IIII', entry_data)
            absolute_data_offset = header.mtcmOffset + data_offset
            blocks.append((absolute_data_offset, data_size))

    return blocks

def export_blocks(file_path, blocks):
    with open(file_path, 'rb') as file:
        for i, (offset, size) in enumerate(blocks):
            file.seek(offset)
            block_data = file.read(size + 4)  # Include 4 extra bytes as per your specification
            with open(f"block_{i}.bin", "wb") as out_file:
                out_file.write(block_data)
                
def parse_mtcm_data_table(file_path, header):
    data_table_entries = []
    with open(file_path, 'rb') as file:
        file.seek(16)  # Skip the MAR header

        while file.tell() < header.mtcmOffset:
            entry_data = file.read(16)
            if not entry_data or len(entry_data) != 16:
                break

            data_offset, _, data_size, _ = struct.unpack('<IIII', entry_data)
            data_table_entries.append((data_offset, data_size))

    return data_table_entries

def modify_block_data(block_data):
    # Step 1: Insert bytes at 0x40
    insert_position = 0x40
    if insert_position < len(block_data):
        block_data[insert_position:insert_position] = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    # Step 2: Modify the first byte of the uint32 at 0x10
    uint32_position = 0x10
    if uint32_position + 4 <= len(block_data):
        original_byte = block_data[uint32_position]
        block_data[uint32_position] = (original_byte + 0x10) % 0x100

        # Step 3: Insert 00 00 00 00 right after the uint32
        block_data[uint32_position + 4:uint32_position + 4] = b'\x00\x00\x00\x00'
        
    return block_data

def import_new_block(file_path, block_index, new_block_path):
    with open(file_path, 'rb+') as file:
        # Read the header
        header = MarHeader(file.read(16))
        
        # Read and update the MTCM data table
        data_table = []
        file.seek(16)  # Start of the MTCM data table
        while file.tell() < header.mtcmOffset:
            data_offset, pad1, data_size, pad2 = struct.unpack('<IIII', file.read(16))
            data_table.append((data_offset, pad1, data_size, pad2))

        # Read new block data
        with open(new_block_path, 'rb') as new_block_file:
            new_block_data = new_block_file.read()
        
        # Check if block index is valid
        if 0 <= block_index < len(data_table):
            # Calculate new offset for the block
            file.seek(0, os.SEEK_END)
            new_offset = file.tell()

            # Update the data table entry
            # Note: The offset is relative to the MTCM offset
            _, pad1, _, pad2 = data_table[block_index]
            updated_entry = (new_offset - header.mtcmOffset, pad1, len(new_block_data), pad2)
            data_table[block_index] = updated_entry

            # Write the new block data to the end of the file
            file.write(new_block_data)

            # Update the MTCM data table
            file.seek(16)  # Start of the MTCM data table
            for entry in data_table:
                file.write(struct.pack('<IIII', *entry))

        else:
            raise ValueError("Invalid block index")



