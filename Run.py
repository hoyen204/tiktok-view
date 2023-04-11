#!/usr/bin/env python3
from PIL import Image
import pytesseract
import requests
import re
import json
import base64
import random
import string
import os
import time
import time
from rich.console import Console
from requests_toolbelt import MultipartEncoder
from rich import print
from requests.exceptions import RequestException
from rich.panel import Panel
from rich.columns import Columns

Dump, Choose, Video, Sudah = [], {
    "Choose": 0
}, {
    "Video": None
}, {
    "Sudah": False
}

def read_captcha(filename):
    with Image.open(filename) as img:
        # Set whitelist and configure Tesseract engine
        config = "--psm 3 -c tessedit_char_whitelist=1234567890abcdefghijklmnopqrstuv tessedit_unrej_any_wd=True"
        # Read the image using Tesseract engine
        text = pytesseract.image_to_string(img, lang='eng', config=config)
        # Process the text and return the result
        text = text.replace('\n', '')
        return text[:5]


def current_milli_time():
    return round(time.time() * 1000)


def submit_followers(username_tiktok):
    with requests.Session() as r:
        r.headers.update({
            'upgrade-insecure-requests': '1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Host': 'fireliker.com',
            'accept-language': 'id,en;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'cache-control': 'max-age=0',
        })
        response = r.get('https://fireliker.com/index.php?').text
        form_username = re.search(
            'name="(.*?)" placeholder="Username"', str(response)).group(1)
        form_text = re.search(
            'type="text" name="(.*?)" value="(.*?)"', str(response))
        form_text2, form_text3 = form_text.group(1), form_text.group(2)

        r.headers.update({
            'origin': 'https://fireliker.com',
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': ("; ".join([str(x)+"="+str(y) for x, y in r.cookies.get_dict().items()])),
            'referer': 'https://fireliker.com/index.php?',
        })
        data = {
            f'{form_username}': username_tiktok,
            f'{form_text2}': f'{form_text3}'
        }
        response2 = r.post('https://fireliker.com/searchs.php', data=data)
        if 'Security Check' in str(response2.text):
            r.headers.pop('origin')
            r.headers.pop('content-type')
            r.headers.pop('referer')
            r.headers.update({
                'cookie': ("; ".join([str(x)+"="+str(y) for x, y in r.cookies.get_dict().items()])),
            })

            response3 = r.get('https://fireliker.com/secure.php').text
            form_code = re.search(
                'name="(.*?)" placeholder="Code"', str(response3)).group(1)
            captcha_image = re.search(
                '<br><img src="(.*?)"', str(response3)).group(1)
            r.headers.pop('cache-control')

            r.headers.update({
                'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'referer': 'https://fireliker.com/secure.php',
                'sec-fetch-dest': 'image',
            })
            response4 = r.get('https://fireliker.com/{}'.format(captcha_image))
            t = current_milli_time()
            captcha_file = 'Data/Captcha{}.png'.format(t)
            with open(captcha_file, 'wb') as w:
                w.write(response4.content)
            w.close()

            r.headers.update({
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'origin': 'https://fireliker.com',
                'content-type': 'application/x-www-form-urlencoded',
                'sec-fetch-dest': 'document',
                'referer': 'https://fireliker.com/secure.php',
            })
            data = {
                f'{form_code}': read_captcha(captcha_file),
                'submit': 'Continue'
            }
            response5 = r.post('https://fireliker.com/secure.php', data=data)
            if 'https://fireliker.com/welcome.php' in str(response5.url):
                print(
                    "[bold bright_white]   ╰─>[bold green] Sukses Bypass Captcha...              ", end='\r')

                r.headers.pop('origin')
                r.headers.pop('content-type')
                r.headers.pop('referer')
                r.headers.update({
                    'cookie': ("; ".join([str(x)+"="+str(y) for x, y in r.cookies.get_dict().items()]))
                })
                response6 = r.get('https://fireliker.com/autoviews.php').text
                find_all_videos = re.findall('''<h5 class="text-warning">(.*?) <i class="fa fa-play-circle"></i> </h5>
<div align="right">
<form action="(.*?)" method="post">
<label for="select" class="col-lg-2 control-label text-success"><b>Choose Limit</b></label>
<div class="col-lg-6">
<select class="form-control" id="select" name="(.*?)">
<option value="(.*?)">(\d+) VIEWS</option>
</select>
<br>
</div>
<input type="hidden" name="crf_auth" value="(.*?)">
<input type="hidden" name="crf_type" value="(.*?)">''', str(response6))
                if len(find_all_videos) == 0:
                    print(
                        "[bold bright_white]   ╰─>[bold red] Views Telah Limit...              ", end='\r')
                    time.sleep(0.5)
                    for sleep in range(1, 0, -1):
                        time.sleep(1.0)
                        Console().print(
                            f"[bold bright_white]   ╰─>[bold white] Tunggu[bold green] {sleep}[bold white] Detik...               ", end='\r')
                    return 0
                else:
                    Dump.clear()
                    pilih_video_views(find_all_videos)
                    z = Video['Video'].split('|')
                    views_count, controller_url, form_data, value_data, send_views_count, crf_auth, crf_type = z[
                        0], z[1], z[2], z[3], z[4], z[5], z[6]
                    if Sudah['Sudah'] == False:
                        Sudah.update({
                            "Sudah": True
                        })
                        print(Panel("[italic white]Sedang Memproses[italic green] Views[italic white] Jika Semua[italic red] Gagal[italic white] Atau Muncul Tulisan[italic red] Error[italic white] Mungkin Website Down Atau Update, Hubungi[italic blue] Developer[italic white] Untuk Solusinya",
                              style="bold bright_white", width=71, title=">>> Catatan <<<"))
                    r.headers.update({
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'origin': 'https://fireliker.com',
                        'referer': 'https://fireliker.com/autoviews.php',
                        'cache-control': 'max-age=0',
                        'content-type': 'application/x-www-form-urlencoded',
                        'cookie': ("; ".join([str(x)+"="+str(y) for x, y in r.cookies.get_dict().items()])),
                    })
                    data = {
                        f'{form_data}': value_data,
                        'crf_auth': crf_auth,
                        'crf_type': crf_type,
                    }
                    response7 = r.post(
                        'https://fireliker.com/{}'.format(controller_url), data=data)
                    if 'Sending Views' in str(response7.text):
                        r.headers.pop('origin')
                        r.headers.pop('content-type')
                        r.headers.pop('referer')
                        r.headers.update({
                            'referer': 'https://fireliker.com/{}'.format(controller_url),
                            'cookie': ("; ".join([str(x)+"="+str(y) for x, y in r.cookies.get_dict().items()]))
                        })
                        response8 = r.get(
                            'https://fireliker.com/welcome.php?info=Views_Send').text
                        if 'Views Has Been Successfully Send To Mentioned Post.' in str(response8):
                            try:
                                tambah = (int(views_count.replace(
                                    ',', '').replace('.', '')) + 200)
                            except:
                                tambah = ('-')
                            print(Panel(f"""[bold white]Username :[bold green] @{username_tiktok}
[bold white]Link :[bold red] fireliker.com/{controller_url}
[bold white]Views :[bold green] +200 > {tambah}""", style="bold bright_white", width=71, title=">>> Sukses <<<"))
                            print(
                                "[bold bright_white]   ╰─>[bold red] Views Telah Limit...              ", end='\r')
                            for sleep in range(1, 0, -1):
                                time.sleep(1.0)
                                Console().print(
                                    f"[bold bright_white]   ╰─>[bold white] Tunggu[bold green] {sleep}[bold white] Detik...               ", end='\r')
                            return 0
                        elif 'Your Session Has Been Expired' in str(response8):
                            print(
                                "[bold bright_white]   ╰─>[bold red] Cookies Invalid...              ", end='\r')
                            return 404
                        else:
                            print(
                                "[bold bright_white]   ╰─>[bold red] Gagal Mengirimkan Views...              ", end='\r')
                            return 2
                    else:
                        print(
                            "[bold bright_white]   ╰─>[bold red] Views Not Sent...              ", end='\r')
                        return 1
            else:
                print(
                    "[bold bright_white]   ╰─>[bold red] Gagal Bypass Captcha...              ", end='\r')
                return 3
        else:
            print(Panel("[italic red]Ada Masalah Saat Login, Harap Kirimkan Respose Error Ke Developer!",
                  style="bold bright_white", width=71, title=">>> Error <<<"))
            exit()


