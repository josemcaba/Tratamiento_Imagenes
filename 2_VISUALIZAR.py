import ft_comunes_img as fci
import cv2
import numpy as np
import fitz  # PyMuPDF

# Función para mostrar los trozos de imagen según las coordenadas del JSON
def show_cropped_images(pdf_path, json_path):
    nif = input("Introduzca NIF del emisor de la factura: ")
    
    rectangles = fci.load_rectangles_from_json(json_path, nif)

    # Abrir el PDF
    doc = fitz.open(pdf_path)
    if not doc:
        return None
    total_pages = len(doc)

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

            # Mostrar la imagen recortada en una ventana
            window_name = f"Pagina {page_num + 1}, {key}"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            fci.adjust_window_size(window_name, cropped_image)
            fci.mostrar_imagen(window_name, cropped_image)

# Función principal
if __name__ == "__main__":
    # if len(sys.argv) != 3:
    #     print("Uso: python mostrar_trozos.py <archivo_pdf> <archivo_json>")
    # else:
    #     pdf_path = sys.argv[1]
    #     json_path = sys.argv[2]
    #     show_cropped_images(pdf_path, json_path)
    show_cropped_images("faccsa_1-3.pdf", "rectangles.json")
