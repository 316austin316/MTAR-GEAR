import struct
import binascii
import os
import tkinter as tk
from tkinter import filedialog, Tk, Button, Text, END, Label, Entry, messagebox, ttk
import mtar_3ds
import mtar_mc
import mtar_editor
import mtar_mgs4
from PIL import Image, ImageTk
import mar_mgs2



# GUI setup for MC MTAR tab
def setup_mc_mtar_tab(tab):
    file_path = None  # Define file_path within the scope of the setup_mc_mtar_tab function

    def open_file():
        response = messagebox.askokcancel("Backup Reminder", 
                                      "Please make a backup of your MTAR file before proceeding!")
        if response:
            nonlocal file_path
            file_path = filedialog.askopenfilename(filetypes=[("MTAR files", "*.mtar")])
            if file_path:
                display_data_table()

    def display_data_table():
        if file_path:  # Check if file_path is not None
            mtar_data = mtar_mc.read_mtar(file_path)
            mtcm_data_table, _ = mtar_mc.parse_mtcm_data_table(mtar_data)
            text_widget.delete("1.0", tk.END)
            if mtcm_data_table:
                for i, entry in enumerate(mtcm_data_table):
                    text_widget.insert(tk.END, f"Block {i}: {entry}\n")
            else:
                text_widget.insert(tk.END, "MTAR data table not found.")

    def extract_data():
        if file_path:
            block_index = int(entry_block_index.get())
            mtar_mc.extract_block(file_path, block_index)

    def replace_data():
        if file_path:
            block_index = int(entry_block_index.get())
            mtar_mc.import_new_data(file_path, block_index)
            display_data_table()

    text_widget = tk.Text(tab, height=15, width=80)
    text_widget.pack(padx=10, pady=10)

    open_button = tk.Button(tab, text="Open MTAR File", command=open_file)
    open_button.pack(pady=10)

    label_block_index = tk.Label(tab, text="Block Index:")
    label_block_index.pack()
    entry_block_index = tk.Entry(tab)
    entry_block_index.pack()

    extract_button = tk.Button(tab, text="Extract Animation Block", command=extract_data)
    extract_button.pack(pady=10)

    replace_button = tk.Button(tab, text="Import New Animation Block", command=replace_data)
    replace_button.pack(pady=10)

    export_all_button = tk.Button(tab, text="Export All Blocks", command=lambda: mtar_mc.export_all_blocks(file_path))
    export_all_button.pack(pady=10)

    import_all_button = tk.Button(tab, text="Import All Blocks", command=lambda: mtar_mc.import_all_blocks(file_path), state=tk.DISABLED)
    import_all_button.pack(pady=10)


# GUI setup for 3DS MTAR tab
file_path = None

def setup_3ds_mtar_tab(tab):
    text_widget = Text(tab, height=15, width=80)
    text_widget.pack(padx=10, pady=10)

    open_button = Button(tab, text="Open MTAR File", command=lambda: open_file_3ds(text_widget))
    open_button.pack(pady=10)
    
    label_block_index = Label(tab, text="Block Index:")
    label_block_index.pack()
    entry_block_index = tk.Entry(tab)
    entry_block_index.pack()

    extract_info_button = Button(tab, text="Extract Animation Blocks From Info File", command=mtar_3ds.extract_blocks_from_info_file)
    extract_info_button.pack(pady=10)

    conversion_button = Button(tab, text="Convert 3DS to MC", command=mtar_3ds.modify_and_save_block)
    conversion_button.pack(pady=10)

    convert_all_button = Button(tab, text="Convert All in Folder", command=mtar_3ds.convert_all_in_folder)
    convert_all_button.pack(pady=10)
    

    def open_file_3ds(text_widget):
        global file_path
        file_path = filedialog.askopenfilename(filetypes=[("MTAR files", "*.mtar")])
        if file_path:
            display_data_table_3ds(text_widget)

    def display_data_table_3ds(text_widget):
        mtar_data = mtar_3ds.read_mtar(file_path)
        mtcm_data_table, _ = mtar_3ds.parse_mtcm_data_table(mtar_data)
        text_widget.delete("1.0", END)
        if mtcm_data_table:
            for i, entry in enumerate(mtcm_data_table):
                text_widget.insert(END, f"Block {i}: {entry}\n")
        else:
            text_widget.insert(END, "MTAR data table not found.")
            
            
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

