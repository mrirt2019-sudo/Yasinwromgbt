import requests
import telebot
import json
import os
from datetime import datetime
from telebot import types

# معلومات المطور
DEVELOPER_TELEGRAM = "@yasin_vipxit"
DEVELOPER_INSTAGRAM = "cr___fans1"
WEBSITE_NAME = "wormyasin"

# تهيئة البوت
token = '7821055940:AAH_tYge4lazPVB19SDfnMH7endhj12Oc4Y'
bot = telebot.TeleBot(token)

# تخزين محادثات المستخدمين (في بيئة حقيقية، استخدم قاعدة بيانات)
user_conversations = {}

class ConversationManager:
    """مدير المحادثات لحفظ واسترجاع محادثات المستخدمين"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.conversation_file = f"conversations/{user_id}.json"
        
        # إنشاء مجلد المحادثات إذا لم يكن موجوداً
        os.makedirs("conversations", exist_ok=True)
        
        # تحميل المحادثة الحالية للمستخدم
        self.load_conversation()
    
    def load_conversation(self):
        """تحميل محادثة المستخدم من الملف"""
        try:
            if os.path.exists(self.conversation_file):
                with open(self.conversation_file, 'r', encoding='utf-8') as f:
                    user_conversations[self.user_id] = json.load(f)
            else:
                user_conversations[self.user_id] = []
        except:
            user_conversations[self.user_id] = []
    
    def save_conversation(self):
        """حفظ محادثة المستخدم إلى الملف"""
        try:
            with open(self.conversation_file, 'w', encoding='utf-8') as f:
                json.dump(user_conversations[self.user_id], f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def add_message(self, role, content):
        """إضافة رسالة إلى المحادثة"""
        if self.user_id not in user_conversations:
            user_conversations[self.user_id] = []
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        user_conversations[self.user_id].append(message)
        
        # حفظ المحادثة
        self.save_conversation()
    
    def get_conversation_history(self, limit=10):
        """الحصول على تاريخ المحادثة (آخر limit رسائل)"""
        if self.user_id not in user_conversations:
            return []
        
        return user_conversations[self.user_id][-limit:]
    
    def clear_conversation(self):
        """مسح محادثة المستخدم"""
        user_conversations[self.user_id] = []
        self.save_conversation()
        return True

def get_ai_response(text, user_id=None):
    """الحصول على رد من الذكاء الاصطناعي"""
    try:
        # إضافة سياق المحادثة إذا كان user_id موجوداً
        if user_id and user_id in user_conversations and user_conversations[user_id]:
            # أخذ آخر 5 رسائل للسياق
            history = user_conversations[user_id][-5:]
            context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
            enhanced_text = f"السياق السابق:\n{context}\n\nالسؤال الحالي: {text}"
        else:
            enhanced_text = text
        
        # استدعاء API الذكاء الاصطناعي
        res = requests.get(f'https://api-vetrex.x10.network/api/wormgpt_ai.php?text={enhanced_text}', timeout=30)
        
        if res.status_code == 200:
            data = res.json()
            return data.get('response', 'لم أتمكن من الحصول على رد. يرجى المحاولة مرة أخرى.')
        else:
            return f"خطأ في الخادم: {res.status_code}"
    except Exception as e:
        return f"حدث خطأ: {str(e)}"

@bot.message_handler(commands=['start'])
def start_command(message):
    """معالج أمر /start"""
    welcome_text = f"""
<strong>مرحباً {message.from_user.first_name}! 👋</strong>

🤖 <b>أنا بوت الذكاء الاصطناعي المتكامل</b>
💬 يمكنني مساعدتك في الإجابة على أسئلتك ومحادثتك

📌 <b>مطور البوت:</b> {DEVELOPER_TELEGRAM}
📷 <b>انستقرام:</b> {DEVELOPER_INSTAGRAM}
🌐 <b>الموقع:</b> {WEBSITE_NAME}.com

🔧 <b>الأوامر المتاحة:</b>
/start - بدء التشغيل
/help - المساعدة
/clear - مسح المحادثة
/history - عرض آخر المحادثات
/copy - نسخ المحادثة الحالية
/about - معلومات عن البوت

<strong>⚠️ تنبيه:</strong> هذا المشروع تم إنشاؤه لأغراض تعليمية وبحثية فقط، وأنا لست مسؤولاً عن أي سوء استخدام أو أنشطة غير قانونية يتم تنفيذها باستخدام هذه الأداة. المستخدم هو المسؤول الوحيد عن كيفية اختياره لاستخدامها.
"""
    
    # إنشاء أزرار الواجهة
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    btn1 = types.KeyboardButton('💬 محادثة جديدة')
    btn2 = types.KeyboardButton('🗑️ مسح المحادثة')
    btn3 = types.KeyboardButton('📋 نسخ المحادثة')
    btn4 = types.KeyboardButton('ℹ️ معلومات')
    
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML', reply_markup=markup)
    
    # تهيئة مدير المحادثات للمستخدم
    ConversationManager(message.chat.id)

@bot.message_handler(commands=['help'])
def help_command(message):
    """معالج أمر /help"""
    help_text = f"""
<strong>📖 دليل المساعدة</strong>

💬 <b>كيفية الاستخدام:</b>
- فقط اكتب سؤالك وسأجيب عليه
- استخدم الأوامر للتحكم في البوت

🔧 <b>قائمة الأوامر:</b>
/start - بدء التشغيل وعرض القائمة الرئيسية
/help - عرض هذه الرسالة المساعدة
/clear - مسح محادثتك الحالية
/history - عرض آخر 5 رسائل من محادثتك
/copy - نسخ محادثتك الحالية كنص
/about - معلومات عن البوت والمطور

