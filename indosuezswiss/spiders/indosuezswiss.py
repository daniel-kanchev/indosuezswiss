import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from indosuezswiss.items import Article


class IndosuezswissSpider(scrapy.Spider):
    name = 'indosuezswiss'
    start_urls = ['https://switzerland.ca-indosuez.com/a-la-une/actualites']

    def parse(self, response):
        links = response.xpath('//a[@class="block-article--link"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//div[@class="listeNews__more--wrapper"]//a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="block-articleTitle--title mb-30"]//h3/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="block-articleTitle--author mb-30"]/p/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="block-wysiwg-text"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
