from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from time import sleep, strftime
from random import randint, choice
import pandas as pd
import instaloader
import pickle
import datetime
from dateutil.relativedelta import relativedelta

user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.2490.71 Safari/537.36'

L = instaloader.Instaloader(user_agent=user_agent, max_connection_attempts=1)

class InstagramBot:
    def __init__(self, username, password, chrome_driver_path, headless=False, follow=False, unfollow=False, comment=False, like=False):
        self.username = username
        self.password = password
        self.chrome_driver_path = chrome_driver_path
        self.window_width = 760
        self.window_height = 629
        self.headless = headless
        self.comment = comment
        self.like = like
        self.follow = follow
        self.unfollow = follow
        self.logged_in = False
        self.comments = []
        self.skip_list = []
        self.unfollow_list = []
        self.unfollow_anyway = []
        self.logs = None

        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=%d,%d" % (self.window_width, self.window_height))
        chrome_options.add_argument("--user-agent=%s" % user_agent)
        self.webdriver = webdriver.Chrome(executable_path=self.chrome_driver_path, options=chrome_options)

        # self.save()

    def login(self):
        self.webdriver.get('https://www.instagram.com/accounts/login/?source=auth_switcher')
        sleep(3)

        username = self.webdriver.find_element_by_name('username')
        username.send_keys(self.username)
        password = self.webdriver.find_element_by_name('password')
        password.send_keys(self.password)
        sleep(3)

        button_login = self.webdriver.find_element_by_css_selector(
            'body > #react-root > section > main > div > article > div > div:nth-child(1) > div > form > div:nth-child(4) > button')
        button_login.click()
        sleep(3)

        try:
            notnow = self.webdriver.find_element_by_xpath('/html/body/div[3]/div/div/div[3]/button[2]')
        except:
            sleep(3)
            notnow = self.webdriver.find_element_by_xpath('/html/body/div[3]/div/div/div[3]/button[2]')

        notnow.click()
        sleep(3)

        L.login(self.username, self.password)

        self.load()
        self.logged_in = True

    def follow_user(self, username):
        if not self.logged_in:
            self.webdriver.quit()
            raise Exception('Not Logged in')

        if not self.follow:
            self.webdriver.quit()
            raise Exception('Follow module not enabled')

        self.webdriver.get('https://www.instagram.com/%s/' % username)
        sleep(3)

        button_follow = self.webdriver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/span/span[1]/button')
        button_follow.click()
        sleep(3)

        self.log('FOLLOW', username)

    def unfollow_user(self, username):
        if not self.logged_in:
            self.webdriver.quit()
            raise Exception('Not Logged in')

        if not self.unfollow:
            self.webdriver.quit()
            raise Exception('Unfollow module not enabled')

        self.webdriver.get('https://www.instagram.com/%s/' % username)
        sleep(3)

        button_unfollow = self.webdriver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/span/span[1]/button')
        button_unfollow.click()
        sleep(3)

        button_unfollow = self.webdriver.find_element_by_xpath('/html/body/div[3]/div/div/div[3]/button[1]')
        button_unfollow.click()
        sleep(3)

        self.log('UNFOLLOW', username)

    def comment_post(self, post, comment):
        if not self.logged_in:
            self.webdriver.quit()
            raise Exception('Not Logged in')

        if (not post or not comment):
            return

        self.webdriver.get(post)
        sleep(3)

        textarea = self.webdriver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/article/div[2]/section[3]/div/form/textarea')
        textarea.click()
        textarea = self.webdriver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/article/div[2]/section[3]/div/form/textarea')
        textarea.send_keys(comment)
        sleep(3)

        comment_button = self.webdriver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/article/div[2]/section[3]/div/form/button')
        comment_button.click()
        sleep(7)

        self.log('COMMENT', post)

    def like_post(self, post):
        if not self.logged_in:
            self.webdriver.quit()
            raise Exception('Not Logged in')

        self.webdriver.get(post)
        sleep(3)

        textarea = self.webdriver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/article/div[2]/section[1]/span[1]/button')
        textarea.click()
        sleep(3)

        self.log('LIKE', post)

    def get_my_stat(self):
        return self.get_stat(self.username)

    def get_stat(self, profile):
        if not L.context.is_logged_in:
            raise Exception('InstaLoader not Logged in')

        if 'instagram.com' in profile:
            profile = profile.split('/')[3]

        profile = instaloader.Profile.from_username(L.context, profile)
        return {
            'is_private': profile.is_private,
            'do_i_follow': profile.followed_by_viewer,
            'does_it_follow_me': profile.follows_viewer,
            'no_of_posts': profile.mediacount,
            'no_of_followers': profile.followers,   # number of profiles that are following 'profile'
            'no_of_followees': profile.followees,   # number of profiles that 'profile' is following
            'has_public_story': profile.has_public_story,
            'has_viewable_story': profile.has_viewable_story
        }

    def get_followees(self, profile):
        if not L.context.is_logged_in:
            raise Exception('InstaLoader not Logged in')

        if 'instagram.com' in profile:
            profile = profile.split('/')[3]

        profile = instaloader.Profile.from_username(L.context, profile)
        # profiles that 'profile' am following
        return profile.get_followees()

    def get_followers(self, profile):
        if not L.context.is_logged_in:
            raise Exception('InstaLoader not Logged in')

        if 'instagram.com' in profile:
            profile = profile.split('/')[3]

        profile = instaloader.Profile.from_username(L.context, profile)
        # profiles that are following 'profile'
        return profile.get_followers()

    def get_profiles_who_liked(self, post_url):
        if 'instagram.com' in post_url:
            post_url = post_url.split('/')[4]
        post = instaloader.Post.from_shortcode(post_url)

        return post.get_likes()

    def check_notifications(self):
        if not self.logged_in:
            self.webdriver.quit()
            raise Exception('Not Logged in')

        self.webdriver.get('https://www.instagram.com/accounts/activity/')
        sleep(randint(3, 7))

    def search(self, keyword):
        # todo fix
        if not self.logged_in:
            self.webdriver.quit()
            raise Exception('Not Logged in')

        search = self.webdriver.find_element_by_xpath('//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]')
        search.click()
        sleep(3)

        search_box = self.webdriver.find_element_by_xpath('//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/input')
        search.send_keys(keyword)
        sleep(3)

        k = randint(1, 5)
        search_result = self.webdriver.find_element_by_xpath('//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/div[2]/div[2]/div/a[%d]' % k)
        search_result.click()

        sleep(3)

        self.webdriver.get('https://www.instagram.com/')
        sleep(3)

    def save(self):
        dump = {
            'comments': self.comments
        }
        with open('dump.pkl', 'wb+') as output:
            pickle.dump(dump, output, pickle.HIGHEST_PROTOCOL)

    def load(self):
        with open('dump.pkl', 'rb') as input:
            dump = pickle.load(input)
            self.comments = dump['comments']

        self.logs = pd.read_csv('logs.csv', header=None)
        self.logs[0] = pd.to_datetime(self.logs[0])

        # get skip list by filtering profiles that u already followed, unfollowed, skipped
        skip_only = self.logs.loc[self.logs.iloc[:, 1].isin(['FOLLOW', 'UNFOLLOW', 'SKIP'])]
        self.skip_list = list(skip_only.iloc[:, 2])

        # get potential unfollow list by getting the list bot followed 2 days ago
        t = datetime.datetime.now() - relativedelta(days=2)
        unfollow_only = self.logs[self.logs[0] > t][self.logs.iloc[:, 1] == 'FOLLOW']
        self.unfollow_list = list(unfollow_only.iloc[:, 2])

        # get potential unfollow_anyway list by getting the list bot followed 5 days ago
        t = datetime.datetime.now() - relativedelta(days=5)
        unfollow_anyway = self.logs[self.logs[0] > t][self.logs.iloc[:, 1] == 'FOLLOW']
        self.unfollow_anyway = list(unfollow_anyway.iloc[:, 2])

    def set_comments_list(self, comments_list):
        self.comments = comments_list
        self.save()

    def get_comments_list(self):
        return self.comments

    def get_random_comment(self):
        k = randint(0, len(self.comments) - 1)
        return self.comments[k]

    def get_random_post(self, profile):
        # todo fix get random post when highlights are there
        # hotfix added using try catch
        if not self.logged_in:
            self.webdriver.quit()
            raise Exception('Not Logged in')

        if (not profile):
            return

        self.webdriver.get('https://www.instagram.com/%s/' % profile)
        sleep(3)

        k1 = randint(1,2)
        k2 = randint(1, 3)
        # post = self.webdriver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[3]/article/div[1]/div/div[%d]/div[%d]/a' % (k1, k2))
        try:
            post = self.webdriver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[3]/article/div[1]/div/div[%d]/div[%d]/a' % (k1, k2))
        except:
            post = self.webdriver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[2]/article/div/div/div[%d]/div[%d]/a' % (k1, k2))

        link = post.get_attribute("href")
        return link

    def get_random_unfollow(self):
        p = choice(self.unfollow_list)
        follows_me = self.get_stat(p)['does_it_follow_me']

        if follows_me:
            return p

        # todo enable this after 5 days
        # else:
        #     if self.unfollow_anyway:
        #         print('anyway')
        #         return choice(self.unfollow_anyway)
        return None

    def skip_user(self, username):
        return username in self.skip_list

    def random_sleep(self):
        t = randint(10, 20)
        sleep(t)

    def log(self, action, msg):
        t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line = "%s,%s,%s" % (t, action, msg)
        print(line)
        with open('logs.csv', 'a+') as logs:
            logs.write(line+"\n")

    def log_stats(self):
        t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self_stat = self.get_my_stat()

        line = "%s,%s,%s,%s" % (t, self_stat['no_of_posts'], self_stat['no_of_followers'], self_stat['no_of_followees'])

        with open('stats.csv', 'a+') as stats:
            stats.write(line+"\n")

    def exit(self):
        self.webdriver.quit()
