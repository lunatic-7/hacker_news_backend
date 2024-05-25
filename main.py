from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import requests
from bs4 import BeautifulSoup

# Hacker news is a website, where we get daily news of Programming community,
# It is a quite popular website. A lot of programmers visit this website to see
# daily news on it. There is one more thing there, (upvotes), Poeple often wants to see,
# That news which has most amount of upvotes on it, It means that, that news is quite
# important and in trend.
# So, we are gonna make a bot which will give us only that news which has more than 100 upvotes,
# by scraping the data from hacker news website.

app = FastAPI()

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


res = requests.get('https://news.ycombinator.com/news')
res2 = requests.get('https://news.ycombinator.com/news?p=2')  # Copied from 2nd page of hacker news
soup = BeautifulSoup(res.text, 'html.parser')
soup2 = BeautifulSoup(res2.text, 'html.parser')

links = soup.select('.titleline')
links2 = soup2.select('.titleline')
subtext = soup.select('.subtext')
subtext2 = soup2.select('.subtext')

main_links = []

for _ in links:
    main_links.append(_.find('a'))

for _ in links2:
    main_links.append(_.find('a'))

# for _ in main_links:
    # print(_.get('href', None))  # None is for default
    # print(_.getText())

mega_links = main_links
mega_subtext = subtext + subtext2


def sort_stories_by_votes(hnlist):
    return sorted(hnlist, key=lambda k: k['Votes'], reverse=True)


def create_custom_hn(links, subtext):
    hn = []
    for idx, item in enumerate(links):
        title = item.getText()
        href = item.get('href', None)  # None is for default
        vote = subtext[idx].select('.score')
        if len(vote):
            points = int(vote[0].getText().replace(' points', ''))
            if points > 99:
                hn.append({'Title': title, 'Link': href, 'Votes': points})
    return sort_stories_by_votes(hn)


@app.get("/get_news/")
async def generate_mcq_endpoint():
    try:
        # Call the function from your existing package
        news = create_custom_hn(mega_links, mega_subtext)        
        return news
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)