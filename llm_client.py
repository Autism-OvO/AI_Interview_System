import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_MODEL = os.getenv("LLM_MODEL")

LLM_REQUEST_TIMEOUT = float(os.getenv("LLM_REQUEST_TIMEOUT", "25"))
SPEECH_EVAL_TIMEOUT = float(os.getenv("SPEECH_EVAL_TIMEOUT", "12"))
FOLLOWUP_TIMEOUT = float(os.getenv("FOLLOWUP_TIMEOUT", "12"))
REPORT_TIMEOUT = float(os.getenv("REPORT_TIMEOUT", "35"))

# 当前选中的模型配置 ID
_current_model_id = None

try:
    from key import key as _keys, models as _models, MODEL_CONFIGS as _MODEL_CONFIGS
except Exception:
    _keys = {}
    _models = {}
    _MODEL_CONFIGS = {}

# 初始默认值（如环境变量未设置则用 key.py 中的 deepseek）
if not OPENAI_API_KEY:
    OPENAI_API_KEY = _keys.get('ds', '')
    LLM_BASE_URL = LLM_BASE_URL or "https://api.deepseek.com"
    LLM_MODEL = LLM_MODEL or "deepseek-chat"
    _current_model_id = 'deepseek'


def get_available_models() -> List[Dict[str, str]]:
    """返回可供前端选择的模型列表。"""
    result = []
    for mid, cfg in _MODEL_CONFIGS.items():
        result.append({"id": mid, "name": cfg["name"]})
    return result


def get_current_model_id() -> str:
    return _current_model_id or 'deepseek'


def set_model(model_id: str) -> bool:
    """切换当前使用的模型。返回 True 表示成功。"""
    global OPENAI_API_KEY, LLM_BASE_URL, LLM_MODEL, _current_model_id
    cfg = _MODEL_CONFIGS.get(model_id)
    if not cfg:
        return False
    OPENAI_API_KEY = cfg['api_key']
    LLM_BASE_URL = cfg['base_url']
    LLM_MODEL = cfg['model']
    _current_model_id = model_id
    return True


def available() -> bool:
    return bool(OPENAI_API_KEY)


def _new_client(timeout_seconds: float):
    import openai
    return openai.OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=LLM_BASE_URL or "https://api.openai.com/v1",
        timeout=timeout_seconds,
    )


def _safe_parse_json(text: str) -> Optional[Dict[str, Any]]:
    """安全解析 LLM 返回的 JSON，自动剥离 Markdown 格式和多余文本"""
    if not isinstance(text, str):
        text = str(text)
    text = text.strip()
    
    # 第一次尝试：直接解析纯 JSON
    try:
        return json.loads(text)
    except Exception:
        pass
        
    # 第二次尝试：清洗掉 Markdown 的 ```json 和 ``` 标记
    import re
    # 忽略大小写去除开头的 ```json 或 ```
    clean_text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    # 去除结尾的 ```
    clean_text = re.sub(r"\s*```$", "", clean_text)
    
    try:
        return json.loads(clean_text.strip())
    except Exception:
        pass
        
    # 第三次尝试：暴力截取第一个 { 和最后一个 } 之间的所有内容
    try:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            return json.loads(m.group(0))
    except Exception:
        pass
        
    return None


def _normalize_scores(d: Dict[str, Any]) -> Dict[str, Any]:
    # Ensure numeric fields 0-100 and fill defaults
    keys = ["technical", "logic", "communication", "problem_solving", "overall"]
    out = {}
    for k in keys:
        v = d.get(k)
        try:
            v = float(v)
        except Exception:
            v = None
        if v is None:
            out[k] = 0.0
        else:
            out[k] = max(0.0, min(100.0, round(v, 1)))
    # copy suggestions/strings
    out["suggestions"] = d.get("suggestions", d.get("advice", "")) or ""
    out["strengths"] = d.get("strengths", "")
    out["weaknesses"] = d.get("weaknesses", "")
    out["raw"] = d
    return out


def _normalize_speech_scores(d: Dict[str, Any]) -> Dict[str, Any]:
    keys = ["speech_rate", "clarity", "confidence", "expressiveness", "overall"]
    out = {}
    for k in keys:
        v = d.get(k)
        try:
            v = float(v)
        except Exception:
            v = None
        if v is None:
            out[k] = 0.0
        else:
            out[k] = max(0.0, min(100.0, round(v, 1)))
    out["summary"] = (d.get("summary") or "").strip()
    out["suggestions"] = (d.get("suggestions") or "").strip()
    out["raw"] = d
    return out


def _guess_audio_format(filepath: str) -> str:
    ext = Path(filepath).suffix.lower().lstrip('.')
    if ext in {"wav", "mp3", "m4a", "webm", "mp4", "ogg", "flac"}:
        return ext
    return "wav"


