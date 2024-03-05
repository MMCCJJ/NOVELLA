# https://playwright.dev/python/

import asyncio
import time
from playwright.async_api import async_playwright
import re
import pandas as pd
from datetime import datetime, timedelta
from dateutil import parser


# leer el df de libros, para cada fila hacer un link con el titulo, hacer todo eso y añadir los valores a las columnas. tener en cuenta la fecha para q la review sea valida y guardar todo al final en un csv
async def main():
    df = pd.read_csv('/Users/maria/Downloads/LIBROS_LIMPIOS.csv')
    
    for index, row in df.iterrows():
        titulo = row['Title']
        browser_url = row['url']
        
        print(browser_url)
        
        try:
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
                await el.dispatch_event('click', timeout=60000)


                await page.locator('xpath=//html/body/div[3]/div/div[1]/div/div/button').click()
                print("popup closed")


                await page.locator('xpath=//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[4]/div[1]/div[2]/div/button').click()
                print('Filters clicked')

                el = page.get_by_text('Oldest first')
                print(el)
                await el.dispatch_event('click')
                print('oldest first clicked')

                el = page.locator('body > div.Overlay.Overlay--floating > div > div.Overlay__actions > div:nth-child(2) > button > span')
                print(el)
                await el.dispatch_event('click')
                print('apply clicked')

                # paginate
                NUM_PAGES = 10
                for idx in range(NUM_PAGES):
                    try:
                        await page.locator('xpath=//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[5]/div[4]/div/button').click()
                    except Exception as e:
                        print(e)
                        break
                print(idx)
                
                # get all ratings
                ratings = await page.locator('section.ReviewCard__row').all()
                
                num_ratings = 0
                sum_ratings = 0
                
                for item in ratings:
                    
                    rs = await item.locator('span').all()
                    
                    if rs:
                        stars_text = await rs[0].get_attribute("aria-label")
                        if stars_text:
                            pattern = r'\b\d+\b'
                            numbers = re.findall(pattern, stars_text)
                            
                            date_text = await rs[6].inner_text()
                            
                            if date_text:
                                try:
                                    review_date = datetime.strptime(date_text, '%B %d, %Y')
                                    limit_date = datetime.strptime(row['Date'], '%Y-%m-%d')
                                    
                                    if review_date <= limit_date and numbers:

                                        rating = int(numbers[0])
                                        num_ratings += 1
                                        sum_ratings += rating
                                        
                                            
                                except ValueError:
                                    print(f"Error parsing date: {date_text}")
                                    continue
                        else:
                            print(f"stars_text is {stars_text}. Skipping this rating.")
                       
                if num_ratings == 0:
                    mean = None
                else:
                    mean = sum_ratings / num_ratings
                    
                print(mean)
                df.at[index, 'Rating'] = round(mean, 2)
                df.at[index, 'numRatings'] = num_ratings
                
                print('sleep5')
                await asyncio.sleep(5)
                await browser.close()
                print('Browser closed')
                
        except Exception as e:
            print(f"An error occurred for book: {str(e)}")
            continue
                
    df.to_csv(f"conRatings.csv")

asyncio.run(main())
