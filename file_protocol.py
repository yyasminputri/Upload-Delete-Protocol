import json
import logging
import shlex
from file_interface import FileInterface

class FileProtocol:
    def __init__(self):
        self.file = FileInterface()

    def proses_string(self, string_datamasuk=''):
        logging.warning(f"string diproses: {string_datamasuk}")
        try:
            c = shlex.split(string_datamasuk)
            c_request = c[0].strip().lower()  # Mengubah perintah menjadi huruf kecil
            logging.warning(f"memproses request: {c_request}")
            params = c[1:]
            logging.warning(f"params: {params}")
            cl = getattr(self.file, c_request)(params)
            return json.dumps(cl)
        except Exception as e:
            logging.error(f"Error: {e}")
            return json.dumps(dict(status='ERROR', data=str(e)))