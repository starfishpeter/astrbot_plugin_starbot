from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api import AstrBotConfig

import astrbot.api.message_components as Comp
import aiohttp

async def is_valid_image_url(url: str):
    # 检查网络图片URL是否有效
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, timeout=5) as response:
                return response.status == 200
    except Exception as e:
        logger.error(f"图片的URL加载失败: {e}")
        return False

@register("astrbot_plugin_starbot", "StarBot", "基础功能多合一", "1.0.1")
class MyPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.is_send_welcome = config.get("is_send_welcome", False)
        self.welcome_text = config.get("welcome_text", "Welcome")
        self.welcome_img = config.get("welcome_img", "")

    # 处理入群事件
    @filter.event_message_type(filter.EventMessageType.ALL)
    async def handle_group_add(self, event: AstrMessageEvent):

        if not hasattr(event, "message_obj") or not hasattr(event.message_obj, "raw_message"):
            return
        raw_message = event.message_obj.raw_message
        if not raw_message or not isinstance(raw_message, dict):
            return
        if raw_message.get("post_type") != "notice":
            return

        # 必须得是入群的群通知 才去做入群欢迎
        if raw_message.get("notice_type") == "group_increase":
            if not self.is_send_welcome:
                return
            welcome_message = self.welcome_text
            if self.welcome_img and await is_valid_image_url(self.welcome_img):
                chain = [
                    # 用零宽空格来解除限制 防止空格被去除掉
                    Comp.Plain("\u200b" + welcome_message),
                    Comp.Image.fromURL(self.welcome_img),
                ]
            else:
                chain = [
                    Comp.Plain("\u200b" + welcome_message),
                    Comp.Plain(welcome_message),
                ]

            yield event.chain_result(chain)

