import streamlit as st
from PIL import Image
from ultralytics import YOLO

# Page Configuration
st.set_page_config(
    page_title="AI Crop Doctor Dashboard",
    page_icon="🌱",
    layout="wide"
)

# ----------------- KNOWLEDGE BASE & DETAILED TREATMENTS -----------------
DISEASE_DB = {
    "strawberry leaf scorch": {
        "plant": "Strawberry",
        "disease": "Leaf Scorch (Diplocarpon earlianum)",
        "dosage": "2.5g Copper Fungicide per 1 Litre of water.",
        "symptoms": {
            "English": "Irregular purple-to-brown blotches on leaves that enlarge and cause foliage to look burned.",
            "Urdu": "پتوں پر جامنی اور بھورے دھبے بنتے ہیں جو پھیل کر پتوں کو جلے ہوئے جیسا بنا دیتے ہیں۔",
            "Pashto": "پر پاڼو ارغواني او نسواري داغونه جوړیږي چې وروسته پاڼې داسې ښکاري لکه سوځیدلې وي."
        },
        "chemical_treatment": {
            "English": "Apply Copper-based fungicides or Captan at first sign of lesions. Repeat spray every 10-14 days.",
            "Urdu": "تانبے (Copper) والے فنگسائڈ یا کیپٹان (Captan) کا فوراً اسپرے کریں۔ 10 سے 14 دن بعد دوبارہ دہرائیں۔",
            "Pashto": "د مسو پر بنسټ فنګس وژونکي یا کیپټان سپری کړئ. هر 10 تر 14 ورځو وروسته یې بیا تکرار کړئ."
        },
        "cultural_prevention": {
            "English": "Prune and incinerate infected foliage. Avoid overhead sprinklers; ensure 12-18 inch plant spacing for proper airflow.",
            "Urdu": "متاثرہ پتوں کو کاٹ کر جلا دیں۔ فوارے سے پانی دینے سے بچیں اور پودوں میں مناسب فاصلہ رکھیں۔",
            "Pashto": "سختې اغیزمنې پاڼې پرې او وسوزوئ. د سر له لارې اوبه مه ورکوئ او د بوټو ترمنځ مناسب واټن وساتئ."
        }
    },
    "tomato early blight": {
        "plant": "Tomato",
        "disease": "Early Blight (Alternaria solani)",
        "dosage": "2g Mancozeb / Chlorothalonil per 1 Litre of water.",
        "symptoms": {
            "English": "Concentric rings forming dark brown target spots on older lower leaves, progressing upwards.",
            "Urdu": "نیچے والے پرانے پتوں پر گول دائروں کی شکل میں گہرے بھورے دھبے جو بتدریج اوپر پھیلتے ہیں۔",
            "Pashto": "په زړو پاڼو تور نسواري ګرد داغونه جوړیږي او پورته نویو پاڼو ته خپریږي."
        },
        "chemical_treatment": {
            "English": "Spray Chlorothalonil, Mancozeb, or Copper Hydroxide immediately to arrest fungal spread.",
            "Urdu": "کلوروتھالونل (Chlorothalonil) یا مینکو زیب (Mancozeb) کا اسپرے کریں تاکہ بیماری کا پھیلاؤ رک سکے۔",
            "Pashto": "کلوروتهالونیل یا مینکوزیب فنګس وژونکي سمدستي سپری کړئ ترڅو ناروغي نوره خپره نشي."
        },
        "cultural_prevention": {
            "English": "Prune lower infected foliage. Stake plants off the ground and use drip irrigation.",
            "Urdu": "نچلے متاثرہ پتوں کی چھٹائی کریں۔ پودوں کو زمین سے اونچا رکھیں اور ڈرپ ایریگیشن اپنائیں۔",
            "Pashto": "لاندینۍ اغیزمنې پاڼې پرې کړئ، بوټي پورته وتړئ او د څاڅکو اوبو سیستم وکاروئ."
        }
    },
    "tomato late blight": {
        "plant": "Tomato",
        "disease": "Late Blight (Phytophthora infestans)",
        "dosage": "2.5g Ridomil Gold (Metalaxyl + Mancozeb) per 1 Litre of water.",
        "symptoms": {
            "English": "Water-soaked dark lesions on leaves and stems expanding rapidly with white fungal growth on undersides.",
            "Urdu": "پتوں اور تنوں پر پانی بھرے سیاہ دھبے جو تیزی سے پھیلتے ہیں اور پتوں کے نیچے سفید پھپھوندی ظاہر ہوتی ہے۔",
            "Pashto": "پر پاڼو او ډډونو تور داغونه چې په چټکۍ سره غټیږي او لاندې یې سپین فنګس ښکاري."
        },
        "chemical_treatment": {
            "English": "Apply systemic fungicides like Metalaxyl + Mancozeb (Ridomil Gold) or Cymoxanil immediately.",
            "Urdu": "ریڈومل گولڈ (Metalaxyl + Mancozeb) یا سائموکسانل کا بلا تاخیر فوری اسپرے کریں۔",
            "Pashto": "ریډومیل ګولډ یا ورته اغیزمن کیمیاوي فنګس وژونکي سمدستي وکاروئ."
        },
        "cultural_prevention": {
            "English": "Uproot and destroy completely diseased plants. Disinfect gardening tools and ensure strict crop rotation.",
            "Urdu": "مکمل خراب پودوں کو جڑ سے اکھاڑ کر تلف کر دیں۔ آلات کو جراثیم سے پاک کریں اور فصلوں کا ہیر پھیر اپنائیں۔",
            "Pashto": "سخت ناروغه بوټي له ریښو وباسئ او تلف کړئ. سامان پاک وساتئ او فصل بدل کړئ."
        }
    },
    "healthy": {
        "plant": "Crop",
        "disease": "Healthy Leaf (No Pathogen Detected)",
        "dosage": "Standard organic compost or balanced N-P-K fertilizer as needed.",
        "symptoms": {
            "English": "Foliage displays vibrant coloration, crisp leaf structure, and no visible necrotic lesions.",
            "Urdu": "پتے قدرتی سرسبز، تروتازہ اور بیماری کے تمام اثرات سے بالکل پاک ہیں۔",
            "Pashto": "پاڼې بشپړې شنې، تازه او د هر ډول ناروغیو له نښو پاکې دي."
        },
        "chemical_treatment": {
            "English": "No chemical treatment needed. Continue regular watering and nutrient cycles.",
            "Urdu": "کسی کیمیائی دوا یا اسپرے کی ضرورت نہیں ہے۔ متوازن کھاد اور معمول کا پانی دیں۔",
            "Pashto": "کیمیاوي درملنې ته هیڅ اړتیا نشته. معمول اوبه او سره ورکړئ."
        },
        "cultural_prevention": {
            "English": "Regular scouting and weed control to maintain peak plant vitality.",
            "Urdu": "معمول کی دیکھ بھال جاری رکھیں اور جڑی بوٹیوں کی تلفی کو یقینی بنائیں۔",
            "Pashto": "خپل کښت ته منظم پام کوئ او هرزه بوټي کنټرول کړئ."
        }
    }
}

