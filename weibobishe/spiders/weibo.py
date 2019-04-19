import json
from scrapy import Request, Spider
from weibobishe.items import *


class WeiboSpider(Spider):
    name = 'weibo'

    allowed_domains = ['m.weibo.cn']

    user_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&value={uid}&containerid=100505{uid}'

    # follow_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&page={page}'
    #
    # fan_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&page={page}'

    weibo_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&page={page}&containerid=107603{uid}'

    start_users = ['6370515370']  # '6370515370','3224580794'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.parse_fans = None

    def start_requests(self):
        for uid in self.start_users:
            yield Request(self.user_url.format(uid=uid), callback=self.parse_user)

    def parse_user(self, response):
        """
        解析用户信息
        :param response: Response对象
        """
        self.logger.debug(response)
        result = json.loads(response.text)
        if result.get('data').get('userInfo'):
            user_info = result.get('data').get('userInfo')
            user_item = UserItem()
            field_map = {
                'id': 'id', 'name': 'screen_name', 'description': 'description', 'verified_reason': 'verified_reason',
                'avatar': 'profile_image_url',
                'cover': 'cover_image_phone',
                'gender': 'gender', 'fans_count': 'followers_count',
                'follows_count': 'follow_count', 'weibos_count': 'statuses_count', 'verified': 'verified',
                'verified_type': 'verified_type'
            }
            for field, attr in field_map.items():
                user_item[field] = user_info.get(attr)
            yield user_item
            uid = user_info.get('id')
            # # 关注
            # yield Request(self.follow_url.format(uid=uid, page=1), callback=self.parse_follows,
            #               meta={'page': 1, 'uid': uid})
            # # 粉丝
            # yield Request(self.fan_url.format(uid=uid, page=1), callback=self.parse_fans,
            #               meta={'page': 1, 'uid': uid})
            # 微博
            yield Request(self.weibo_url.format(uid=uid, page=1), callback=self.parse_weibos,
                          meta={'page': 1, 'uid': uid})
            # 微博正文
            yield Request(self.weibo_url.format(uid=uid, page=1), callback=self.parse_weibotexts,
                          meta={'page': 1, 'uid': uid})

    def parse_weibos(self, response):
        """
        解析微博列表
        :param response: Response对象
        """
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards'):
            weibos = result.get('data').get('cards')
            for weibo in weibos:
                mblog = weibo.get('mblog')
                if mblog:
                    weibo_item = WeiboItem()
                    field_map = {
                        'id': 'id', 'text': 'text',
                        'attitudes_count': 'attitudes_count', 'comments_count': 'comments_count',
                        'reposts_count': 'reposts_count',
                        'crawled_at': 'crawled_at',
                        'picture': 'original_pic', 'pictures': 'pics',
                        'created_at': 'created_at', 'source': 'source', 'raw_text': 'raw_text',
                        'thumbnail': 'thumbnail_pic',
                    }
                    for field, attr in field_map.items():
                        weibo_item[field] = mblog.get(attr)
                    weibo_item['user'] = response.meta.get('uid')
                    yield weibo_item
            # 下一页微博
            uid = response.meta.get('uid')
            page = response.meta.get('page') + 1
            yield Request(self.weibo_url.format(uid=uid, page=page), callback=self.parse_weibos,
                          meta={'uid': uid, 'page': page})

    def parse_weibotexts(self, response):
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards'):
            weibotexts = result.get('data').get('cards')
            for weibotext in weibotexts:
                mblog = weibotext.get('mblog')
                if mblog:
                    weibotext_item = WeiboTextItem()
                    field_map = {
                        'id': 'id', 'text': 'text',
                    }
                    for field, attr in field_map.items():
                        weibotext_item[field] = mblog.get(attr)
                    weibotext_item['user'] = response.meta.get('uid')
                    yield weibotext_item
            uid = response.meta.get('uid')
            page = response.meta.get('page') + 1
            yield Request(self.weibo_url.format(uid=uid, page=page), callback=self.parse_weibotexts,
                          meta={'uid': uid, 'page': page})

            # def parse_follows(self, response):
            #     """
            #     解析用户关注
            #     :param response: Response对象
            #     """
            #     result = json.loads(response.text)
            #     if result.get('ok') and result.get('data').get('cards') and len(result.get('data').get('cards')) and result.get('data').get('cards')[-1].get(
            #         'card_group'):
            #         # 解析用户
            #         follows = result.get('data').get('cards')[-1].get('card_group')
            #         for follow in follows:
            #             if follow.get('user'):
            #                 uid = follow.get('user').get('id')
            #                 yield Request(self.user_url.format(uid=uid), callback=self.parse_user)
            #
            #         uid = response.meta.get('uid')
            #         # 关注列表
            #         user_relation_item = UserRelationItem()
            #         follows = [{'id': follow.get('user').get('id'), 'name': follow.get('user').get('screen_name')} for follow in
            #                    follows]
            #         user_relation_item['id'] = uid
            #         user_relation_item['follows'] = follows
            #         user_relation_item['fans'] = []
            #         yield user_relation_item
            #         # 下一页关注
            #         page = response.meta.get('page') + 1
            #         yield Request(self.follow_url.format(uid=uid, page=page),
            #                       callback=self.parse_follows, meta={'page': page, 'uid': uid})

            # def parse_fans(self, response):
            #     """
            #     解析用户粉丝
            #     :param response: Response对象
            #     """
            #     result = json.loads(response.text)
            #     if result.get('ok') and result.get('data').get('cards') and len(result.get('data').get('cards')) and result.get('data').get('cards')[-1].get(
            #         'card_group'):
            #         # 解析用户
            #         fans = result.get('data').get('cards')[-1].get('card_group')
            #         for fan in fans:
            #             if fan.get('user'):
            #                 uid = fan.get('user').get('id')
            #                 yield Request(self.user_url.format(uid=uid), callback=self.parse_user)
            #
            #         uid = response.meta.get('uid')
            #         # 粉丝列表
            #         user_relation_item = UserRelationItem()
            #         fans = [{'id': fan.get('user').get('id'), 'name': fan.get('user').get('screen_name')} for fan in
            #                 fans]
            #         user_relation_item['id'] = uid
            #         user_relation_item['fans'] = fans
            #         user_relation_item['follows'] = []
            #         yield user_relation_item
            #         # 下一页粉丝
            #         page = response.meta.get('page') + 1
            #         yield Request(self.fan_url.format(uid=uid, page=page),
            #                       callback=self.parse_fans, meta={'page': page, 'uid': uid})
