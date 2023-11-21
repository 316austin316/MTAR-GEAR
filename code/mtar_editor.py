import struct
import tkinter as tk
from tkinter import filedialog, Tk, Button, Text, END, Label, Entry, messagebox, ttk

class MtcmHeader:
    def __init__(self, data):
        # Unpack each field sequentially
        self.name = struct.unpack_from('<I', data, 0)[0]
        self.flags = struct.unpack_from('<I', data, 4)[0]
        self.baseTick = struct.unpack_from('<I', data, 8)[0]
        self.numFrames = struct.unpack_from('<I', data, 12)[0]
        self.archiveOffset = struct.unpack_from('<I', data, 16)[0]
        self.archiveSize = struct.unpack_from('<I', data, 20)[0]
        self.numJoints = struct.unpack_from('<I', data, 24)[0]
        self.bitCheck0 = struct.unpack_from('<I', data, 28)[0]
        self.bitCheck1 = struct.unpack_from('<I', data, 32)[0]
        self.bitCheck2 = struct.unpack_from('<I', data, 36)[0]
        self.bitCheck3 = struct.unpack_from('<I', data, 40)[0]
        self.quatLowBit = struct.unpack_from('<B', data, 44)[0]
        self.quatHighBit = struct.unpack_from('<B', data, 45)[0]
        self.indiciesOffset = struct.unpack_from('<H', data, 46)[0]
        self.rootOffset = struct.unpack_from('<I', data, 48)[0]
        self.moveOffset = struct.unpack_from('<I', data, 52)[0]
        self.turnOffset = struct.unpack_from('<I', data, 56)[0]
        self.fixOffset = struct.unpack_from('<I', data, 60)[0]
        # Note: quatOffset is not included because its size is dynamic

        


def read_mtcm_header(file_path):
    with open(file_path, 'rb') as file:
        header_data = file.read(64)  # Reading the first 64 bytes for the header
        return MtcmHeader(header_data)


def display_block_info(mtcm_header, info_text_widget):
    info_text_widget.delete("1.0", tk.END)
    info = f"""
    Name: {mtcm_header.name}
    Flags: {mtcm_header.flags}
    Base Tick: {mtcm_header.baseTick}
    Number of Frames: {mtcm_header.numFrames}
    Archive Offset: {mtcm_header.archiveOffset}
    Archive Size: {mtcm_header.archiveSize}
    Number of Joints: {mtcm_header.numJoints}
    Bit Checks: {mtcm_header.bitCheck0}, {mtcm_header.bitCheck1}, {mtcm_header.bitCheck2}, {mtcm_header.bitCheck3}
    Quat Low/High Bits: {mtcm_header.quatLowBit}, {mtcm_header.quatHighBit}
    Indicies Offset: {mtcm_header.indiciesOffset}
    Root Offset: {mtcm_header.rootOffset}
    Move Offset: {mtcm_header.moveOffset}
    Turn Offset: {mtcm_header.turnOffset}
    Fix Offset: {mtcm_header.fixOffset}
    """
    info_text_widget.insert(tk.END, info)

def update_num_frames(file_path, new_num_frames):
    with open(file_path, 'r+b') as file:
        file.seek(12)
        file.write(struct.pack('<I', new_num_frames))
        
def update_num_joints(file_path, new_num_joints):
    with open(file_path, 'r+b') as file:
        file.seek(24)
        file.write(struct.pack('<I', new_num_joints))
