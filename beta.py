import os
import sys
import typing
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

import amulet_nbt
from leveldb import LevelDB

StructureDict = typing.Dict[str, amulet_nbt.NamedTag]


class StructureExtractorGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Structure Extractor")

        self.worlds_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.structure_id = tk.StringVar(value="all")

        self.force = tk.BooleanVar()
        self.delete = tk.BooleanVar()
        self.behavior_pack = tk.BooleanVar()

        self.world_paths = {}

        self.build_ui()

    def build_ui(self):

        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill="both", expand=True)

        # Worlds folder
        ttk.Label(frame, text="minecraftWorlds folder").grid(row=0, column=0, sticky="w")

        ttk.Entry(frame, textvariable=self.worlds_folder, width=50).grid(row=0, column=1)

        ttk.Button(frame, text="Browse", command=self.select_worlds_folder).grid(row=0, column=2)

        # World dropdown
        ttk.Label(frame, text="World").grid(row=1, column=0, sticky="w")

        self.world_dropdown = ttk.Combobox(frame, state="readonly")
        self.world_dropdown.grid(row=1, column=1, sticky="ew")

        ttk.Button(frame, text="Refresh Worlds", command=self.load_worlds).grid(row=1, column=2)

        # Structure ID
        ttk.Label(frame, text="Structure ID").grid(row=2, column=0, sticky="w")

        ttk.Entry(frame, textvariable=self.structure_id).grid(row=2, column=1, sticky="ew")

        ttk.Label(frame, text='Use "all" to export everything').grid(row=2, column=2)

        # Output folder
        ttk.Label(frame, text="Output Folder").grid(row=3, column=0, sticky="w")

        ttk.Entry(frame, textvariable=self.output_folder, width=50).grid(row=3, column=1)

        ttk.Button(frame, text="Browse", command=self.select_output_folder).grid(row=3, column=2)

        # Options
        ttk.Checkbutton(frame, text="Force overwrite", variable=self.force).grid(row=4, column=0, sticky="w")

        ttk.Checkbutton(frame, text="Delete structures", variable=self.delete).grid(row=4, column=1, sticky="w")

        ttk.Checkbutton(frame, text="Save to behavior pack", variable=self.behavior_pack).grid(row=4, column=2, sticky="w")

        # Extract button
        ttk.Button(frame, text="Extract Structures", command=self.extract_structures).grid(row=5, column=0, columnspan=3, pady=10)

    def select_worlds_folder(self):

        folder = filedialog.askdirectory(title="Select minecraftWorlds folder")

        if folder:
            self.worlds_folder.set(folder)
            self.load_worlds()

    def select_output_folder(self):

        folder = filedialog.askdirectory(title="Select Output Folder")

        if folder:
            self.output_folder.set(folder)

    def load_worlds(self):

        folder = self.worlds_folder.get()

        if not os.path.exists(folder):
            messagebox.showerror("Error", "Invalid minecraftWorlds folder")
            return

        self.world_paths = {}

        for file in os.scandir(folder):
            if file.is_dir():

                name_path = os.path.join(file.path, "levelname.txt")

                if os.path.exists(name_path):

                    with open(name_path) as f:
                        name = f.readline().strip()

                    self.world_paths[name] = file.path

        self.world_dropdown["values"] = list(self.world_paths.keys())

        if self.world_paths:
            self.world_dropdown.current(0)

    def save_structures(self, dir, structures, force):

        for structure_id, nbt in structures.items():

            ns_id, name = structure_id.split(':')
            namespace, *rest = ns_id.split('.')

            folder = '/'.join(rest)

            if not namespace:
                namespace = 'mystructure'

            file_name = name + '.mcstructure'

            path = Path(os.path.join(dir, 'structures', namespace, folder))
            path.mkdir(parents=True, exist_ok=True)

            path = path.joinpath(file_name)

            if path.exists() and not force:
                continue

            with open(path, 'wb') as f:
                nbt.save_to(filepath_or_buffer=f, little_endian=True, compressed=False)

    def extract_structures(self):

        world_name = self.world_dropdown.get()

        if world_name not in self.world_paths:
            messagebox.showerror("Error", "World not found")
            return

        world_path = self.world_paths[world_name]

        output_folder = self.output_folder.get()

        if not output_folder:
            output_folder = world_path

            if self.behavior_pack.get():

                bp_path = os.path.join(world_path, "behavior_packs")

                packs = [f.path for f in os.scandir(bp_path) if f.is_dir()]

                if not packs:
                    messagebox.showerror("Error", "No behavior pack found")
                    return

                output_folder = packs[0]

        structure_id = self.structure_id.get()

        if structure_id != "all" and ":" not in structure_id:
            structure_id = "mystructure:" + structure_id

        db_path = os.path.join(world_path, "db")

        db = LevelDB(db_path)

        structures = {}

        for key, data in db.iterate():

            try:

                key_str = key.decode("ascii")

                if key_str.startswith("structuretemplate_"):

                    sid = key_str[len("structuretemplate_"):]

                    structure = amulet_nbt.load(filepath_or_buffer=data, little_endian=True)

                    structures[sid] = structure

                    if (sid == structure_id or structure_id == "all") and self.delete.get():
                        db.delete(key)

            except:
                pass

        db.close()

        if structure_id == "all":
            filtered = structures
        else:
            filtered = {k: v for k, v in structures.items() if k == structure_id}

        if not filtered:
            messagebox.showinfo("Result", "No structures found")
            return

        self.save_structures(output_folder, filtered, self.force.get())

        messagebox.showinfo("Done", f"Exported {len(filtered)} structure(s)")


if __name__ == "__main__":

    root = tk.Tk()
    app = StructureExtractorGUI(root)
    root.mainloop()