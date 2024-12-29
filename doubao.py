import requests
import json
from api.logger import logger



# 截止2024.12.27,当前32k豆包模型计费价格为0.0008/ktokens输入，0.002/ktokens输出，
# 一次答题约为1ktokens,根据测试，其中0.0008*853/1000+0.002*187/1000～=0.00105元
# 成本大概在946.6次答题/元左右
# 目前火山引擎官方每个模型提供的免费额度为500ktokens，即单个模型可用于免费答题约500次
def talk_by_openai_compatible(user_content, api_url, model_endpoint, api_key, system_prompt=""):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"  # 假设使用 Bearer Token 认证，根据实际情况修改
    }
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_content})

    data = {
        "model": model_endpoint,
        "messages": messages,
        "max_tokens": 2000  # 根据需要调整生成的最大 tokens 数
    }
    res = requests.post(api_url, headers=headers, json=data)
    logger.debug(f"status_code:{res.status_code}")
    if res.status_code < 400:
        json_data = res.json()
        json_data_str = json.dumps(json_data, indent=4, ensure_ascii=False)
        logger.debug(f"json data:{json_data_str}")
        output_data =  json_data["choices"][0]["message"]["content"]
        return output_data, json_data["usage"]["total_tokens"]
    logger.error(f"api error: {res.text}")
    return None, 0



json_format = {"question_check_point": "题目考察点,例如：'宿舍内盗'的定义\r马克思名言的背诵\r考察是否认同题意，送分题\r考察常识",
               "question_loss_point": "丢分点，例如：题目中使用了双重否定，容易误解\r题目中使用了生僻词汇\r题目前半部分是场景定义，但却理解成了需要判断的内容\r没有考虑国内大学生情况，如国内宿舍不能使用大功率电器",
               "depend_message":"每个选项的依据分析",
               "answer":"返回答案或选项原内容，完形填空题填入答案,多个答案、选项以回车符\r区分,例如：具体的人\r社会\r社会\r社会",
               }

q_info_template = {"question":"人生观的主要内容包括对( )等问题的根本看法。",
 "options":"\rA人生价值\rB人生意义\rC人生目的\rD人生态度",
}
response_template = {
"depend_message": "A人生价值：人生观的重要组成部分，探讨人生的意义和价值所在，即个体生命存在的价值体现。C人生目的：明确人一生所追求的目标和方向，是人生观的核心要素之一，决定着人生道路的走向。D人生态度：反映人们对待生活的基本心态和行为倾向，积极或消极的人生态度会影响个体的生活体验和发展，也是人生观的关键方面。B人生意义表述较为宽泛模糊，未精准涵盖人生观主要内容的特定范畴。",
"answer": "A人生价值\rC人生目的\rD人生态度"
}

q_info_template2 = {'id': '404478301', 
                    'leeson_name': '思想道德与法治（2024）',
                    'chapter_name': '3.1.1.1 马克思主义关于人的本质的认识',
                    'title': '1【填空题】马克思指出:“人的本质不是单个人所固有的抽象物，在其 现实性上，它是____。”', 
                    'options': '', 
                    'type': 'completion', 
                    'answerField': {'answer404478301': '', 'answertype404478301': '2'}}
response_template2 = {
    "depend_message": "根据输入字典信息分析，并从题目中的'填空题'和type:'completion'来看，这是一题完形填空题，需要根据已知信息和个人经验填入合适答案，从题目形式来看，这是一句马克思的名人名言，属于固定答案的填空题，从已知课程名称和章节名称无法得出结论，'options'中没有可选项，我将依据自身经验尝试作答",
    "answer": "一切社会关系的总和"
}
q_info_template3 = {
    "question":"】所谓宿舍内盗，即作案人员非本宿舍或本宿舍楼内的人员，其基本特征是撬门破锁进入宿舍内进行盗窃。",
    "options":"A对\rB错",
}
response_template3 = {
    "depend_message": "这一题属于概念定义题，考察'宿舍内盗'的定义，也考察对'宿舍内盗'的特征的理解，国内宿舍到处是监控，校园撬锁这种行为很容易被查到，所以是错的",
    "answer": "错"
}
def dump(obj):
    return json.dumps(obj, indent=4, ensure_ascii=False)
