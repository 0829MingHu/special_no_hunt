import multiprocessing.dummy
import sys
import warnings
from pathlib import Path

import pandas as pd
# from youtube_dl import YoutubeDL
from yt_dlp import YoutubeDL

warnings.filterwarnings('ignore')
# raw = False
# part = False
download_videos = False

NUMS = 100  # maximal items you can download
iMaxDuration = 600  # maximal duration in seconds
YDL_OPTIONS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'writeautomaticsub': True,
    # 'skip_download': True,
    'writesubtitles': True,
    "extractor-args":"youtube:player-client=web",
}
YDL_OPTIONS_EXTRACT = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'writeautomaticsub': True,
    # 'skip_download': True,
    'writesubtitles': True,
    "extractor-args":"youtube:player-client=web",
    #"age-limit":12,
}


download_path = "./test"
YDL_OPTIONS_AUDIO_ONLY = {
    'format': 'bestaudio[ext=m4a]',
}


def search(arg, nums):

    with YoutubeDL(YDL_OPTIONS_EXTRACT) as ydl:
        videos=None
        tag=True
        while tag:
            try:
                # print("nums",nums)
                videos = ydl.extract_info(f"ytsearch{nums}:{arg}", download=False)['entries']
                tag = False
            except:

                if nums >6:
                    nums -= 5
                elif nums <=5:
                    nums-=2
                if nums<1:
                    return "network link failed"





            # return "Network link failed!"
    return videos


def download(index):
    print("index", index)
    arg, title, folder, action, name = download_information[index]

    path = Path(folder) / name / action / 'videos'
    path.mkdir(exist_ok=True, parents=True)

    YDL_OPTIONS['outtmpl'] = str(path / (arg + ".mp4"))
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            video = ydl.extract_info("https://www.youtube.com/watch?v={}".format(arg), download=True)
            YDL_OPTIONS_AUDIO_ONLY['outtmpl'] = str(path / ( arg + ".m4a"))
            with YoutubeDL(YDL_OPTIONS_AUDIO_ONLY) as ydl_audio:
                audio = ydl_audio.extract_info("https://www.youtube.com/watch?v={}".format(arg), download=True)
                return True
        except Exception:
            video = ydl.extract_info("https://www.youtube.com/watch?v={}".format(arg), download=False)
            return False

def filter(arg):
    try:
        if arg["duration"] > iMaxDuration:
            return None
        else:
            return arg
    except Exception:
        return None


def mut_download(folder, animals, action_list):
    people_tag = ['child', 'man', 'men', 'people', 'shoot', 'hunter', 'archery', 'person', 'boy', 'girl', 'toy', 'bushpig', 'viralhog', 'milk']
    download_information = []
    for actions in action_list:
        DIR2 = True
        ll = []
        for action in actions.split("/"):
            rm_action = action
            food_list = ['grass', 'leaf', 'fruit', 'leaves', 'food', 'water']
            for food_word in food_list:
                if food_word in action:
                    rm_action = rm_action.replace(food_word, '').strip()

            if DIR2:
                dir_name2 = rm_action
                DIR2 = False

            DIR = True

            for animal in animals.split("/"):

                rm_animal = animal

                if 'animal' in animal:
                    rm_animal = rm_animal.replace('animal', '').strip()
                if DIR:
                    dir_name = rm_animal
                    DIR = False
                args = f"{animal} {action}"
                print(args)
                retry = 0
                while True:
                    try:
                        video_infos = search(args, NUMS)
                        for info in video_infos:
                            video = filter(info)
                            try:
                                title = info['title']
                            except Exception:
                                continue
                            if video is None:
                                continue
                            if rm_animal.lower() not in title.lower() :
                                continue
                            if rm_action.lower() not in title.lower() :
                                continue
                            for p in people_tag:
                                if p in  title.lower():
                                    continue


                            times = info['duration']
                            url = info['requested_formats'][0]['url']
                            id = info['id']
                            size = info['requested_formats'][0]['filesize']
                            title = info['title']
                            format_note = info['requested_formats'][0]['format_note']
                            ll.append([times, id, size, title, format_note])
                            download_information.append([info["id"], info["title"], folder, dir_name2, dir_name])
                        break
                    except Exception:
                        retry += 1
                        if retry > 10:
                            break

        path = Path(folder) / dir_name / dir_name2
        path.mkdir(exist_ok=True, parents=True)
        file_name = path / f'{dir_name}_{dir_name2}.csv'
        df1 = pd.DataFrame(ll, columns=['id', 'time', 'file_size', 'title', 'Clarity'])
        df1.to_csv(file_name)
        print("the number o f download inforamtion", len(download_information))

    return download_information


CPU = 10
folder, animal_name, action_list = "".join(sys.argv[1:]).split("||")
action_list = eval(action_list)
print(folder)
print(animal_name)
print(action_list)

download_information = mut_download(folder, animal_name, action_list)

print(download_information)
num_videos = len(download_information)
video_index = [i for i in range(0, num_videos)]
print(video_index)
print("the number of videos", num_videos)

if download_videos:
    with multiprocessing.dummy.Pool(CPU) as pool:       
        pool.map(download, video_index)



