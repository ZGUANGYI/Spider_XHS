import json
import requests
import pandas as pd
from xhs_utils.xhs_util import get_headers, get_params, js, check_cookies, get_note_data, handle_note_info, norm_str, check_and_create_path, save_note_detail, download_media

class OneNote:
    def __init__(self, cookies=None):
        if cookies is None:
            self.cookies = check_cookies()
        else:
            self.cookies = cookies
        self.feed_url = 'https://edith.xiaohongshu.com/api/sns/web/v1/feed'
        self.detail_url = 'https://www.xiaohongshu.com/explore/'
        self.headers = get_headers()
        self.params = get_params()

    # 单个视频
    def get_one_note_info(self, url):
        note_id = url.split('/')[-1]
        data = get_note_data(note_id)
        data = json.dumps(data, separators=(',', ':'))
        ret = js.call('get_xs', '/api/sns/web/v1/feed', data, self.cookies['a1'])
        self.headers['x-s'], self.headers['x-t'] = ret['X-s'], str(ret['X-t'])
        response = requests.post(self.feed_url, headers=self.headers, cookies=self.cookies, data=data)
        res = response.json()
        try:
            data = res['data']['items'][0]
        except:
            print(f'笔记 {note_id} 不允许查看')
            return
        note = handle_note_info(data)
        return note

    # cover 是否覆盖
    def save_one_note_info(self, url, need_cover=False, info='', dir_path='datas'):
        try:
            note = self.get_one_note_info(url)
            nickname = norm_str(note.nickname)
            user_id = note.user_id
            title = norm_str(note.title)
            if title.strip() == '':
                title = f'无标题'
            path = f'./{dir_path}/{nickname}_{user_id}/{title}_{note.note_id}'
            
            #save_note_detail(path, note)
            note_type = note.note_type
            img_url_list=[]
            video_cover_url=""
            if note_type == 'normal':
                for img_index, img in enumerate(note.image_list):
                    img_url = img['info_list'][1]['url']
                    img_url_list.append(img_url)
                    #download_media(path, f'image_{img_index}', img_url, 'image', f'第{img_index}张图片')

            elif note_type == 'video':
                video_cover_url = note.image_list[0]['info_list'][1]['url']
                #download_media(path, 'cover', img_url, 'image', '视频封面')
                video_url = note.video_addr
                #download_media(path, 'video', video_url, 'video')
            series = pd.Series([note.note_id,note.nickname, note.title, note.desc, json.dumps(img_url_list), note.upload_time, note.ip_location, note.note_type, note.video_addr, video_cover_url, f'https://www.xiaohongshu.com/explore/{note.note_id}', note.user_id], index=['note_id','nickname','title','content','pic_url_lsit','publish_time','ip_location','type', 'video_url', 'video_cover_url', 'note_url', 'user_id'])

            print(f'用户: {nickname}, {info}标题: {title} 笔记保存成功')
            print('===================================================================')
            return note, series
        except Exception as e:
            print(f'笔记 {url} 保存失败')
            print(e)
            return None, None

    def main(self, url_list):
        for url in url_list:
            try:
                self.save_one_note_info(url)
            except:
                print(f'笔记 {url} 保存失败')
                continue

if __name__ == '__main__':
    one_note = OneNote()
    url_list = [
         'https://www.xiaohongshu.com/explore/5f1a3e89000000000100029c'
    ]
    one_note.main(url_list)

