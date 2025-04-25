import os
import sqlite3
from datetime import datetime
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from openai import OpenAI
import gradio as gr
import tempfile
import PyPDF2

# Ensure OpenAI API key is set
# api_key = os.getenv("OPENAI_API_KEY")
api_key = ''
if not api_key:
    raise ValueError("请设置环境变量 OPENAI_API_KEY 以使用本应用。")
# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Database setup
DB_PATH = "assistant.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()
# History table
c.execute('''CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY,
    doctor TEXT,
    patient TEXT,
    date TEXT,
    transcript TEXT,
    summary TEXT,
    diseases TEXT
)''')
conn.commit()

# Internationalization
i18n = {
    '中文': {
        'new': '新对话', 'history': '历史记录',
        'doctor': '医生姓名', 'patient': '病人姓名', 'date': '日期',
        'audio': '录制/上传音频', 'file': '上传文件', 'submit': '提交',
        'transcript': '转录文本', 'summary': '医用总结', 'download': '下载文档',
        'text_input': '📄 文本输入（上传后自动填入，也可手动修改）',
        'md_preview': '📄 格式化总结（仅预览）',
        'md_editor': '✏️ 编辑总结（可修改）'
        
    },
    'English': {
        'new': 'New Conversation', 'history': 'History',
        'doctor': 'Doctor Name', 'patient': 'Patient Name', 'date': 'Date',
        'audio': 'Record/Upload Audio', 'file': 'Upload File', 'submit': 'Submit',
        'transcript': 'Transcript', 'summary': 'Medical Summary', 'download': 'Download PDF',
        'text_input': '📄 Input Text (Auto-filled from upload, editable)',
        'md_preview': '📄 Markdown Summary (Preview)',
        'md_editor': '✏️ Edit Summary (Markdown)'

    }
}

# Audio transcription (Whisper)
def transcribe_audio(audio_path, file_obj):
    if audio_path:
        f = open(audio_path, 'rb')
    elif file_obj:
        f = open(file_obj.name, 'rb')
    else:
        return ""
    resp = client.audio.transcriptions.create(
        file=f,
        model="whisper-1"
    )
    f.close()
    return resp.text

# Summarize and extract possible diagnoses
def summarize_and_extract(text, info):
    prompt = (
        f"Patient Info: {info}\n"
        f"Transcript: {text}\n"
        "Please summarize the above dialogue in a medical report style and list possible diagnoses."
    )
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content

# File reading
def handle_uploaded_file(file):
    if file is None:
        return ""
    ext = os.path.splitext(file.name)[-1].lower()
    if ext == ".txt":
        with open(file.name, "r", encoding="utf-8") as f:
            return f.read()
    elif ext == ".pdf":
        reader = PyPDF2.PdfReader(file.name)
        return "\n".join([page.extract_text() or "" for page in reader.pages])
    return "❌ Unsupported file format. Please upload PDF or TXT."


# Generate downloadable PDF report
def generate_report(info, transcript, summary, session_id, knowledge=[]):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(f"Session #{session_id} — Patient Info: {info}", styles['Title']))
    story.append(Spacer(1,12))
    story.append(Paragraph("Transcript:", styles['Heading2']))
    story.append(Paragraph(transcript.replace("\n","<br/>"), styles['BodyText']))
    story.append(Spacer(1,12))
    story.append(Paragraph("Summary & Possible Diagnoses:", styles['Heading2']))
    story.append(Paragraph(summary.replace("\n","<br/>"), styles['BodyText']))
    story.append(Spacer(1,12))
    if knowledge:
        story.append(Paragraph("Related Knowledge:", styles['Heading2']))
        for q, a in knowledge:
            story.append(Paragraph(f"Q: {q}", styles['BodyText']))
            story.append(Paragraph(f"A: {a}", styles['BodyText']))
            story.append(Spacer(1,8))
    doc.build(story)
    buffer.seek(0)
    return buffer