🎛️ <b>الأزرار:</b>
- يمكنك استخدام الأزرار الظاهرة أسفل الشاشة للتحكم السريع

<strong>📞 الدعم:</strong>
{DEVELOPER_TELEGRAM} - {DEVELOPER_INSTAGRAM}
"""
    
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')

@bot.message_handler(commands=['clear'])
def clear_command(message):
    """معالج أمر /clear لمسح المحادثة"""
    conv_manager = ConversationManager(message.chat.id)
    if conv_manager.clear_conversation():
        bot.send_message(message.chat.id, "✅ تم مسح محادثتك بنجاح!")
    else:
        bot.send_message(message.chat.id, "❌ حدث خطأ أثناء محاولة مسح المحادثة.")

@bot.message_handler(commands=['history'])
def history_command(message):
    """معالج أمر /history لعرض تاريخ المحادثة"""
    conv_manager = ConversationManager(message.chat.id)
    history = conv_manager.get_conversation_history(5)
    
    if not history:
        bot.send_message(message.chat.id, "📭 لا توجد محادثات سابقة.")
        return
    
    history_text = "<strong>📜 آخر 5 رسائل من محادثتك:</strong>\n\n"
    
    for i, msg in enumerate(history, 1):
        role_emoji = "👤" if msg["role"] == "user" else "🤖"
        history_text += f"{role_emoji} <b>{msg['role']}:</b> {msg['content'][:50]}...\n"
        history_text += f"   <i>⏰ {msg['timestamp']}</i>\n\n"
    
    bot.send_message(message.chat.id, history_text, parse_mode='HTML')

@bot.message_handler(commands=['copy'])
def copy_command(message):
    """معالج أمر /copy لنسخ المحادثة"""
    conv_manager = ConversationManager(message.chat.id)
    history = conv_manager.get_conversation_history(50)
    
    if not history:
        bot.send_message(message.chat.id, "📭 لا توجد محادثات لنسخها.")
        return
    
    copy_text = f"💾 محادثة من بوت {WEBSITE_NAME}\n\n"
    
    for msg in history:
        role = "أنت" if msg["role"] == "user" else "البوت"
        copy_text += f"{role}: {msg['content']}\n"
        copy_text += f"الوقت: {msg['timestamp']}\n\n"
    
    # في بيئة حقيقية، قد ترغب في حفظ النص في ملف وإرساله
    bot.send_message(message.chat.id, f"📋 <b>تم تجهيز المحادثة للنسخ:</b>\n\n<code>{copy_text[:1000]}...</code>\n\n<strong>يمكنك نسخ النص أعلاه</strong>", parse_mode='HTML')

@bot.message_handler(commands=['about'])
def about_command(message):
    """معالج أمر /about"""
    about_text = f"""
<strong>🤖 معلومات عن البوت</strong>

<b>اسم البوت:</b> WormYasin AI
<b>الوصف:</b> بوت ذكاء اصطناعي متكامل مع موقع ويب

<b>👨‍💻 المطور:</b> {DEVELOPER_TELEGRAM}
<b>📷 انستقرام:</b> {DEVELOPER_INSTAGRAM}
<b>🌐 الموقع الإلكتروني:</b> {WEBSITE_NAME}.com

<b>⚙️ الإصدار:</b> 2.0 متكامل
<b>📅 تاريخ التحديث:</b> {datetime.now().strftime('%Y-%m-%d')}

<strong>⚠️ تنبيه:</strong>
هذا المشروع تم إنشاؤه لأغراض تعليمية وبحثية فقط. المستخدم هو المسؤول الوحيد عن كيفية استخدامه.
"""
    
    bot.send_message(message.chat.id, about_text, parse_mode='HTML')

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """معالج جميع الرسائل النصية"""
    user_id = message.chat.id
    user_text = message.text.strip()
    
    # التحقق من الأزرار
    if user_text == '💬 محادثة جديدة':
        conv_manager = ConversationManager(user_id)
        conv_manager.clear_conversation()
        bot.send_message(user_id, "🆕 تم بدء محادثة جديدة! يمكنك البدء بالكتابة.")
        return
    
    elif user_text == '🗑️ مسح المحادثة':
        conv_manager = ConversationManager(user_id)
        conv_manager.clear_conversation()
        bot.send_message(user_id, "✅ تم مسح المحادثة بنجاح!")
        return
    
    elif user_text == '📋 نسخ المحادثة':
        copy_command(message)
        return
    
    elif user_text == 'ℹ️ معلومات':
        about_command(message)
        return
    
    # إدارة المحادثة
    conv_manager = ConversationManager(user_id)
    
    # إضافة رسالة المستخدم إلى المحادثة
    conv_manager.add_message("user", user_text)
    
    # إظهار أن البوت يكتب
    bot.send_chat_action(user_id, 'typing')
    
    # الحصول على رد الذكاء الاصطناعي
    ai_response = get_ai_response(user_text, user_id)
    
    # إضافة رد البوت إلى المحادثة
    conv_manager.add_message("assistant", ai_response)
    
    # إرسال الرد مع توقيع
    response_text = f"{ai_response}\n\n<strong>📍 {DEVELOPER_TELEGRAM} | {WEBSITE_NAME}</strong>"
    bot.send_message(user_id, response_text, parse_mode='HTML')

if __name__ == "__main__":
    print("🤖 بدأ تشغيل بوت الذكاء الاصطناعي المتكامل...")
    print(f"👨‍💻 المطور: {DEVELOPER_TELEGRAM}")
    print(f"🌐 الموقع: {WEBSITE_NAME}.com")
    
    # تشغيل البوت
    bot.polling(none_stop=True)