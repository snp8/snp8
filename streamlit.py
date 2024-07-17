import streamlit as st
from PIL import Image

def load_image(image_file):
    img = Image.open(image_file)
    return img

def get_exif_dict(image):
    try:
        exif_data = image.getexif()
        if exif_data:
            exif_dict = {Image.TAGS.get(tag, tag): value for tag, value in exif_data.items()}
        else:
            exif_dict = {}
    except Exception as e:
        st.error(f"Erreur lors de l'extraction des métadonnées EXIF : {e}")
        exif_dict = {}
    
    return exif_dict

def update_exif(image, exif_dict):
    try:
        exif_data = {tag: value for tag, value in exif_dict.items()}
        image.save("edited_image.jpg", exif=exif_data)
        st.success("Métadonnées mises à jour et image enregistrée sous 'edited_image.jpg'")
        
        return True
    except Exception as e:
        st.error(f"Erreur lors de la mise à jour des métadonnées EXIF : {e}")
        return False

st.title("Éditeur de métadonnées EXIF")

# Téléchargement de l'image
image_file = st.file_uploader("Téléchargez une image", type=["jpg", "jpeg"])

if image_file:
    img = load_image(image_file)
    st.image(img, caption='Image téléchargée', use_column_width=True)

    exif_dict = get_exif_dict(img)

    st.write("Métadonnées EXIF actuelles :")
    st.json(exif_dict)

    # Formulaire pour éditer les métadonnées
    st.header("Modifier les métadonnées EXIF")

    updated_exif_dict = exif_dict.copy()

    for tag, value in exif_dict.items():
        new_value = st.text_input(f"{tag}:", str(value))
        if new_value != str(value):
            updated_exif_dict[tag] = new_value

    if st.button("Sauvegarder les modifications"):
        if update_exif(img, updated_exif_dict):
            # Afficher le lien pour télécharger l'image éditée
            with open("edited_image.jpg", "rb") as file:
                btn = st.download_button(
                    label="Télécharger l'image modifiée",
                    data=file,
                    file_name="edited_image.jpg",
                    mime="image/jpeg"
                )

