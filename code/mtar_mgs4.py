import struct
import binascii
import os
from tkinter import filedialog, Tk, Button, Text, END, Label, Entry, messagebox


class MtarHeader:
    def __init__(self, data):
        self.magic = struct.unpack_from('>I', data, 0)[0]
        self.maxJoint = struct.unpack_from('>H', data, 4)[0]
        self.maxEffPos = struct.unpack_from('>H', data, 6)[0]
        self.numBoneName = struct.unpack_from('>H', data, 8)[0]
        self.numMotion = struct.unpack_from('>H', data, 10)[0]
        self.flags = struct.unpack_from('>I', data, 12)[0]
        self.mtcmOffset = struct.unpack_from('>I', data, 16)[0]
        self.mtexOffset = struct.unpack_from('>I', data, 20)[0]
        self.boneNameTableOffset = struct.unpack_from('>I', data, 24)[0]
        self.dataTableOffset = struct.unpack_from('>I', data, 28)[0]

def extract_blocks(file_path, header):
    blocks = []
    with open(file_path, 'rb') as file:
        # Go to the start of the MTCM data table
        file.seek(header.dataTableOffset)

        while file.tell() < header.mtcmOffset:
            entry_data = file.read(16)  # Each entry is 16 bytes
            if not entry_data or len(entry_data) != 16:
                break  # End of table or file

            # Unpack the entry data in big-endian format
            relative_offset, data_size, unk, unk2 = struct.unpack('>IIII', entry_data)

            # Calculate the absolute data offset (relative to the start of the file)
            absolute_data_offset = header.mtcmOffset + relative_offset

            # Append the block information (identifier, start position, size)
            blocks.append((absolute_data_offset, relative_offset, data_size, unk, unk2))

    return blocks


def export_mtcm_data_table(file_path, header, export_path):
    with open(file_path, 'rb') as file:
        file.seek(header.dataTableOffset)
        mtcm_data = file.read(header.mtcmOffset - header.dataTableOffset)
        with open(export_path, 'wb') as export_file:
            export_file.write(mtcm_data)

def read_mtar_mgs4(file_path):
    with open(file_path, 'rb') as file:
        data = file.read(36)  # Read the first 36 bytes for the header
        header = MtarHeader(data)
        # Potentially swap endian here if necessary
        # swapEndianMtar(data)
        return header

def modify_and_save_block():
    # Open a .bin file
    block_file_path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin")])
    if not block_file_path:
        return  # User cancelled or no file selected

    with open(block_file_path, 'rb') as file:
        block_data = bytearray(file.read())  # Use bytearray for mutability


    # Step 1: Insert bytes at 0x32
    insert_position = 0x32
    if insert_position < len(block_data):
        block_data[insert_position:insert_position] = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    # Step 2: Modify the first byte of the uint32 at 0x10
    uint32_position = 0x10
    if uint32_position + 4 <= len(block_data):  # Ensure there's enough data for a uint32
        original_byte = block_data[uint32_position]
        print("Original Byte at 0x10:", format(original_byte, '02x'))

        # Modify only the first byte of the uint32
        block_data[uint32_position] = (original_byte + 0x10) % 0x100
        modified_byte = block_data[uint32_position]
        print("Modified Byte at 0x10:", format(modified_byte, '02x'))

        # Step 3: Insert 00 00 00 00 right after the uint32
        block_data[uint32_position + 4:uint32_position + 4] = b'\x00\x00\x00\x00'

    # Save the modified block
    save_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("Binary files", "*.bin")])
    if save_path:
        with open(save_path, 'wb') as file:
            file.write(block_data)
        messagebox.showinfo("Success", "Block modified and saved successfully.")
        
        
def modify_block_data(block_data):
    # Step 1: Insert bytes at 0x32
    insert_position = 0x32
    if insert_position < len(block_data):
        block_data[insert_position:insert_position] = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    # Step 2: Modify the first byte of the uint32 at 0x10
    uint32_position = 0x10
    if uint32_position + 4 <= len(block_data):  # Ensure there's enough data for a uint32
        original_byte = block_data[uint32_position]
        print("Original Byte at 0x10:", format(original_byte, '02x'))

        # Modify only the first byte of the uint32
        block_data[uint32_position] = (original_byte + 0x10) % 0x100
        modified_byte = block_data[uint32_position]
        print("Modified Byte at 0x10:", format(modified_byte, '02x'))

        # Step 3: Insert 00 00 00 00 right after the uint32
        block_data[uint32_position + 4:uint32_position + 4] = b'\x00\x00\x00\x00'
        
    return block_data

def convert_all_in_folder():
    source_folder = filedialog.askdirectory()
    if not source_folder:
        return  # User cancelled or no folder selected

    destination_folder = filedialog.askdirectory()
    if not destination_folder:
        return  # User cancelled or no folder selected

    for file_name in os.listdir(source_folder):
        if file_name.endswith('.bin'):
            file_path = os.path.join(source_folder, file_name)

            with open(file_path, 'rb') as file:
                block_data = bytearray(file.read())

            modified_data = modify_block_data(block_data)

            save_path = os.path.join(destination_folder, file_name)
            with open(save_path, 'wb') as file:
                file.write(modified_data)

    messagebox.showinfo("Success", "All .bin files converted successfully.")
    
    


