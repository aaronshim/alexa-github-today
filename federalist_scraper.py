import re
import scrapy


class FederalistScraper(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://avalon.law.yale.edu/18th_century/fed01.asp',
    ]

    def parse(self, response):

        # Helper
        strip_list = lambda strs : [ x.strip() for x in strs ]
        remove_newlines_list = lambda strs : [ re.sub(r'\n', ' ', x) for x in strs ]

        # Grab which # of The Federalist Papers this is
        document_title = response.css('div.document-title::text').extract_first().strip()
        number = re.search(r'\d+', document_title).group()

        # Grab the title / subtitle / author
        title_box =  remove_newlines_list(strip_list(response.css('h3::text').extract()))
        if not title_box: # sneaky, sneaky!
            title_box = remove_newlines_list(strip_list(response.css('h4::text').extract()))
        title = " ".join(title_box[:-2])
        subtitle = title_box[-2]
        author = title_box[-1]

        # Grab the content
        paragraphs = []
        for paragraph in response.css('p'):
            paragraph_text = " ".join(remove_newlines_list(strip_list(paragraph.css('::text').extract())))
            # This precedes the bibliography, which we do not want
            if re.match(r'PUBLIUS\.', paragraph_text):
                break
            else:
                paragraphs.append(paragraph_text)
        
        # Our results of scraping this page
        yield {
            'number': number,
            'title': title,
            'subtitle': subtitle,
            'author': author,
            'paragraphs': paragraphs
        }

        # Move on to the next page
        next_page = response.xpath('//a[contains(text(), "Next Document")]/@href').extract_first()
        if next_page is not None:
            yield response.follow(next_page, self.parse)