import ft_comunes_img as fci
import cv2

# Variables globales
windowName = "Factura"
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
            cv2.imshow(windowName, img_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        fx, fy = x, y
        fx=img.shape[1] if (fx > img.shape[1]) else fx
        fy=img.shape[0] if (fy > img.shape[0]) else fy
        cv2.rectangle(img, (ix, iy), (fx, fy), (255, 0, 255), 5)  # Grosor del borde aumentado
        cv2.imshow(windowName, img)
        print(f"Rectángulo desde: ({ix}, {iy}) hasta ({fx}, {fy})")

        # Guardar las coordenadas del rectángulo en el diccionario con una clave única
        key = f"rectangulo_{rectangle_counter}"
        rectangles[key] = {"x1": ix, "y1": iy, "x2": fx, "y2": fy}
        rectangle_counter += 1  # Incrementar el contador

def main(pdf_path):
    global img, rectangles

    nif = input("Introduzca NIF del emisor de la factura: ")

    # Extraer la imagen del PDF
    img = fci.extract_first_image_from_pdf(pdf_path)
    if img is None:
        print("No se encontró ninguna imagen en el PDF.")
        return

    # Mostrar la imagen en una ventana
    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
    fci.adjust_window_size(windowName, img)
    cv2.setMouseCallback(windowName, draw_rectangle)
    fci.mostrar_imagen(windowName, img)

    # Guardar las coordenadas de los rectángulos en un archivo JSON
    json_path = "rectangles.json"
    fci.save_rectangles_to_json(json_path, nif, rectangles)

if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     print("Uso: python mostrar_imagen_pdf.py <archivo_pdf>")
    # else:
    #     main(sys.argv[1])
    main("faccsa_1-3.pdf")
