from bs4 import BeautifulSoup as soup

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
        <style>
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }

            .lunasima-regular {
                font-family: "Lunasima", sans-serif;
                font-weight: 400;
                font-size: 120%;
                font-style: normal;
                color: black;
                background-color: white;
                border-bottom-color: black;
            }

            .keep-together {
                page-break-inside: avoid;
            }

            .break-before {
                page-break-before: always;
            }

            .break-after {
                page-break-after: always;
            }

            .work {
                display: flex;
                flex-direction: column;
                padding: 1rem;
                align-items: center;
                justify-content: center;
                text-align: center;
            }

            .info {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }

            .preface {
                display: flex;
                width: 100%;
                margin-top: 1rem;
                line-height: 30px;
                justify-content: center;
                align-items: center;
                text-align: left;
            }

            .heading {
                text-decoration: none;
                margin-top: 0.1rem;
                margin-bottom: 0.1rem;
                font-weight: 400;
            }

            .byline {
                font-size: larger;
                padding-bottom: .5rem;
            }

            .title {
                font-size: xx-large;
            }

            .seperator {
                width: 100%;
                border-bottom-width: 1px;
                border-bottom-style: solid;
                justify-content: center;
                align-items: center;
                text-align: left;
            }

            .summary-text {
                margin-left: 15px;
                margin-top: 1rem;
            }

            .section-end {
                margin-top: 2rem;
                margin-bottom: 5rem;
                width: 100%;
                align-self: center;
                border-bottom-width: 2px;
                border-bottom-style: solid;
            }

            .chapters {
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: column;
            }

            .chapter {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }

            .chapter-title {
                margin-top: -3rem;    
            }

            .chapter-title > span {
                border-bottom-width: 1px;
                border-bottom-style: solid;
            }

            .content {
                text-decoration: none;
                font-weight: 400;
                justify-content: center;
                align-items: center;
                text-align: left;
                line-height: 1.5;
                font-size: 1em;
                width: 100%;
            }        

            .content > p {
                margin-top: 2rem;
                margin-bottom: 2rem;
            }
        </style>
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
