import json
import os
import uuid
import pickle
import logging
import random
from pathlib import Path
from typing import List, Dict, Any, Optional

import numpy as np

# 抑制 HF Hub / sentence-transformers 加载时的所有冗余输出
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
for _logger_name in ("sentence_transformers", "huggingface_hub", "transformers",
                     "torch", "safetensors", "transformers.modeling_utils"):
    logging.getLogger(_logger_name).setLevel(logging.CRITICAL)

# 模型加载时 safetensors/huggingface_hub 直接向 stderr 写入冗余信息，
# 需要在 OS 文件描述符层面静默
import sys as _sys, io as _io
_orig_stderr = _sys.stderr
_sys.stderr = _io.StringIO()
_fd_backup = os.dup(2)
_devnull = os.open(os.devnull, os.O_WRONLY)
os.dup2(_devnull, 2)
os.close(_devnull)

from sentence_transformers import SentenceTransformer
import faiss

os.dup2(_fd_backup, 2)
os.close(_fd_backup)
_sys.stderr = _orig_stderr
del _orig_stderr, _fd_backup

from question_bank import test as QUESTION_BANK
from llm_client import available as llm_available, score_answer_with_llm, generate_followup_question
from storage import storage


BASE_DIR = Path(__file__).parent
VECTOR_INDEX_DIR = BASE_DIR / "vector_index"


