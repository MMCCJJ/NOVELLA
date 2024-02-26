# https://playwright.dev/python/

import asyncio
import time
from playwright.async_api import async_playwright
import re

browser_url = f'https://www.goodreads.com/book/show/11588.The_Shining?from_search=true&from_srp=true&qid=taAZMILcU8&rank=1'


async def main():
    async with async_playwright() as pw:
        print('start');
        browser = await pw.chromium.launch_persistent_context(
                "",
                headless=False,
                args=[f"--disable-extensions",]
                )
        print('launched');
        page = await browser.new_page()
        await page.goto(browser_url, timeout=120000)
        print('loaded')

        el = page.get_by_text('More reviews and ratings')
        print(el)
        await el.dispatch_event('click')


        await page.locator('xpath=//html/body/div[3]/div/div[1]/div/div/button').click()
        print("popup closed")


        await page.locator('xpath=//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[4]/div[1]/div[2]/div/button').click()
        print('Filters clicked')

        el = page.get_by_text('Oldest first')
        print(el)
        await el.dispatch_event('click')
        print('oldest first clicked')

        el = page.get_by_text('Apply')
        print(el)
        await el.dispatch_event('click')
        print('apply clicked')

        # paginate
        for idx in range(10):
            print(f"Page {idx}")
            await page.locator('xpath=//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[5]/div[4]/div/button').click()


        # get all ratings
        ratings = await page.locator('section.ReviewCard__row > div.ShelfStatus').all()

        for item in ratings:
            rs = await item.locator('span').all()
            if rs:
                stars_text = await rs[0].get_attribute("aria-label")
                pattern = r'\b\d+\b'
                numbers = re.findall(pattern, stars_text)
                if numbers:
                    rating = int(numbers[0])
                    print(f"Rating: {rating}")

        time.sleep(100)
        await browser.close()

asyncio.run(main())
