import json
from bs4 import BeautifulSoup
import bleach
def filter_data(tag):

    with open(tag+'.txt', 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Phân tích cú pháp HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Lọc các thẻ <a> có class="title"
    title_links = soup.find_all('a', class_='title')

    # Tạo danh sách để lưu trữ văn bản và liên kết
    responses = []

    # Lưu trữ thông tin và thêm vào danh sách
    for link in title_links:
        # Lấy văn bản và liên kết
        text = link.text
        href = link.get('href')

        # Tạo URL đầy đủ bằng cách thêm "https://muaban.net" vào href
        full_href = f"https://muaban.net{href}"

        # Kết hợp text và href theo định dạng mong muốn
        combined = f"{text} {full_href}"

        # Thêm dữ liệu vào danh sách
        responses.append(combined)

    # Tạo cấu trúc JSON theo yêu cầu
    with open('../DataJson/data.json', 'r+', encoding='utf-8') as data:
        json_file = json.load(data)
        intents = json_file["intents"]
        for intent in intents:
            if intent["tag"] == tag:
                intent["responses"] = responses


    # Ghi dữ liệu JSON vào tệp
    with open('../DataJson/data.json', 'w', encoding='utf-8') as data:
        json.dump(json_file,data,ensure_ascii=False)

    print("Dữ liệu đã được lưu vào 'data.json'")

