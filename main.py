from functions import InstagramBot
from random import randint
# import schedule

bot = InstagramBot(
    username='my_username',
    password='my_password',
    chrome_driver_path='chrome_driver_path',
    follow=True,
    unfollow=True,
    like=True,
    comment=True
)

# bot.login()
bot.log_stats()

profile = bot.get_followers('target_username')

try:
    while True:
        username = profile.__next__().username

        if bot.skip_user(username):
            continue

        stat = bot.get_stat(username)

        if (not stat['is_private'] and not stat['does_it_follow_me'] and stat['no_of_followers'] < 10000 and stat['no_of_posts'] > 5):
            bot.follow_user(username)

            k = randint(0, 25)

            if 19 < k < 22:
                random_post = bot.get_random_post(username)
                random_comment = bot.get_random_comment()
                bot.comment_post(random_post, random_comment)
            elif 22 < k < 25:
                random_post = bot.get_random_post(username)
                bot.like_post(random_post)
            elif 0 < k < 5:
                bot.check_notifications()
            elif 5 < k < 19:
                p = bot.get_random_unfollow()
                if p:
                    bot.unfollow_user(p)

            bot.random_sleep()
        else:
            bot.log('SKIP', username)
            continue
except KeyboardInterrupt:
    print('Saving stats')
    bot.log_stats()
    bot.exit()
except Exception as e:
    bot.log_stats()
    bot.exit()
    print(e.with_traceback())
