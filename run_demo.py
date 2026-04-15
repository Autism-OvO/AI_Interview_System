"""
简单命令行演示：无需启动 Flask，直接使用 core 模块进行模拟面试。
"""
from interview_core import create_session, get_current_question, submit_answer
import tempfile
import os

try:
    import sounddevice as sd
    import soundfile as sf
    HAVE_SOUND = True
except Exception:
    HAVE_SOUND = False

from transcribe import transcribe_file


def run():
    print("AI 面试演示 (命令行)\n可选岗位：Python_Algorithm_Engineer, Java_Backend_Engineer, Web_Frontend_Engineer")
    role = input("选择岗位 (精确名称): ").strip()
    name = input("输入你的姓名 (回车默认 匿名): ").strip() or "匿名"
    try:
        sid = create_session(role, name)
    except Exception as e:
        print("创建会话失败：", e)
        return
    while True:
        q = get_current_question(sid)
        if not q:
            print("面试结束，感谢练习！")
            break
        print("\n问题：", q.get('question'))
        mode = input("输入方式：1 文本  2 语音(麦克风)  3 退出 请输入 1/2/3: ").strip()
        if mode == '3':
            print("提前结束")
            break
        if mode == '1':
            ans = input("你的回答（输入 /quit 结束）：\n")
            if ans.strip() == "/quit":
                print("提前结束")
                break
            res = submit_answer(sid, ans)
        elif mode == '2':
            if not HAVE_SOUND:
                print("本地未检测到录音依赖 (sounddevice/soundfile)。请安装或使用文本输入。")
                continue
            try:
                dur = input("录音时长(秒，默认5): ").strip()
                dur = float(dur) if dur else 5.0
            except Exception:
                dur = 5.0
            print(f"开始录音 {dur} 秒... 请在麦克风前答题。按 Ctrl+C 可中断")
            fs = 16000
            try:
                rec = sd.rec(int(dur * fs), samplerate=fs, channels=1, dtype='int16')
                sd.wait()
            except Exception as e:
                print("录音失败：", e)
                continue
            tmpf = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            try:
                sf.write(tmpf.name, rec, fs)
                print("录音保存至:", tmpf.name)
                print("正在转录...")
                text = transcribe_file(tmpf.name)
                print("转录结果：", text)
                res = submit_answer(sid, text)
            finally:
                try:
                    os.unlink(tmpf.name)
                except Exception:
                    pass
        else:
            print("无效选项")
            continue

        print("评估结果：")
        # print llm_detail if exists
        if res.get('evaluation'):
            print(res.get('evaluation'))
        elif res.get('llm_detail'):
            print(res.get('llm_detail'))
        else:
            print(res)
        print("推荐知识片段：")
        for r in res.get('rag', []):
            print(" -", r.get('text')[:200].replace('\n', ' '))

        # allow user to request final report at any time
        ask = input("输入 /report 获取会话最终报告，或按回车继续下一题：\n")
        if ask.strip() == "/report":
            from interview_core import generate_report
            rep = generate_report(sid)
            print("\n=== 最终报告 ===")
            import json
            print(json.dumps(rep, ensure_ascii=False, indent=2))
            print("=== 报告结束 ===\n")


if __name__ == '__main__':
    run()
