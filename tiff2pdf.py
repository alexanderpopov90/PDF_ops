from PIL import Image, TiffImagePlugin
import os
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import tempfile 

class TiffToPdfConverter:
    def __init__(self, directory:str, outputPath:str='_out'):
        self.directory = directory
        self.subfolder = outputPath

    def is_tiff(self, filename):
        return filename.lower().endswith('.tif') or filename.lower().endswith('.tiff')

    def extract_file_info(self, filename):
        match = re.match(r'(\d+)_\d+_(f\d+)_(.+?)\.TIF{1,2}', filename, re.IGNORECASE)
        if match:
            return match.group(1), int(match.group(2)[1:]), match.group(3)
        return None, None, None

    def tiffs_to_pdf(self, tiff_paths, pdf_path):
        # Wenn tiff_paths eine Liste ist, iteriere über jeden Dateipfad
        if isinstance(tiff_paths, list):
            c = canvas.Canvas(pdf_path, pagesize=letter)
            for tiff_file in tiff_paths:
                self._convert_tiff_to_pdf(tiff_file, pdf_path, c)
            c.save()
        # Wenn tiff_paths ein einzelner Dateipfad ist, rufe die _convert_tiff_to_pdf Methode direkt auf
        else:
            c = canvas.Canvas(pdf_path, pagesize=letter)
            self._convert_tiff_to_pdf(tiff_paths, pdf_path, c)
            c.save()

    def _convert_tiff_to_pdf(self, tiff_file, pdf_path, c):
        tiff_images = TiffImagePlugin.TiffImageFile(tiff_file)
        
        width, height = letter
        with tempfile.TemporaryDirectory() as temp_dir:
            for i in range(tiff_images.n_frames): # eine Tiff kann subImages haben. Wird hier abgefangen.
                tiff_images.seek(i)
                image = tiff_images.copy()
                temp_image_path = os.path.join(temp_dir, f"temp_image_{i}.png")
                image.save(temp_image_path)
                c.setPageSize((image.width, image.height))
                c.drawImage(temp_image_path, 0, 0)
                c.showPage()
        

    def convert(self):
        tiff_files = [f for f in os.listdir(self.directory) if self.is_tiff(f)]
        directory = os.path.join(self.directory, self.subfolder)
        self.create_directory_if_not_exists(directory)
        if not tiff_files:
            print("No TIFF files found.")
            return

        tiff_groups = {}
        for tiff_file in tiff_files:
            identifier, page_num, title = self.extract_file_info(tiff_file)
            if identifier:
                if identifier not in tiff_groups:
                    tiff_groups[identifier] = []
                tiff_groups[identifier].append((page_num, title, tiff_file))

        for identifier in tiff_groups:
            tiff_groups[identifier].sort(key=lambda x: x[0])  # Sortiere nach Seitennummer
            sorted_files = [os.path.join(self.directory, f) for _, _, f in tiff_groups[identifier]]
            title = tiff_groups[identifier][0][1]  # Verwende den Titel des ersten Eintrags
            output_pdf = os.path.join(self.directory, "_out", f"{identifier}_{title}_output.pdf")
            self.tiffs_to_pdf(sorted_files, output_pdf)
            print(f"Created PDF: {output_pdf}")

    def create_directory_if_not_exists(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Directory '{directory}' created.")

if __name__ == "__main__":
    directory = r"C:\Users\popov\Documents\Python\PDF_ops\tmp_docs"
    converter = TiffToPdfConverter(directory)
    converter.convert()


# tiff_paths = ["10228747_101_f0_TITEL_BESTANDSDOKUMENT.TIF", "10228747_101_f1_TITEL_BESTANDSDOKUMENT.TIF", "10228747_101_f2_TITEL_BESTANDSDOKUMENT.TIF"]
# pdf_path = "10228747_101_f0_TITEL_BESTANDSDOKUMENT.pdf"
# tiffs_to_pdf(tiff_paths, pdf_path)
