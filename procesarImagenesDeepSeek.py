import pytesseract
from pdf2image import convert_from_path
import pandas as pd
import cv2
import re
import os
import numpy as np

# Configura la ruta de Tesseract si es necesario
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_invoice_data(text):
    # Expresiones regulares para extraer los datos
    fecha_regex = r"FECHA (\d{2}\.\d{2}\.\d{4})"
    base_regex = r"BASE IMPONIB\. (\d+,\d{2})"
    iva_percent_regex = r"% IVA (\d+,\d{2})"
    iva_cuota_regex = r"TOTAL IVA (\d+,\d{2})"
    total_regex = r"TOTAL (\d+,\d{2})"

    fecha = re.search(fecha_regex, text)
    base = re.search(base_regex, text)
    iva_percent = re.search(iva_percent_regex, text)
    iva_cuota = re.search(iva_cuota_regex, text)
    total = re.search(total_regex, text)

    return {
        "Fecha factura": fecha.group(1) if fecha else None,
        "Base": base.group(1) if base else None,
        "% I.V.A.": iva_percent.group(1) if iva_percent else None,
        "Cuota I.V.A.": iva_cuota.group(1) if iva_cuota else None,
        "Total Factura": total.group(1) if total else None,
    }

def process_pdf(pdf_path):
    # Lista para almacenar los datos de las facturas
    invoices_data = []

    # Archivo de texto para guardar todo el texto extraído
    output_text_file = "texto_extraido.txt"
    with open(output_text_file, "w", encoding="utf-8") as text_file:
        # Convertir PDF a imágenes una por una
        for page_number, image in enumerate(convert_from_path(pdf_path), start=1):
            print(f"Procesando página {page_number}...")

            # Convertir la imagen a escala de grises usando numpy
            gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)

            # Aplicar OCR a la imagen
            text = pytesseract.image_to_string(gray_image, lang='spa')

            # Guardar el texto extraído en el archivo de texto
            text_file.write(f"=== Página {page_number} ===\n")
            text_file.write(text)
            text_file.write("\n\n")

            # Extraer los datos de la factura
            invoice_data = extract_invoice_data(text)
            invoices_data.append(invoice_data)

    print(f"Texto extraído guardado en {output_text_file}")
    return invoices_data

def main():
    # Solicitar el nombre del archivo PDF al usuario
    pdf_path = input("Introduce el nombre del archivo PDF: ")

    if not os.path.exists(pdf_path):
        print("El archivo no existe.")
        return

    # Procesar el PDF y extraer los datos
    invoices_data = process_pdf(pdf_path)

    # Crear un DataFrame con los datos
    df = pd.DataFrame(invoices_data)

    # Guardar el DataFrame en un archivo Excel
    output_excel = "facturas.xlsx"
    df.to_excel(output_excel, index=False)

    print(f"Datos estructurados guardados en {output_excel}")

if __name__ == "__main__":
    main()
