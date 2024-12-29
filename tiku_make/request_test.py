import json
import requests

# url ="https://easylearn.baidu.com/edu-web/config/getconfig?key=bgk_download&token=521c23e9afb70400"
url = r"https://easylearn.baidu.com/edu-web/bgk/searchlist?query=%E4%BA%BA%E7%94%9F%E8%A7%82%E7%9A%84%E4%B8%BB%E8%A6%81%E5%86%85%E5%AE%B9%E5%8C%85%E6%8B%AC%E5%AF%B9%EF%BC%88%EF%BC%89%E7%AD%89%E9%97%AE%E9%A2%98%E7%9A%84%E6%A0%B9%E6%9C%AC%E7%9C%8B%E6%B3%95%E3%80%82A.%E4%BA%BA%E7%94%9F%E7%9B%AE%E7%9A%84B.%E4%BA%BA%E7%94%9F%E6%80%81%E5%BA%A6C.%E4%BA%BA%E7%94%9F%E4%BB%B7%E5%80%BCD.%E4%BA%BA%E7%94%9F%E6%84%8F%E4%B9%89&rn=10&pn=0"

"""
GET /edu-web/bgk/searchlist?query=%E4%BA%BA%E7%94%9F%E8%A7%82%E7%9A%84%E4%B8%BB%E8%A6%81%E5%86%85%E5%AE%B9%E5%8C%85%E6%8B%AC%E5%AF%B9%EF%BC%88%EF%BC%89%E7%AD%89%E9%97%AE%E9%A2%98%E7%9A%84%E6%A0%B9%E6%9C%AC%E7%9C%8B%E6%B3%95%E3%80%82A.%E4%BA%BA%E7%94%9F%E7%9B%AE%E7%9A%84B.%E4%BA%BA%E7%94%9F%E6%80%81%E5%BA%A6C.%E4%BA%BA%E7%94%9F%E4%BB%B7%E5%80%BCD.%E4%BA%BA%E7%94%9F%E6%84%8F%E4%B9%89&rn=10&pn=0 HTTP/1.1
Host: easylearn.baidu.com
Connection: keep-alive
sec-ch-ua-platform: "Android"
User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 EdgA/131.0.0.0
Accept: application/json, text/plain, */*
sec-ch-ua: "Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"
sec-ch-ua-mobile: ?0
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://easylearn.baidu.com/edu-page/tiangong/bgklist?query=%E4%BA%BA%E7%94%9F%E8%A7%82%E7%9A%84%E4%B8%BB%E8%A6%81%E5%86%85%E5%AE%B9%E5%8C%85%E6%8B%AC%E5%AF%B9%EF%BC%88%EF%BC%89%E7%AD%89%E9%97%AE%E9%A2%98%E7%9A%84%E6%A0%B9%E6%9C%AC%E7%9C%8B%E6%B3%95%E3%80%82A.%E4%BA%BA%E7%94%9F%E7%9B%AE%E7%9A%84B.%E4%BA%BA%E7%94%9F%E6%80%81%E5%BA%A6C.%E4%BA%BA%E7%94%9F%E4%BB%B7%E5%80%BCD.%E4%BA%BA%E7%94%9F%E6%84%8F%E4%B9%89
Accept-Encoding: gzip, deflate, br, zstd
Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7
"""
headers = {
    "Host": "easylearn.baidu.com",
    "Connection": "keep-alive",
    "sec-ch-ua-platform": '"Android"',
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 EdgA/131.0.0.0",
    "Accept": "application/json, text/plain, */*",
    "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://easylearn.baidu.com/edu-page/tiangong/bgklist?query=%E4%BA%BA%E7%94%9F%E8%A7%82%E7%9A%84%E4%B8%BB%E8%A6%81%E5%86%85%E5%AE%B9%E5%8C%85%E6%8B%AC%E5%AF%B9%EF%BC%88%EF%BC%89%E7%AD%89%E9%97%AE%E9%A2%98%E7%9A%84%E6%A0%B9%E6%9C%AC%E7%9C%8B%E6%B3%95%E3%80%82A.%E4%BA%BA%E7%94%9F%E7%9B%AE%E7%9A%84B.%E4%BA%BA%E7%94%9F%E6%80%81%E5%BA%A6C.%E4%BA%BA%E7%94%9F%E4%BB%B7%E5%80%BCD.%E4%BA%BA%E7%94%9F%E6%84%8F%E4%B9%89",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
}

res = requests.get(url, headers=headers, verify=False)
print(f"status_code: {res.status_code}")
res_json = res.json()
print(f"text: {res_json}")
with open("./analyze/searchlist.json", "w") as f:
    f.write(json.dumps(res_json, indent=4, ensure_ascii=False))