# ----------------- SIDEBAR -----------------
st.sidebar.title("🌿 Control Panel")
lang = st.sidebar.selectbox("Select Language / زبان منتخب کریں", ["English", "Urdu", "Pashto"])
input_mode = st.sidebar.radio("Image Input Mode", ["Upload Leaf Photo", "Live Camera Capture"])

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Architecture & Engine:**
    - Model: YOLOv11 Neural Classifier
    - Real-time Localized Translations
    - Cloud Deployment: Streamlit Container
    """
)

# ----------------- MAIN INTERFACE -----------------
st.title("🌱 AI Crop Doctor Dashboard")
st.caption("Automated Plant Disease Classification & Severity Advisory System")

@st.cache_resource
def load_model():
    return YOLO("best.pt")

model = load_model()

file_img = None
if input_mode == "Upload Leaf Photo":
    file_img = st.file_uploader("Upload Leaf Image (JPG, PNG)", type=["jpg", "jpeg", "png"])
else:
    file_img = st.camera_input("Capture Leaf Photo")

if file_img:
    img = Image.open(file_img)
    
    col_img, col_act = st.columns([1.2, 1])
    with col_img:
        st.image(img, caption="Input Leaf Sample", use_container_width=True)
    with col_act:
        st.write("### 🔍 Model Diagnostic")
        st.info("Leaf loaded. Click below to execute YOLOv11 inference.")
        scan_btn = st.button("🚀 Scan & Diagnose", type="primary", use_container_width=True)

    if scan_btn:
        with st.spinner("Analyzing pathological markers with YOLOv11..."):
            results = model.predict(img)
            
            raw_class_name = "healthy"
            conf = 0.95
            
            if hasattr(results[0], 'probs') and results[0].probs is not None:
                top_idx = int(results[0].probs.top1)
                conf = float(results[0].probs.top1conf.item())
                raw_class_name = results[0].names[top_idx]
            elif len(results[0].boxes) > 0:
                top_idx = int(results[0].boxes[0].cls[0].item())
                conf = float(results[0].boxes[0].conf[0].item())
                raw_class_name = results[0].names[top_idx]

            clean_key = raw_class_name.replace("___", " ").replace("__", " ").replace("_", " ").lower().strip()
            
            db_entry = None
            for k in DISEASE_DB.keys():
                if k in clean_key or clean_key in k:
                    db_entry = DISEASE_DB[k]
                    break
            if not db_entry:
                db_entry = DISEASE_DB["healthy"]

            # Severity Calculations
            if conf > 0.80:
                severity_label = "High (🔴 Urgent Attention)"
            elif conf >= 0.50:
                severity_label = "Medium (🟡 Moderate Spread)"
            else:
                severity_label = "Low (🟢 Early / Mild Stage)"

            st.markdown("---")
            
            # Metric Cards
            m1, m2, m3 = st.columns(3)
            m1.metric(label="Diagnosed Disease", value=db_entry["disease"].split("(")[0].strip())
            m2.metric(label="Model Confidence", value=f"{conf * 100:.1f}%")
            m3.metric(label="Severity Level", value=severity_label.split()[0])

            # Advisory Layout
            st.write(f"### 📋 Full Advisory & Prescription ({lang})")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("#### 🔬 Symptoms / علامات")
                st.write(db_entry["symptoms"].get(lang, db_entry["symptoms"]["English"]))
            
            with c2:
                st.markdown("#### 🧪 Chemical Treatment / علاج")
                st.success(db_entry["chemical_treatment"].get(lang, db_entry["chemical_treatment"]["English"]))
                st.info(f"**Recommended Spray Dosage:**\n{db_entry['dosage']}")
            
            with c3:
                st.markdown("#### 🛡️ Prevention / احتیاطی تدابیر")
                st.warning(db_entry["cultural_prevention"].get(lang, db_entry["cultural_prevention"]["English"]))

            # Quick Advisory Q&A Expander
            with st.expander("💬 Frequently Asked Questions for this Disease"):
                st.write("**Q: How many times should I spray?**")
                st.write("A: Apply the fungicide once, observe for 7 days, and re-apply after 10-14 days if spreading persists.")
                st.write("**Q: Can rain wash the treatment away?**")
                st.write("A: Yes, avoid spraying right before rain. Ensure at least 4-6 hours of dry weather after spraying.")

            # Diagnostic Report Downloader
            report_text = f"""==============================================
AI CROP DOCTOR - DIAGNOSTIC ADVISORY REPORT
==============================================
Target Crop: {db_entry['plant']}
Diagnosed Condition: {db_entry['disease']}
Confidence: {conf * 100:.2f}%
Severity: {severity_label}
Recommended Dosage: {db_entry['dosage']}

[SYMPTOMS]
{db_entry['symptoms'].get(lang, db_entry['symptoms']['English'])}

[CHEMICAL TREATMENT]
{db_entry['chemical_treatment'].get(lang, db_entry['chemical_treatment']['English'])}

[PREVENTATIVE MEASURES]
{db_entry['cultural_prevention'].get(lang, db_entry['cultural_prevention']['English'])}
==============================================
"""
            st.download_button(
                label="📥 Download Diagnostic Report (.txt)",
                data=report_text,
                file_name=f"{db_entry['plant']}_diagnosis_report.txt",
                mime="text/plain"
            )
