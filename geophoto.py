import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import googlemaps

geocoding_api_key = "YOUR_GEOCODING_API_KEY"

def get_exif_data(image_path):
    exif_data = {}
    with Image.open(image_path) as img:
        exif_info = img._getexif()
        if exif_info:
            for tag, value in exif_info.items():
                tag_name = TAGS.get(tag, tag)
                exif_data[tag_name] = value
    return exif_data

def get_gps_info(exif_data):
    gps_info = {}
    if 'GPSInfo' in exif_data:
        for key in exif_data['GPSInfo'].keys():
            tag_name = GPSTAGS.get(key, key)
            gps_info[tag_name] = exif_data['GPSInfo'][key]
    return gps_info

def get_decimal_coords(coord_tuple):
    degrees = coord_tuple[0]
    minutes = coord_tuple[1]
    seconds = coord_tuple[2]
    return degrees + (minutes / 60.0) + (seconds / 3600.0)

def get_coordinates(gps_info):
    latitude = get_decimal_coords(gps_info['GPSLatitude'])
    longitude = get_decimal_coords(gps_info['GPSLongitude'])

    if gps_info['GPSLatitudeRef'] == 'S':
        latitude *= -1
    if gps_info['GPSLongitudeRef'] == 'W':
        longitude *= -1

    return latitude, longitude

def extract_gps_from_image(image_path):
    exif_data = get_exif_data(image_path)
    gps_info = get_gps_info(exif_data)
    if gps_info:
        latitude, longitude = get_coordinates(gps_info)
        return latitude, longitude
    else:
        return None

def process_images_in_folder(folder_path):
    image_coordinates = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(folder_path, filename)
            coordinates = extract_gps_from_image(image_path)
            if coordinates:
                image_coordinates[filename] = coordinates
    return image_coordinates

def get_address(latitude, longitude, api_key):
    gmaps = googlemaps.Client(key=api_key)
    reverse_geocode_result = gmaps.reverse_geocode((latitude, longitude), language="ko")
    if reverse_geocode_result:
        address_components = reverse_geocode_result[0]['address_components']
        city = None
        for component in address_components:
            if 'locality' in component['types']:
                city = component['long_name']
                break
        return city
    else:
        return None


if __name__ == "__main__":
    folder_path = "photo/"  # 이미지가 있는 폴더의 경로를 지정하세요.
    image_coordinates = process_images_in_folder(folder_path)
    if image_coordinates:
        for filename, coordinates in image_coordinates.items():
            print(f"{filename}: 위도 {coordinates[0]}, 경도 {coordinates[1]}")
            address = get_address(coordinates[0],coordinates[1], geocoding_api_key )
            print(f"주소:", address)
    else:
        print("폴더 내에서 GPS 정보가 포함된 이미지를 찾을 수 없습니다.")
