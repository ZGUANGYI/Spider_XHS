import requests
import pandas as pd
from one import OneNote
from profile import Profile
from xhs_utils.xhs_util import get_headers, get_params, js, check_cookies


class Home:
    def __init__(self, cookies=None):
        if cookies is None:
            self.cookies = check_cookies()
        else:
            self.cookies = cookies
        self.more_url = 'https://edith.xiaohongshu.com/api/sns/web/v1/user_posted'
        self.profile = Profile(self.cookies)
        self.oneNote = OneNote(self.cookies)
        self.headers = get_headers()
        self.params = get_params()


    # 主页
    def get_all_note_info(self, url):
        profile = self.profile.get_profile_info(url)
        note_id_list = []
        user_id = profile.userId
        cursor = ''
        self.params['user_id'] = user_id
        self.params['cursor'] = cursor
        while True:
            api = f"/api/sns/web/v1/user_posted?num=30&cursor={cursor}&user_id={user_id}&image_scenes="
            ret = js.call('get_xs', api, '', self.cookies['a1'])
            self.headers['x-s'], self.headers['x-t'] = ret['X-s'], str(ret['X-t'])
            response = requests.get(self.more_url, headers=self.headers, cookies=self.cookies, params=self.params)
            res = response.json()
            data = res["data"]
            if not data["notes"][0]:
                print(f"用户{user_id}没有笔记")
                break
            cursor, has_more, note_list = data["cursor"], data["has_more"], data["notes"]
            self.params['cursor'] = cursor
            for note in note_list:
                note_id_list.append(note['note_id'])
            if not has_more:
                break
        return note_id_list, profile

    # 主页
    def save_all_note_info(self, url, need_cover=False):
        profile = self.profile.save_profile_info(url)
        user_id = profile.userId
        cursor = ''
        self.params['user_id'] = user_id
        self.params['cursor'] = cursor
        index = 0
        one_user_note_list = pd.DataFrame(columns=['note_id','title','content','pic_url_lsit','publish_time','ip_location','type', 'video_url', 'video_cover_url', 'note_url', 'user_id','nickname'])
        while True:
            api = f"/api/sns/web/v1/user_posted?num=30&cursor={cursor}&user_id={user_id}&image_scenes="
            ret = js.call('get_xs', api, '', self.cookies['a1'])
            self.headers['x-s'], self.headers['x-t'] = ret['X-s'], str(ret['X-t'])
            response = requests.get(self.more_url, headers=self.headers, cookies=self.cookies, params=self.params)
            res = response.json()
            data = res["data"]
            if not data["notes"][0]:
                print(f"用户{user_id}没有笔记")
                break
            cursor, has_more, note_list = data["cursor"], data["has_more"], data["notes"]
            self.params['cursor'] = cursor
            try:
                for one_note in note_list:
                    if index >=1000:
                        return one_user_note_list;
                    index += 1
                    info = f'第{index}个笔记, '
                    note, series = self.oneNote.save_one_note_info(self.oneNote.detail_url + one_note['note_id'], need_cover, info)
                    if series is not None:
                        one_user_note_list.loc[len(one_user_note_list)] = series;
                if not has_more:
                    break
            except:
                return one_user_note_list;
        print(f'用户 {profile.nickname} 全部视频信息保存成功')
        return one_user_note_list;


    def main(self, url_list):
        # url_list = [
        #     'https://www.xiaohongshu.com/user/profile/6185ce66000000001000705b',
        #     'https://www.xiaohongshu.com/user/profile/6034d6f20000000001006fbb',
        # ]
        all_note = pd.DataFrame(columns=['note_id','title','content','pic_url_lsit','publish_time','ip_location','type', 'video_url', 'video_cover_url', 'note_url', 'user_id','nickname'])
        for url in url_list:
            try:
                one_user_note_list = self.save_all_note_info(url)
                all_note = all_note._append(one_user_note_list, ignore_index=True)
            except:
                print(f'用户 {url} 查询失败')
        all_note.to_csv('all_note.csv', encoding='utf-8-sig', sep=",")


if __name__ == '__main__':
    home = Home()
    url_list = []
    with open ('./static/profile_url.txt') as f:
        for line in f.readlines():
            url_list.append(line.strip())
    home.main(url_list)

