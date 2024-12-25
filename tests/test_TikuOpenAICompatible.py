import unittest
from unittest.mock import patch, MagicMock
import configparser

from api.answer import TikuOpenAICompatible


class TestTikuOpenAICompatible(unittest.TestCase):

    def setUp(self):
        # 创建 TikuOpenAICompatible 实例，并设置一些必要的属性和模拟数据
        self.tiku = TikuOpenAICompatible()
        self.tiku.api = 'test_api_endpoint'
        self.tiku._token = 'test_token'
        parser = configparser.ConfigParser()
        parser.add_section("tiku")
        self.tiku._conf = parser["tiku"]
        self.tiku._conf.setdefault('tokens', 'token1,token2')
        self.tiku._conf.setdefault('submit', 'false')  # 根据实际需求设置 submit 的值，这里示例设为 false
        print(list(self.tiku._conf.items()))
        self.question_info = {
            'title': '这是一个测试问题'
        }


    @patch("api.answer.CacheDAO.getCache")
    @patch('requests.post')
    def test_query_success(self, mock_post, mock_getcache):
        # 模拟成功的 API 响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'answer': '测试答案',
            'times': 99
        }
        mock_post.return_value = mock_response
        mock_getcache.return_value = None

        answer = self.tiku.query(self.question_info)

        self.assertEqual(answer, '测试答案')
        mock_post.assert_called_once_with(
            'test_api_endpoint',
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_token"
            },
            json={'prompt': '''请回答以下问题并按照指定格式返回结果：{\'title\': \'问题\'}\n以下为指定json格式返回结果: {"answer":"具体答案","depend_message":"每个选项的依据分析","invert_message":"部分选项的排除法分析"}''', 
                  'max_tokens': 100}
        )

    @patch("api.answer.CacheDAO.getCache")
    @patch('requests.post')
    def test_query_token_expired(self, mock_post, mock_getcahce):
        self.tiku._token_index = 0  # 添加这行，重置 token 索引，避免出现 token 用完的异常
        mock_getcahce.return_value = None
        # 模拟 token 过期的 API 响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'error': {
               'message': 'token expired'
            }
        }
        mock_post.return_value = mock_response
        import logging
        import traceback
        logging.basicConfig(level=logging.DEBUG)

        try:
            with self.assertLogs(level='INFO') as cm:
                answer = self.tiku.query(self.question_info)
        except:
            answer = None
            traceback.print_exc()
        self.assertEqual(answer, None)
        # self.assertEqual(len(cm.records), 1)
        self.assertEqual(cm.records[0].getMessage(), 'TOKEN 过期, 将会更换并重新搜题')
        mock_post.assert_called_once_with(
            'test_api_endpoint',
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_token"
            },
            json={
                "prompt": "请回答以下问题：这是一个测试问题，并按照以下格式返回结果：{\"answer\":\"具体答案\",\"depend_message\":\"每个选项的依据分析\",\"invert_message\":\"部分选项的排除法分析\"}",
                "max_tokens": 100
            }
        )
        
    @patch("api.answer.CacheDAO.getCache")
    @patch('requests.post')
    def test_query_failure(self, mock_post, mock_getcahce):
        mock_getcahce.return_value = None
        # 模拟 API 调用失败的情况
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        with self.assertLogs(level='ERROR') as cm:
            answer = self.tiku.query(self.question_info)

        self.assertEqual(answer, None)
        self.assertEqual(len(cm.records), 1)
        self.assertEqual(cm.records[0].getMessage(), 'OpenAI Compatible 题库查询失败:\n')
        mock_post.assert_called_once_with(
            'test_api_endpoint',
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_token"
            },
            json={
                "prompt": "请回答以下问题：这是一个测试问题，并按照以下格式返回结果：{\"answer\":\"具体答案\",\"depend_message\":\"每个选项的依据分析\",\"invert_message\":\"部分选项的排除法分析\"}",
                "max_tokens": 100
            }
        )

    def test_load_token(self):
        # 测试加载 token 的功能
        self.tiku._token_index = 0
        self.tiku.load_token()
        self.assertEqual(self.tiku._token, 'token1')

        self.tiku._token_index = 1
        self.tiku.load_token()
        self.assertEqual(self.tiku._token, 'token2')

        self.tiku._token_index = 2
        with self.assertRaises(Exception) as cm:
            self.tiku.load_token()
        self.assertEqual(str(cm.exception), 'OpenAI Compatible 题库 TOKEN 已用完, 请更换')
    
    @patch('requests.post')
    def test_query_doubao_ai(self, mock_post):
        """
        测试模拟使用火山引擎相关（这里实际关联豆包AI，只是模拟场景）的情况
        """
        # 假设调用豆包AI时，配置不同的 api 地址来区分，这里设置模拟的豆包AI服务地址
        self.tiku.api = 'doubao_api_endpoint'
        # 模拟成功从豆包AI获取到的响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "answer": "这是豆包AI模拟返回的测试答案",
            "depend_message": "模拟每个选项的依据分析内容",
            "invert_message": "模拟部分选项的排除法分析内容"
        }
        mock_post.return_value = mock_response

        answer = self.tiku.query(self.question_info)

        self.assertEqual(answer, "这是豆包AI模拟返回的测试答案")
        mock_post.assert_called_once_with(
            'doubao_api_endpoint',
            headers={
                "Content-Type": "application/json",
                # 这里假设认证等相关机制类似，实际中如果不同需要调整
                "Authorization": "Bearer test_token"
            },
            json={
                "prompt": "请回答以下问题：这是一个测试问题，并按照以下格式返回结果：{\"answer\":\"具体答案\",\"depend_message\":\"每个选项的依据分析\",\"invert_message\":\"部分选项的排除法分析\"}",
                "max_tokens": 100
            }
        )




if __name__ == '__main__':
    unittest.main()
