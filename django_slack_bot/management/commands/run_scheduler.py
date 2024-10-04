# -*- coding: utf-8 -*-
import time
import logging
import datetime
from concurrent.futures import ThreadPoolExecutor

from django.core.management.base import BaseCommand
from django.utils.module_loading import autodiscover_modules

from ...chat import tab

log = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run the chat scheduler.'

    def handle(self, *args, **options):
        autodiscover_modules('chat')
        log.info("Starting chat scheduler...")
        with ThreadPoolExecutor() as executor:
            for _ in self.run_scheduler(executor):
                #log.debug("Pending jobs completed.")
                pass

    def run_pending(self, executor, **kwargs):
        """Run all commands in this crontab if pending (generator)"""
        for job in tab:
            ret = job.run_pending(**kwargs)
            if ret not in [None, -1]:
                executor.submit(job.func)
                yield ret

    def run_scheduler(self, executor, timeout=-1, **kwargs):
        """Run the CronTab as an internal scheduler (generator)"""
        count = 0
        while count != timeout:
            now = datetime.datetime.now()
            if 'warp' in kwargs:
                now += datetime.timedelta(seconds=count * 60)
            try:
                yield from self.run_pending(executor, now=now)
            except Exception as e:  # pylint: disable=broad-except
                log.info(f"Error running pending job: {e}")
            try:
                time.sleep(kwargs.get('cadence', 60))
            except KeyboardInterrupt:
                log.info("Terminating after interrupt...")
                break
            count += 1