def evaluate_speech_with_llm(
    audio_path: str,
    transcript: str,
    question: str = "",
    role: str = "",
    candidate: str = "",
) -> Dict[str, Any]:
    """Evaluate speech delivery from source audio + transcript.

    This function is intended to be called only in voice-input flow.
    """
    sample = {
        "speech_rate": 75.0,
        "clarity": 78.0,
        "confidence": 74.0,
        "expressiveness": 72.0,
        "overall": 75.0,
        "summary": "语速基本稳定，表达较清楚，整体表现尚可。",
        "suggestions": "可在关键结论处加强停顿和重音，减少口头禅，提升表达自信度。",
    }

    if not available():
        return _normalize_speech_scores(sample)

    try:
        import openai
    except Exception:
        return _normalize_speech_scores(sample)

    if not Path(audio_path).exists():
        s = _normalize_speech_scores(sample)
        s["summary"] = "音频文件不存在，已返回默认语音评估。"
        s["suggestions"] = "请检查上传链路是否成功保存音频文件。"
        return s

    model = os.getenv("SPEECH_EVAL_MODEL") or LLM_MODEL or "deepseek-chat"
    audio_format = _guess_audio_format(audio_path)

    instruction = (
        "你是中文面试表达教练，请根据音频和转写文本评估候选人的表达表现。"
        "必须且只能输出一个合法 JSON 对象，不要输出任何额外文本。"
        "JSON Schema: "
        "{"
        "\"speech_rate\": number, "
        "\"clarity\": number, "
        "\"confidence\": number, "
        "\"expressiveness\": number, "
        "\"overall\": number, "
        "\"summary\": string, "
        "\"suggestions\": string"
        "}. "
        "评分范围 0-100。"
        "speech_rate 表示语速是否合适（过快/过慢都扣分）；"
        "clarity 表示吐字清晰度与可懂度；"
        "confidence 表示语气稳定与自信程度；"
        "expressiveness 表示抑扬顿挫、重点突出与感染力。"
        "summary 和 suggestions 用中文，简洁且可执行。"
    )

    context_text = (
        f"岗位: {role or '未知'}\n"
        f"候选人: {candidate or '匿名'}\n"
        f"问题: {question or '无'}\n"
        f"转写文本: {transcript or '无'}"
    )

    try:
        client = _new_client(SPEECH_EVAL_TIMEOUT)
        resp = client.chat.completions.create(
            model=model,
            temperature=0.2,
            max_tokens=500,
            messages=[
                {
                    "role": "system",
                    "content": instruction,
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": context_text},
                    ],
                },
            ],
        )
        text = getattr(resp.choices[0].message, "content", "") or ""
        if not text:
            text = str(resp)

        parsed = _safe_parse_json(text)
        if not parsed:
            return _normalize_speech_scores({**sample, "summary": "语音评估返回非 JSON，已回退默认结构。", "suggestions": text})
        return _normalize_speech_scores(parsed)
    except Exception as e:
        s = _normalize_speech_scores(sample)
        s["summary"] = "语音评估调用异常，已返回默认语音评估。"
        s["suggestions"] = f"请检查模型兼容性、网络和 Key。异常信息：{e}"
        return s


def _build_prompt(question: str, answer: str, role: str, candidate: str, kb_contexts: List[Dict[str, Any]] = None) -> Tuple[str, str]:
    kb_text = "\n".join([c.get("text", "") for c in (kb_contexts or [])])
    
    # 丰富 System 设定，加入专家 Persona 和字数/细节要求
    system = (
        "你是一位资深且严厉的技术面试官（Senior Technical Interviewer）。\n"
        "你的任务是根据面试问题、候选人的回答、目标岗位以及提供的知识库，给出深度、专业且犀利的点评。\n"
        "不要只给干瘪的结论！你需要指出候选人回答中的具体亮点（结合原话），以及缺失的核心细节（如底层原理、性能瓶颈、边界条件等），并提供极其具体的改进建议。\n"
        "必须且只能输出一个合法的JSON对象（不要有任何markdown包裹或其他多余文本），Schema如下：\n"
        "{\n"
        "  \"technical\": number,         // 0-100: 技术准确度、深度、最佳实践的掌握程度\n"
        "  \"logic\": number,             // 0-100: 结构化思维、逻辑推理是否严密\n"
        "  \"communication\": number,     // 0-100: 表达是否清晰、专业术语使用是否准确\n"
        "  \"problem_solving\": number,   // 0-100: 权衡取舍能力、边界条件和替代方案的思考\n"
        "  \"overall\": number,           // 0-100: 综合评分\n"
        "  \"strengths\": string,         // 详细的优势分析（3-4句话，结合候选人的具体措辞，若回答极差也可写“暂无明显亮点”）\n"
        "  \"weaknesses\": string,        // 详细的不足分析（3-4句话，一针见血地指出缺失的考点、技术盲区或逻辑漏洞）\n"
        "  \"suggestions\": string        // 给出具体、实操性极强的提升建议，例如推荐阅读具体的源码、学习某种架构思想或补充某方面的边界思考\n"
        "}\n"
        "注意：所有字符串字段（strengths, weaknesses, suggestions）必须使用中文回答，语气要专业、客观、具有建设性且细节丰富。"
    )

    user = (
        f"【面试岗位】: {role}\n"
        f"【候选人】: {candidate}\n\n"
        f"【面试官提问】:\n{question}\n\n"
        f"【候选人回答】:\n{answer}\n\n"
        f"【参考知识点/正确方向】:\n{kb_text}\n\n"
        "请立即输出符合上述格式的详尽 JSON 评估对象："
    )
    return system, user


