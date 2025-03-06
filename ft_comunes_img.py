import fitz  # Módulo PyMuPDF
import cv2
import numpy as np
import json
from screeninfo import get_monitors

def extract_first_image_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    if not doc:
        return None
    # for img in doc.get_page_images(0):
    img = doc.get_page_images(0)[0]
    xref = img[0]
    base_image = doc.extract_image(xref)
    image_bytes = base_image["image"]
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)

    # Verificar la orientación de la imagen y rotarla si es necesario
    if image.shape[0] < image.shape[1]:  # Si la altura es menor que el ancho, rotar 90 grados
        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return image

def save_rectangles_to_json(json_path, nif, rectangles):
    coords = {nif: rectangles}
    with open(json_path, "w") as f:
        json.dump(coords, f, indent=4)
    print(f"Coordenadas guardadas en {json_path}")

def load_rectangles_from_json(json_path, nif):
    with open(json_path, "r") as f:
        coords = json.load(f)
    rectangles = coords[nif]
    return rectangles

def get_screen_resolution():
    width = 1440 # Resolución predeterminada si no se detecta el monitor
    height = 900 # Resolución predeterminada si no se detecta el monitor
    monitors = get_monitors()
    if monitors:
        for monitor in monitors:
            width = monitor.width if monitor.width < width else width
            height = monitor.height if monitor.height < height else height
    return width, height

def adjust_window_size(windowName, image):
    screen_width, screen_height = get_screen_resolution()
    img_height, img_width = image.shape[:2]

    # Factor de escala para imagen ajustada a la pantalla
    scale_width = screen_width / img_width
    scale_height = screen_height / img_height
    scale = 0.9 * min(scale_width, scale_height)
    scale = 1.0 if scale > 1.0 else scale

    new_width = int(img_width * scale)
    new_height = int(img_height * scale)
    
    cv2.resizeWindow(windowName, new_width, new_height)

def mostrar_imagen(window_name, image):
    ''' Mostrar la imagen en una ventana '''
    cv2.imshow(window_name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()