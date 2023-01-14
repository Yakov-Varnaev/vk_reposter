from vk_api.bot_longpoll import VkBotEvent


class EventParser:

    def __init__(self, event: VkBotEvent):
        self.event = event
        self.object = event.object

    @staticmethod
    def __extract_picture_url(attachment):
        photo_sizes = {size['height']: size for size in attachment['photo']['sizes']}
        max_size = max(photo_sizes.keys())
        return photo_sizes[max_size]['url']

    def extract_pictures(self):
        res = []
        for attachment in self.object.attachments:
            if attachment.get('type') != 'photo':
                continue
            res.append(self.__extract_picture_url(attachment))
        return res

    @property
    def text(self):
        return self.event.object.text

    @property
    def has_attachment(self):
        return bool(self.object.attachments)
