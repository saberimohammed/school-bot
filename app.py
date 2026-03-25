import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import google.generativeai as genai
import datetime

# 1. إعداد الاتصال بجدول بيانات جوجل
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# محاولة الاتصال باستخدام Secrets الخاصة بـ Streamlit (للأمان)
try:
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        # تأكد أن اسم ملف الجدول في حسابك هو SchoolData
        sheet = client.open("SchoolData").sheet1
    else:
        st.error("لم يتم العثور على مفاتيح الربط في Secrets.")
except Exception as e:
    st.error(f"خطأ في الاتصال بجدول البيانات: {e}")

# 2. إعداد ذكاء Gemini الاصطناعي
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
else:
    st.error("لم يتم العثور على مفتاح API الخاص بـ Gemini.")

st.set_page_config(page_title="نظام مدرسة الطفاحة", page_icon="🍎")
st.title("🍎 نظام مدرسة الطفاحة الذكي")
st.subheader("أتمتة تسجيل الحضور والغياب")

user_input = st.text_input("ماذا تريد أن تسجل اليوم؟ (مثلاً: سجل حضور شمس)")

if st.button("تنفيذ"):
    if user_input:
        with st.spinner('جاري معالجة الطلب...'):
            # تحليل النص باستخدام Gemini
            prompt = f"استخرج اسم الطالب وحالته (حضور أو غياب) من النص التالي: '{user_input}'. أجب فقط بصيغة: الاسم، الحالة"
            try:
                response = model.generate_content(prompt)
                res_text = response.text
                
                if "،" in res_text:
                    name, status = res_text.split("،")
                    name = name.strip()
                    status = status.strip()
                    date_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # إضافة البيانات للجدول
                    sheet.append_row([name, status, date_now])
                    st.success(f"✅ تم تسجيل {status} للطالب {name} بنجاح!")
                else:
                    st.warning("يرجى كتابة الاسم والحالة بشكل أوضح.")
            except Exception as e:
                st.error(f"حدث خطأ أثناء التنفيذ: {e}")
    else:
        st.warning("يرجى كتابة نص أولاً.")

st.info("ملاحظة: هذا النظام مربوط بجدول بيانات جوجل SchoolData وبوت التيليجرام الخاص بك.")