class Retriever:
    """知识库检索器，使用 sentence-transformers 生成向量 + FAISS 进行语义检索。"""

    EMBED_MODEL = "BAAI/bge-small-zh-v1.5"

    def __init__(self, kb_path: str = None):
        self.kb_path = kb_path or (BASE_DIR / "knowledge_base.json")
        self.docs: List[str] = []
        self.role_map: List[str] = []

        self._embed_model = None
        self._faiss_index = None
        self._dim: int = 0

        self._load()

    # ================================================================== #
    #                         加载 & 构建索引
    # ================================================================== #
    def _load(self):
        if not Path(self.kb_path).exists():
            return

        with open(self.kb_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.docs = []
        self.role_map = []
        for role, items in data.items():
            for doc in items:
                text = doc.get("text") or (doc.get("title", "") + "\n" + doc.get("content", ""))
                self.docs.append(text)
                self.role_map.append(role)

        if not self.docs:
            return

        self._build_index()

    def _get_model(self):
        """懒加载 embedding 模型（只实例化一次）。"""
        if self._embed_model is None:
            _orig = _sys.stderr
            _sys.stderr = _io.StringIO()
            _fd = os.dup(2)
            _dn = os.open(os.devnull, os.O_WRONLY)
            os.dup2(_dn, 2)
            os.close(_dn)
            try:
                self._embed_model = SentenceTransformer(self.EMBED_MODEL)
            finally:
                os.dup2(_fd, 2)
                os.close(_fd)
                _sys.stderr = _orig
        return self._embed_model

    def _build_index(self):
        """使用 sentence-transformers 编码文档并构建 FAISS 索引。"""
        index_file = VECTOR_INDEX_DIR / "faiss.index"
        meta_file = VECTOR_INDEX_DIR / "meta.pkl"
        kb_mtime = os.path.getmtime(self.kb_path)
        model_tag = self.EMBED_MODEL

        # 尝试从缓存加载
        if index_file.exists() and meta_file.exists():
            with open(meta_file, "rb") as f:
                meta = pickle.load(f)
            if meta.get("kb_mtime") == kb_mtime and meta.get("model") == model_tag:
                self._faiss_index = faiss.read_index(str(index_file))
                self._get_model()
                self._dim = meta.get("dim", 0)
                return

        # 编码并构建新索引
        model = self._get_model()
        embeddings = model.encode(self.docs, normalize_embeddings=True)
        embeddings = np.ascontiguousarray(embeddings, dtype="float32")

        self._dim = embeddings.shape[1]
        self._faiss_index = faiss.IndexFlatIP(self._dim)
        self._faiss_index.add(embeddings)

        VECTOR_INDEX_DIR.mkdir(exist_ok=True)
        faiss.write_index(self._faiss_index, str(index_file))
        with open(meta_file, "wb") as f:
            pickle.dump({"kb_mtime": kb_mtime, "model": model_tag, "dim": self._dim}, f)

    # ================================================================== #
    #                            检索
    # ================================================================== #
    def retrieve(self, query: str, role: str = None, k: int = 3) -> List[Dict[str, Any]]:
        if not self.docs or self._faiss_index is None:
            return []
        qv = self._embed_model.encode([query], normalize_embeddings=True).astype("float32")
        search_k = min(len(self.docs), k * 5)
        scores, indices = self._faiss_index.search(qv, search_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            if role and self.role_map[idx] != role:
                continue
            results.append({"role": self.role_map[idx], "text": self.docs[idx], "score": float(score)})
            if len(results) >= k:
                break
        return results

    # ================================================================== #
    #              知识库更新（热更新，无需重启）
    # ================================================================== #
    def reload(self):
        """重新读取 knowledge_base.json 并重建向量索引。"""
        index_file = VECTOR_INDEX_DIR / "faiss.index"
        meta_file = VECTOR_INDEX_DIR / "meta.pkl"
        if index_file.exists():
            index_file.unlink()
        if meta_file.exists():
            meta_file.unlink()

        self.docs = []
        self.role_map = []
        self._faiss_index = None
        self._load()

    def add_entry(self, role: str, title: str, text: str):
        """向 knowledge_base.json 新增一条知识，并重建索引。"""
        kb_path = Path(self.kb_path)
        if kb_path.exists():
            with open(kb_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}

        if role not in data:
            data[role] = []
        data[role].append({"title": title, "text": text})

        with open(kb_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.reload()

    def list_entries(self) -> Dict[str, Any]:
        """返回当前知识库内容摘要。"""
        kb_path = Path(self.kb_path)
        if not kb_path.exists():
            return {}
        with open(kb_path, "r", encoding="utf-8") as f:
            return json.load(f)


# simple in-memory sessions
SESSIONS: Dict[str, Dict[str, Any]] = {}
retriever = Retriever()


def create_session(role: str, candidate: str, num_questions: int = 5, followup_enabled: bool = True) -> str:
    if role not in QUESTION_BANK:
        raise ValueError("unknown role")
    sid = str(uuid.uuid4())
    all_questions = QUESTION_BANK[role]["question_bank"]
    questions = random.sample(all_questions, min(num_questions, len(all_questions)))
    SESSIONS[sid] = {
        "role": role,
        "candidate": candidate,
        "questions": questions,
        "index": 0,
        "history": [],
        "followup_enabled": bool(followup_enabled),
    }
    return sid


def add_speech_evaluation(session_id: str, eval_data: Dict[str, Any]) -> None:
    """将语音表达评估结果挂到会话上，用于最终报告的综合语音分析。

    这里只做简单的累积，不与具体题目强绑定，后续在 generate_report 中做整体聚合。
    """
    s = SESSIONS.get(session_id)
    if not s:
        return
    speech_list = s.setdefault("speech_evaluations", [])
    if isinstance(eval_data, dict):
        # 存一份浅拷贝，避免后续被前端意外修改
        speech_list.append(dict(eval_data))


def get_current_question(session_id: str):
    s = SESSIONS.get(session_id)
    if not s:
        return None
    idx = s["index"]
    if idx >= len(s["questions"]):
        return None
    return s["questions"][idx]


def evaluate_answer(answer: str, answer_key: str, question: str = "", role: str = "", candidate: str = "") -> Dict[str, Any]:
    # If LLM available, use it for deep scoring and suggestions, passing richer context
    try:
        if llm_available():
            # build kb_contexts from retriever using question and answer
            kb_contexts = []
            try:
                # prefer question-context retrieval, then answer-based retrieval
                if role and question:
                    kb_contexts = retriever.retrieve(question, role=role, k=3)
                if len(kb_contexts) < 3:
                    more = retriever.retrieve(answer or question, role=role, k=3)
                    # merge while keeping order
                    seen = set()
                    merged = []
                    for it in (kb_contexts + more):
                        t = it.get('text')
                        if t and t not in seen:
                            merged.append(it)
                            seen.add(t)
                    kb_contexts = merged[:5]
            except Exception:
                kb_contexts = []

            try:
                parsed = score_answer_with_llm(question=question, answer=answer, role=role, candidate=candidate, kb_contexts=kb_contexts)
                overall = parsed.get('overall') if parsed.get('overall') is not None else round(((parsed.get('technical',0)+parsed.get('logic',0)+parsed.get('communication',0))/3),1)
                return {"score": float(overall), "llm_detail": parsed}
            except Exception:
                # fallback to local heuristic
                pass
    except Exception:
        pass

    # Local heuristic fallback (keyword matching + fluency)
    if not answer_key:
        return {"score": 0, "feedback": "无答案要点，无法评估"}
    keys = [k.strip().lower() for k in answer_key.replace(';', ',').replace('；', ',').split(',') if k.strip()]
    ans_low = answer.lower()
    matched = [k for k in keys if k and k in ans_low]
    matched_cnt = len(matched)
    base = matched_cnt / max(1, len(keys))
    score = base * 70
    # length bonus (fluency) up to 30
    words = len(answer.split())
    fluency_bonus = min(30, (words / 20) * 10)
    score = min(100, score + fluency_bonus)
    feedback = []
    if matched_cnt == len(keys):
        feedback.append("覆盖了主要考点")
    else:
        missing = [k for k in keys if k not in matched]
        feedback.append(f"未覆盖要点：{', '.join(missing)}")
    if words < 10:
        feedback.append("回答过短，建议阐述思路与关键细节")
    return {"score": round(float(score), 1), "matched": matched, "feedback": "；".join(feedback)}


def submit_answer(session_id: str, answer: str) -> Dict[str, Any]:
    s = SESSIONS.get(session_id)
    if not s:
        return {"error": "invalid session"}
    idx = s["index"]
    if idx >= len(s["questions"]):
        return {"done": True, "message": "面试题已完成"}
    q = s["questions"][idx]

    followup_enabled = bool(s.get("followup_enabled", True))

    # 单轮模式：收到第一次回答后直接评测并进入下一题
    if not followup_enabled:
        eval_res = evaluate_answer(
            answer,
            q.get("answer_key", ""),
            question=q.get('question', ''),
            role=s.get('role', ''),
            candidate=s.get('candidate', '')
        )
        rag = retriever.retrieve(answer or q.get("question", ""), role=s["role"], k=3)
        s["history"].append({
            "question": q,
            "answer": answer,
            "followup_question": None,
            "followup_answer": None,
            "evaluation": eval_res,
            "rag": rag
        })
        s["index"] += 1
        next_q = None
        if s["index"] < len(s["questions"]):
            next_q = s["questions"][s["index"]]
        return {"evaluation": eval_res, "rag": rag, "next_question": next_q, "done": next_q is None}

    # ── 两阶段流程：第一次回答 → 追问 → 追问回答后才评测 ──
    if not s.get("awaiting_followup"):
        # 阶段1：收到第一次回答，生成追问
        s["first_answer"] = answer

        # 检索知识库用于生成追问
        kb_contexts = []
        try:
            if s.get('role') and q.get('question'):
                kb_contexts = retriever.retrieve(q['question'], role=s['role'], k=3)
        except Exception:
            pass

        followup = generate_followup_question(
            question=q.get('question', ''),
            answer=answer,
            role=s.get('role', ''),
            kb_contexts=kb_contexts
        )
        s["awaiting_followup"] = True
        s["followup_question"] = followup
        return {"followup": True, "followup_question": followup, "done": False}
    else:
        # 阶段2：收到追问的回答，进行综合评测
        first_answer = s.pop("first_answer", "")
        followup_q = s.pop("followup_question", "")
        s.pop("awaiting_followup", None)

        combined_answer = (
            f"{first_answer}\n\n"
            f"【追问】{followup_q}\n"
            f"【追问回答】{answer}"
        )

        eval_res = evaluate_answer(
            combined_answer,
            q.get("answer_key", ""),
            question=q.get('question', ''),
            role=s.get('role', ''),
            candidate=s.get('candidate', '')
        )
        # RAG: retrieve related knowledge for role
        rag = retriever.retrieve(combined_answer or q.get("question", ""), role=s["role"], k=3)
        # record history
        s["history"].append({
            "question": q,
            "answer": first_answer,
            "followup_question": followup_q,
            "followup_answer": answer,
            "evaluation": eval_res,
            "rag": rag
        })
        s["index"] += 1
        next_q = None
        if s["index"] < len(s["questions"]):
            next_q = s["questions"][s["index"]]
        score = eval_res.get("score") if isinstance(eval_res, dict) else None
        if score is None and isinstance(eval_res, dict):
            llm_detail = eval_res.get("llm_detail") or {}
            if isinstance(llm_detail, dict):
                score = llm_detail.get("overall")

        done = next_q is None
        return {"evaluation": eval_res, "rag": rag, "next_question": next_q, "done": done}


def generate_report(session_id: str) -> Dict[str, Any]:
    s = SESSIONS.get(session_id)
    if not s:
        return {"error": "invalid session"}
    from llm_client import generate_report_with_llm
    history = s.get('history', [])
    # prepare kb contexts (use retriever to fetch role-specific snippets)
    # build a safe query string from history questions (questions may be dicts)
    q_parts = []
    for h in history:
        q = h.get('question', '')
        if isinstance(q, dict):
            q_text = q.get('question') or q.get('text') or ''
        else:
            q_text = str(q)
        if q_text:
            q_parts.append(q_text)
    kb_query = ' '.join(q_parts) if q_parts else s.get('role','')
    kb_contexts = retriever.retrieve(kb_query, role=s.get('role',''), k=5)

    def _aggregate_speech_evals(items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """对多次语音评估结果做简单数值平均，生成一份会话级的综合语音分析。

        不额外调用 LLM，避免增加时延；summary / suggestions 采用最近一次结果，
        同时在 summary 中注明是基于多次语音作答的整体评估。
        """
        if not items:
            return None

        keys = ["speech_rate", "clarity", "confidence", "expressiveness", "overall"]
        totals = {k: 0.0 for k in keys}
        count = 0
        for ev in items:
            if not isinstance(ev, dict):
                continue
            has_any = False
            for k in keys:
                v = ev.get(k)
                if isinstance(v, (int, float)):
                    totals[k] += float(v)
                    has_any = True
            if has_any:
                count += 1

        if count == 0:
            return None

        agg = {k: round(totals[k] / count, 1) for k in keys}

        # 文本部分：优先采用最近一次语音评估的结论
        summaries = [str(ev.get("summary", "")).strip() for ev in items if isinstance(ev, dict) and ev.get("summary")]
        suggestions = [str(ev.get("suggestions", "")).strip() for ev in items if isinstance(ev, dict) and ev.get("suggestions")]

        if summaries:
            base_summary = summaries[-1]
        else:
            base_summary = "本报告基于多次语音作答的整体平均表现给出综合评估。"

        if suggestions:
            base_suggestions = suggestions[-1]
        else:
            base_suggestions = "建议在后续面试中继续保持稳定语速与清晰吐字，并有意识地在关键结论处增加停顿与重音。"

        agg["summary"] = f"基于 {count} 次语音回答的整体表现：" + base_summary
        agg["suggestions"] = base_suggestions
        agg["sample_count"] = count
        return agg
    try:
        report = generate_report_with_llm(history=history, role=s.get('role',''), candidate=s.get('candidate',''), kb_contexts=kb_contexts)
        # attach simple aggregates if not present
        if isinstance(report, dict) and 'overall' not in report:
            # compute simple average of per-turn evaluation scores when available
            scores = []
            for h in history:
                ev = h.get('evaluation', {})
                sc = None
                if isinstance(ev, dict):
                    sc = ev.get('score') or (ev.get('llm_detail', {}) or {}).get('overall')
                if isinstance(sc, (int, float)):
                    scores.append(float(sc))
            if scores:
                report['overall'] = round(sum(scores)/len(scores),1)

        # 若会话存在多次语音评估结果，则在最终报告中补充一个综合语音分析字段
        if isinstance(report, dict):
            speech_items = s.get("speech_evaluations", [])
            speech_summary = _aggregate_speech_evals(speech_items)
            if speech_summary is not None:
                report["speech_evaluation"] = speech_summary
        try:
            storage.save_report_scores(
                session_id=session_id,
                candidate=s.get('candidate', '匿名'),
                role=s.get('role', ''),
                report=report if isinstance(report, dict) else {"raw": report}
            )
        except Exception as oe:
            print("save_report_scores error", oe)
            pass
        return report
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print("interview_core loaded. available roles:", list(QUESTION_BANK.keys()))
