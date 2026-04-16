from flask import Flask, request, jsonify, send_from_directory
from interview_core import create_session, get_current_question, submit_answer, retriever, add_speech_evaluation
from transcribe import transcribe_file
from llm_client import get_available_models, get_current_model_id, set_model, evaluate_speech_with_llm
from storage import storage
from pathlib import Path

app = Flask(__name__, static_folder="static")
BASE_DIR = Path(__file__).parent


def build_position_overview():
    """聚合题库与知识库信息，供前端岗位展示使用。"""
    import json
    from question_bank import test as question_bank

    kb_path = BASE_DIR / 'knowledge_base.json'
    kb_data = {}
    if kb_path.exists():
        with open(kb_path, 'r', encoding='utf-8') as f:
            kb_data = json.load(f)

    all_roles = sorted(set(question_bank.keys()) | set(kb_data.keys()))
    overview = {}

    for role in all_roles:
        q_role = question_bank.get(role, {}) if isinstance(question_bank, dict) else {}
        q_items = q_role.get('question_bank', []) if isinstance(q_role, dict) else []
        q_items = q_items if isinstance(q_items, list) else []

        type_stats = {}
        for q in q_items:
            q_type = (q or {}).get('type', 'other') if isinstance(q, dict) else 'other'
            type_stats[q_type] = type_stats.get(q_type, 0) + 1

        kb_items = kb_data.get(role, [])
        kb_items = kb_items if isinstance(kb_items, list) else []
        kb_titles = []
        for item in kb_items:
            if not isinstance(item, dict):
                continue
            title = str(item.get('title') or '').strip()
            if title:
                kb_titles.append(title)
            if len(kb_titles) >= 5:
                break

        overview[role] = {
            'role': role,
            'definition': q_role.get('definition', '') if isinstance(q_role, dict) else '',
            'question_count': len(q_items),
            'question_types': type_stats,
            'knowledge_count': len(kb_items),
            'knowledge_titles': kb_titles,
        }

    return overview


@app.route('/')
def index():
    return send_from_directory(str(BASE_DIR / 'static'), 'index_v3.html')


@app.route('/growth')
def growth_page():
    return send_from_directory(str(BASE_DIR / 'static'), 'growth.html')


@app.route('/api/positions', methods=['GET'])
def positions():
    try:
        overview = build_position_overview()
        return jsonify({"positions": list(overview.keys()), "overview": overview})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/position_overview', methods=['GET'])
def position_overview():
    """获取岗位画像，支持通过 role 查询单个岗位。"""
    role = (request.args.get('role') or '').strip()
    try:
        overview = build_position_overview()
        if role:
            if role not in overview:
                return jsonify({"error": f"unknown role: {role}"}), 404
            return jsonify(overview[role])
        return jsonify({"positions": overview})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/candidates', methods=['GET'])
def candidates():
    try:
        cands = storage.get_candidates()
        return jsonify({"candidates": cands})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/start', methods=['POST'])
def start():
    body = request.json or {}
    role = body.get('role')
    candidate = body.get('candidate', '匿名')
    num_questions = body.get('num_questions', 5)
    followup_enabled = body.get('followup_enabled', True)

    if isinstance(followup_enabled, str):
        followup_enabled = followup_enabled.strip().lower() in ('1', 'true', 'yes', 'on')

    try:
        sid = create_session(
            role,
            candidate,
            num_questions=int(num_questions),
            followup_enabled=bool(followup_enabled)
        )
        q = get_current_question(sid)
        return jsonify({"session_id": sid, "first_question": q})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/question', methods=['GET'])
def question():
    sid = request.args.get('session_id')
    q = get_current_question(sid)
    if not q:
        return jsonify({"message": "no question or invalid session"}), 404
    return jsonify(q)


@app.route('/api/answer', methods=['POST'])
def answer():
    body = request.json or {}
    sid = body.get('session_id')
    answer_text = body.get('answer', '')
    res = submit_answer(sid, answer_text)
    return jsonify(res)



