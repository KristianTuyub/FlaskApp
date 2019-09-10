from urllib.parse import quote


class RedditPost:

    def __init__(self):
        self.__post_id = 1
        self.__title = "What's everyone working on this week?"
        self.__description = "Tell /r/python what you're working on this week! You can be bragging, grousing, " \
                             "sharing your passion, or explaining your pain. Talk about your current project or your " \
                             "pet project; whatever you want to share."
        self.__author = "Lone Ranger"
        self.__community = "r/Python"
        self.__post_votes = 0

    def get_post_id(self):
        return self.__post_id

    def get_title(self):
        return self.__title

    def get_description(self):
        return self.__description

    def get_post_url(self):
        return "{0}".format(quote(self.get_title()))

    def get_author(self):
        return self.__author

    def get_community(self):
        return self.__community

    def get_post_votes(self):
        return self.__post_votes

    def add_post_vote(self):
        self.__post_votes += 1

    def rest_post_vote(self):
        self.__post_votes -= 1
