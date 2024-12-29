import json
from question_manager import QuestionManager

if __name__ == "__main__":
    cache_json_file = "cache.json"
    with open(cache_json_file, 'r') as f:
        cache = json.load(f)
    manager = QuestionManager()
    for question in cache.keys():
        print("sending question: ", question)
        answer = manager.send_question(question)
        # if not answer:
        #     answer = manager.wait_for_answer(question)
        # if answer:
        #     print(answer)
        # else:
        #     print("Failed to get an answer within the timeout period.")