import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import json

def crawl_sclocal_page(page_num=1):
    """
    순천로컬푸드 함께가게 웹사이트의 특정 페이지에서 상품명과 가격 정보를 크롤링합니다.
    
    Args:
        page_num (int): 크롤링할 페이지 번호
        
    Returns:
        list: 상품 정보 (상품명, 가격) 리스트
    """
    # 기본 URL과 페이지 번호를 조합하여 크롤링할 URL 생성
    
    if page_num == 1:
        url = "https://sclocal.kr/?pn=product.list&_event=type&typeuid=15"
    else:
        url = f"https://sclocal.kr/?pn=product.list&_event=type&typeuid=15&listpg={page_num}"
    
    # HTTP 요청 헤더 설정 (웹사이트가 봇으로 인식하지 않도록)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    
    # 웹 페이지 요청
    response = requests.get(url, headers=headers)
    
    # 응답 상태 확인
    if response.status_code != 200:
        print(f"페이지 {page_num} 요청 실패: 상태 코드 {response.status_code}")
        return []
    
    # HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 상품 목록 컨테이너 찾기
    product_items = soup.select('.item_box')
    
    products = []
    
    # 각 상품 정보 추출
    for item in product_items:
        try:
            # 상품명 추출
            name_tag = item.select_one('.item_name')
            if name_tag:
                name = name_tag.get_text(strip=True)
            else:
                name = "상품명 없음"
            
            # 가격 추출
            # HTML 구조를 확인하여 클래스가 "won"인 span 태그를 직접 선택
            price_tag = item.select_one('.won')
            if price_tag:
                price_text = price_tag.get_text(strip=True)
                # 가격에서 숫자만 추출
                price = re.sub(r'[^\d]', '', price_text)
            else:
                price = "가격 정보 없음"
            
            # 상품 정보 저장
            products.append({
                '상품명': name,
                '가격': price
            })
            
        except Exception as e:
            print(f"상품 정보 추출 중 오류 발생: {e}")
    
    print(f"페이지 {page_num}에서 {len(products)}개 상품 정보 추출 완료")
    return products

def crawl_all_pages(max_pages=10):
    """
    여러 페이지의 상품 정보를 크롤링합니다.
    
    Args:
        max_pages (int): 크롤링할 최대 페이지 수
        
    Returns:
        DataFrame: 모든 상품 정보가 담긴 데이터프레임
    """
    all_products = []
    
    for page_num in range(1, max_pages + 1):
        print(f"페이지 {page_num} 크롤링 중...")
        page_products = crawl_sclocal_page(page_num)
        
        # 더 이상 상품이 없으면 종료
        if not page_products:
            print(f"페이지 {page_num}에 상품이 없습니다. 크롤링을 종료합니다.")
            break
        
        all_products.extend(page_products)
        
        # 서버에 부담을 주지 않기 위해 잠시 대기
        time.sleep(1)
    
    # 데이터프레임으로 변환
    df = pd.DataFrame(all_products)
    return df

def save_to_json(df, filename='sclocal_products.json'):
    """
    크롤링한 데이터를 JSON 파일로 저장합니다.
    
    Args:
        df (DataFrame): 저장할 데이터프레임
        filename (str): 저장할 파일명
    """
    # DataFrame을 JSON 형식으로 변환 (레코드 리스트 형태로)
    df.to_json(filename, orient='records', indent=4, force_ascii=False)
    print(f"데이터가 {filename}에 저장되었습니다.")

if __name__ == "__main__":
    # 크롤링 실행
    print("순천로컬푸드 함께가게 상품 정보 크롤링을 시작합니다...")
    products_df = crawl_all_pages(max_pages=5)  # 최대 5페이지까지 크롤링
    
    # 결과 출력
    print(f"\n총 {len(products_df)}개 상품 정보를 크롤링했습니다.")
    print("\n상품 정보 샘플:")
    print(products_df.head())
    
    # JSON 파일로 저장
    save_to_json(products_df)
