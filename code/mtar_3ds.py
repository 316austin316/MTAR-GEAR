import struct
import binascii
import os
from tkinter import filedialog, Tk, Button, Text, END, Label, Entry, messagebox


def read_mtar(file_path):
    with open(file_path, 'rb') as file:
        data = file.read()
    return data


def parse_mtcm_data_table(mtar_data):
    header_end = 32  # Assuming the header is 32 bytes. Adjust as necessary.
    mtcm_offset = struct.unpack('<I', mtar_data[12:16])[0]
    current_offset = header_end
    mtcm_data_table = []

    # Skip over padding bytes and the first instance of 90 0A 00 00
    target_sequence = b'\x90\x0A\x00\x00'
    while current_offset < len(mtar_data):
        if mtar_data[current_offset:current_offset + 4] == target_sequence:
            current_offset += 4  # Skip the first instance
            break
        current_offset += 1
    
    # Keep reading entries until reaching the offset of the first block
    while current_offset < mtcm_offset:
        data_offset, data_size = struct.unpack_from('<II', mtar_data, current_offset)
        mtcm_data_table.append((data_offset, data_size))
        current_offset += 8  # Each entry is 8 bytes

    return mtcm_data_table, current_offset


def extract_all_blocks_from_file(mtar_data, blocks_info_path):
    with open(blocks_info_path, 'r') as f:
        lines = f.read().splitlines()

    # Initialize variables
    first_offset = None
    first_size = None
    block_sizes = []

    # Parse the lines
    for line in lines:
        line = line.strip()  # Remove any leading/trailing whitespace
        if not line or line.startswith('#'):  # Skip empty lines and comments
            continue
        if '=' not in line:
            raise ValueError(f"Line '{line}' does not contain an '=' character for key-value splitting.")
        
        key, value = line.split('=', 1)  # Split on the first '=' only
        if key == 'first_offset':
            first_offset = int(value, 0)
        elif key == 'first_size':
            first_size = int(value, 0)
        elif key.startswith('size'):
            block_sizes.append(int(value, 0))
        else:
            raise ValueError(f"Unknown key '{key}' in line '{line}'.")

    if first_offset is None or first_size is None:
        raise ValueError("The first_offset or first_size is not defined in the blocks info file.")

    # Include the first size in the block sizes
    block_sizes.insert(0, first_size)

    # Extract all blocks using the sizes
    return extract_all_blocks(mtar_data, first_offset, block_sizes)

def extract_all_blocks(mtar_data, first_block_offset, block_sizes):
    blocks = []
    current_offset = first_block_offset
    for size in block_sizes:
        block_data = mtar_data[current_offset:current_offset + size]
        blocks.append(block_data)
        current_offset += size
    return blocks
    
    
def modify_and_save_block():
    # Open a .bin file
    block_file_path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin")])
    if not block_file_path:
        return  # User cancelled or no file selected

    with open(block_file_path, 'rb') as file:
        block_data = bytearray(file.read())  # Use bytearray for mutability


    # Step 1: Insert bytes at 0x40
    insert_position = 0x40
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
    # Step 1: Insert bytes at 0x40
    insert_position = 0x40
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
    
def extract_blocks_from_info_file():
    if file_path:
        blocks_info_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if blocks_info_path:
            mtar_data = read_mtar(file_path)
            blocks = extract_all_blocks_from_file(mtar_data, blocks_info_path)
            
            # Now you can save each block to a file
            for i, block in enumerate(blocks):
                with open(f"block_{i}.bin", "wb") as f:
                    f.write(block)
            messagebox.showinfo("Success", "All blocks extracted successfully.")
    else:
        messagebox.showerror("Error", "No MTAR file selected.")


