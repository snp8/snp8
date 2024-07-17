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
    img_byte_arr.seek(0)
    
    exif_img = ExifImage(img_byte_arr)
    exif_dict = {tag: getattr(exif_img, tag, None) for tag in exif_img.list_all()}
    return exif_dict, exif_img

def update_exif(exif_img, field, value):
    try:
        if isinstance(getattr(exif_img, field, None), bytes):
            value = value.encode()
        setattr(exif_img, field, value)
    except Exception as e:
        st.error(f"Erreur lors de la mise à jour de {field}: {e}")
    return exif_img

st.title("Éditeur de métadonnées EXIF")

# Téléchargement de l'image
image_file = st.file_uploader("Téléchargez une image", type=["jpg", "jpeg"])

if image_file:
    img = load_image(image_file)
    st.image(img, caption='Image téléchargée', use_column_width=True)

    try:
        exif_dict, exif_img = get_exif_dict(img)
        if not exif_dict:
            st.write("Aucune métadonnée EXIF trouvée.")
        else:
            st.write("Métadonnées EXIF actuelles :")
            st.json(exif_dict)
    except Exception as e:
        st.error(f"Erreur lors de l'extraction des métadonnées EXIF: {e}")

    # Formulaire pour éditer les métadonnées
    st.header("Modifier les métadonnées EXIF")

    updated_exif_img = exif_img

    if exif_dict:
        for field, value in exif_dict.items():
            new_value = st.text_input(f"{field}:", str(value))
            if new_value and new_value != str(value):
                try:
                    if isinstance(value, int):
                        new_value = int(new_value)
                    elif isinstance(value, float):
                        new_value = float(new_value)
                    updated_exif_img = update_exif(updated_exif_img, field, new_value)
                except ValueError:
                    st.error(f"Valeur incorrecte pour {field}")

    if st.button("Sauvegarder les modifications"):
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
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

