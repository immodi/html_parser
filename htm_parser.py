from bs4 import BeautifulSoup as soup
import json

chapter_html_template = """
    <div class="chapter keep-together">
        <h3 class="chapter-title heading"><replace id="chapterName"></replace></h3>
        <div class="content">
            <replace id="content"></replace>
        </div>
    </div>
    <div class="break-after seperator section-end"></div>
"""

html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Novel Template</title>
        <link rel="stylesheet" href="style.css">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Lunasima:wght@400;700&display=swap" rel="stylesheet">
    </head>
    <body>
        <div class="work lunasima-regular">
            <div class="info">
                <p class="title heading">
                    <replace id="title"></replace>
                </p>
                <p class="byline heading">
                    <p class="heading"><replace id="author"></replace></p>
                </p>
                <div class="preface">
                    <div class="summary">
                        <p class="heading byline seperator">Summary:</p>
                        <blockquote>
                            <p class="summary-text"><replace id="summary"></replace></p>
                        </blockquote>
                    </div>
                </div>
            </div>
            
            <div class="seperator section-end"></div>

            <div class="chapters" role="article">
            </div>
        </div>
    </body>
    </html>
"""


def parser(data: object, output_file_name: str):
    # parse the html raw tempelate string to a bs4 object
    parsed_html = soup(html_template, 'html.parser')

    # parse the individual 'chapter' html peice to bs4 object 
    parsed_chapter_template = soup(chapter_html_template, 'html.parser')

    return extract(data, parsed_html, parsed_chapter_template, output_file_name)
    

def extract(data, parsed_html, parsed_chapter_template, output_file_name):
   # find all <replace> tags in the main html file 
    replace_tags = parsed_html.body.find_all('replace')

    # get the work info object from supplied data json file
    info_object = data.get("info")

    # get the work content array from supplied data json file
    content_array = data.get("content")

    # find the 'div' that has the class 'chapters'
    main_work = parsed_html.find('div', class_='chapters')

    return process(replace_tags, info_object, content_array, main_work, parsed_html, parsed_chapter_template, output_file_name)


def process(replace_tags, info_object, content_array, main_work, parsed_html, parsed_chapter_template, output_file_name):
    for index, tag in enumerate(replace_tags):
        # loop over <replace> tags and replace the fields based on index
        # index - 0 => title
        # index - 1 => author
        # index - 2 => summary
        tag.replace_with(info_object.get(list(info_object.keys())[index]))

    # loop over the content array supplied for the chapters' individual data
    for chapter_data in content_array:
        # grap a deep copy of the 'chapter' html peice to mutate later
        template_copy = parsed_chapter_template.__copy__()

        # find all tags to be replaced in the copy above
        replace_tags_chapter = template_copy.find_all('replace')
        
        # loop over tags to be replaced
        for i, rep_tag in enumerate(replace_tags_chapter):
            if i == 0:
                # create a <span>
                span = template_copy.new_tag('span')
                
                # insert the chapter title in the <span>
                span.insert(0, chapter_data.get("chapterTitle"))

                # insert the <span> in the document
                rep_tag.parent.insert(0, span)

                # self-destruct the <replace> tag
                rep_tag.decompose()
            else:
                # lastly loop over the chapters paragraphs supplied in the data json object
                for p_i, para in enumerate(chapter_data.get("chapterContent")):
                    # make a new 'p' tag for each string in the 'chapterContent' array
                    inserted_para = template_copy.new_tag('p')
                    
                    # add the paragraph data from the data json object to the new tag
                    inserted_para.insert(0, para)

                    # insert the new 'p' tag to the parent of the <replace> element which is the current 'chapter'
                    rep_tag.parent.insert(p_i+1, inserted_para)

                # delete the replace tag when finished 
                rep_tag.decompose()
        
        # insert the mutated chapter html into the last index of the 'div' classed 'chapters'
        main_work.insert(main_work.contents.__len__()+1, template_copy)
    
    return export(parsed_html, output_file_name)


def export(parsed_html, output_file_name):
    with open(f"{output_file_name}.html", "w") as file: 
        # write the mutated html into a new file
        file.write(str(parsed_html.prettify()))


def data_object_maker(title: str, author: str, summary: str, chapter_titles_array: list, chapter_content_array: list):
    data = {}
    
    data["info"] = {
        "title": title,
        "author": author,
        "summary": summary
    }

    data["content"] = [{
        "chapterTitle": chapter_titles_array[index],
        "chapterContent": chapter_content_array[index]
    } for index in range(len(chapter_content_array))]

    return data


title = "Second Try Idol"
author = "Tinta"
summary = "Six years after being ousted from his debut group due to facial burns, Suh Hyun-Woo finds himself regressing back to his days as a trainee, engulfed once more in the world of ruthless competition. This time, he's determined: he will make his debut, no matter what it takes"
with open('sample.json', 'r') as openfile:
    json_object = json.load(openfile)

data = data_object_maker(title, author, summary, json_object.get("titles"), json_object.get("content"))
parser(data, 'output')