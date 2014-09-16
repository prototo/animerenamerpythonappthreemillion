from lib.models import Subscription, session_scope, engine
from lib.nyaa import Nyaa
from os.path import isfile
from threading import Thread, Timer

class SubscriptionHandler:
    timer = None
    interval = 5

    def step(self):
        # set a timer to run this function after an interval
        self.handleAllSubscriptions()
        interval = self.interval * 60
        self.timer = Timer(interval, self.step)
        self.timer.start()

    def start(self):
        # return if the timer has already been started
        if self.timer:
            return False

        print("Stating subscription handler with", self.interval, "minute interval")
        self.step()

    # cancel any current timer
    def stop(self):
        if self.timer:
            self.timer.cancel()

    # get all the subscriptions from the database
    def getAllSubscriptions(self):
        return Subscription.getAll()

    # run the handle method for all available subscriptions
    def handleAllSubscriptions(self):
        for subscription in self.getAllSubscriptions():
            self.handleSubscription(subscription)

    # check a subscription for new episodes and download any found
    def handleSubscription(self, subscription):
        if not subscription.anime:
            return False
        print('handling', subscription.anime)

        aid = subscription.anime.id
        nyaa = Nyaa(aid)
        group = nyaa.get_groups()[0][0]
        # gotta wait for groups to be available 8D
        if not group:
            return False
        # FUCK THE CONFIG
        qualities = ['720p', '480p', '']

        for episode in subscription.anime.episodes:
            if episode.download:
                # if theres an entry for this episode in the download table, skip it
                continue

            if episode.files:
                found = False
                for file in episode.files:
                    if isfile(file.path):
                        # set the found flag is we find a valid file
                        found = True
                    else:
                        # delete any invalid looking rows
                        with session_scope() as session:
                            session.delete(file)
                if found:
                    # if we found a valid file for this episode, skip it
                    continue

            # get all the available torrents for this episode
            available = nyaa.find_episode(episode.epno)
            if len(available):
                # TODO have group/quality preference/order to pick the right one
                # and download the one we want if there was any
                chosen = None
                for quality in qualities:
                    for torrent in available:
                        title = torrent[0].lower()
                        good = group.lower() in title and quality in title
                        if good:
                            chosen = torrent
                            break
                    if chosen:
                        break
                if chosen:
                    Nyaa.download_torrent(chosen, eid=episode.id)
