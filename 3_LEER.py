import ft_comunes_img as fci
import cv2
import numpy as np
import fitz  # PyMuPDF
import pytesseract  # OCR
from PIL import Image  # Para convertir imágenes a formato compatible con pytesseract


# Configura la ruta de Tesseract-OCR (ajusta según tu instalación)
# Si Tesseract está en el PATH, no es necesario configurar esto.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def correct_text_orientation(image):
    ''' Obtener la orientación del texto usando Tesseract 
        ¡¡¡¡¡¡ Parece que no hace nada !!!!!!
    '''
    osd = pytesseract.image_to_osd(image)
    rotation_angle = int(osd.split("\n")[1].split(": ")[1])
    print("ANGULO:", rotation_angle)
    
    # Rotar la imagen para corregir la orientación
    if rotation_angle != 0:
        image = image.rotate(rotation_angle, expand=True)
    
    return image

# Función para preprocesar la imagen antes de aplicar OCR
def preprocess_image(image):
    # Verificar el número de canales de la imagen
    if len(image.shape) == 2:  # La imagen ya está en escala de grises (1 canal)
        gray = image
    elif len(image.shape) == 3:  # La imagen tiene 3 canales (BGR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        raise ValueError("La imagen no tiene un formato válido (1 o 3 canales).")

    # Aplicar un desenfoque para reducir el ruido
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Aplicar umbralización (binarización)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Opcional: Ajustar el contraste y el brillo
    alpha = 1.5  # Control de contraste (1.0 es neutral)
    beta = 0     # Control de brillo (0 es neutral)
    adjusted = cv2.convertScaleAbs(binary, alpha=alpha, beta=beta)

    return adjusted

# Función para ajustar la resolución de la imagen
def adjust_resolution(image, target_dpi=300):
    # Calcular el factor de escala para alcanzar el DPI objetivo
    height, width = image.shape[:2]
    scale_factor = target_dpi / 70  # 70 es el DPI predeterminado que Tesseract asume
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    
    # Redimensionar la imagen
    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
    return resized_image

# Función para verificar si la imagen tiene suficiente texto
def has_enough_text(image, min_text_area=100):
    # Verificar el número de canales de la imagen
    if len(image.shape) == 2:  # La imagen ya está en escala de grises (1 canal)
        gray = image
    elif len(image.shape) == 3:  # La imagen tiene 3 canales (BGR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        raise ValueError("La imagen no tiene un formato válido (1 o 3 canales).")

    # Aplicar umbralización (binarización)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Calcular el área de píxeles blancos (texto)
    text_area = cv2.countNonZero(binary)
    return text_area > min_text_area

# Función para aplicar OCR a una imagen
def extract_text_from_image(image):
    # Preprocesar la imagen
    processed_image = preprocess_image(image)
    processed_image = image

    # Ajustar la resolución
    # processed_image = adjust_resolution(processed_image)
    
    # Verificar si la imagen tiene suficiente texto
    if not has_enough_text(processed_image):
        return ""  # Si no hay suficiente texto, devolver una cadena vacía
    
    # Convertir la imagen de OpenCV a formato PIL
    pil_image = Image.fromarray(processed_image)
    
    # Aplicar OCR con configuración personalizada
    custom_config = r'--psm 6 -l spa'  # Modo 11 para texto disperso, idioma español
    text = pytesseract.image_to_string(pil_image, config=custom_config)

    return text

# Función principal
def extract_text_from_pdf_regions(pdf_path, json_path, output_txt_path):
    nif = input("Introduzca NIF del emisor de la factura: ")
    # Cargar las coordenadas desde el archivo JSON
    rectangles = fci.load_rectangles_from_json(json_path, nif)

    # Abrir el PDF
    doc = fitz.open(pdf_path)
    if not doc:
        return None
    total_pages = len(doc)

    # Variable para almacenar todo el texto extraído
    full_text = ""

    # Recorrer todas las páginas del PDF
    for page_num in range(total_pages):
        print(f"Procesando página {page_num + 1} de {total_pages}")

        img = doc.get_page_images(page_num)[0]
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)

        # Verificar la orientación de la imagen y rotarla si es necesario
        if image.shape[0] < image.shape[1]:  # Si la altura es menor que el ancho, rotar 90 grados
            image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # Recortar y mostrar cada trozo de imagen según las coordenadas del JSON
        for key, coords in rectangles.items():
            x1, y1 = coords["x1"], coords["y1"]
            x2, y2 = coords["x2"], coords["y2"]
            cropped_image = image[y1:y2, x1:x2]  # Recortar la región de la imagen

            # Aplicar OCR a la imagen recortada
            text = extract_text_from_image(cropped_image)
            full_text += f"--- Página {page_num + 1}, {key} ---\n{text}\n"

            # Mostrar la imagen recortada en una ventana
            # print(text)
            # window_name = f"Pagina {page_num + 1}, {key}"
            # cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            # fci.adjust_window_size(window_name, cropped_image)
            # fci.mostrar_imagen(window_name, cropped_image, 1)

    # Guardar el texto extraído en un archivo de texto
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"Texto extraído guardado en {output_txt_path}")

# Ejecución del programa
if __name__ == "__main__":
    # if len(sys.argv) != 4:
    #     print("Uso: python extraer_texto.py <archivo_pdf> <archivo_json> <archivo_salida.txt>")
    # else:
    #     pdf_path = sys.argv[1]
    #     json_path = sys.argv[2]
    #     output_txt_path = sys.argv[3]
    #     extract_text_from_pdf_regions(pdf_path, json_path, output_txt_path)
    extract_text_from_pdf_regions("faccsa.pdf", "rectangles.json", "texto.txt")