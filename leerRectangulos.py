import cv2
import json
import numpy as np
import fitz  # PyMuPDF
import pytesseract  # OCR
from PIL import Image  # Para convertir imágenes a formato compatible con pytesseract
import sys

# Configura la ruta de Tesseract-OCR (ajusta según tu instalación)
# Si Tesseract está en el PATH, no es necesario configurar esto.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Función para extraer todas las imágenes del PDF
def extract_images_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    images = []  # Lista para almacenar las imágenes de todas las páginas

    for i in range(len(doc)):
        page_images = []
        for img in doc.get_page_images(i):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)

            # Verificar la orientación de la imagen y rotarla si es necesario
            if image.shape[0] < image.shape[1]:  # Si la altura es menor que el ancho, rotar 90 grados
                image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            page_images.append(image)
        images.append(page_images)
    return images

# Función para cargar las coordenadas desde un archivo JSON
def load_rectangles_from_json(json_path):
    with open(json_path, "r") as f:
        rectangles = json.load(f)
    return rectangles

def mostrar_imagen(window_name, image):
    ''' Mostrar la imagen recortada en una ventana '''
    return
    cv2.imshow(window_name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

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
    mostrar_imagen("Original", image)

    # Verificar el número de canales de la imagen
    if len(image.shape) == 2:  # La imagen ya está en escala de grises (1 canal)
        gray = image
    elif len(image.shape) == 3:  # La imagen tiene 3 canales (BGR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        raise ValueError("La imagen no tiene un formato válido (1 o 3 canales).")
    mostrar_imagen("Escala de grises", gray)

    # Aplicar un desenfoque para reducir el ruido
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    mostrar_imagen("Blurred", blurred)

    # Aplicar umbralización (binarización)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    mostrar_imagen("Binary", binary)

    # Opcional: Ajustar el contraste y el brillo
    alpha = 1.5  # Control de contraste (1.0 es neutral)
    beta = 0     # Control de brillo (0 es neutral)
    adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    mostrar_imagen("Contraste y brillo", adjusted)

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
    
    # Ajustar la resolución
    processed_image = adjust_resolution(processed_image)
    
    # Verificar si la imagen tiene suficiente texto
    if not has_enough_text(processed_image):
        return ""  # Si no hay suficiente texto, devolver una cadena vacía
    
    # Convertir la imagen de OpenCV a formato PIL
    pil_image = Image.fromarray(processed_image)
    
    # Aplicar OCR con configuración personalizada
    custom_config = r'--psm 11 -l spa'  # Modo 6 para bloques de texto, idioma español
    text = pytesseract.image_to_string(pil_image, config=custom_config)
    print(text)
    return text

# Función principal
def extract_text_from_pdf_regions(pdf_path, json_path, output_txt_path):
    # Extraer todas las imágenes del PDF
    all_page_images = extract_images_from_pdf(pdf_path)
    if not all_page_images:
        print("No se encontraron imágenes en el PDF.")
        return

    # Cargar las coordenadas desde el archivo JSON
    rectangles = load_rectangles_from_json(json_path)

    # Variable para almacenar todo el texto extraído
    full_text = ""

    # Recorrer todas las páginas y sus imágenes
    for page_num, page_images in enumerate(all_page_images):
        for img_num, image in enumerate(page_images):
            print(f"Procesando pagina {page_num + 1}, imagen {img_num + 1}")

            # Recortar y aplicar OCR a cada trozo de imagen según las coordenadas del JSON
            for key, coords in rectangles.items():
                x1, y1 = coords["x1"], coords["y1"]
                x2, y2 = coords["x2"], coords["y2"]
                cropped_image = image[y1:y2, x1:x2]  # Recortar la región de la imagen

                # Aplicar OCR al trozo de imagen
                text = extract_text_from_image(cropped_image)
                full_text += f"--- Pagina {page_num + 1}, {key} ---\n{text}\n\n"

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
    extract_text_from_pdf_regions("faccsa_1-3.pdf", "rectangles.json", "texto.txt")