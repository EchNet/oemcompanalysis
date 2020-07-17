import json
import logging

from channels.generic.websocket import WebsocketConsumer

logger = logging.getLogger(__name__)


class EchoConsumer(WebsocketConsumer):
  def connect(self):
    logger.info(f"connect {self.channel_name}")
    self.accept()

  def disconnect(self, close_code):
    logger.info(f"disconnect {self.channel_name}")

  def receive(self, text_data=None, bytes_data=None):
    logger.info(f"text_data={text_data}")
    self.send(text_data=text_data)
