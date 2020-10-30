#!/usr/bin/env python3




def docx_parser(proposal):
    doc = Document(proposal.current_doc_name)
    # doc.save('media/695614.docx')

    for content in doc.paragraphs:
        if content.style.name == 'Heading 2':
            try:
                proposal.get_next_title_id()
            except StopIteration:
                return True
        elif not content.text:
            pass
        else:
            proposal.store_content(content.text)


def test_parser():
    doc = Document('media/154171.docx')
    # doc.save('media/695614.docx')
    for content in doc.paragraphs:
        if content.style.name == 'Heading 2':
            print('its a header')
        elif not content.text:
            print('1')
        else:
            print(content.text)


if __name__ == "__main__":
    test_parser()
