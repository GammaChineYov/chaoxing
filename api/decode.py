# -*- coding: utf-8 -*-
import re
import json
from bs4 import BeautifulSoup
from api.logger import logger
from api.font_decoder import FontDecoder


def decode_course_list(_text):
    logger.trace("开始解码课程列表...")
    _soup = BeautifulSoup(_text, "lxml")
    _raw_courses = _soup.select("div.course")
    _course_list = list()
    for course in _raw_courses:
        if not course.select_one("a.not-open-tip") and not course.select_one(
            "div.not-open-tip"
        ):
            _course_detail = {}
            _course_detail["id"] = course.attrs["id"]
            _course_detail["info"] = course.attrs["info"]
            _course_detail["roleid"] = course.attrs["roleid"]

            _course_detail["clazzId"] = course.select_one("input.clazzId").attrs[
                "value"
            ]
            _course_detail["courseId"] = course.select_one("input.courseId").attrs[
                "value"
            ]
            _course_detail["cpi"] = re.findall(
                r"cpi=(.*?)&", course.select_one("a").attrs["href"]
            )[0]
            _course_detail["title"] = course.select_one("span.course-name").attrs[
                "title"
            ]
            if course.select_one("p.margint10") is None:
                _course_detail["desc"] = ""
            else:
                _course_detail["desc"] = course.select_one("p.margint10").attrs["title"]
            _course_detail["teacher"] = course.select_one("p.color3").attrs["title"]
            _course_list.append(_course_detail)
    return _course_list


def decode_course_folder(_text):
    logger.trace("开始解码二级课程列表...")
    _soup = BeautifulSoup(_text, "lxml")
    _raw_courses = _soup.select("ul.file-list>li")
    _course_folder_list = list()
    for course in _raw_courses:
        if course.attrs["fileid"]:
            _course_folder_detail = {}
            _course_folder_detail["id"] = course.attrs["fileid"]
            _course_folder_detail["rename"] = course.select_one(
                "input.rename-input"
            ).attrs["value"]
            _course_folder_list.append(_course_folder_detail)
    return _course_folder_list


def decode_course_point(_text):
    logger.trace("开始解码章节列表...")
    _soup = BeautifulSoup(_text, "lxml")
    _course_point = {
        "hasLocked": False,  # 用于判断该课程任务是否是需要解锁
        "points": [],
    }

    for _chapter_unit in _soup.find_all("div", class_="chapter_unit"):
        _point_list = []
        _raw_points = _chapter_unit.find_all("li")
        for _point in _raw_points:
            _point = _point.div
            if not "id" in _point.attrs:
                continue
            _point_detail = {}
            _point_detail["id"] = re.findall(r"^cur(\d{1,20})$", _point.attrs["id"])[0]
            _point_detail["title"] = (
                _point.select_one("a.clicktitle").text.replace("\n", "").strip(" ")
            )
            _point_detail["jobCount"] = 1  # 默认为1
            if _point.select_one("input.knowledgeJobCount"):
                _point_detail["jobCount"] = _point.select_one(
                    "input.knowledgeJobCount"
                ).attrs["value"]
            else:
                # 判断是不是因为需要解锁
                if "解锁" in _point.select_one("span.bntHoverTips").text:
                    _course_point["hasLocked"] = True

            _point_list.append(_point_detail)
        _course_point["points"] += _point_list
    return _course_point


