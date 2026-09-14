import streamlit as st
from PIL import Image
from ultralytics import YOLO

# Page Configuration
st.set_page_config(
    page_title="AI Crop Doctor Dashboard",
    page_icon="🌱",
    layout="wide"
)

# ----------------- KNOWLEDGE BASE (TREATMENTS & ADVISORY) -----------------
# Keys are standardized lowercase without underscores for 100% accurate matching
DISEASE_DB = {
    "strawberry leaf scorch": {
        "plant": "Strawberry",
        "disease": "Leaf Scorch (Diplocarpon earlianum)",
        "symptoms": {
            "English": "Irregular purple-to-brown blotches on leaves that enlarge and cause foliage to look burned.",
            "Urdu": "پتوں پر جامنی اور بھورے دھبے بنتے ہیں جو پھیل کر پتوں کو جلے ہوئے جیسا بنا دیتے ہیں۔",
            "Pashto": "پر پاڼو ارغواني او نسواري داغونه جوړیږي چې وروسته پاڼې داسې ښکاري لکه سوځیدلې وي."
        },
        "chemical_treatment": {
            "English": "Apply Copper-based fungicides or Captan at the first sign of lesions. Repeat every 10-14 days.",
            "Urdu": "تانبے (Copper) والے فنگسائڈ یا کیپٹان (Captan) کا فوراً اسپرے کریں۔ 10 سے 14 دن بعد دوبارہ دہرائیں۔",
            "Pashto": "د مسو پر بنسټ فنګس وژونکي یا کیپټان سپری کړئ. هر 10 تر 14 ورځو وروسته یې بیا تکرار کړئ."
        },
        "cultural_prevention": {
            "English": "Remove and burn heavily infected leaves. Avoid overhead sprinkling; maintain 12-18 inch plant spacing for aeration.",
            "Urdu": "شدید متاثرہ پتوں کو کاٹ کر جلا دیں۔ فوارے سے پانی دینے سے گریز کریں اور ہوا کی آمد و رفت کے لیے فاصلہ رکھیں۔",
            "Pashto": "سختې اغیزمنې پاڼې پرې او وسوزوئ. د سر له لارې اوبه مه ورکوئ او د بوټو ترمنځ مناسب واټن وساتئ."
        }
    },
    "tomato early blight": {
        "plant": "Tomato",
        "disease": "Early Blight (Alternaria solani)",
        "symptoms": {
            "English": "Concentric rings forming dark brown target-like spots on older lower leaves, progressing upwards.",
            "Urdu": "نیچے والے پرانے پتوں پر گول دائروں کی شکل میں گہرے بھورے دھبے جو بتدریج اوپر پھیلتے ہیں۔",
            "Pashto": "په زړو پاڼو تور نسواري ګرد داغونه جوړیږي او پورته نویو پاڼو ته خپریږي."
        },
        "chemical_treatment": {
            "English": "Spray Chlorothalonil, Mancozeb, or Copper Hydroxide immediately to arrest fungal progression.",
            "Urdu": "کلوروتھالونل (Chlorothalonil) یا مینکو زیب (Mancozeb) کا اسپرے کریں تاکہ بیماری کا پھیلاؤ رک سکے۔",
            "Pashto": "کلوروتهالونیل یا مینکوزیب فنګس وژونکي سمدستي سپری کړئ ترڅو ناروغي نوره خپره نشي."
        },
        "cultural_prevention": {
            "English": "Prune lower infected foliage. Stake plants off the ground and use drip irrigation instead of sprinkler.",
            "Urdu": "نچلے متاثرہ پتوں کی چھٹائی کریں۔ پودوں کو سہارا دے کر زمین سے اٹھائیں اور ڈرپ ایریگیشن استعمال کریں۔",
            "Pashto": "لاندینۍ اغیزمنې پاڼې پرې کړئ، بوټي پورته وتړئ او د څاڅکو اوبو سیستم وکاروئ."
        }
    },
    "tomato late blight": {
        "plant": "Tomato",
        "disease": "Late Blight (Phytophthora infestans)",
        "symptoms": {
            "English": "Water-soaked dark lesions on leaves and stems that expand rapidly with white fungal growth underneath.",
            "Urdu": "پتوں اور تنوں پر پانی بھرے سیاہ دھبے جو تیزی سے پھیلتے ہیں اور پتوں کے نیچے سفید پھپھوندی ظاہر ہوتی ہے۔",
            "Pashto": "پر پاڼو او ډډونو تور داغونه چې په چټکۍ سره غټیږي او لاندې یې سپین فنګس ښکاري."
        },
        "chemical_treatment": {
            "English": "Apply systemic fungicides like Metalaxyl + Mancozeb (Ridomil Gold) or Cymoxanil without delay.",
            "Urdu": "ریڈومل گولڈ (Metalaxyl + Mancozeb) یا سائموکسانل کا بلا تاخیر فوری اسپرے کریں۔",
            "Pashto": "ریډومیل ګولډ یا ورته اغیزمن کیمیاوي فنګس وژونکي سمدستي وکاروئ."
        },
        "cultural_prevention": {
            "English": "Uproot and destroy completely infected plants. Avoid damp soil conditions and maintain crop rotation.",
            "Urdu": "مکمل خراب پودوں کو جڑ سے اکھاڑ کر زمین میں دبا دیں یا جلا دیں۔ فصلوں کا ہیر پھیر (Crop Rotation) اپنائیں۔",
            "Pashto": "سخت ناروغه بوټي له ریښو وباسئ او له منځه یوسئ. په ورته ځای کې پرله پسې رومیان مه کروئ."
        }
    },
    "healthy": {
        "plant": "Detected Crop",
        "disease": "Healthy Crop (No Disease Detected)",
        "symptoms": {
            "English": "Foliage shows vibrant color, strong vascular structure, and no necrotic lesions.",
            "Urdu": "پتے قدرتی سرسبز، تروتازہ اور بیماری کے تمام اثرات سے بالکل پاک ہیں۔",
            "Pashto": "پاڼې بشپړې شنې، تازه او د هر ډول ناروغیو له نښو پاکې دي."
        },
        "chemical_treatment": {
            "English": "No chemical intervention needed. Maintain balanced N-P-K fertilization.",
            "Urdu": "کسی کیمیائی دوا یا اسپرے کی ضرورت نہیں ہے۔ متوازن کھاد اور پانی دیں۔",
            "Pashto": "کیمیاوي درملنې ته هیڅ اړتیا نشته. منظمې اوبه او سره ورکړئ."
        },
        "cultural_prevention": {
            "English": "Continue routine field scouting and maintain weed-free boundary beds.",
            "Urdu": "معمول کی دیکھ بھال جاری رکھیں اور جڑی بوٹیوں کی تلفی کو یقینی بنائیں۔",
            "Pashto": "خپل کښت ته منظم پام کوئ او هرزه بوټي کنټرول کړئ."
        }
    }
}