def setup_mtar_editor_tab(tab):
    file_path = None
    num_frames_var = tk.StringVar()
    num_joints_var = tk.StringVar() 
    
    # Define the Text widget for displaying block info
    info_text_widget = tk.Text(tab, height=15, width=80)
    info_text_widget.pack(padx=10, pady=10)

    def open_block_file():
        nonlocal file_path
        file_path = filedialog.askopenfilename(filetypes=[("BIN files", "*.bin")])
        if file_path:
            header = mtar_editor.read_mtcm_header(file_path)  # Read the header from the file
            num_frames_var.set(str(header.numFrames))
            num_joints_var.set(str(header.numJoints))
            mtar_editor.display_block_info(header, info_text_widget)

    def display_block_info():
        if file_path:
            header = mtar_editor.read_mtcm_header(file_path)
            num_frames_var.set(str(header.numFrames))
            

    def save_changes(file_path, num_frames, num_joints, text_widget):
        if file_path and num_frames.isdigit() and num_joints.isdigit():
            new_num_frames = int(num_frames)
            new_num_joints = int(num_joints)
            mtar_editor.update_num_frames(file_path, new_num_frames)  # Update number of frames
            mtar_editor.update_num_joints(file_path, new_num_joints)  # Update number of joints
            header = mtar_editor.read_mtcm_header(file_path)  # Refresh the displayed info
            mtar_editor.display_block_info(header, text_widget)
            messagebox.showinfo("Success", "Changes updated successfully.")

    open_button = tk.Button(tab, text="Open Block File", command=open_block_file)
    open_button.pack(pady=10)

    frames_label = tk.Label(tab, text="Number of Frames:")
    frames_label.pack()

    frames_entry = tk.Entry(tab, textvariable=num_frames_var)
    frames_entry.pack()
    
    joints_label = tk.Label(tab, text="Number of Joints:")  # Label for number of joints
    joints_label.pack()
    joints_entry = tk.Entry(tab, textvariable=num_joints_var)  # Entry for number of joints
    joints_entry.pack()

    save_button = tk.Button(tab, text="Save Changes", command=lambda: save_changes(file_path, num_frames_var.get(), num_joints_var.get(), info_text_widget))
    save_button.pack(pady=10)