def pilih_video_views(find_all_videos):
    Looping, Join_Panel, Width = -1, [], {
        "Width": 23
    }
    for z in find_all_videos:
        Looping += 1
        views_count, controller_url, form_data, value_data, send_views_count, crf_auth, crf_type = z[
            0], z[1], z[2], z[3], z[4], z[5], z[6]
        if len(find_all_videos) == 1:
            Width.update({
                "Width": 71
            })
            Join_Panel.append(
                Panel(f"[bold green]{Looping}[bold white]. {views_count}", width=Width['Width']))
        elif len(find_all_videos) == 2:
            Width.update({
                "Width": 35
            })
            Join_Panel.append(
                Panel(f"[bold green]{Looping}[bold white]. {views_count}", width=Width['Width']))
        else:
            Join_Panel.append(
                Panel(f"[bold green]{Looping}[bold white]. {views_count}", width=Width['Width']))
        Dump.append(
            f'{views_count}|{controller_url}|{form_data}|{value_data}|{send_views_count}|{crf_auth}|{crf_type}')
    if Video['Video'] == None:
        print(Columns(Join_Panel))
        print(Panel("[italic white]Silahkan Pilih Salah Satu[italic green] Video[italic white] Dari Jumlah Views Di Atas, Kamu Juga[italic red] Diwajibkan[italic white] Untuk Memasukan[italic red] Hanya Angka[italic white], Misalnya :[italic green] 0",
              style="bold bright_white", width=71, subtitle="[bold bright_white]╭─────", subtitle_align="left", title=">>> Select Videos <<<"))
        choose_videos = int(Console().input("[bold bright_white]   ╰─> "))
        Choose.update({
            "Choose": choose_videos
        })
        Video.update({
            "Video": Dump[choose_videos]
        })
    else:
        Video.update({
            "Video": Dump[Choose['Choose']]
        })
    return 0


