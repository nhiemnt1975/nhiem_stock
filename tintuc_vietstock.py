import requests
from bs4 import BeautifulSoup
import schedule
import time
from datetime import datetime
import pytz

# Cấu hình
TELEGRAM_BOT_TOKEN = '5880026221:AAHYTnqSnf3dR1HrrzPCysQWDYtjazTDbw4'
TELEGRAM_CHAT_ID = '940992533'
VIETSTOCK_URL = 'https://vietstock.vn/chu-de/1-2/moi-cap-nhat.htm'

# Biến toàn cục
sent_news = set()
last_request_time = 0
request_count = 0


def get_latest_news():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        print(f"Đang kết nối đến {VIETSTOCK_URL}...")
        response = requests.get(VIETSTOCK_URL, headers=headers, timeout=10)
        response.raise_for_status()

        print("Đã nhận được phản hồi, đang phân tích nội dung...")
        soup = BeautifulSoup(response.text, 'html.parser')

        news_items = soup.select('.article-list .article-item') or \
                     soup.find_all('div', class_=lambda x: x and 'news' in x.lower())

        print(f"Tìm thấy {len(news_items)} tin tức")

        news_list = []
        for item in news_items[:10]:
            try:
                title_elem = item.select_one('a[href]')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem['href']
                    if link.startswith('/'):
                        link = f'https://vietstock.vn{link}'
                    news_id = hash(link)
                    if news_id not in sent_news:
                        news_list.append({'title': title, 'link': link, 'id': news_id})
                        if len(news_list) >= 3:
                            break
            except Exception as e:
                print(f"Lỗi khi xử lý mục tin: {e}")

        return news_list if news_list else None

    except Exception as e:
        print(f"Lỗi khi lấy tin tức: {e}")
        return None


def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, data=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Lỗi khi gửi Telegram: {e}")
        return False


def update_request_count():
    global last_request_time, request_count

    current_time = time.time()
    # Nếu đã qua 1 phút kể từ lần request cuối, reset counter
    if current_time - last_request_time >= 60:
        request_count = 0
        last_request_time = current_time

    request_count += 1
    print(f"[DEBUG] Request count: {request_count}")

    # Nếu vượt quá 2 request trong 1 phút
    if request_count > 2:
        error_msg = "⚠️ CẢNH BÁO: Quá nhiều request (3 lần/phút)"
        send_telegram_message(error_msg)
        return True
    return False


def job():
    if update_request_count():
        print("Vượt quá giới hạn request, bỏ qua lần này")
        return

    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(tz)
    time_str = now.strftime("%d/%m/%Y %H:%M:%S")
    print(f"\n=== Bắt đầu lấy tin lúc {time_str} ===")

    news = get_latest_news()
    if news:
        message = f"📰 Tin mới nhất ({time_str}):\n"
        for item in news:
            message += f"- {item['title']}\n{item['link']}\n\n"
            sent_news.add(item['id'])

        if not send_telegram_message(message):
            print("Gửi thất bại, thử lại sau 5s...")
            time.sleep(5)
            send_telegram_message(f"[Gửi lại] {message}")


def main():
    print("Khởi động chương trình kiểm tra rate limit")
    print("Chế độ TEST - chạy mỗi 1 phút")

    # Test kết nối ban đầu
    if get_latest_news():
        print("Kết nối thành công")

    # Chạy ngay lần đầu
    job()

    # Lập lịch mỗi 60 phút
    schedule.every(60).minutes.do(job)

    print("Đang chạy...")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