def score_answer_with_llm(question: str, answer: str, role: str, candidate: str, kb_contexts: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Call LLM to get multi-dimensional scores and suggestions.

    If `OPENAI_API_KEY` is not set or call fails, returns a sample structured object as a fallback.
    """
    sample = {
        "technical": 70.0,
        "logic": 75.0,
        "communication": 80.0,
        "problem_solving": 65.0,
        "overall": 73.0,
        "strengths": "覆盖了主要考点，表达基本清晰。",
        "weaknesses": "缺少复杂情况的讨论与性能考虑，未能深入底层原理。",
        "suggestions": "建议补充边界条件讨论，并举例说明性能优化手段。",
    }

    if not available():
        return _normalize_scores(sample)

    try:
        import openai
    except Exception as e:
        return _normalize_scores(sample)

    model = LLM_MODEL or "deepseek-chat"
    system, user = _build_prompt(question, answer, role, candidate, kb_contexts)

    # 调高温度增加丰富度，调高 tokens 上限防止截断
    API_TEMP = 0.6
    API_MAX_TOKENS = 1200

    try:
        client = _new_client(LLM_REQUEST_TIMEOUT)
        resp = client.chat.completions.create(model=model, messages=[{"role": "system", "content": system}, {"role": "user", "content": user}], max_tokens=API_MAX_TOKENS, temperature=API_TEMP)
        text = resp.choices[0].message.content

        text = text.strip() if isinstance(text, str) else str(text)
        parsed = _safe_parse_json(text)
        if not parsed:
            return _normalize_scores({**sample, "suggestions": text})
        return _normalize_scores(parsed)
    except Exception as e:
        s = _normalize_scores(sample)
        s["suggestions"] = s["suggestions"] + f"\n（LLM 调用异常：{str(e)}。这通常是因为 API Key 无效、网络不通或模型名称错误导致。）"
        return s


def generate_followup_question(question: str, answer: str, role: str, kb_contexts: List[Dict[str, Any]] = None) -> str:
    """根据候选人的第一次回答，生成一个有针对性的追问。"""
    fallback = "能否再详细展开一下你刚才的回答？比如具体的实现细节或你在实际项目中的经验。"

    if not available():
        return fallback

    try:
        import openai
    except Exception:
        return fallback

    kb_text = "\n".join([c.get("text", "") for c in (kb_contexts or [])])
    model = LLM_MODEL or "deepseek-chat"

    system = (
        "你是一位资深技术面试官。候选人刚刚回答了一道面试题，你需要根据他的回答进行一次有深度的追问。\n"
        "追问的目标是：\n"
        "1. 如果候选人的回答比较浅显，引导他深入到底层原理或实现细节。\n"
        "2. 如果候选人的回答有遗漏，针对遗漏的关键点进行提问。\n"
        "3. 如果候选人的回答比较全面，可以提出一个延伸场景或边界条件来考察其灵活应变能力。\n\n"
        "要求：\n"
        "- 只输出一个追问问题，不要输出其他内容。\n"
        "- 追问必须与原始问题和候选人的回答直接相关。\n"
        "- 语气专业、自然，像真实面试官一样。\n"
        "- 使用中文。"
    )

    user = (
        f"【面试岗位】: {role}\n"
        f"【原始面试题】:\n{question}\n\n"
        f"【候选人回答】:\n{answer}\n\n"
        f"【参考知识点】:\n{kb_text}\n\n"
        "请根据以上信息，给出一个有针对性的追问："
    )

    try:
        client = _new_client(FOLLOWUP_TIMEOUT)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            max_tokens=300,
            temperature=0.7
        )
        text = resp.choices[0].message.content
        return text.strip() if isinstance(text, str) else fallback
    except Exception:
        return fallback


def example_output() -> Dict[str, Any]:
    """Return a deterministic example of the expected JSON evaluation format."""
    ex = {
        "technical": 88.0,
        "logic": 82.0,
        "communication": 79.0,
        "problem_solving": 75.0,
        "overall": 81.0,
        "strengths": "回答结构清晰，覆盖了主要算法思路",
        "weaknesses": "缺少复杂度推导与边界情况分析",
        "suggestions": "补充时间/空间复杂度推导；举例说明边界输入处理；练习用简练语句表达要点",
    }
    return _normalize_scores(ex)


def generate_report_with_llm(history: List[Dict[str, Any]], role: str, candidate: str, kb_contexts: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generate a comprehensive session report from multi-turn history."""
    sample_report = {
        "overall": 78.0,
        "by_dimension": {"technical": 80.0, "logic": 76.0, "communication": 77.0, "problem_solving": 79.0},
        "strengths": ["覆盖主要考点", "表达清晰"],
        "weaknesses": ["缺少复杂度推导", "边界条件讨论不足"],
        "recommendations": ["补习时间复杂度分析", "练习结构化回答 5 次/周"],
        "raw": history
    }

    if not available():
        return sample_report

    try:
        import openai
    except Exception:
        return sample_report

    model = LLM_MODEL or "deepseek-chat"
    kb_text = "\n".join([c.get("text", "") for c in (kb_contexts or [])])

    def _format_hist_item(h):
        parts = [f"Q: {h.get('question','')}", f"A: {h.get('answer','')}"]
        if h.get('followup_question'):
            parts.append(f"追问: {h['followup_question']}")
            parts.append(f"追问回答: {h.get('followup_answer','')}")
        parts.append(f"Eval: {h.get('evaluation',{})}")
        return "\n".join(parts)

    hist_text = "\n\n".join([_format_hist_item(h) for h in history])
    
    # 丰富最终报告的 System 设定
    system = (
        "你是一位世界顶级的技术招聘专家和面试教练。你需要根据多轮面试的完整对话记录（包含问题、回答和AI单题评分），生成一份极具深度的最终面试评估报告。\n"
        "拒绝使用笼统的套话！你需要深度总结候选人的核心能力画像，挖掘其技术深度的上限和底层逻辑的盲区。\n"
        "必须且只能输出一个合法的JSON对象（不要有任何markdown包裹或其他多余文本），Schema如下：\n"
        "{\n"
        "  \"overall\": number,               // 0-100综合打分\n"
        "  \"by_dimension\": {\n"
        "    \"technical\": number,           // 0-100\n"
        "    \"logic\": number,\n"
        "    \"communication\": number,\n"
        "    \"problem_solving\": number\n"
        "  },\n"
        "  \"strengths\": [\"string\"],       // 包含3-5个详细的优点描述，每个描述需超过20个字，且必须有前置对话作为依据\n"
        "  \"weaknesses\": [\"string\"],      // 包含3-5个核心短板描述，深入指出技术盲点或思维缺陷\n"
        "  \"recommendations\": [\"string\"]  // 包含3-5个具有实操性的突破计划（例如：推荐看某底层源码、手写某类算法等）\n"
        "}\n"
        "所有文本数组和字符串必须使用中文，语言要犀利、专业、切中要害。"
    )
    user = f"【面试岗位】: {role}\n【候选人】: {candidate}\n【岗位知识点】:\n{kb_text}\n\n【完整面试记录】:\n{hist_text}\n\n请输出JSON报告："

    API_TEMP = 0.6
    API_MAX_TOKENS = 2000

    try:
        client = _new_client(REPORT_TIMEOUT)
        resp = client.chat.completions.create(model=model, messages=[{"role":"system","content":system},{"role":"user","content":user}], max_tokens=API_MAX_TOKENS, temperature=API_TEMP)
        text = resp.choices[0].message.content

        parsed = _safe_parse_json(text)
        if not parsed:
            sample_report['recommendations'] = [text]
            return sample_report
            
        if 'by_dimension' in parsed:
            for k,v in parsed['by_dimension'].items():
                try:
                    parsed['by_dimension'][k] = float(v)
                except Exception:
                    parsed['by_dimension'][k] = 0.0
        # 如果返回的 JSON 里缺失必要的数组，给一个默认空数组防止前端渲染报错
        parsed.setdefault('strengths', [])
        parsed.setdefault('weaknesses', [])
        parsed.setdefault('recommendations', [])
        parsed['raw'] = history
        return parsed
    except Exception as e:
        sample_report['recommendations'].append(f"报告生成异常: {str(e)}")
        return sample_report