@app.route('/api/answer_audio', methods=['POST'])
def answer_audio():
    # expects multipart form: session_id and file field 'audio'
    sid = request.form.get('session_id')
    if 'audio' not in request.files:
        return jsonify({"error": "no audio file"}), 400
    f = request.files['audio']
    tmp_dir = BASE_DIR / 'tmp_audio'
    tmp_dir.mkdir(exist_ok=True)
    tmp_path = tmp_dir / f"upload_{f.filename}"
    f.save(str(tmp_path))
    try:
        text = transcribe_file(str(tmp_path))
    except Exception as e:
        return jsonify({"error": f"transcription failed: {e}"}), 500

    # Capture question context before submit (submit may advance state)
    current_q = get_current_question(sid) or {}
    question_text = current_q.get('question', '') if isinstance(current_q, dict) else ''

    res = submit_answer(sid, text)
    # Voice-expression evaluation is only executed for audio input flow.
    try:
        speech_eval = evaluate_speech_with_llm(
            audio_path=str(tmp_path),
            transcript=text,
            question=question_text,
        )
        # 记录到会话，用于最终报告生成综合语音分析
        try:
            add_speech_evaluation(sid, speech_eval)
        except Exception:
            # 不影响主流程，静默失败
            pass
        res['speech_evaluation'] = speech_eval
    except Exception as e:
        res['speech_evaluation'] = {
            "speech_rate": 0,
            "clarity": 0,
            "confidence": 0,
            "expressiveness": 0,
            "overall": 0,
            "summary": "语音评估失败",
            "suggestions": str(e),
        }
    # include transcription for user
    res['transcription'] = text
    return jsonify(res)


@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "no audio file"}), 400
    f = request.files['audio']
    tmp_dir = BASE_DIR / 'tmp_audio'
    tmp_dir.mkdir(exist_ok=True)
    tmp_path = tmp_dir / f"upload_{f.filename}"
    f.save(str(tmp_path))
    try:
        text = transcribe_file(str(tmp_path))
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/report', methods=['GET', 'POST'])
def report():
    # accept session_id via query or json form
    sid = request.args.get('session_id') or (request.json or {}).get('session_id')
    if not sid:
        return jsonify({"error": "session_id required"}), 400
    try:
        from interview_core import generate_report
        rep = generate_report(sid)
        return jsonify(rep)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── 模型选择接口 ──────────────────────────────────────────────

@app.route('/api/models', methods=['GET'])
def list_models():
    """返回可用模型列表及当前选中模型。"""
    return jsonify({
        "models": get_available_models(),
        "current": get_current_model_id()
    })


@app.route('/api/set_model', methods=['POST'])
def set_model_api():
    """切换当前使用的 LLM 模型。Body: {"model_id": "deepseek"}"""
    body = request.json or {}
    model_id = body.get('model_id', '').strip()
    if not model_id:
        return jsonify({"error": "model_id 为必填字段"}), 400
    if set_model(model_id):
        return jsonify({"message": f"已切换到 {model_id}", "current": get_current_model_id()})
    return jsonify({"error": f"未知的模型 ID: {model_id}"}), 400


# ── 知识库管理接口 ──────────────────────────────────────────────

@app.route('/api/kb/list', methods=['GET'])
def kb_list():
    """查看当前知识库所有内容。"""
    data = retriever.list_entries()
    summary = {role: len(items) for role, items in data.items()}
    return jsonify({"doc_count": len(retriever.docs), "summary": summary, "data": data})


@app.route('/api/kb/add', methods=['POST'])
def kb_add():
    """添加一条知识到知识库，自动重建向量索引。
    Body: {"role": "岗位名", "title": "标题", "text": "知识内容"}
    """
    body = request.json or {}
    role = body.get('role', '').strip()
    title = body.get('title', '').strip()
    text = body.get('text', '').strip()
    if not role or not text:
        return jsonify({"error": "role 和 text 为必填字段"}), 400
    try:
        retriever.add_entry(role, title or "未命名", text)
        return jsonify({"message": "添加成功并已重建索引", "doc_count": len(retriever.docs)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/kb/reload', methods=['POST'])
def kb_reload():
    """手动触发知识库重新加载（修改 JSON 后调用）。"""
    try:
        retriever.reload()
        return jsonify({"message": "知识库已重建", "doc_count": len(retriever.docs)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/growth_curve', methods=['GET'])
def growth_curve():
    """获取候选人的成长曲线数据。Query: candidate, role(optional), limit(optional)"""
    candidate = (request.args.get('candidate') or '').strip()
    role = (request.args.get('role') or '').strip()
    limit = request.args.get('limit', '20')

    if not candidate:
        return jsonify({"error": "candidate is required"}), 400

    try:
        points = storage.get_growth_curve(candidate=candidate, role=role or None, limit=int(limit))
        scores = [p.get("score") for p in points if isinstance(p.get("score"), (int, float))]
        latest = scores[-1] if scores else None
        best = max(scores) if scores else None
        delta = round(latest - scores[0], 2) if len(scores) >= 2 and latest is not None else None
        return jsonify({
            "candidate": candidate,
            "role": role or None,
            "count": len(points),
            "latest": latest,
            "best": best,
            "delta": delta,
            "points": points,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