def bypass_captcha(captcha_file: str):
    with requests.Session() as r:
        with open(captcha_file, "rb") as f:
            image_encode = base64.b64encode(
                f.read()
            )
        boundary = '----WebKitFormBoundary' \
            + ''.join(random.sample(string.ascii_letters + string.digits, 16))
        r.headers.update({
            'Host': 'www.imagetotext.info',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'cache-control': 'max-age=0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'accept-language': 'id,en;q=0.9',
        })
        response = r.get('https://www.imagetotext.info/').text
        csrf_token = re.search(
            'name="_token" content="(.*?)"', str(response)).group(1)
        r.headers.update({
            'x-requested-with': 'XMLHttpRequest',
            'x-csrf-token': csrf_token,
            'origin': 'https://www.imagetotext.info',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'accept': '*/*',
            'referer': 'https://www.imagetotext.info/',
            'content-type': 'multipart/form-data; boundary={}'.format(boundary),
            'cookie': ("; ".join([str(x)+"="+str(y) for x, y in r.cookies.get_dict().items()]))
        })

        data = MultipartEncoder({
            'base64': f"data:image/png;base64,{image_encode.decode('utf-8')}"
        }, boundary=boundary)

        response = json.loads(
            r.post('https://www.imagetotext.info/image-to-text', data=data).text)
        if bool(response['error']) == False:
            text = (re.search('<br />(.*?)<br />',
                    str(response['text']).replace('\n', '').replace('\r', '')).group(1))
            # os.remove(captcha_file)
            return text
        else:
            return 404


while 0 < 999999999:
    try:
        if int(re.search('columns=(\d+),', str(os.get_terminal_size())).group(1)) < 71:
            Console(style="bold bright_white", width=71).print(Panel(
                "[italic red]Silahkan Kecilkan Tampilan Termux Sampai Panel Ini Tidak Terlihat Terputus-Putus, Dengan Cara Mencubit Layar Di Termux!", title=">>> Error <<<"))
            break
    except Exception as e:
        print(Panel(f"[italic red]{str(e).title()}!",
              style="bold bright_white", width=71, title=">>> Error <<<"))
        break
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        try:
            response = requests.get('https://justpaste.it/2ylvz').text
            jumlah, online = re.search('"viewsText":"(.*?)"', str(response)).group(
                1), re.search('"onlineText":"(\d+)"', str(response)).group(1)
        except Exception as e:
            jumlah, online = ('0', '0')
        print(Panel("""[bold red]●[bold yellow] ●[bold green] ●[bold white]
 ___________.__                 .____    .__ __                 
 \_   _____/|__|______   ____   |    |   |__|  | __ ___________ 
  |    __)  |  \_  __ \_/ __ \  |    |   |  |  |/ // __ \_  __ \\
  |     \   |  ||  | \/\  ___/  |    |___|  |    <\  ___/|  | \/
  \___  /   |__||__|    \___  > |_______ \__|__|_ \\\___  >__|   
      \/                    \/          \/       \/    \/       
\t[bold blue]Get Tiktok Views With Fire-Liker[bold white] - Coded By[bold red] Rozhak""", style="bold bright_white", width=71))
        print(Columns([
            Panel(
                f"[bold white]Pengguna :[bold green] {jumlah}", width=35, style="bold bright_white"),
            Panel(
                f"[bold white]Online :[bold green] {online}", width=35, style="bold bright_white"),
        ]))
        print(Panel("[italic white]Silahkan Masukan[italic green] Username[italic white] Akun Tiktok Kamu Dan Pastikan Akun[italic red] Tidak Terkunci[italic white] Lalu Memiliki Satu Video, Misalnya :[italic green] @rozhak_official",
              style="bold bright_white", width=71, subtitle="[bold bright_white]╭─────", subtitle_align="left", title=">>> Your Username <<<"))
        username_tiktok = Console().input(
            "[bold bright_white]   ╰─> ").replace('@', '')
        if len(username_tiktok) < 3 or ' ' in str(username_tiktok):
            print(Panel("[italic red]Username Akun Tiktok Yang Anda Masukan Tidak Ditemukan!",
                  style="bold bright_white", width=71, title=">>> Username Tidak Ditemukan <<<"))
            break
        else:
            while True:
                try:
                    submit_followers(username_tiktok)
                    continue
                except AttributeError:
                    print(
                        "[bold bright_white]   ╰─>[bold red] AttributeError...                  ", end='\r')
                    time.sleep(0.5)
                    continue
                except RequestException:
                    print(
                        "[bold bright_white]   ╰─>[bold red] Koneksi Error...                  ", end='\r')
                    time.sleep(0.5)
                    continue
            break
    except Exception as e:
        print(Panel(f"[italic red]{str(e).title()}!",
              style="bold bright_white", width=71, title=">>> Error <<<"))
        break
