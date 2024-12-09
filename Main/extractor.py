import asyncio
import logging
import re
from .loggingsettings import ColorfulLogger
from playwright.async_api import async_playwright
from .models import Customer, Tweet
from .GPT import GPT

class XExtractor:
    def __init__(self, username: str, amount_of_posts: int, get_data_from_DB: bool):
        self.username = username
        self.amount_of_posts = amount_of_posts
        self.logging = ColorfulLogger("XExtrator")
        self.get_data_from_DB = get_data_from_DB

    async def extract_user_descriptions(self, page):
        descriptions = await page.query_selector_all('[data-testid="UserDescription"]')
        result = []
        for desc in descriptions:
            text = await desc.text_content()
            if text:
                result.append(text.strip())
        return str(*result)

    async def fetch_user_descriptions(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                await page.goto(f'https://x.com/{self.username}')
            except Exception as ex:
                return logging.error("Problem with loading page", ex)
            try:
                await page.wait_for_selector('[data-testid="UserDescription"]', timeout=20000)
            except Exception as ex:
                return logging.error("Bad internet connection, retry", ex)
            descriptions = await self.extract_user_descriptions(page)
            await browser.close()
            return descriptions

    async def fetch_posts(self, page):
        await page.evaluate('window.scrollBy(0, window.innerHeight * 2.5);')
        await asyncio.sleep(0.2)

        posts = await page.query_selector_all('article')
        return posts

    def parse_stat_number(self, stat: str) -> int:
        stat = stat.replace(",", "")
        if 'K' in stat:
            return int(float(stat.replace('K', '')) * 1000)
        elif 'M' in stat:
            return int(float(stat.replace('M', '')) * 1000000)
        return int(stat)

    def extract_statistics(self, text: str):
        stats_pattern = r"(\d+(?:\.\d+)?[KM]?)"
        stats = re.findall(stats_pattern, text.split("\n")[-1])
        cleaned_text = re.sub(stats_pattern, "", text).strip()
        while len(stats) < 4:
            stats.insert(0, "0")
        parsed_stats = [self.parse_stat_number(stat) for stat in stats]
        return cleaned_text, {
            "comments": parsed_stats[0],
            "reposts": parsed_stats[1],
            "likes": parsed_stats[2],
            "views": parsed_stats[3],
        }

    async def extract_post_data(self, post):
        text_elements = await post.query_selector_all('span')
        unique_text = []
        for el in text_elements:
            text = await el.text_content()
            text = text.strip()
            if text not in unique_text:
                unique_text.append(text)
        post_text = ' '.join(unique_text)
        cleaned_text, stats = self.extract_statistics(post_text)
        return cleaned_text, stats

    async def fetch_clean_posts(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(f'https://x.com/{self.username}')
            try:
                await page.wait_for_selector('[data-testid="primaryColumn"]', timeout=10000)
            except Exception:
                logging.error("User profile page did not load or is inaccessible")
                return {}
            try:
                await page.wait_for_selector('article', timeout=20000)
            except Exception as ex:
                self.logging.error(str(ex))
                return {}
            pattern_to_delete = r"^.*?@.*?·\s*"
            posts = {}
            seen_posts = set()
            scroll_count = 0
            unchanged_iterations = 0
            last_count = 0

            while len(posts) < int(self.amount_of_posts):
                new_posts = await self.fetch_posts(page)
                if not new_posts:
                    break

                for post in new_posts:
                    post_text, stats = await self.extract_post_data(post)
                    real_text = re.sub(pattern_to_delete,"", post_text)
                    if real_text and real_text not in seen_posts:
                        seen_posts.add(real_text)
                        posts[len(posts) + 1] = {real_text: stats}

                scroll_count += 1
                current_count = len(posts)
                self.logging.info(f"Downloading iteration #{scroll_count}, tweets retrieved: {current_count}")

                if current_count == last_count:
                    unchanged_iterations += 1
                    if unchanged_iterations >= 5:
                        self.logging.warning("No more new tweets available or can't retrieve additional tweets.")
                        break
                else:
                    unchanged_iterations = 0

                last_count = current_count

            await browser.close()
            return posts

    async def main(self):
        list_of_tweets = []
        endings = [
            "The media could not be played. Reload . ",
            "The media could not be played. Reload",
        ]
        user = await Customer.get_or_none(user_login=self.username)
        description = await self.fetch_user_descriptions()
        if not user:
            await Customer.create_with_user_login(self.username, description)
        if self.get_data_from_DB:
            data = await self.get_tweets_from_DB()
            if len(data) >= self.amount_of_posts:
                return await self.GPT_response(description, data)
        posts = await self.fetch_clean_posts()
        if len(posts)>=1:
            for key, value in posts.items():
                for message, message_data in value.items():
                    for ex in endings:
                        if ex in message:
                            message = message.removesuffix(ex)
                    list_of_tweets.append(message)
                    if not await Tweet.check_tweet_by_text(self.username, message):
                        await Tweet.create(
                            Tweet_sender=self.username,
                            Tweet_text=message,
                            Tweet_comments=message_data["comments"],
                            Tweet_reposts=message_data["reposts"],
                            Tweet_likes=message_data["likes"],
                            Tweet_views=message_data["views"],
                        )
        else:
            self.logging.warning("No tweets available.")
            return "User page is closed or bad internet connection"
        return await self.GPT_response(description, list_of_tweets)

    async def get_tweets_from_DB(self):
        list_of_tweets =[]
        try:
            tweets = await Tweet.get_tweets_by_sender(self.username)
            if tweets:
                self.logging.info(f"Getting tweets of {self.username}")
            for tweet in tweets:
                self.logging.info(f" {tweet}")
                list_of_tweets.append(tweet["Tweet_text"])
        except Exception as e:
            self.logging.error(f"Error: {e}")
        return list_of_tweets

    async def GPT_response(self, description, list_of_tweets):
        gpt = GPT(self.username,description, list_of_tweets)
        answer = await gpt.get_response()
        return answer

