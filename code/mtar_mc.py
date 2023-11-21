import struct
import binascii
import os
from tkinter import filedialog, Tk, Button, Text, END, Label, Entry, messagebox


def read_mtar(file_path):
    with open(file_path, 'rb') as file:
        data = file.read()
    return data

file_path = None

def parse_mtcm_data_table(mtar_data):
    header_end = 32  # Assuming the header is 32 bytes. Adjust as necessary.
    mtcm_offset = struct.unpack('<I', mtar_data[12:16])[0]
    current_offset = header_end
    mtcm_data_table = []

    # Skip over padding bytes to find the start of the data table
    while current_offset < len(mtar_data) and mtar_data[current_offset] == 0:
        current_offset += 1
    
    # Keep reading entries until reaching the offset of the first block
    while current_offset < mtcm_offset:
        data_offset, unk, data_size, unk2 = struct.unpack_from('<IIII', mtar_data, current_offset)
        mtcm_data_table.append((data_offset, unk, data_size, unk2))
        current_offset += 16  # Each entry is 16 bytes

    return mtcm_data_table, current_offset
    


def extract_block(file_path, block_index):
    mtar_data = read_mtar(file_path)
    mtcm_data_table, _ = parse_mtcm_data_table(mtar_data)

    if mtcm_data_table and 0 <= block_index < len(mtcm_data_table):
        data_offset, _, data_size, _ = mtcm_data_table[block_index]
        block_data = mtar_data[data_offset:data_offset+data_size]
        
        save_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("Binary files", "*.bin")])
        if save_path:
            with open(save_path, 'wb') as file:
                file.write(block_data)
            messagebox.showinfo("Success", "Data block extracted successfully.")
    else:
        messagebox.showerror("Error", "Invalid block index or MTCM data table not found.")


def import_new_data(file_path, block_index):
    mtar_data = read_mtar(file_path)
    mtcm_data_table, mtcm_data_end_offset = parse_mtcm_data_table(mtar_data)

    if mtcm_data_table and 0 <= block_index < len(mtcm_data_table):
        open_path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin")])
        
        if open_path:
            with open(open_path, 'rb') as file:
                new_data = file.read()
            
            new_offset = len(mtar_data)  # New data will be appended at the end
            
            # Update the block's data table entry with new offset and size
            mtcm_data_table[block_index] = (
                new_offset,
                mtcm_data_table[block_index][1],
                len(new_data),
                mtcm_data_table[block_index][3],
            )

            # Write the updated MTCM data table back to the file
            with open(file_path, 'r+b') as file:
                file.seek(mtcm_data_end_offset - len(mtcm_data_table) * 16)  # Move to the start of the MTCM data table
                for entry in mtcm_data_table:
                    file.write(struct.pack('<IIII', *entry))
                
                # Append the new data at the end of the file
                file.seek(0, 2)  # Move to the end of the file
                file.write(new_data)
            
            messagebox.showinfo("Success", "Data block imported successfully.")
            
    else:
        messagebox.showerror("Error", "Invalid block index or MTCM data table not found.")




def export_all_blocks(file_path):
    mtar_data = read_mtar(file_path)
    mtcm_data_table, _ = parse_mtcm_data_table(mtar_data)
    
    if mtcm_data_table:
        export_directory = filedialog.askdirectory()
        if export_directory:
            for i, (data_offset, _, data_size, _) in enumerate(mtcm_data_table):
                block_data = mtar_data[data_offset:data_offset+data_size]
                save_path = os.path.join(export_directory, f"block_{i}.bin")
                with open(save_path, 'wb') as file:
                    file.write(block_data)
            messagebox.showinfo("Success", "All data blocks exported successfully.")
    else:
        messagebox.showerror("Error", "MTCM data table not found.")

def import_all_blocks(file_path):
    mtar_data = read_mtar(file_path)
    mtcm_data_table, mtcm_data_end_offset = parse_mtcm_data_table(mtar_data)
    
    if mtcm_data_table:
        import_directory = filedialog.askdirectory()
        if import_directory:
            for i in range(len(mtcm_data_table)):
                open_path = os.path.join(import_directory, f"block_{i}.bin")
                if os.path.exists(open_path):
                    with open(open_path, 'rb') as file:
                        new_data = file.read()

                    # Replace the block of data and update subsequent offsets
                    data_offset, _, data_size, _ = mtcm_data_table[i]
                    with open(file_path, 'r+b') as file:
                        file.seek(data_offset)
                        file.write(new_data)

                        # Calculate the offset difference
                        offset_difference = len(new_data) - data_size

                        # Update the replaced block's size
                        mtcm_data_table[i] = (
                            mtcm_data_table[i][0],
                            mtcm_data_table[i][1],
                            len(new_data),
                            mtcm_data_table[i][3],
                        )

                        # Update all subsequent data offsets if necessary
                        if offset_difference != 0:
                            for j in range(i + 1, len(mtcm_data_table)):
                                mtcm_data_table[j] = (
                                    mtcm_data_table[j][0] + offset_difference,
                                    mtcm_data_table[j][1],
                                    mtcm_data_table[j][2],
                                    mtcm_data_table[j][3],
                                )

                            # Write the updated MTCM data table back to the file
                            file.seek(mtcm_data_end_offset - len(mtcm_data_table) * 16)
                            for entry in mtcm_data_table:
                                file.write(struct.pack('<IIII', *entry))
            
            messagebox.showinfo("Success", "All data blocks imported successfully.")
    else:
        messagebox.showerror("Error", "MTCM data table not found.")
        