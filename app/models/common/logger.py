from fastapi.logger import logger
import requests
import json

url = "https://hooks.slack.com/services/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"


class Logger:
    def error(self, message, **kwargs):
        logger.error(message)
        payload = json.dumps({
          "username": "PayRoll Services Bot",
          "channel": "#taxslips-observability-monitoring-qa",
          "attachments": [
            {
              "color": "#000000",
              "fields": [
                {
                  "title": "PayRoll Services and Monitoring",
                  "value": str(message),
                  "short": "false"
                }
              ]
            }
          ]
        })

        headers = {
          'Content-Type': 'application/json'
        }

        requests.request("POST", url, headers=headers, data=payload)

    def warning(self, message):
        logger.warning(message)

    def info(self, message):
        logger.info(message)
