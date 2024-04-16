import requests
import json
from FiltersData import filter_data


def scrape_data(tag):
    # URL cần lấy dữ liệu
    url = 'https://muaban.net/bat-dong-san/quan-'+ tag +'-ha-noi?q=hanoi'

    # Thông tin xác thực
    username = 'vietanhls113'
    api_key = 'RKnDq5Q4MeFSUDN8K6kMWbW8E'

    # Địa chỉ endpoint của API
    api_endpoint = "http://api.scraping-bot.io/scrape/raw-html"

    # Tùy chọn cấu hình
    options = {
        "useChrome": False,  # Đặt thành True nếu muốn sử dụng headless Chrome để render JavaScript.
        "premiumProxy": False,  # Đặt thành True nếu muốn sử dụng proxy cao cấp.
        "proxyCountry": None,  # Chọn proxy theo quốc gia (ví dụ: proxyCountry: "FR").
        "waitForNetworkRequests": False  # Đợi cho hầu hết các yêu cầu mạng Ajax hoàn thành.
    }

    # Chuẩn bị payload dưới dạng JSON
    payload = json.dumps({"url": url, "options": options})

    # Cài đặt tiêu đề của yêu cầu
    headers = {
        'Content-Type': "application/json"
    }

    # Gửi yêu cầu POST tới API endpoint
    response = requests.post(api_endpoint, data=payload, auth=(username, api_key), headers=headers)

    # Lưu nội dung của phản hồi vào tệp văn bản
    with open(tag+'.txt', 'w', encoding='utf-8') as file:
        file.write(response.text)

    # Gọi hàm filter_data để xử lý dữ liệu trong 'response_data.txt'
    filter_data(tag)


# Gọi hàm để chạy
scrape_data("hoang-mai")
