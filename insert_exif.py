from datetime import datetime
import piexif

filename = r"D:\temp\Сортировка фото\Несортированные\007.jpg"
exif_dict = piexif.load(filename)
new_date = datetime(2022, 7, 12, 8, 20, 10).strftime("%Y:%m:%d %H:%M:%S")
exif_dict['0th'][piexif.ImageIFD.DateTime] = new_date
exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_date
exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_date
exif_bytes = piexif.dump(exif_dict)
piexif.insert(exif_bytes, filename)