def decode_course_card(_text: str):
    logger.trace("开始解码任务点列表...")
    _job_info = {}
    _job_list = []
    # 对于未开放章节检测
    if "章节未开放" in _text:
        _job_info["notOpen"] = True
        return [], _job_info

    _temp = re.findall(r"mArg=\{(.*?)\};", _text.replace(" ", ""))
    if _temp:
        _temp = _temp[0]
    else:
        return [], {}
    _cards = json.loads("{" + _temp + "}")

    if _cards:
        _job_info = {}
        _job_info["ktoken"] = _cards["defaults"]["ktoken"]
        _job_info["mtEnc"] = _cards["defaults"]["mtEnc"]
        _job_info["reportTimeInterval"] = _cards["defaults"]["reportTimeInterval"]  # 60
        _job_info["defenc"] = _cards["defaults"]["defenc"]
        _job_info["cardid"] = _cards["defaults"]["cardid"]
        _job_info["cpi"] = _cards["defaults"]["cpi"]
        _job_info["qnenc"] = _cards["defaults"]["qnenc"]
        _job_info["knowledgeid"] = _cards["defaults"]["knowledgeid"]
        _cards = _cards["attachments"]
        _job_list = []
        for _card in _cards:
            # 已经通过的任务
            if "isPassed" in _card and _card["isPassed"] is True:
                continue
            # 不属于任务点的任务
            if "job" not in _card or _card["job"] is False:
                if _card.get("type") and _card["type"] == "read":
                    # 发现有在视频任务下掺杂阅读任务，不完成可能会导致无法开启下一章节
                    if _card["property"].get("read", False):
                        # 已阅读，跳过
                        continue
                    _job = {}
                    _job["title"] = _card["property"]["title"]
                    _job["type"] = "read"
                    _job["id"] = _card["property"]["id"]
                    _job["jobid"] = _card["jobid"]
                    _job["jtoken"] = _card["jtoken"]
                    _job["mid"] = _card["mid"]
                    _job["otherinfo"] = _card["otherInfo"]
                    _job["enc"] = _card["enc"]
                    _job["aid"] = _card["aid"]
                    _job_list.append(_job)
                continue
            # 视频任务
            if _card["type"] == "video":
                _job = {}
                _job["type"] = "video"
                _job["jobid"] = _card["jobid"]
                _job["name"] = _card["property"]["name"]
                _job["otherinfo"] = _card["otherInfo"]
                try:
                    _job["mid"] = _card["mid"]
                except KeyError:
                    logger.warning("出现转码失败视频，已跳过...")
                    continue
                _job["objectid"] = _card["objectId"]
                _job["aid"] = _card["aid"]
                # _job["doublespeed"] = _card["property"]["doublespeed"]
                _job_list.append(_job)
                continue
            if _card["type"] == "document":
                _job = {}
                _job["type"] = "document"
                _job["jobid"] = _card["jobid"]
                _job["otherinfo"] = _card["otherInfo"]
                _job["jtoken"] = _card["jtoken"]
                _job["mid"] = _card["mid"]
                _job["enc"] = _card["enc"]
                _job["aid"] = _card["aid"]
                _job["objectid"] = _card["property"]["objectid"]
                _job_list.append(_job)
                continue
            if _card["type"] == "workid":
                # 章节检测
                _job = {}
                _job["type"] = "workid"
                _job["jobid"] = _card["jobid"]
                _job["otherinfo"] = _card["otherInfo"]
                _job["mid"] = _card["mid"]
                _job["enc"] = _card["enc"]
                _job["aid"] = _card["aid"]
                _job_list.append(_job)
                continue

            if _card["type"] == "vote":
                # 调查问卷 同上
                continue
        return _job_list, _job_info


