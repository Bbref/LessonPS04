import requests
from bs4 import BeautifulSoup

WIKI_URL = "https://ru.wikipedia.org"

def search_wikipedia(query):
    search_url = f"{WIKI_URL}/w/index.php"
    params = {'search': query, 'title': 'Special:Search', 'profile': 'default', 'fulltext': 1, 'ns0': 1}
    response = requests.get(search_url, params=params)
    soup = BeautifulSoup(response.content, 'html.parser')
    results = soup.find_all('div', class_='mw-search-result-heading')
    if not results:
        print(f"Страница по запросу '{query}' не найдена.")
        return None
    first_result = results[0].find('a')['href']
    return f"{WIKI_URL}{first_result}"

def get_page_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find(id='firstHeading').text
    paragraphs = soup.find_all('p')
    links = soup.find(id='bodyContent').find_all('a', href=True)
    return title, paragraphs, links

def wrap_text(text, width=80):
    lines = []
    words = text.split()
    line = []
    current_length = 0
    for word in words:
        if current_length + len(word) + 1 > width:
            lines.append(' '.join(line))
            line = [word]
            current_length = len(word) + 1
        else:
            line.append(word)
            current_length += len(word) + 1
    if line:
        lines.append(' '.join(line))
    return '\n'.join(lines)

def print_page_summary(paragraphs):
    print("\n=== Summary ===")
    summary = ""
    for paragraph in paragraphs[:3]:  # Limit to the first 3 paragraphs for summary
        summary += paragraph.text
    print(wrap_text(summary))
    print("================\n")

def list_paragraphs(paragraphs):
    if not paragraphs:
        print("На странице нет параграфов.")
        return

    for i, paragraph in enumerate(paragraphs):
        print(f"\n=== Paragraph {i+1} ===")
        print(wrap_text(paragraph.text[:1000]))  # Ограничиваем вывод до 1000 символов
        print("================")

def list_links(links):
    if not links:
        print("На странице нет связанных страниц.")
        return

    link_titles = [link['title'] for link in links if link['href'].startswith('/wiki/') and 'title' in link.attrs]
    for i, title in enumerate(link_titles):
        print(f"{i+1}. {title}")

    while True:
        choice = input("Введите номер связанной страницы для перехода или 'b' для возврата: ").strip().lower()
        if choice == 'b':
            break
        if choice.isdigit() and 1 <= int(choice) <= len(link_titles):
            sub_url = f"{WIKI_URL}/wiki/{link_titles[int(choice) - 1]}"
            navigate_page(sub_url)
        else:
            print("Неверный ввод. Пожалуйста, попробуйте снова.")

def navigate_page(url):
    title, paragraphs, links = get_page_content(url)
    while True:
        print(f"\n=== {title} ===")
        print_page_summary(paragraphs)
        action = input("Выберите действие: 1 - Листать параграфы, 2 - Перейти на связанную страницу, 3 - Выйти: ").strip()
        if action == '1':
            list_paragraphs(paragraphs)
        elif action == '2':
            list_links(links)
        elif action == '3':
            break
        else:
            print("Неверный выбор. Пожалуйста, попробуйте снова.")

def main():
    query = input("Введите запрос для поиска на Википедии: ").strip()
    page_url = search_wikipedia(query)
    if page_url:
        navigate_page(page_url)

if __name__ == "__main__":
    main()
