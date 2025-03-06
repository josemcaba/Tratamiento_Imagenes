import cv2
import fitz  # PyMuPDF
import numpy as np
import json

# Variables globales
drawing = False
ix, iy = -1, -1
fx, fy = -1, -1
rectangles = {}  # Diccionario para almacenar las coordenadas de los rectángulos
rectangle_counter = 1  # Contador para generar claves únicas

# Función para manejar los eventos del ratón
def draw_rectangle(event, x, y, flags, param):
    global ix, iy, fx, fy, drawing, img, rectangles, rectangle_counter

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        print(f"Click en: ({ix}, {iy})")

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = img.copy()
            cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 5)  # Grosor del borde aumentado
            cv2.imshow("Imagen", img_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        fx, fy = x, y
        fx=img.shape[1] if (fx > img.shape[1]) else fx
        fy=img.shape[0] if (fy > img.shape[0]) else fy
        cv2.rectangle(img, (ix, iy), (fx, fy), (255, 0, 255), 5)  # Grosor del borde aumentado
        cv2.imshow("Imagen", img)
        print(f"Rectángulo dibujado desde: ({ix}, {iy}) hasta ({fx}, {fy})")

        # Guardar las coordenadas del rectángulo en el diccionario con una clave única
        key = f"rectangulo_{rectangle_counter}"
        rectangles[key] = {"x1": ix, "y1": iy, "x2": fx, "y2": fy}
        rectangle_counter += 1  # Incrementar el contador

# Función para extraer la imagen del PDF
def extract_image_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    for i in range(len(doc)):
        for img in doc.get_page_images(i):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)

            # Verificar la orientación de la imagen y rotarla si es necesario
            if image.shape[0] < image.shape[1]:  # Si la altura es menor que el ancho, rotar 90 grados
                image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            return image
    return None

# Función para guardar las coordenadas en un archivo JSON
def save_rectangles_to_json(rectangles, json_path):
    with open(json_path, "w") as f:
        json.dump(rectangles, f, indent=4)
    print(f"Coordenadas guardadas en {json_path}")

# Función principal
def main(pdf_path):
    global img, rectangles

    # Extraer la imagen del PDF
    img = extract_image_from_pdf(pdf_path)
    if img is None:
        print("No se encontró ninguna imagen en el PDF.")
        return

    # Mostrar la imagen en una ventana
    cv2.namedWindow("Imagen", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Imagen", draw_rectangle)

    # Ajustar el tamaño de la ventana al máximo posible
    cv2.imshow("Imagen", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Guardar las coordenadas de los rectángulos en un archivo JSON
    json_path = "rectangles.json"
    save_rectangles_to_json(rectangles, json_path)

if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     print("Uso: python mostrar_imagen_pdf.py <archivo_pdf>")
    # else:
    #     main(sys.argv[1])
    main("faccsa_1-3.pdf")
