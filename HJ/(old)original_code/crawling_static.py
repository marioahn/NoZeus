from bs4 import BeautifulSoup
import requests
import csv
import warnings

# 경고를 무시
warnings.filterwarnings(
    "ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning
)

# 프록시 설정
# https://brdta.com/kimfl 가입링크
host = "brd.superproxy.io:22225"
user_name = "brd-customer-hl_fc8f72f8-zone-web_unlocker_hj"
password = "jjiaapr0kbv2"
proxy_url = f"http://{user_name}:{password}@{host}"

proxies = {"http": proxy_url, "https": proxy_url}


def find_list(page_num, url):
    response = requests.get(url, proxies=proxies, verify=False)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select("[class=search-product]")  # 광고제거

    link_list = []

    rank = 1
    for item in items:
        name = item.select_one(".name")
        price = item.select_one(".price-value")  # 리퍼상품일 경우 None
        if not price:
            continue

        link = f"https://www.coupang.com{item.a['href']}"
        thumb = item.select_one(".search-product-wrap-img")

        name = "" if not name else name.text
        price = "" if not price else price.text
        if thumb.get("data-img-src"):
            img_url = f"https:{thumb.get('data-img-src')}"
        else:
            img_url = f"https:{thumb.get('src')}"
        img_url = img_url.replace("230x230ex", "700x700ex")

        writer.writerow([name, price, link, img_url])

        print(f"{page_num}페이지: {rank}위 {name} {price}원, {link}")
        print()

        link_list.append(link)

        rank += 1

    return link_list


def pdp(url):
    response = requests.get(url, proxies=proxies, verify=False)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    brand = soup.select_one(".prod-brand-name")
    title = soup.select_one(".prod-buy-header__title").text.strip()
    seller = soup.select_one(".prod-sale-vendor-name")
    prod_other_seller_count = soup.select_one(".prod-other-seller-count")

    offer_badge_item = soup.select_one(".offer-badge-item")  # 리퍼 제품에 붙음

    prod_sale_price = soup.select_one(".prod-sale-price")  # 현재 판매가. text로 추출할것
    prod_coupon_price = soup.select_one(".prod-coupon-price")  # 회원 할인가. text로 추출할것

    prod_option_item = soup.select(".prod-option__item")  # 옵션

    prod_description = soup.select(".prod-description .prod-attr-item")  # 상세정보

    brand = "" if not brand else brand.text.strip()
    seller = "로켓배송" if not seller else seller.text.strip()

    if offer_badge_item:
        print(f"{offer_badge_item.string} 입니다.\n")

    prod_info_text = ""

    if brand:
        prod_info_text += f"브랜드: {brand}, "

    if title:
        prod_info_text += f"제품명: {title}"

    # 현재 판매가
    if prod_sale_price:
        prod_sale_price = prod_sale_price.select_one(".total-price").text.strip()
        prod_info_text += f", 현재 판매가: {prod_sale_price}"

    # 회원 할인가
    if prod_coupon_price:
        prod_coupon_price = prod_coupon_price.select_one(".total-price").text.strip()
        prod_info_text += f", 회원 할인가: {prod_coupon_price}"

    if seller:
        prod_info_text += f", 판매자: {seller}"

    if prod_other_seller_count:
        prod_other_seller_count = (
            "없음"
            if not prod_other_seller_count.text
            else prod_other_seller_count.text.strip()
        )
        prod_info_text += f", 다른 판매자: {prod_other_seller_count}"

    print(prod_info_text)

    # 옵션
    if prod_option_item:
        option_list = []
        for i in prod_option_item:
            option_list.append(
                f'{i.select_one(".title").string.strip()}: {i.select_one(".value").string.strip()}'
            )
        prod_option_item = ", ".join(option_list)
        print(prod_option_item)
    else:
        prod_option_item = None

    # 상세정보
    if prod_description:
        description_list = []
        for text in prod_description:
            description_list.append(text.string)
        prod_description = ", ".join(description_list)
        print(prod_description)
    else:
        prod_description = None

    writer.writerow(
        [
            brand,
            title,
            prod_sale_price,
            prod_coupon_price,
            seller,
            prod_other_seller_count,
            prod_option_item,
            prod_description,
            url,
        ]
    )


keyword = input("Enter product: ")
page_num = 1

link_list = []

with open(
    f"coupang_discovery_{keyword}.csv", "w", newline="", encoding="utf-8"
) as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Name", "Price", "Link", "Img_url"])
    for page_num in range(1, 4):
        url = f"https://www.coupang.com/np/search?component=&q={keyword}&page={page_num}&listSize=72"
        if not page_num:
            break
        print(page_num)
        link_list += find_list(page_num, url)

print(link_list)
print(f"{len(link_list)}개 {keyword} 상제페이지 스크랩 시작")
print()

with open(f"coupang_pdp_{keyword}.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(
        ["브랜드", "제품명", "현재 판매가", "회원 할인가", "판매자", "다른 판매자", "옵션", "상세정보", "URL"]
    )
    for e, url in enumerate(link_list, 1):
        print(f"<<<<<{e}>>>>>")
        print(url)
        pdp(url)
        print()

print("finished")