def setup_mtar_mgs4_tab(tab):
    file_path = None
    blocks_text_widget = None

    def open_mgs4_file():
        nonlocal file_path
        file_path = filedialog.askopenfilename(filetypes=[("MGS4 MTAR files", "*.mtar")])
        if file_path:
            display_mgs4_file_info()
            
    def export_data_table():
        if file_path:
            header = mtar_mgs4.read_mtar_mgs4(file_path)
            export_path = filedialog.asksaveasfilename(defaultextension=".bin",
                                                       filetypes=[("Binary files", "*.bin"), ("All files", "*.*")])
            if export_path:
                mtar_mgs4.export_mtcm_data_table(file_path, header, export_path)
                messagebox.showinfo("Export Complete", "MTCM data table exported successfully as a raw binary file.")


    def display_mgs4_file_info():
        if file_path:
            header = mtar_mgs4.read_mtar_mgs4(file_path)
            blocks = mtar_mgs4.extract_blocks(file_path, header)
            # Display header information in the Text widget
            info_text_widget.delete("1.0", tk.END)
            info_text_widget.insert(tk.END, f"Magic: {header.magic}\n")
            info_text_widget.insert(tk.END, f"Max Joint: {header.maxJoint}\n")
            info_text_widget.insert(tk.END, f"Max Eff Pos: {header.maxEffPos}\n")
            info_text_widget.insert(tk.END, f"Num Bone Name: {header.numBoneName}\n")
            info_text_widget.insert(tk.END, f"Num Motion: {header.numMotion}\n")
            info_text_widget.insert(tk.END, f"Flags: {header.flags}\n")
            info_text_widget.insert(tk.END, f"MTCM Offset: {header.mtcmOffset}\n")
            info_text_widget.insert(tk.END, f"MTEX Offset: {header.mtexOffset}\n")
            info_text_widget.insert(tk.END, f"Bone Name Table Offset: {header.boneNameTableOffset}\n")
            info_text_widget.insert(tk.END, f"Data Table Offset: {header.dataTableOffset}\n")
            # Display blocks information
            blocks_text_widget.delete("1.0", tk.END)
            block_id = 0
            for true_offset, relative_offset, block_size, _, _ in blocks:
                blocks_text_widget.insert(tk.END, f"Block ID: {block_id}, True Offset: {true_offset}, Relative Offset: {relative_offset}, Size: {block_size}\n")
                block_id += 1


            
    def extract_and_save_blocks():
        if file_path:
            header = mtar_mgs4.read_mtar_mgs4(file_path)
            blocks = mtar_mgs4.extract_blocks(file_path, header)
            success_count = 0
            block_id = 0

        for block in blocks:
            true_offset, _, block_size, _, _ = block  # Using _ for unused values
            try:
                save_block(file_path, true_offset, block_size, block_id)
                success_count += 1
                block_id += 1  # Increment block_id for each block
            except Exception as e:
                print(f"Error extracting block {block_id} at offset {true_offset}: {e}")

        messagebox.showinfo("Extraction Complete", f"{success_count} out of {len(blocks)} blocks extracted successfully.")


    def save_block(file_path, start, size, block_id):
        with open(file_path, 'rb') as file:
            file.seek(start)
            block_data = file.read(size)

        # Generate a file name based on the offset and size
            block_file_name = f"anim_block_{block_id}.bin"
            with open(block_file_name, "wb") as block_file:
                block_file.write(block_data)


    open_button = tk.Button(tab, text="Open MGS4 MTAR File", command=open_mgs4_file)
    open_button.pack(pady=10)

    info_text_widget = tk.Text(tab, height=15, width=80)
    info_text_widget.pack(padx=10, pady=10)
    
    blocks_text_widget = tk.Text(tab, height=10, width=80)
    blocks_text_widget.pack(padx=10, pady=10)

    extract_blocks_button = tk.Button(tab, text="Extract and Save Animation Blocks", command=extract_and_save_blocks)
    extract_blocks_button.pack(pady=10)

    conversion_button = tk.Button(tab, text="Convert MGS4 to MC (experimental)", command=mtar_mgs4.modify_and_save_block)
    conversion_button.pack(pady=10)

    convert_all_button = tk.Button(tab, text="Convert All in Folder (experimental)", command=mtar_mgs4.convert_all_in_folder)
    convert_all_button.pack(pady=10)
    
    export_table_button = tk.Button(tab, text="Export MTCM Data Table", command=export_data_table)
    export_table_button.pack(pady=10)
    
