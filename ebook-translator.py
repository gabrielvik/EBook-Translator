import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup, NavigableString
import openai

def translate_text(text, source_lang, target_lang):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a book translator. You are to translate a snippet of a book into a given language. Respond only with the translated text."},
                {"role": "user", "content": f"Translate this text from {source_lang} to {target_lang}: {text}"}
            ],
            max_tokens=2048,
            temperature=0.5
        )
        translated_text = response.choices[0].message['content'].strip()
        return translated_text
    except Exception as e:
        print(f"Error during translation for text '{text}': {str(e)}")
        return text

def should_translate(text):
    if text.isdigit() or len(text) <= 2:
        return False
    return True

def process_item(item, source_lang, target_lang):
    soup = BeautifulSoup(item.get_content(), 'html.parser')
    for element in soup.find_all(text=True):
        if isinstance(element, NavigableString):
            parent_tag = element.parent.name
            if parent_tag in ['style', 'script', 'head', 'title', 'meta', '[document]']:
                continue
            original_text = element.strip()
            if original_text and should_translate(original_text):
                translated_text = translate_text(original_text, source_lang, target_lang)
                element.replace_with(NavigableString(translated_text))
    return str(soup)

def translate_epub(file_path, source_lang, target_lang):
    book = epub.read_epub(file_path)
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            translated_html = process_item(item, source_lang, target_lang)
            item.set_content(translated_html.encode('utf-8'))
    new_file_path = f"translated_{target_lang}_" + os.path.basename(file_path)
    epub.write_epub(new_file_path, book, {})
    print(f"Translated EPUB has been saved to: {new_file_path}")

def main():
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if not openai.api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        return
    file_path = input("Enter EPUB file path: ")
    source_lang = input("Enter source language code (e.g., 'English'): ")
    target_lang = input("Enter target language code (e.g., 'Swedish'): ")
    translate_epub(file_path, source_lang, target_lang)

if __name__ == "__main__":
    main()