def decode_questions_info(html_content) -> dict:
    def replace_rtn(text):
        return text.replace("\r", "").replace("\t", "").replace("\n", "")

    soup = BeautifulSoup(html_content, "lxml")
    form_data = {}
    form_tag = soup.find("form")

    fd = FontDecoder(html_content)  # 加载字体

    # 抽取表单信息
    for input_tag in form_tag.find_all("input"):
        if "name" not in input_tag.attrs or "answer" in input_tag.attrs["name"]:
            continue
        form_data.update({input_tag.attrs["name"]: input_tag.attrs.get("value", "")})

    form_data["questions"] = []
    for div_tag in form_tag.find_all(
        "div", class_="singleQuesId"
    ):  # 目前来说无论是单选还是多选的题class都是这个
        q_title = replace_rtn(fd.decode(div_tag.find("div", class_="Zy_TItle").text))
        q_options = ""
        for li_tag in div_tag.find("ul").find_all("li"):
            q_options += replace_rtn(fd.decode(li_tag.text)) + "\n"
        q_options = q_options[:-1]  # 去除尾部'\n'

        # 尝试使用 data 属性来判断题型
        q_type_code = div_tag.find("div", class_="TiMu").attrs["data"]
        q_type = ""
        q_type_name = ""
        # 此处可能需要完善更多题型的判断
        # TODO： [4, 5, 6, 7, 8, 18, 26] 归为一类, 为限定字数的写作填空题型
        # js取值方式: $("#answer" + id).val();
        # TODO： 填空题类型
            #     function setAllClozeAnswer() {
            # 	$(".clozeTextQues").each(function() {
            # 		var qid = $(this).attr("data");
            # 		var answerObj = {};
            # 		$(".clozeTextItem" + qid).each(function() {
            # 			var itemId = $(this).attr("data");
            # 			var content = $("#answer" + qid + itemId).val();
            # 			var info = {};
            # 			info.answer = content;
            # 			answerObj[itemId] = info;
            # 		});
            # 		var answer = [];
            # 		answer.push(answerObj);
            # 		var answerStr = JSON.stringify(answer);
            # 		$("#answer" + qid).val(answerStr);
            # 	});
            # }
        if q_type_code == "0":
            q_type = "single"
            q_type_name = "单选题"
        elif q_type_code == "1":
            # answer格式为string: "ABCD"
            q_type = "multiple"
            q_type_name = "多选题"
        elif q_type_code == "2":
            # 1开始
            # 答题框数量： var blankNum = $("#blankNum" + qtid).val();
            # answer格式为json: [{"name": "1", "content": "答案1"}, {"name": "2", "content": "答案2"}]
            q_type = "completion" 
            q_type_name = "填空题"
        elif q_type_code == "3":
            # answer格式为bool: true/false
            q_type = "judgement"
            q_type_name = "判断题"
        elif q_type_code == "4":
            q_type = "simple"
            q_type_name = "简答题"
        elif q_type_code == "5":
            q_type = "unknown"
            q_type_name = "名词解释"
        elif q_type_code == "6":
            q_type = "unknown"
            q_type_name = "论述题"  
        elif q_type_code == "7":
            q_type = "unknown"
            q_type_name = "计算题"
        elif q_type_code == "9":
            q_type = "unknown" # 分录题
            q_type_name = "分录题"
        elif q_type_code == "10":
            q_type = "unknown" # 资料题
            q_type_name = "资料题"
        elif q_type_code == "11":
            q_type = "unknown"
            q_type_name = "连线题"
        elif q_type_code == "12":
            q_type = "unknown"
            q_type_name = "投票题"
        elif q_type_code == "13":
            q_type = "unknown"
            q_type_name = "排序题"
        elif q_type_code == "14":
            q_type = "unknown"
            q_type_name = "完型填空"
        elif q_type_code == "15":
            q_type = "unknown"
            q_type_name = "阅读理解"
        elif q_type_code == "16":
            q_type = "unknown"
            q_type_name = "综合题"
        elif q_type_code == "17":
            # js取值语法：UE.getEditor("textarea" + id).getContentTxt();
            q_type = "unknown"
            q_type_name = "程序题"
            
        elif q_type_code == "19":
            q_type = "unknown"
            q_type_name = "听力题"
        elif q_type_code == "20":
            q_type = "unknown"
            q_type_name = "共用选项题"        
        elif q_type_code == "22":
            q_type = "unknown"
            q_type_name = "口语测评题"
        elif q_type_code == "18":
            q_type = "unknown"
            q_type_name = "口语题"
        elif q_type_code == "26":
            q_type = "unknown"
            q_type_name = "写作题"
        else:
            logger.info("未知题型代码 -> " + q_type_code)
            q_type = "unknown"  # 避免出现未定义取值错误
            q_type_name = "未知题型"

        form_data["questions"].append(
            {
                "id": div_tag.attrs["data"],
                "title": q_title,  # 题目
                "options": q_options,  # 选项 可提供给题库作为辅助
                "type": q_type,  # 题型 可提供给题库作为辅助
                "typeName": q_type_name,  # 题型名称 可提供给题库作为辅助
                "answerField": {
                    "answer" + div_tag.attrs["data"]: "",  # 答案填入处
                    "answertype" + div_tag.attrs["data"]: q_type_code,
                },
            }
        )
    # 处理答题信息
    form_data["answerwqbid"] = ",".join([q["id"] for q in form_data["questions"]]) + ","
    return form_data
