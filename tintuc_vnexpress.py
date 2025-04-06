import requests
from bs4 import BeautifulSoup
import time
import schedule
from datetime import datetime

# Cấu hình Telegram Bot
TELEGRAM_BOT_TOKEN = '5880026221:AAHYTnqSnf3dR1HrrzPCysQWDYtjazTDbw4'
TELEGRAM_CHAT_ID = '940992533'
VNEXPRESS_URL = 'https://vnexpress.net/'


def get_latest_news():
    try:
        # Gửi request đến trang VNExpress
        response = requests.get(VNEXPRESS_URL)
        response.raise_for_status()

        # Phân tích HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Lấy các bài báo mới nhất (giả sử nằm trong thẻ h3 có class là 'title-news')
        news_items = soup.find_all('h3', class_='title-news', limit=3)

        latest_news = []
        for item in news_items:
            title = item.a.get('title', 'Không có tiêu đề')
            link = item.a.get('href', '#')
            latest_news.append({'title': title, 'link': link})

        return latest_news

    except Exception as e:
        print(f"Lỗi khi lấy tin tức: {e}")
        return []


def send_to_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print(f"Đã gửi tin nhắn đến Telegram lúc {datetime.now()}")
    except Exception as e:
        print(f"Lỗi khi gửi đến Telegram: {e}")


def job():
    print(f"Bắt đầu lấy tin tức lúc {datetime.now()}")
    news = get_latest_news()

    if news:
        message = "<b>3 BẢN TIN MỚI NHẤT TỪ VNEXPRESS:</b>\n\n"
        for idx, item in enumerate(news, 1):
            message += f"{idx}. <a href='{item['link']}'>{item['title']}</a>\n"

        send_to_telegram(message)
    else:
        send_to_telegram("Không thể lấy tin tức mới từ VNExpress.")


def main():
    # Lập lịch chạy mỗi phút
    schedule.every(30).minutes.do(job)

    # Chạy ngay lần đầu
    job()

    print("Chương trình đã bắt đầu. Nhấn Ctrl+C để dừng.")

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()