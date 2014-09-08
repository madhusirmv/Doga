# -*- coding: utf-8 -*-

"""
Doga.statistics

This module manage information about log statistics
update and keep track of usage summary periodically
"""

import time
import threading
from collections import Counter

from configer import value
from thread_timer import ThreadTimer
#from gui import DogaGUI


class Statistics:

    def __init__(self):
        self.queue = []
        self.total = 0

        self.alert_queue = []

        self.stop_event = threading.Event()

        self.stats_timer = ThreadTimer(10, self.stop_event, self.update_queue)
        self.stats_timer.start()

        self.alert_timer = ThreadTimer(30, self.stop_event, self.update_alert_queue)
        self.alert_timer.start()

        self.stats_scanner = ThreadTimer(1, self.stop_event, self.check_stats)
        self.stats_scanner.start()

        self.stats_template = ""
        self.alert_template = "Traffic status: Normal, Alert state: No"

        self.is_alert = False

        self.alert_start = ""
        self.alert_end = ""

        #self.app = DogaGUI(self)
        #self.app.run()

    def queue_event(self, method, host, section):
        """ Queue each request to be used in statistics

        param: method(str) : request method type
        param: host(str) : requested resource host
        param: section(str) : requested resource section
        """

        self.queue.append(host + section)
        self.alert_queue.append(host + section)

    def update_statistics(self):
        """ return resource section info having maximum hits and count of total hits
        """

        self.total += len(self.queue)

        status = "[No recent requests]"
        if (len(self.queue) > 0):
            counts = Counter(self.queue)
            frequency = counts.most_common()

            status = "[%s : %d]" % (frequency[0][0], frequency[0][1])

        self.stats_template = "Maximum : %s, Recent : %d, Total : %d" % (status, len(self.queue), self.total)

    def update_queue(self):
        """ update the queue periodically and call for 'max_queue' method
        """

        self.update_statistics()
        self.queue = []

    def update_alert_queue(self):
        """ update the alert queue periodically
        """

        self.alert_queue = []

    def check_stats(self):
        """ call for an alert if request count is not in threshold range
        """

        maximum = int(value('maximum'))

        # we are in alert state
        if (self.is_alert):
            if (len(self.alert_queue) < maximum):
                self.is_alert = False
                self.alert_end = time.strftime("%H:%M:%S")
                self.alert_status = "Traffic status: Normal Alert state: No Max Hits: %d Recovered at: %s" % (len(self.alert_queue), self.alert_end)
        # we are alert free now
        else:
            if (len(self.alert_queue) > maximum):
                self.is_alert = True
                self.alert_start = time.strftime("%H:%M:%S")
                self.alert_status = "Traffic status: High Alert state: Yes Max Hits: %d Triggered at: %s" % (len(self.alert_queue), self.alert_start)