def setup_mar_mgs2_tab(tab):
    file_path = None

    # Initialize Text widgets for displaying header, block info, and data table
    info_text_widget = tk.Text(tab, height=10, width=80)
    info_text_widget.pack(padx=10, pady=10)

    def open_mar_file():
        response = messagebox.askokcancel("Backup Reminder", 
                                          "Please make a backup of your MAR file before proceeding!")
        if response:
            nonlocal file_path
            file_path = filedialog.askopenfilename(filetypes=[("MGS2 MAR files", "*.mar")])
            if file_path:
                display_mar_file_info()

    def display_mar_file_info():
        if file_path:
            header = mar_mgs2.read_mar(file_path)
            data_table = mar_mgs2.parse_mtcm_data_table(file_path, header)
            # Display header and data table information in the Text widget
            info_text_widget.delete("1.0", tk.END)
            info_text_widget.insert(tk.END, f"Magic: {header.magic}\n")
            info_text_widget.insert(tk.END, f"Max Joint: {header.maxJoint}\n")
            info_text_widget.insert(tk.END, f"Num Motion: {header.numMotion}\n")
            info_text_widget.insert(tk.END, f"MTCM Offset: {header.mtcmOffset}\n")
            for offset, size in data_table:
                info_text_widget.insert(tk.END, f"Offset: {offset}, Size: {size}\n")

    def export_animation_blocks():
        if file_path:
            header = mar_mgs2.read_mar(file_path)
            blocks = mar_mgs2.extract_blocks(file_path, header)
            mar_mgs2.export_blocks(file_path, blocks)
            messagebox.showinfo("Export Complete", "Animation blocks exported successfully.")
            
    def convert_mgs2_to_mgs3():
        block_file_path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin")])
        if block_file_path:
            with open(block_file_path, 'rb') as file:
                block_data = bytearray(file.read())
            
            modified_data = mar_mgs2.modify_block_data(block_data)

            save_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("Binary files", "*.bin")])
            if save_path:
                with open(save_path, 'wb') as file:
                    file.write(modified_data)
                messagebox.showinfo("Conversion Complete", "MGS2 block converted to MGS3 format successfully.")
                
    def refresh_mar_display():
        if file_path:
            header = mar_mgs2.read_mar(file_path)
            data_table = mar_mgs2.parse_mtcm_data_table(file_path, header)
            info_text_widget.delete("1.0", tk.END)
            info_text_widget.insert(tk.END, f"Magic: {header.magic}\n")
            info_text_widget.insert(tk.END, f"Max Joint: {header.maxJoint}\n")
            info_text_widget.insert(tk.END, f"Num Motion: {header.numMotion}\n")
            info_text_widget.insert(tk.END, f"MTCM Offset: {header.mtcmOffset}\n")
            for offset, size in data_table:
                info_text_widget.insert(tk.END, f"Offset: {offset}, Size: {size}\n")
                
    def import_block():
        if file_path:
            block_index = int(entry_block_index.get())
            new_block_path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin")])
            if new_block_path:
                try:
                    mar_mgs2.import_new_block(file_path, block_index, new_block_path)
                    messagebox.showinfo("Success", f"Block {block_index} imported successfully.")
                    refresh_mar_display()  # Refresh the GUI
                except ValueError as e:
                        messagebox.showerror("Error", str(e))
                    
    open_button = tk.Button(tab, text="Open MGS2 MAR File", command=open_mar_file)
    open_button.pack(pady=10)
                    
    label_block_index = tk.Label(tab, text="Block Index to Replace:")
    label_block_index.pack()
    entry_block_index = tk.Entry(tab)
    entry_block_index.pack()

    import_button = tk.Button(tab, text="Import Animation Block", command=import_block)
    import_button.pack(pady=10)

    convert_button = tk.Button(tab, text="Convert MGS2 to MGS3", command=convert_mgs2_to_mgs3)
    convert_button.pack(pady=10)



    export_button = tk.Button(tab, text="Export Animation Blocks", command=export_animation_blocks)
    export_button.pack(pady=10)



# Main GUI
root = tk.Tk()
root.title("MTAR GEAR")
style = ttk.Style(root)
style.theme_use('classic')

notebook = ttk.Notebook(root)

# MC MTAR Tab
mc_mtar_tab = ttk.Frame(notebook)
notebook.add(mc_mtar_tab, text="MC MTAR")
setup_mc_mtar_tab(mc_mtar_tab)

# 3DS MTAR Tab
ds_mtar_tab = ttk.Frame(notebook)
notebook.add(ds_mtar_tab, text="3DS MTAR")
setup_3ds_mtar_tab(ds_mtar_tab)

notebook.pack(expand=True, fill="both")

# MTAR Editor Tab
mtar_editor_tab = ttk.Frame(notebook)
notebook.add(mtar_editor_tab, text="MTAR Editor")
setup_mtar_editor_tab(mtar_editor_tab)

# Add the MGS4 MTAR tab
mtar_mgs4_tab = ttk.Frame(notebook)
notebook.add(mtar_mgs4_tab, text="MGS4 MTAR")
setup_mtar_mgs4_tab(mtar_mgs4_tab)

# Add the MGS2 MTAR tab
mar_mgs2_tab = ttk.Frame(notebook)
notebook.add(mar_mgs2_tab, text="MGS2 MAR")
setup_mar_mgs2_tab(mar_mgs2_tab)

root.mainloop()