import pdf2image
import pytesseract
from PIL import Image
import openpyxl
import re
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extraer_datos_factura(imagen):
    """Extrae los datos relevantes de la factura a partir de la imagen."""

    texto = pytesseract.image_to_string(imagen, lang='spa')  # OCR con idioma español

    fecha_factura = re.search(r"FECHA\s*(\d{2}\.\d{2}\.\d{4})", texto)
    base_imponible = re.search(r"BASE IMP\.\s*([\d,.]+)", texto)
    porcentaje_iva = re.search(r"% IVA\s*([\d,.]+)", texto)
    cuota_iva = re.search(r"CUOTA\s*([\d,.]+)", texto)
    total_factura = re.search(r"TOTAL FACTURA \(EUR\)\s*([\d,.]+)", texto)

    datos = {
        "Fecha Factura": fecha_factura.group(1) if fecha_factura else None,
        "Base": base_imponible.group(1).replace(",", ".") if base_imponible else None,
        "% I.V.A.": porcentaje_iva.group(1).replace(",", ".") if porcentaje_iva else None,
        "Cuota I.V.A.": cuota_iva.group(1).replace(",", ".") if cuota_iva else None,
        "Total Factura": total_factura.group(1).replace(",", ".") if total_factura else None,
    }
    return datos


def procesar_pdf(pdf_path, nombre_excel="resultados.xlsx"):
    """Procesa el PDF, extrae los datos de cada factura y guarda en Excel."""

    try:
        # Convertir PDF a lista de imágenes
        imagenes = pdf2image.convert_from_path(pdf_path) # Ajusta la ruta a poppler si es necesario

    except pdf2image.exceptions.PDFInfoNotInstalledError as e:
        print(f"Error: Poppler no está instalado o no se encuentra en el PATH.  Por favor, instala Poppler y ajusta el 'poppler_path' en el código.")
        return

    datos_facturas = []

    for i, imagen in enumerate(imagenes):
        print(f"Procesando página {i+1}...")
        datos = extraer_datos_factura(imagen)
        datos_facturas.append(datos)

    # Crear el archivo Excel
    libro = openpyxl.Workbook()
    hoja = libro.active

    # Escribir los encabezados
    encabezados = ["Fecha Factura", "Base", "% I.V.A.", "Cuota I.V.A.", "Total Factura"]
    hoja.append(encabezados)

    # Escribir los datos de las facturas
    for factura in datos_facturas:
        fila = [factura["Fecha Factura"], factura["Base"], factura["% I.V.A."], factura["Cuota I.V.A."], factura["Total Factura"]]
        hoja.append(fila)

    # Guardar el archivo Excel
    libro.save(nombre_excel)
    print(f"Archivo Excel '{nombre_excel}' creado exitosamente.")


if __name__ == "__main__":
    pdf_path = input("Por favor, introduce el nombre del archivo PDF: ")
    pdf_path = "faccsa_1-3.pdf"

    if not os.path.exists(pdf_path):
        print(f"Error: El archivo '{pdf_path}' no existe.")
    else:
        procesar_pdf(pdf_path)
