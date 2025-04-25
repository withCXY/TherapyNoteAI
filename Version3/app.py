import os
import sqlite3
from datetime import datetime
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from openai import OpenAI
import gradio as gr

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
        'transcript': '转录文本', 'summary': '医用总结', 'download': '下载文档'
    },
    'English': {
        'new': 'New Conversation', 'history': 'History',
        'doctor': 'Doctor Name', 'patient': 'Patient Name', 'date': 'Date',
        'audio': 'Record/Upload Audio', 'file': 'Upload File', 'submit': 'Submit',
        'transcript': 'Transcript', 'summary': 'Medical Summary', 'download': 'Download PDF'
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

# Generate downloadable PDF report
def generate_report(info, transcript, summary, knowledge=[]):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(f"Patient Info: {info}", styles['Title']))
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
                file_obj = gr.File(label=i18n['中文']['file'])
                btn = gr.Button(value=i18n['中文']['submit'])
                transcript_out = gr.Textbox(label=i18n['中文']['transcript'])
                summary_out = gr.Textbox(label=i18n['中文']['summary'])
                pdf_file = gr.File(label=i18n['中文']['download'], visible=False)

                import tempfile

                def new_conversation(lang_sel, doc_name, pat_name, date_str, audio_path, file_upload):
                    # Transcription and summary
                    info = f"Doctor: {doc_name}; Patient: {pat_name}; Date: {date_str}"
                    transcript = transcribe_audio(audio_path, file_upload)
                    summary = summarize_and_extract(transcript, info)

                    # Save to history
                    diseases = [l for l in summary.splitlines() if 'possible' in l.lower() or '可能' in l]
                    c.execute(
                        "INSERT INTO history (doctor, patient, date, transcript, summary, diseases) VALUES (?,?,?,?,?,?)",
                        (doc_name, pat_name, date_str, transcript, summary, ','.join(diseases))
                    )
                    conn.commit()

                    # Generate PDF in memory
                    pdf_buffer = generate_report(info, transcript, summary)

                    # Write to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(pdf_buffer.read())
                        tmp_path = tmp.name

                    return transcript, summary, gr.update(value=tmp_path, visible=True)


                btn.click(
                    fn=new_conversation,
                    inputs=[lang, doctor, patient, date, audio, file_obj],
                    outputs=[transcript_out, summary_out, pdf_file]
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
                gr.update(value=labels['history'])   # hist_btn
            ]

        lang.change(
            fn=update_labels,
            inputs=[lang],
            outputs=[new_tab, history_tab, doctor, patient, date, audio, file_obj, btn, transcript_out, summary_out, pdf_file, hist_btn]
        )
        return demo

app = build_ui()
app.launch()
