# -*- coding: utf-8 -*-
import os

from slack_bolt import App
from slackblocks import SectionBlock, HeaderBlock, DividerBlock
from slackblocks.messages import BaseMessage
from crontab import CronTab

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

tab = CronTab()
def app_schedule(s):
    def _schedule(f):
        job = tab.new(command='/bin/true')
        job.setall(s)
        job.func = f
        return f
    return _schedule
app.schedule = app_schedule

class ViewMessage(BaseMessage):
    def _resolve(self):
        result = {**super()._resolve()}
        result.pop("mrkdwn", None)
        result.pop("text", None)
        return result

@app.event("app_home_opened")
def app_home_opened(event, ack, client):
    ack()
    details = client.auth_test()
    channels = client.users_conversations(types="public_channel,private_channel")
    channellist = ''
    for channel in channels['channels']:
        channellist += f"* <#{channel['id']}>\n"
    view = ViewMessage(blocks=[
        HeaderBlock(f":wave: Hello, I'm {details['user']}!"),
        DividerBlock(),
        SectionBlock("\n*Active in Channels:*"),
        DividerBlock(),
        SectionBlock(f"{channellist}"),
    ])
    client.views_publish(
        user_id = event['user'],
        view = dict(type="home", **view)
    )

def check_access(client, group_id, user_id):
    response = client.usergroups_users_list(usergroup=group_id)
    return user_id in response['users']
