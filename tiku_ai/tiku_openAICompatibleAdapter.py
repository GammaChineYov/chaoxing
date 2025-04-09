from api.answer import Tiku
from .doubao import query_answer_with_ai
from api.stats import stats
from api.logger import logger

class TikuOpenAICompatibleAdapter(Tiku):
    def __init__(self) -> None:
        super().__init__()
        self.name = 'OpenAI Compatible 题库'
        self.ai_conf = {}
        self._token_index = 0  # token 队列计数器
        self._times = 100  # 查询次数剩余, 初始化为 100, 查询后校对修正
        self._use_token_count = 0  # 使用的 token 计数器

    def _query(self, q_info: dict):
        send_message = q_info.copy()
        send_message['stats'] = stats
        answer, use_tokens = query_answer_with_ai(q_info, self.ai_conf)
        if answer:
            answer = answer.strip()
            if q_info['type'] == 'judgement':
                answer = answer[:1]
            self._use_token_count += use_tokens
            print(f'使用 token 数: {use_tokens}, 本轮总使用 token 数: {self._use_token_count}')
            return answer
        else:
            self._token_index += 1
            self.load_token()
            logger.error(f'{self.name}查询失败, 没有获得答案，设置下一个 token 重试')
            return self._query(q_info)

    def load_token(self):
        token_list = self._conf['model_endpoints'].split(',')
        if self._token_index == len(token_list):
            # TOKEN 用完
            logger.error('TOKEN 用完, 请自行更换再重启脚本')
            raise Exception(f'{self.name} TOKEN 已用完, 请更换')
        _token = token_list[self._token_index]
        self.ai_conf.update({
            'api_url': self._conf["url"],
            'api_key': self._conf["api_key"],
            'model_endpoint': _token,
        })

    def _init_tiku(self):
        self.load_token()