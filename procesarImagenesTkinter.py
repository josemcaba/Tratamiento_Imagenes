import pdf2image
import pytesseract
from PIL import Image
import openpyxl
import re
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

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


def procesar_pdf(pdf_path, nombre_excel, progress_bar):
    """Procesa el PDF, extrae los datos de cada factura y guarda en Excel."""

    try:
        # Convertir PDF a lista de imágenes
        imagenes = pdf2image.convert_from_path(pdf_path) # Ajusta la ruta a poppler si es necesario

    except pdf2image.exceptions.PDFInfoNotInstalledError as e:
        messagebox.showerror("Error", "Poppler no está instalado o no se encuentra en el PATH.  Por favor, instala Poppler y ajusta el 'poppler_path' en el código.")
        return

    datos_facturas = []
    total_paginas = len(imagenes)

    for i, imagen in enumerate(imagenes):
        print(f"Procesando página {i+1}...")
        datos = extraer_datos_factura(imagen)
        datos_facturas.append(datos)
        progress_bar['value'] = (i + 1) / total_paginas * 100  # Actualizar barra de progreso
        root.update_idletasks() # Forzar la actualización de la GUI

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
    messagebox.showinfo("Éxito", f"Archivo Excel '{nombre_excel}' creado exitosamente.")
    progress_bar['value'] = 0  # Resetear barra de progreso


def seleccionar_pdf():
    """Abre un diálogo para seleccionar el archivo PDF."""
    global pdf_path
    pdf_path = filedialog.askopenfilename(filetypes=[("Archivos PDF", "*.pdf")])
    pdf_entry.delete(0, tk.END)
    pdf_entry.insert(0, pdf_path)

def seleccionar_excel():
    """Abre un diálogo para seleccionar el nombre del archivo Excel de salida."""
    global excel_path
    excel_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Archivos Excel", "*.xlsx")])
    excel_entry.delete(0, tk.END)
    excel_entry.insert(0, excel_path)


def iniciar_proceso():
    """Inicia el proceso de extracción y creación del archivo Excel."""
    global pdf_path, excel_path

    pdf_path = pdf_entry.get()
    excel_path = excel_entry.get()

    if not pdf_path:
        messagebox.showerror("Error", "Por favor, selecciona un archivo PDF.")
        return

    if not excel_path:
         excel_path = "resultados.xlsx" # Valor por defecto si no se selecciona nombre

    if not os.path.exists(pdf_path):
        messagebox.showerror("Error", f"El archivo '{pdf_path}' no existe.")
        return

    procesar_pdf(pdf_path, excel_path, progress_bar)


# --- Configuración de la interfaz gráfica ---
root = tk.Tk()
root.title("Extractor de Facturas PDF")

# PDF File Selection
pdf_label = tk.Label(root, text="Archivo PDF:")
pdf_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

pdf_path = ""  # Variable para almacenar la ruta del PDF
pdf_entry = tk.Entry(root, width=50)
pdf_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

pdf_button = tk.Button(root, text="Seleccionar PDF", command=seleccionar_pdf)
pdf_button.grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)

# Excel File Selection
excel_label = tk.Label(root, text="Archivo Excel de Salida:")
excel_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

excel_path = "" # Variable para almacenar la ruta del Excel
excel_entry = tk.Entry(root, width=50)
excel_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

excel_button = tk.Button(root, text="Seleccionar Excel", command=seleccionar_excel)
excel_button.grid(row=1, column=2, padx=10, pady=5, sticky=tk.W)


# Process Button
process_button = tk.Button(root, text="Iniciar Proceso", command=iniciar_proceso)
process_button.grid(row=2, column=1, padx=10, pady=10)

# Progress Bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.grid(row=3, column=0, columnspan=3, padx=10, pady=10)


root.mainloop()