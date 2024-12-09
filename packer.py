import tkinter as tk
from tkinter import filedialog
import zipfile
import json
import os
from typing import Any, Dict, List, Tuple


class Packer:

    ILDX_HEADER_SIZE: int = 32

    _dmx_filename: str | None
    _ildx_filename: str | None
    _fuses_filename: str | None
    _music_filename: str | None

    _dmx_device_ids: List[str]
    _ildx_device_ids: List[str]
    _fuses_device_ids: List[str]
    _music_device_ids: List[str]

    _metadata: Dict[str, Any] | None

    def __init__(self):
        self._dmx_filename = None
        self._ildx_filename = None
        self._fuses_filename = None
        self._music_filename = None

        self._dmx_device_ids = []
        self._ildx_device_ids = []
        self._fuses_device_ids = []
        self._music_device_ids = []

        self._metadata = None

    def _select_file(self, title: str, filetypes: List[Tuple[str, str]]) -> str | None:
        root = tk.Tk()
        root.withdraw()
        root.update()
        filetypes.append(('All files', '*.*'))
        filename = filedialog.askopenfilename(title=title, filetypes=filetypes)
        root.destroy()
        return filename
    
    def _select_save_file(self, title: str, filetypes: List[Tuple[str, str]], defaultextension: str) -> str | None:
        root = tk.Tk()
        root.withdraw()
        root.update()
        filetypes.append(('All files', '*.*'))
        filename = filedialog.asksaveasfilename(title=title, filetypes=filetypes, defaultextension=defaultextension)
        root.destroy()
        return filename

    def _set_dmx_file(self):
        filename = self._select_file(
            'Select DMX file', 
            [('BIN files', '*.bin')]
        )
        if filename:
            self._dmx_filename = filename

    def _set_ildx_file(self):
        filename = self._select_file(
            'Select ILDX file', 
            [('ILDX files', '*.ildx')]
        )
        if filename:
            self._ildx_filename = filename

    def _set_fuses_file(self):
        filename = self._select_file(
            'Select fuses file', 
            [('JSON files', '*.json')]
        )
        if filename:
            self._fuses_filename = filename

    def set_music_file(self):
        filename = self._select_file(
            'Select music file', 
            [('MP3 files', '*.mp3'), ('WAV files', '*.wav')]
        )
        if filename:
            self._music_filename = filename
    
    def _set_device_ids(self):
        if self._fuses_filename:
            fuses_device_ids = set()
            with open(self._fuses_filename, 'r') as f:
                fuses_data = json.load(f)
                for fuse in fuses_data:
                    fuses_device_ids.add(fuse['device_id'])
            self._fuses_device_ids = list(fuses_device_ids)
        if self._ildx_filename:
            print("ILDX Device IDs")
            ildx_device_ids = input("Enter device IDs separated by commas: ")
            self._ildx_device_ids = ildx_device_ids.split(',')
        if self._dmx_filename:
            print("DMX Device IDs")
            dmx_device_ids = input("Enter device IDs separated by commas: ")
            self._dmx_device_ids = dmx_device_ids.split(',')
        if self._music_filename:
            print("Music Device IDs")
            music_device_ids = input("Enter device IDs separated by commas: ")
            self._music_device_ids = music_device_ids.split(',')

    def _build_metadata(self) -> Dict[str, Any]:
        if self._music_filename is None:
            music_filename = None
        elif self._music_filename.endswith('.mp3'):
            music_filename = 'music.mp3'
        elif self._music_filename.endswith('.wav'):
            music_filename = 'music.wav'
        else:
            raise ValueError("Invalid music file format")
        return {
            "music_device_ids": self._music_device_ids,
            "ilda_device_ids": self._ildx_device_ids,
            "dmx_device_ids": self._dmx_device_ids,
            "fuses_device_ids": self._fuses_device_ids,
            "music_filename": music_filename,
            "has_fuses": bool(self._fuses_filename),
            "has_music": bool(self._music_filename),
            "has_ilda": bool(self._ildx_filename),
            "has_dmx": bool(self._dmx_filename)
        }

    def _save(self):
        filename = self._select_save_file(
            'Save as', 
            [('ZIP files', '*.zip')],
            ".zip"
        )
        if not filename:
            return
        
        with zipfile.ZipFile(filename, 'w') as zip_file:
            zip_file.writestr('metadata.json', json.dumps(self._metadata, indent=4))

            if self._music_filename:
                if self._music_filename.endswith('.mp3'):
                    zip_file.write(self._music_filename, 'music.mp3')
                elif self._music_filename.endswith('.wav'):
                    zip_file.write(self._music_filename, 'music.wav')

            if self._dmx_filename:
                zip_file.write(self._dmx_filename, 'dmx.bin')

            if self._fuses_filename:
                fuses_data = []
                with open(self._fuses_filename, 'r') as f:
                    fuses_data.extend(json.load(f))
                zip_file.writestr('fuses.json', json.dumps(fuses_data, indent=4))

            if self._ildx_filename:
                zip_file.write(self._ildx_filename, 'ilda.ildx')


    def _ask_yes_no(self, prompt: str) -> bool:
        answer = ""
        while answer not in ["y", "n"]:
            answer = input(f"{prompt} (yn): ").lower()
        return answer == "y"

    def run(self):
        if self._ask_yes_no("Do you want to add a DMX file?"):
            self._set_dmx_file()

        if self._ask_yes_no("Do you want to add a ILDX file?"):
            self._set_ildx_file()

        if self._ask_yes_no("Do you want to add a fuses file?"):
            self._set_fuses_file()

        if self._ask_yes_no("Do you want to add a music file?"):
            self.set_music_file()

        self._set_device_ids()
        self._metadata = self._build_metadata()
        self._save()


def mainloop():
    packer = Packer()    
    packer.run()                           
    print("Done")    


if __name__ == '__main__':
    mainloop()
