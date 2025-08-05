#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование поддержки архивов и различных форматов книг
"""

import os
import sys
import django
import base64
import zipfile
import io

# Настройка Django
sys.path.append('/Users/aleksandrkocergin/Documents/kpit.pw/reader/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.external_sources import FlibustaTorClient

def test_base64_decode():
    """Тестирование декодирования base64 строки из примера пользователя"""
    print("=== Тестирование декодирования base64 строки ===")
    
    # Строка из примера пользователя (первые несколько символов)
    sample_base64 = "UEsDBBQAAAAIADGF4kAyVhXwWpwBAM9EAgBMAAAAS3V6bWluYV9MeXVibHl1X3RlYnlhX1BldHJhX3R2b3JlbmUuX1B1c2hraW5za2llX21lc3RhX0xlbmluZ3JhZGEuMzgyMDc0LmZiZOz92dLzWpomhp3rKnbkgU9QXRgJEHJ2KQBinghiBk4UADEQ8wwCOOrqDll2WJYi5AM7pLB9C11VXVK7h9QtZN6RF7//3zv3zsquqpYcdh8k//h+EsNa613v+DxYBPjr/2Jvmx+2bJrLvvunv0L/HPnVD1n37NOyK/7pr9Yl/yfXX/0Xf/Gf/Voonws4g+37+gfQopv/6a9eyzL85zD8fr//vJjKZJ2z6c+nFQZH4fzb2Qk4G8Y+XX41+c+bXzR643/eTwWM0jQN703Z1b/6i//sh1+n2fycyuHTHGz+8OulXJrsn5Rd3n82f/h1kXVT9hfzs/wvX+W89NPxa/jbrp8d7fou/y+Tsi+meHj9sROKrP8vi7UEY/3iYLwur376+vzDr/Nympd/0sVt9he//R9/99/+9l/99t/+9l//9t/+9l/+Gv7ZoW/ntmWaAim/nfx//+1f//Zf/vbf//Y34P3ff07/+dFv5zfxT13/D7/7F7/9n3/333x1/nX27499O7dM/wKlMAL5NQw+fYkJ/0zO/7DM//1v//Z3/+wflvZ/AHL++9/95e/++Udm8P+//kdL/n8DLf6n3/0LMMhHLb/5D0lO0v+xkv9fP3J/BPgI9Q9qG0jwl/9Rcv8/QOf/M+j8n32d/x/QOI0jGPkfEPzj1v/kyy//4n83rv3yv//yj7/67b/93X/7A5Dkb3/7V7/77/7sh9/+v4AB/vlnKp+df/3b34CPfwtU/N/89m+/tfpzcAoQ/v/423/zEf53f/n1/rc/AE/422/2+OG3/+OnxdfU/uZLJ//qI+7Phv+mx67rl/jHgAE7ho9VP83+5tPH//I17r/6buK/BlL+dx/BfgAD/gYI/Zvf/r/BOV++8uUvn13fnOFLoUCef/0DGPc34JzfAMP/+y+JfjwC9Pivvk79Evyvf/d/BrP5jPX5/29++xuw6weUpogfPhtg97/4DPpXX5r4NPk3QLxf/a/Rwa+A6v6fH0t/TeLrxN/89l+DOX0k+uFL/n8FWv1boOt/D2T6rz67/uuv6f2bj83/7Ievyfz19zH+Ggjw3/7u/wQ6+Jz4OfYvf/vvfvffgSPfG/8kzGfj45Y/Te9vvubym49Mf/aR5a+Bbv/nb7r7avq7v/yI9O++ZvC3v/13vzD4p8lHt9/s8z99JP6o8C9/7Ps339T+7z7D/tlnqK8T/qdPsH3a/eRTX9t//Znul0r/9Rd7/uZ3/5ff/fNfetgPQDQw6rfmH2cFpvhq/OWoX+r5q69w/ps/+3T4m8/EP4b+my/NfGb3peX/6pvIv/my/mfcf/XNQEBjH/19xvlfwNZffhvpF0oC8gOb//bf/PA5/jHal/j/5ps8X0L85nvbv/3d/+HPfjr5r4Auf3/oX36FGLAt8J2f6f8j1cf9vkn8mz/74ZcH/+pL0O8Hf/Xnv4aH3wfLf/+Lyf3Vl7X/8svq/+wnJ/h5CP841+9a/uHL5J8Q+q+/hPu3H/GA8B9v/fLPfw4c/2Oxv/zudP/sy4G+Jd2//gM3+nKwH0CO+tvPqX/2rdG3KPvrTzh9944vdwbtgRZ+FANI9bXzRx/4my/P+/c/TRXksF8mCpATu+IvpvWTAMGHT7GFf1ltfz2sSVPOr5+V3+97sukvfgrML+l+98/BOD8d+zr1yOIJJNIryP9fH78G+MMef/1cQRVvv7Z/+Pz3T5ZjyP7pr5oymQCieP6TMv3VX+BXDKGIX8M/O/cDFeBfYoVfJ2UXT8cPZfpPf/XsAaT582oofvXDs++WrFu+91u2cZHB1ZAVAG3AdAUTDPOw60ixCoZlHjwbF8LIMBxMWbHtiq8tFekzFum3zOmrzjDEo24M9uYyXy+W+aOvO68ozsNcvm8+GH/Cna+zZTbeUtANzzDV62a7CK8U307iil90ARc/9fMwvu/jP/9l3Ld24uNnIrDEl1wMrH8/tf5ZV/yP/ajM75t8na/sP57Tf6T88XX7Lj/6/XSZudFt9NGPuH/exZ/6+XG/Kkbtz/dz8rd3of+8/2y/+70d8ov938cjvm++P/r/+14M9E1Zf+9Jb/NrcMb8+066cuQ37f/D433X++3nxvj6X/nS2Xf1ffMPlvjJ9L/3h0f8bZ8hfM3yl/Zmrc+2/rVTZjieMd4MwnA6c38wxPf3n0b9o6/HLzePz39u+I869+8c+fG4eEET8f01vy8hW2VL/Uv9ROgybvVfRIDbGoj++H1j7xMz4r4l7fNnrrg3UWfNCXbpfjb1G4ixJRHpNXr/Xma3Tfv0p/bfHaoz5tg3micazY70bXwHU8bw/XPdeGciNlX0+Oa64CU9sX0IMU+x/kAeFkuPBPfetvuHMkXbEzCW2L80Sed9xTHHe85Xvy59xH46JF+mQl9pYG0W5q1RoLxS0fsWeIJ1eYreT21v9fe23mf/t9xh+2gnfxurBDKskWSYYTtUv9C/oFQpx/9+coK1PW/sH+pPj/wI+Ul/Pxqys7bE/3G+gvi9vy6Wfj/X45s/os92dy3v5f5d2/+R/Tx6Rpj3d/azrTCngvWKUEvwhcfPfeMOdD8ngtVkkqU8kZfruHuZYPT8re2rivx99kSPAO3/sK0Ccu+R1QKwe7pGPpDp6zAtuN9sKie4Qj78fYiwr5iTItFrw8Cb06/mDQbsgnw7/jNbIj/aI2qencWCz903e6Y10OUr9fevBHXDlO4B5ARjuFnANj+Nzwo/jn+zEGMDuj88qXlH30S/A/02X+2Bbzx5Gk0lo0n/wPdu7VcsmMB/zij4Q/8D+sEtJMHQ/8Dx5eODffrH+v6ep35M9tw3o8HXH5t+Py4wPy9h/Le8xXxzIP7++0PhRy9fnfEgn94uX59AoAOHYv9O/Sx4xv4KOlA/H4z+8K0tbL38gQB15vDKMBc2EukyerD1t/Qnwdj7Bnz7Ld+YQrkxb+X2eFu3d6/xlmtyzNsUrMLhdxf8FRbY1j9//OPb+z/wx3KPWeMehMEzxJ1nH3euIFwBfP68/9gHb/E/nm/9I/rUORMGM+flj07CQmflgrnxD57jHxKMPz5xmsM70PdHfyzAE8zX30+GA+bgbyzjiuwbzLeYgY6BKX4872c1myl0IHIo3ZhavX3q9OMBzCPzTOFKbFEIzPt9gn7B2DovW/LOuoIVWnr5DPmDfdlWnwg3+Xh47iyU+mkdxSJw7OHbLsy9rr5xGlZczr3eWorhRnxw6/EHJtCKR7TBMRMOh+BBdUXCrlFtYVECHr07yJAEApoFqNdG2GuI22VO/MsW4haadimRBQOVSyiU4zyQC/gCmOeD+zbXp8g67gf/WMzB73xhsa4v7PJLF/RetARV3B+lybqL9NYPqyQC9VbXhiN85DT5hn19ySopVXBDatvxVD2IeM8zOqshNvV86aaTZuZpDXb9SmxvN5yaVn10T4OG9iJQSWJ/mBIRXRNMOVPJw1L8dQGg8JrDWMHozBvo+/WxIQMzWvF07kSe9r2oXM2yvlkX1YkpaX5eDSU8PWoVKwjJEzh0Mpk30mph+Lq8w5GhKcWdNffb4unrNIXQMoxG1Rt7pNFDhWAERA8xnkM1bHswvWblHt+f2mS0jOa/6Anf5jlLkVth0n4YJznpkKhjdBBLpmQH1fZi3GV2HPZr75UdMyvxs6D8Be58hjdjmGbn3exXPBKmKyUO9GQi3jaiMKE4SeEHvo7dp4GOr8SpFsHKPBFKusc0dKEpkcrdjIIZObieMFuiLnrrOtu1cXEeR9ra4XuMLEVRZSiK3uEUyqCmm+4j1NkHVqFmHkHVLYTxXrRHNzXc4pbKqOdVNoYOsXZjo9DRecZ8nnhu4XeoWSfYHGB7fsDOzFmUxrE4+3oyHIvdNpLbkLTiVtq8MrQ0PO1M2F7bboGo6Yqx2FfMmReiaM63UkW0sq009k5AZpu2K7N744wYT+TOJqFhUV0tZj7cwh0YdYPfjAK/2di6lTwiXUPbzTvoZht9Dj/m1wu6OHGwxHQV8EYmZ/dHTmmD805T11+XOqFwoQEZjH1e9jJdEguiNIPCV0eNSa9NIz/AEHSJ8jA9JzswsRXOpjGn0tO8CuQ2QeVLhCB60tPJr9siTMSFVTSO42jj3JClykMavuJQs8HIAthXN9DB4Ps3mvJRqhcaV8JiDMiPJ9FKaxgCQyLwiXryvGXxBEobO2gigy1ZxXfWM7nTrDTVefpMGxRMK7ABtdWA2Ak5BCbZo9QE0I54xpeBwV7v5Q6hk7jh0EZPM2zANhjnnCfYIrbhEPyEfExrqGI6jroIMsdBjS+CQ5ILENqh1fFYKzRHNixHVRjxRk98YvOSksnE2mTfnN2RNpa5Ak10E0bbG4QBB4e6Oo/I7cq/KiM+upBcTuDEmm8+4TURL2yaUilFU+QzR5f2pKXKc9GsCYCPWdQwp4j/gOj3RD9n+Xm7vCbNRncWOjHfsS9UYOIh3Od0BD/6O94abqBs4oPw+Tv9MCJfAU3QKU9DGtFh2w/ywZjExMzj182Cp74lVdWkjGCNQzS0L+uAPIMbusMnNprYvXjqWnp/2HfimV+ZwUNhekF7Ar01fMmPXhS/37N/Q9A3+gYcT64NqDDJJYc4i8T0EI8RnnOLuHO7J0UG18FcnAdpGoqjOW/bSTpF8RsYthCM3YqH14eoYYUM+uaMFUZx3xCxNyklJi2lPk46+KTF8GWEvYqgSDEZ8fuhifyMYhCJUs9kIBJgxyTG5RkGcYT66wGBwB5iHTiRBe34PA0hkUevEF0m605RpidUlOQBX50O/QW/uTsFX9pKhN9HeWrYItTourAg+zF3BOQ7qwohCttoM81ToMwNjv0NIeHLiSDEuPe55+dOfyQ300OV2MfycM7WgcLvtPNE27z1Z/gJW3JiVexrTm1fz+ckVVKoSJZ7UJcOzcnjkL68hDIh1MN7qKPvg2ZlrTCpZwDVnaQV7/iRqHr62lsj9ZEMGill3ZY5BrJb8zTCxOI+dzQZx2vWXACYo/CEXbFS7nd6mDGQ64wgIiscZhQas2p/JHAxJhGiaeE0WHo62p/KnFJTh7rAfWMyfgbGMsLvfIAaqFzhTgs5oV+mKL68BnNYNyOJUrIKXjSdetIKstzp5ZHoQx1Uwr55oVBfEWvh4Px89S1UGlGAK40hZlR1qabokqHvBkLgVg9RfMFgwt/gKSbtY5yhMRHF19nxrpEoyb2nzQCDWvxKnjmwcQAXJJXpZIUKWFSXaM+p5KIC9ngw6ZlIGIeDkLYNWB+A7BA/z+GjZebNrvm7FrV3+Ope38ZjDSUv65dkAUnNqO8Nck/lO0Um2DpjSQs/PJglz1Bt53Wnkgeo9ehDO4K7NnFkZaznFSbNUVbv+npKt9hVK3WnLrRyXXlqxJllFkGlSchgB0FwEVBIFfohzuVBoUEcuYPytMccRiYnUxg3wP0XtPdcC/cLt9btTo03ccWNKSETEfgwUpcMADJRsrQ4rZNDi2JXUJmYc3kS+V"
    
    try:
        # Декодируем base64
        decoded_bytes = base64.b64decode(sample_base64)
        print(f"Размер декодированных данных: {len(decoded_bytes)} байт")
        
        # Проверяем, является ли это ZIP архивом
        is_zip = zipfile.is_zipfile(io.BytesIO(decoded_bytes))
        print(f"Является ли ZIP архивом: {is_zip}")
        
        if is_zip:
            # Открываем архив и смотрим содержимое
            with zipfile.ZipFile(io.BytesIO(decoded_bytes), 'r') as zip_file:
                file_list = zip_file.namelist()
                print(f"Файлы в архиве: {file_list}")
                
                # Пробуем извлечь первый файл
                if file_list:
                    first_file = file_list[0]
                    print(f"Извлекаем файл: {first_file}")
                    
                    file_content = zip_file.read(first_file)
                    print(f"Размер извлеченного файла: {len(file_content)} байт")
                    
                    # Показываем первые 200 символов
                    try:
                        text_content = file_content.decode('utf-8')
                        print(f"Первые 200 символов:\n{text_content[:200]}...")
                    except UnicodeDecodeError:
                        print("Файл не является текстовым или имеет другую кодировку")
        else:
            print("Данные не являются ZIP архивом")
            
    except Exception as e:
        print(f"Ошибка при обработке: {e}")

def test_flibusta_client():
    """Тестирование клиента Флибусты с новой функциональностью"""
    print("\n=== Тестирование клиента Флибусты ===")
    
    try:
        client = FlibustaTorClient(use_tor=False)
        
        # Создаем тестовый ZIP архив с FB2 файлом
        test_fb2_content = '''<?xml version="1.0" encoding="utf-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">
<description>
<title-info>
<genre>sf</genre>
<author><first-name>Тест</first-name><last-name>Автор</last-name></author>
<book-title>Тестовая книга</book-title>
</title-info>
</description>
<body>
<section>
<title><p>Глава 1</p></title>
<p>Это тестовый текст книги в формате FB2.</p>
<p>Вторая строка текста.</p>
</section>
</body>
</FictionBook>'''
        
        # Создаем ZIP архив в памяти
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('test_book.fb2', test_fb2_content.encode('utf-8'))
        
        zip_content = zip_buffer.getvalue()
        print(f"Создан тестовый ZIP архив размером {len(zip_content)} байт")
        
        # Тестируем декодирование
        decoded_content = client._decode_content(zip_content, 'fb2')
        print(f"Результат декодирования:\n{decoded_content[:200]}...")
        
    except Exception as e:
        print(f"Ошибка при тестировании: {e}")

if __name__ == '__main__':
    test_base64_decode()
    test_flibusta_client()
    print("\n=== Тестирование завершено ===")