import streamlit as st
from PIL import Image
from exif import Image as ExifImage
import io

def load_image(image_file):
    img = Image.open(image_file)
    return img

def get_exif_dict(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    
    exif_img = ExifImage(img_byte_arr)
    exif_dict = {tag: getattr(exif_img, tag, None) for tag in exif_img.list_all()}

    return exif_dict, exif_img

def update_exif(exif_img, field, value):
    setattr(exif_img, field, value)
    return exif_img

st.title("Éditeur de métadonnées EXIF")

# Téléchargement de l'image
image_file = st.file_uploader("Téléchargez une image", type=["jpg", "jpeg"])

if image_file:
    img = load_image(image_file)
    st.image(img, caption='Image téléchargée', use_column_width=True)

    exif_dict, exif_img = get_exif_dict(img)

    st.write("Métadonnées EXIF actuelles :")
    st.json(exif_dict)

    # Formulaire pour éditer les métadonnées
    st.header("Modifier les métadonnées EXIF")

    updated_exif_img = exif_img

    for field, value in exif_dict.items():
        new_value = st.text_input(f"{field}:", str(value))
        if new_value:
            try:
                if isinstance(value, int):
                    new_value = int(new_value)
                elif isinstance(value, float):
                    new_value = float(new_value)
                elif isinstance(value, bytes):
                    new_value = new_value.encode()
            except ValueError:
                pass
            updated_exif_img = update_exif(updated_exif_img, field, new_value)

    if st.button("Sauvegarder les modifications"):
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        with open("edited_image.jpg", "wb") as edited_image_file:
            edited_image_file.write(updated_exif_img.get_file())

        st.success("Métadonnées mises à jour et image enregistrée sous 'edited_image.jpg'")

        # Afficher le lien pour télécharger l'image éditée
        with open("edited_image.jpg", "rb") as file:
            btn = st.download_button(
                label="Télécharger l'image modifiée",
                data=file,
                file_name="edited_image.jpg",
                mime="image/jpeg"
            )

