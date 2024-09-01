from bs4 import BeautifulSoup as soup

data = {
    "info": {
        "title": "",
        "author": "",
        "summary": "",
    },
    "content": [
        {
            "chapterTitle": "",
            "chapterContent": [
                ""
            ]
        },
        {
            "chapterTitle": "",
            "chapterContent": [
                ""
            ]
        },
    ]
}

chapter_html_template = """
    <div class="chapter keep-together">
        <h3 class="chapter-title heading"><span>Chapter <replace id="chapterNumber"></replace></span>: <replace id="chapterName"></replace></h3>
        <div class="content">
            <replace id="content"></replace>
        </div>
    </div>
    <div class="break-after seperator section-end"></div>
"""


def main():
    with open("template.html", "r") as file:
        # get the html file raw string
        html_template_raw = "".join(file.readlines())

        # parse it to a bs4 object
        parsed_html = soup(html_template_raw, 'html.parser')

        # parse the individual 'chapter' html peice to bs4 object 
        parsed_chapter_template = soup(chapter_html_template, 'html.parser')

        # find all <replace> tags in the main html file 
        replace_tags = parsed_html.body.find_all('replace')

        # get the work info object from supplied data json file
        info_object = data.get("info")

        # get the work content array from supplied data json file
        content_array = data.get("content")

        # find the 'div' that has the class 'chapters'
        main_work = parsed_html.find('div', class_='chapters')

        for index, tag in enumerate(replace_tags):
            # loop over <replace> tags and replace the fields based on index
            # index - 0 => title
            # index - 1 => author
            # index - 2 => summary
            tag.replace_with(info_object.get(list(info_object.keys())[index]))

        # loop over the content array supplied for the chapters' individual data
        for chapter_number, chapter_data in enumerate(content_array):
            # grap a deep copy of the 'chapter' html peice to mutate later
            template_copy = parsed_chapter_template.__copy__()

            # find all tags to be replaced in the copy above
            replace_tags_chapter = template_copy.find_all('replace')
            
            # loop over tags to be replaced
            for i, rep_tag in enumerate(replace_tags_chapter):
                if i == 0:
                    # replace the chapter number with the loop number called 'chapter_number'
                    rep_tag.replace_with(str(chapter_number+1))
                elif i == 1:
                    # replace the chapter name with the name in the object instance
                    rep_tag.replace_with(chapter_data.get("chapterTitle"))
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

        with open("output.html", "w") as file: 
            # write the mutated html into a new file
            file.write(str(parsed_html.prettify()))

if __name__ == "__main__":
    main()