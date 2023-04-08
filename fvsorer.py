#coding=utf8
#import os
from pathlib import  Path
from exif import Image
from datetime import datetime, timedelta
from shutil import move
from pymediainfo import MediaInfo

dir_path = r'D:\temp\Сортировка фото\Несортированные'
dir_path = Path(dir_path)

target_dir = r'D:\temp\Сортировка фото\Сортированные'
target_dir = Path(target_dir)

video_ext = ['.mp4', '.mts', '.avi', '.mov', '.3gp', '.mpg', '.mkv']
photo_ext = ['.jpg', '.jpeg', '.nef']



photo_date_format = '%Y:%m:%d %H:%M:%S'
video_date_format = '%Y-%m-%d %H:%M:%S'

year_folders = set()  # для наполнения годами, чтоб создать папки
date_folders = set()  # для наполнения датами, чтобы созадть вложенные папки
pathes_list = []

for old_path in dir_path.glob('**/*.*'):      # full_path

    # для фото
    if old_path.is_file() and old_path.suffix.lower() in photo_ext:
        with open(old_path, 'rb') as image_file:
            my_image = Image(image_file)        
        try:
            datetime_original = my_image['datetime_original']
            datetime_original = datetime.strptime(
                datetime_original, photo_date_format)
        except:
            datetime_original = None
        
        try:
            datetime_digitized = my_image['datetime_digitized']
            datetime_digitized = datetime.strptime(
                datetime_digitized, photo_date_format)
        except:
            datetime_digitized = None
        
        if datetime_original != None or datetime_digitized != None:
            date = min(
                [x for x in [datetime_original, datetime_digitized] if x != None]
            )

            # собираем папки с годами
            year_path = target_dir / str(date.year)
            year_folders.add(year_path)

            # собираем папки с датами
            date_path = year_path / str(date.date())
            date_folders.add(date_path)

            # новое имя файла
            new_name = str(date.date()) + '_' + \
                str(date.time()).replace(':', '') + \
                old_path.suffix.lower()
            
            # новый путь файла
            new_path = date_path / new_name       # target_path

            # добавляем в список пару начальный путь и новый
            pathes_list.append([old_path, new_path])
            
    # для видео
    # часовой пояс
    time_zone = timedelta(hours=7)
    
    if old_path.is_file() and old_path.suffix.lower() in video_ext:
        media_info = MediaInfo.parse(old_path)
        for track in media_info.tracks:
            if track.track_type == "General":
                exif_vdata = track.to_data()        

        # вытаскиваем тег tagged_date, в формате UTS и прибавляем часовой пояс
        try:
            tag_date = exif_vdata['tagged_date']
            tag_date = datetime.strptime(tag_date[4:], video_date_format) + time_zone
        except:
            tag_date = None        

        try:
            enc_date = exif_vdata['encoded_date']
            enc_date = datetime.strptime(enc_date[4:], video_date_format) + time_zone
        except:
            enc_date = None
        
        try:
            mast_date = exif_vdata['mastered_date']
            #print(mast_date)
            # (день недели) (месяц) (день) (время) (год)
            pattern = re.compile('([A-Z][A-Z][A-Z]) ([A-Z][A-Z][A-Z]) (\d\d) (\d\d:\d\d:\d\d) (\d\d\d\d)')  
            date_list = pattern.findall(mast_date)
            month_dic = {
                         'JAN': '01', 
                         'FEB': '02', 
                         'MAR': '03',
                         'APR': '04',
                         'MAY': '05',
                         'JUN': '06',
                         'JUL': '07',
                         'AUG': '08',
                         'SEP': '09',
                         'OCT': '10',
                         'NOV': '11',
                         'DEC': '12'
                        }
            mast_date = (
                date_list[0][4]                             # год 
                + '-' + 
                date_list[0][1]                             # месяц с заменой буквеннгого обозначения на числовое
                    .replace(date_list[0][1]
                             , month_dic[date_list[0][1]]) 
                + '-' + 
                date_list[0][2]                             #  день 
                + ' ' + 
                date_list[0][3]                             # время
            )
            mast_date = datetime.strptime(mast_date, video_date_format)           # переводим в формат времени
        except:
            mast_date = None                

        if tag_date != None or enc_date != None or mast_date != None:
            date = min(
                [x for x in [tag_date, enc_date, mast_date] if x != None]
            )

            # собираем папки с годами
            year_path = target_dir / str(date.year)
            year_folders.add(year_path)

            # собираем папки с датами
            date_path = year_path / str(date.date())
            date_folders.add(date_path)

            # новое имя файла
            new_name = str(date.date()) + '_' + \
                str(date.time()).replace(':', '') + \
                old_path.suffix.lower()

            # новый путь файла
            new_path = date_path / new_name

            # добавляем в список пару начальный путь и новый
            pathes_list.append([old_path, new_path])

# создаём папки годов
for year in year_folders:
    year.mkdir(parents=True, exist_ok=True)

# создаём вложенные папки дат
for dat in date_folders:
    dat.mkdir(parents=True, exist_ok=True)

# перемещаем файл в папку даты
for old_path, new_path in pathes_list:
    #old_path = pathes[0]
    #new_path = pathes[1]
    #print(old_path)
    #print(new_path)
    #print()

    # если такой файл уже существует и их размеры не равны
    #if new_path.exists() and \
       #old_path.stat().st_size != new_path.stat().st_size:
        #print(
            #'Файл', old_path, 'имеет точно такие же дату и время съёмки, как и уже существующий файл', new_path, 'но их размеры отличаются'
        #)
    parent_path = new_path.parent
    file_suffix = new_path.suffix
    file_stem = new_path.stem
    i = 0
    while new_path.exists() and \
            old_path.stat().st_size != new_path.stat().st_size:      # пока существует такой файл будем дописывать к нему циферку
        i += 1
        #file_stem = file_stem + f'({i})'
        new_path = parent_path / (file_stem + f' ({i})' + file_suffix)
        #print(new_path)
    move(old_path, new_path)
