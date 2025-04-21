from typing import Dict, Optional
import json
import os

class LanguageService:
    def __init__(self):
        self.default_language = "en"
        self.current_language = self.default_language
        self.translations = self._load_translations()
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        translations = {}
        translations_dir = "backend/data/translations"
        
        if not os.path.exists(translations_dir):
            os.makedirs(translations_dir)
        
        # Load English translations
        en_file = os.path.join(translations_dir, "en.json")
        if os.path.exists(en_file):
            with open(en_file, "r", encoding="utf-8") as f:
                translations["en"] = json.load(f)
        else:
            translations["en"] = {
                "welcome": "Medical Conversation Analysis System",
                "new_conversation": "New Conversation",
                "new_conversation_desc": "Start a new conversation with a patient",
                "search_conversations": "Search Conversations",
                "search_conversations_desc": "Find and review previous conversations",
                "start_recording": "Start Recording",
                "start_recording_desc": "Record and transcribe a conversation",
                "generate_summary": "Generate Summary",
                "generate_report": "Generate Report",
                "export_pdf": "Export PDF",
                "patient_id": "Patient ID",
                "doctor_id": "Doctor ID",
                "date": "Date",
                "summary": "Summary",
                "transcript": "Transcript",
                "report": "Report",
                "save": "Save",
                "cancel": "Cancel",
                "edit": "Edit",
                "delete": "Delete",
                "confirm_delete": "Are you sure you want to delete this conversation?",
                "yes": "Yes",
                "no": "No"
            }
            with open(en_file, "w", encoding="utf-8") as f:
                json.dump(translations["en"], f, ensure_ascii=False, indent=2)
        
        # Load Chinese translations
        zh_file = os.path.join(translations_dir, "zh.json")
        if os.path.exists(zh_file):
            with open(zh_file, "r", encoding="utf-8") as f:
                translations["zh"] = json.load(f)
        else:
            translations["zh"] = {
                "welcome": "医疗对话分析系统",
                "new_conversation": "新建对话",
                "new_conversation_desc": "开始与患者的新对话",
                "search_conversations": "搜索对话",
                "search_conversations_desc": "查找和查看历史对话",
                "start_recording": "开始录音",
                "start_recording_desc": "录制并转录对话",
                "generate_summary": "生成摘要",
                "generate_report": "生成报告",
                "export_pdf": "导出PDF",
                "patient_id": "患者ID",
                "doctor_id": "医生ID",
                "date": "日期",
                "summary": "摘要",
                "transcript": "转录文本",
                "report": "报告",
                "save": "保存",
                "cancel": "取消",
                "edit": "编辑",
                "delete": "删除",
                "confirm_delete": "确定要删除此对话吗？",
                "yes": "是",
                "no": "否"
            }
            with open(zh_file, "w", encoding="utf-8") as f:
                json.dump(translations["zh"], f, ensure_ascii=False, indent=2)
        
        return translations
    
    def set_language(self, language: str) -> bool:
        if language in self.translations:
            self.current_language = language
            return True
        return False
    
    def get_translation(self, key: str) -> str:
        return self.translations[self.current_language].get(key, key)
    
    def get_all_translations(self) -> Dict[str, str]:
        return self.translations[self.current_language] 