# Build Gradio UI
def build_ui():
    with gr.Blocks() as demo:
        # Language selector
        lang = gr.Radio(choices=['中文', 'English'], value='中文', label="Language")
        # Tabs for new conversation and history
        with gr.Tabs() as tabs:
            with gr.Tab(i18n['中文']['new']) as new_tab:
                doctor = gr.Textbox(label=i18n['中文']['doctor'])
                patient = gr.Textbox(label=i18n['中文']['patient'])
                date = gr.Textbox(label=i18n['中文']['date'], value=str(datetime.today().date()))
                audio = gr.Audio(label=i18n['中文']['audio'], type='filepath')
                file_obj = gr.File(label=i18n['中文']['file'], 
                    file_types=[".pdf", ".txt", ".docx"],
                    interactive=True
                )
                text_input = gr.Textbox(label=i18n['中文']['text_input'], lines=10)
                btn = gr.Button(value=i18n['中文']['submit'])
                transcript_out = gr.Textbox(label=i18n['中文']['transcript'])
                summary_out = gr.Textbox(label=i18n['中文']['summary'])
                pdf_file = gr.File(label=i18n['中文']['download'], visible=False)
                summary_md = gr.Markdown(label="📄 格式化总结（仅预览）", visible=False)
                summary_editor = gr.Textbox(label="✏️ 编辑总结 (Markdown)", lines=10, visible=False, interactive=True)

                file_obj.change(
                    fn=handle_uploaded_file,
                    inputs=file_obj,
                    outputs=text_input
                )

                import tempfile

                def new_conversation(lang_sel, doc_name, pat_name, date_str, audio_path, file_upload, manual_text):
                    if manual_text.strip():
                        transcript = manual_text
                    else:
                        transcript = transcribe_audio(audio_path, file_upload)
                        
                    # Transcription and summary
                    info = f"Doctor: {doc_name}; Patient: {pat_name}; Date: {date_str}"
                    # transcript = transcribe_audio(audio_path, file_upload)
                    summary = summarize_and_extract(transcript, info)
                    
                    c.execute("SELECT MAX(id) FROM history")
                    last_id = c.fetchone()[0] or 0
                    session_id = last_id + 1

                    # Save to history
                    diseases = [l for l in summary.splitlines() if 'possible' in l.lower() or '可能' in l]
                    c.execute(
                        "INSERT INTO history (id, doctor, patient, date, transcript, summary, diseases) VALUES (?,?,?,?,?,?,?)",
                        (session_id, doc_name, pat_name, date_str, transcript, summary, ','.join(diseases))
                    )
                    conn.commit()

                    # Generate PDF in memory
                    pdf_buffer = generate_report(info, transcript, summary, session_id)

                    # Write to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(pdf_buffer.read())
                        tmp_path = tmp.name
                    
                    # Markdown Summary: 显示 session 编号
                    md_summary = f"**This conversation is Session #{session_id}**\n\n{summary}"

                    return (
                        transcript,
                        summary,
                        gr.update(value=tmp_path, visible=True),
                        gr.update(value=md_summary, visible=True),   # 格式化 Markdown 展示
                        gr.update(value=summary, visible=True)    # 文本框可编辑
                        
                    )



                btn.click(
                    fn=new_conversation,
                    inputs=[lang, doctor, patient, date, audio, file_obj, text_input],
                    outputs=[transcript_out, summary_out, pdf_file, summary_md, summary_editor]
                )

            with gr.Tab(i18n['中文']['history']) as history_tab:
                hist_btn = gr.Button(value=i18n['中文']['history'])
                history_table = gr.Dataframe(visible=False)

                def view_history(lang_sel):
                    labels = i18n[lang_sel]
                    history_tab.update(label=labels['history'])
                    hist_btn.update(value=labels['history'])
                    c.execute("SELECT id, date, patient FROM history ORDER BY id DESC")
                    rows = c.fetchall()
                    return gr.Dataframe.update(
                        value=[[rid, dt, pt] for rid, dt, pt in rows],
                        headers=["ID", "Date", "Patient"],
                        visible=True
                    )

                hist_btn.click(
                    fn=view_history,
                    inputs=[lang],
                    outputs=[history_table]
                )
        # Language switch callback
        def update_labels(lang_sel):
            labels = i18n[lang_sel]
            return [
                gr.update(label=labels['new']),      # new_tab
                gr.update(label=labels['history']),  # history_tab
                gr.update(label=labels['doctor']),   # doctor
                gr.update(label=labels['patient']),  # patient
                gr.update(label=labels['date']),     # date
                gr.update(label=labels['audio']),    # audio
                gr.update(label=labels['file']),     # file_obj
                gr.update(value=labels['submit']),   # btn
                gr.update(label=labels['transcript']),# transcript_out
                gr.update(label=labels['summary']),  # summary_out
                gr.update(label=labels['download']), # pdf_file
                gr.update(value=labels['history']),   # hist_btn
                gr.update(label=labels['text_input']),
                gr.update(label=labels['md_preview']),
                gr.update(label=labels['md_editor'])

            ]

        lang.change(
            fn=update_labels,
            inputs=[lang],
            outputs=[new_tab, history_tab, doctor, patient, date, audio, file_obj, btn, transcript_out, summary_out, pdf_file, hist_btn, text_input, summary_md, summary_editor]
        )
        return demo

app = build_ui()
app.launch()