system_prompt = f"""请按照指定格式返回结果,以下为指定格式(json)返回结果: {dump(json_format)}
示例1:
user>>:\n{dump(q_info_template)}
assistant>>:\n{dump(response_template)}
示例2:
user>>:\n{dump(q_info_template2)}
assistant>>:\n{dump(response_template2)}
示例3:
user>>:\n{dump(q_info_template3)}
assistant>>:\n{dump(response_template3)}
"""

def query_answer_with_ai(q_info, config_dict):
    global system_prompt
    api_url = config_dict["api_url"]
    model_endpoint = config_dict["model_endpoint"]
    api_key = config_dict["api_key"]
    system_prompt = config_dict.get("system_prompt", system_prompt)
    if isinstance(q_info, dict) or isinstance(q_info, list):
        user_content = dump(q_info)
    else:
        user_content = q_info
    logger.debug(f"用户输入: {user_content}")
    content, use_tokens = talk_by_openai_compatible(user_content=user_content,
                                api_url=api_url, model_endpoint=model_endpoint, api_key=api_key, 
                                system_prompt=system_prompt)
    if content:
        answer = json.loads(content)["answer"]
        logger.info(f"ai答案: {content}")
        return answer, use_tokens
    else:
        return None, 0
if __name__ == "__main__":
    # 推理模型本地识别名
    name= "豆包-pro-32k"
    # 推理接入点，推理模型名称
    endpoint="ep-20241129235300-j4jd7"
    # api_key from: https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D
    api_key= "6b8b6ae1-4882-4a3e-839e-ad264a46dd77"
    # api from: https://www.volcengine.com/docs/82379/1298454
    api_url= "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    ai_conf = {"api_url": api_url, "model_endpoint": endpoint, "api_key": api_key}
    q_info = {
"title":"1.[单选题] 面对性骚扰，大学生错误的做法是：( )",
"options": "\r".join([
    "A 要建立坚强的心理防线；",
    "B 要自尊、自爱、衣着打扮要得体；",
    "C 要提高子午防卫能力和手段；",
    "D 经常深夜外出；"]),
"type": "single"
    }
    # query_answer_with_ai(q_info, ai_conf)
    q_info = {'id': '404478311', 
               'title': '在社会主义社会中，个人利益与社会利益在根本上是____的。____离不开个人利益，____也离不开社会利益。社会利益不是个人利益的简单相加，而是____。社会利益体现了作为社会成员的个人的根本利益和长远利益，是个人利益得以实现的____，同时它也保障着个人利益的实现。', 'options': '', 
               'type': 'completion', 
               'answerField': {'answer404478311': '', 'answertype404478311': '2'}}
    # query_answer_with_ai(q_info, ai_conf)
    q_info = {"type_name": "判断题",
              "title": "】花园、草坪、食堂、运动场是盗窃案的高发区域，到食堂和运动场时要将随身携带的背包放置在视野可及的范围内，做到人走物随，物不离身。",
              "options": "A对\rB错"}
    query_answer_with_ai(q_info, ai_conf)
"""
OUTPUT:
status_code: 200
json_data: {
    "choices": [
        {
            "finish_reason": "stop",
            "index": 0,
            "logprobs": null,
            "message": {
                "content": "{\"depend_message\": \"这是一道完形填空题，需要根据对社会主义社会中个人利益与社会利益关系的理解来填写。对于第一个空，在社会主义社会，个人利益与社会利益在根本上是一致的，这是社会主义社会的本质特征所决定的；第二个空应填社会利益，因为社会整体利益的发展是由众多个人利益汇聚而成，离不开个人利益；第三个空应填个人利益，因为个人利益的实现是在社会的大环境下，离不开社会利益；第四个空应填全体社会成员共同利益的有机统一，这体现了社会利益的内涵；第五个空应填前提和基础，因为社会利益为个人利益的实现提供了必要的条件和保障。\",  \"answer\": \"一致\\r社会利益\\r个人利益\\r全体社会成员共同利益的有机统一\\r前提和基础\"}",
                "role": "assistant"
            }
        }
    ],
    "created": 1735235143,
    "id": "02173523513584832b8fb9c2ace19b7fe814bde39c812aa454152",
    "model": "doubao-pro-32k-240828",
    "object": "chat.completion",
    "usage": {
        "completion_tokens": 187,
        "prompt_tokens": 853,
        "total_tokens": 1040,
        "prompt_tokens_details": {
            "cached_tokens": 0
        }
    }
}
"""


