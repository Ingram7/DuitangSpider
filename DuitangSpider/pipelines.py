# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
import os
from scrapy.utils.misc import md5sum
from scrapy.pipelines.images import ImagesPipeline


class DuitangPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        yield scrapy.Request(item['src_url'], meta={'item': item})

    def file_path(self, request, response=None, info=None):
        # item = request.meta['item']
        image_name = request.url.split('/')[-1]
        # path = u'{}/{}'.format(item['title'], image_name)
        path = u'{}'.format(image_name)
        return path

    def check_gif(self, image):
        if image.format is None:
            return True

    def persist_gif(self, key, data, info):
        root, ext = os.path.splitext(key)
        absolute_path = self.store._get_filesystem_path(key)
        self.store._mkdir(os.path.dirname(absolute_path), info)
        f = open(absolute_path, 'wb')  # use 'b' to write binary data.
        f.write(data)

    def image_downloaded(self, response, request, info):
        try:
            checksum = None
            for path, image, buf in self.get_images(response, request, info):
                if checksum is None:
                    buf.seek(0)
                    checksum = md5sum(buf)
                width, height = image.size
                if self.check_gif(image):
                    self.persist_gif(path, response.body, info)
                else:
                    self.store.persist_file(
                        path, buf, info,
                        meta={'width': width, 'height': height},
                        headers={'Content-Type': 'image/jpeg'})
                return checksum
        except:
            pass