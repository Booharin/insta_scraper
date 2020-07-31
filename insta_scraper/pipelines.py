from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
import scrapy


class DataBasePipeline:
    def __init__(self):
        self.mongo_client = MongoClient("mongodb://admin:12345@18.197.155.243/my_db")
        self.profiles = self.mongo_client.my_db.profiles

    def process_item(self, item, spider):
        self.profiles.replace_one(item, item, upsert=True)
        return item

    def __del__(self):
        self.mongo_client.close()


class ProfilesPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['profile_photo_link']:
            try:
                yield scrapy.Request(item['profile_photo_link'], meta=item)
            except Exception as e:
                print(e)

    def file_path(self, request, response=None, info=None):
        item = request.meta
        name = item['profile_photo_link'].split('/')[-1]
        return f"/{item['name']}/{name}.jpg"
