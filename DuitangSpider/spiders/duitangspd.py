# -*- coding: utf-8 -*-

import json
import scrapy
from scrapy import Request
from ..items import DuitangspiderItem


class DuitangspdSpider(scrapy.Spider):
    name = 'duitangspd'
    allowed_domains = ['duitang.com']

    base_url = "https://www.duitang.com/napi/blog/list/by_search/?kw={keyword}&start={start}&limit=100"
    base_album_url = 'https://www.duitang.com/napi/album/list/by_search/?include_fields=is_root%2Csource_link%2Citem%2Cbuyable%2Croot_id%2Cstatus%2Clike_count%2Csender%2Calbum%2Ccover&kw={keyword}&limit=12&type=album&_type=&start={start}'
    base_album_info_url='https://www.duitang.com/napi/blog/list/by_album/?album_id={album_id}&limit=24&include_fields=top_comments%2Cis_root%2Csource_link%2Cbuyable%2Croot_id%2Cstatus%2Clike_count%2Clike_id%2Csender%2Creply_count&start={start}&_=1567854920893'

    keyword_list = [
                    '美食动图',
                    # '宫崎骏',
                    # '阴阳师',
                    # '古风'
                    ]

    def start_requests(self):
        for keyword in self.keyword_list:
            # 直接搜索图片
            for start in range(0, 3600, 100):
                yield Request(self.base_url.format(keyword=keyword, start=start), callback=self.parse)
            # 搜索图片专辑
            yield Request(self.base_album_url.format(keyword=keyword, start=0), callback=self.parse_album)

    # 直接搜索图片
    def parse(self, response):
        result = json.loads(response.text)
        if result.get('data').get('object_list') and len(result.get('data').get('object_list')) != 0:
            node_list = result.get('data').get('object_list')
            for node in node_list:
                item = DuitangspiderItem()
                url = node.get('photo').get('path')
                if url.endswith('.gif_jpeg'):
                    item['src_url'] = url.replace('_jpeg', '')
                else:
                    item['src_url'] = url
                yield item


    # 搜索图片专辑
    def parse_album(self, response):
        result = json.loads(response.text)

        if result.get('data').get('object_list') and len(result.get('data').get('object_list')) != 0:
            # 如果是第一页，则获取所有页
            if 'start=0' in response.url:
                total = result.get('data').get('total')
                for page_num in range(12, total, 12):
                    page_url = response.url.replace('start=0', 'start={}'.format(page_num))
                    yield Request(page_url, callback=self.parse_album)

            node_list = result.get('data').get('object_list')
            for node in node_list:
                album_id = node.get('id')
                album_id = str(album_id)
                yield Request(self.base_album_info_url.format(album_id=album_id, start=0), self.parse_album_info)

    # 搜索专辑中图片
    def parse_album_info(self, response):
        result = json.loads(response.text)
        if result.get('data').get('object_list') and len(result.get('data').get('object_list')) != 0:
            # 如果是第一页，则获取所有页
            if 'start=0' in response.url:
                total = result.get('data').get('total')
                for page_num in range(24, total, 24):
                    page_url = response.url.replace('start=0', 'start={}'.format(page_num))
                    yield Request(page_url, callback=self.parse_album_info)

            node_list = result.get('data').get('object_list')
            for node in node_list:
                item = DuitangspiderItem()
                url = node.get('photo').get('path')
                if url.endswith('.gif_jpeg'):
                    item['src_url'] = url.replace('_jpeg', '')
                else:
                    item['src_url'] = url
                yield item
