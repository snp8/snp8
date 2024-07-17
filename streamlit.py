import streamlit as st
from PIL import Image
import piexif
import io

def load_image(image_file):
    img = Image.open(image_file)
    return img

def get_exif_dict(image):
    exif_bytes = image.info.get('exif', None)
    if exif_bytes:
        exif_dict = piexif.load(exif_bytes)
    else:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}
    return exif_dict

def exif_dict_to_bytes(exif_dict):
    return piexif.dump(exif_dict)

def update_exif(exif_dict, field, value):
    if field in exif_dict["0th"]:
        exif_dict["0th"][field] = value
    elif field in exif_dict["Exif"]:
        exif_dict["Exif"][field] = value
    elif field in exif_dict["GPS"]:
        exif_dict["GPS"][field] = value
    elif field in exif_dict["Interop"]:
        exif_dict["Interop"][field] = value
    return exif_dict

def to_deg(value, loc):
    """Convert decimal coordinates into degrees, minutes, and seconds."""
    if value < 0:
        loc_value = loc[0]
        value = -value
    else:
        loc_value = loc[1]

    deg = int(value)
    t1 = (value - deg) * 60
    min = int(t1)
    sec = round((t1 - min) * 60 * 10000)

    return (deg, min, sec), loc_value

def set_gps_location(exif_dict, lat, lon):
    """Add GPS information to exif data."""
    lat_deg, lat_ref = to_deg(lat, ['S', 'N'])
    lon_deg, lon_ref = to_deg(lon, ['W', 'E'])

    exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef] = lat_ref.encode()
    exif_dict['GPS'][piexif.GPSIFD.GPSLatitude] = [(int(lat_deg[0]), 1), (int(lat_deg[1]), 1), (int(lat_deg[2]), 10000)]
    exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef] = lon_ref.encode()
    exif_dict['GPS'][piexif.GPSIFD.GPSLongitude] = [(int(lon_deg[0]), 1), (int(lon_deg[1]), 1), (int(lon_deg[2]), 10000)]

    return exif_dict

        # Afficher le lien pour télécharger l'image éditée
        with open("edited_image.jpg", "rb") as file:
            btn = st.download_button(
                label="Télécharger l'image modifiée",
                data=file,
                file_name="edited_image.jpg",
                mime="image/jpeg"
            )