# ----------------- SIDEBAR CONTROLS -----------------
st.sidebar.title("🌿 Control Panel")
lang = st.sidebar.selectbox("Select Language / زبان منتخب کریں", ["English", "Urdu", "Pashto"])
input_mode = st.sidebar.radio("Image Input Mode", ["Upload Leaf Photo", "Live Camera Capture"])

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Project Info:**
    - Model: YOLOv11 Deep Neural Net
    - Localisation: English, Urdu, Pashto
    - Deployment: Headless Cloud Ready
    """
)

# ----------------- MAIN INTERFACE -----------------
st.title("🌱 AI Crop Doctor Dashboard")
st.caption("Automated Plant Disease Classification & Severity Advisory System")

@st.cache_resource
def load_model():
    return YOLO("best.pt")

model = load_model()

# Handle Image Input
file_img = None
if input_mode == "Upload Leaf Photo":
    file_img = st.file_uploader("Upload Leaf Image (JPG, PNG)", type=["jpg", "jpeg", "png"])
else:
    file_img = st.camera_input("Take a photo of the infected leaf")

if file_img:
    img = Image.open(file_img)
    
    col_img, col_act = st.columns([1.2, 1])
    with col_img:
        st.image(img, caption="Input Leaf Sample", use_container_width=True)
    with col_act:
        st.write("### 🔍 Model Diagnostic")
        st.info("Model ready. Click below to run inference through YOLOv11.")
        scan_btn = st.button("🚀 Scan & Diagnose", type="primary", use_container_width=True)

    if scan_btn:
        with st.spinner("Analyzing leaf pathology..."):
            results = model.predict(img)
            
            # Prediction parsing
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
            
            # Standardize string for lookup: 'Strawberry___Leaf_scorch' -> 'strawberry leaf scorch'
            clean_key = raw_class_name.replace("___", " ").replace("__", " ").replace("_", " ").lower().strip()
            
            # Find closest match or fallback
            db_entry = None
            for k in DISEASE_DB.keys():
                if k in clean_key or clean_key in k:
                    db_entry = DISEASE_DB[k]
                    break
            if not db_entry:
                db_entry = DISEASE_DB["healthy"]

            # Severity Calculations
            if conf > 0.80:
                severity_label = "High Severity (🔴 Fauran Ilaaj Zaroori)"
                severity_color = "red"
            elif conf >= 0.50:
                severity_label = "Medium Severity (🟡 Ibtidai Marahil)"
                severity_color = "orange"
            else:
                severity_label = "Low Severity (🟢 Mamooli Asraat)"
                severity_color = "green"

            st.markdown("---")
            
            # Metric Cards
            m1, m2, m3 = st.columns(3)
            m1.metric(label="Diagnosed Disease", value=db_entry["plant"])
            m2.metric(label="Model Confidence", value=f"{conf * 100:.1f}%")
            m3.metric(label="Severity Level", value=severity_label.split()[0])

            st.write(f"### 📋 Full Advisory & Prescription ({lang})")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("#### 🔬 Symptoms / علامات")
                st.write(db_entry["symptoms"].get(lang, db_entry["symptoms"]["English"]))
            
            with c2:
                st.markdown("#### 🧪 Chemical Treatment / علاج")
                st.success(db_entry["chemical_treatment"].get(lang, db_entry["chemical_treatment"]["English"]))
            
            with c3:
                st.markdown("#### 🛡️ Prevention / احتیاطی تدابیر")
                st.warning(db_entry["cultural_prevention"].get(lang, db_entry["cultural_prevention"]["English"]))

            # Generate Downloadable Diagnostic Report
            report_text = f"""==============================================
AI CROP DOCTOR - DIAGNOSTIC ADVISORY REPORT
==============================================
Crop: {db_entry['plant']}
Identified Condition: {db_entry['disease']}
Confidence: {conf * 100:.2f}%
Severity: {severity_label}
Language: {lang}

1. OBSERVED SYMPTOMS:
{db_entry['symptoms'].get(lang, db_entry['symptoms']['English'])}

2. RECOMMENDED CHEMICAL / MEDICAL TREATMENT:
{db_entry['chemical_treatment'].get(lang, db_entry['chemical_treatment']['English'])}

3. CULTURAL / PREVENTATIVE MEASURES:
{db_entry['cultural_prevention'].get(lang, db_entry['cultural_prevention']['English'])}
==============================================
"""
            st.download_button(
                label="📥 Download Diagnostic Report (.txt)",
                data=report_text,
                file_name="crop_doctor_advisory_report.txt",
                mime="text/plain"
            )
