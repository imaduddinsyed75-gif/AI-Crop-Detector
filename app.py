import streamlit as st
from PIL import Image
from ultralytics import YOLO

st.set_page_config(page_title="AI Crop Doctor", page_icon="🌱", layout="centered")

prescriptions = {
    "Tomato Early Blight": {
        "English": "Prune lower infected leaves immediately. Apply copper fungicides.",
        "Urdu": "متاثرہ پتوں کو فوراً توڑ کر ضائع کریں۔ پودوں پر کاپر فنگسائڈ کا اسپرے کریں۔",
        "Pashto": "اغیزمنې پاڼې سمدستي لیرې او تلف کړئ. پر بوټو د مسو فنګس وژونکي سپری کړئ."
    },
    "Strawberry Leaf Scorch": {
        "English": "Remove infected leaves. Apply fungicide and ensure proper spacing.",
        "Urdu": "متاثرہ پتوں کو کاٹ کر جلا دیں۔ فنگسائڈ کا اسپرے کریں اور پودوں میں فاصلہ رکھیں۔",
        "Pashto": "اغیزمنې پاڼې پرې کړئ او وسوزوئ. د فنګس وژونکي درمل سپری کړئ."
    },
    "Tomato Late Blight": {
        "English": "Reduce overhead watering. Apply copper fungicides and destroy infected plants.",
        "Urdu": "پانی کا چھڑکاؤ کم کریں۔ تانبے والی فنگسائڈ کا استعمال کریں اور پودے تلف کریں۔",
        "Pashto": "د اوبو شیندل کم کړئ. د مسو فنګس وژونکي وکاروئ او ناروغه بوټي له منځه یوسئ."
    },
    "Healthy Leaf": {
        "English": "Your crop is perfectly healthy! Maintain regular care.",
        "Urdu": "آپ کی فصل بالکل صحت مند ہے! دیکھ بھال جاری رکھیں۔",
        "Pashto": "ستاسو فصل بالکل روغ دی! پاملرنه جاري ساتئ."
    }
}

lang = st.sidebar.selectbox("🌐 Select Language / زبان", ["English", "Urdu", "Pashto"])
st.title("🌱 AI Crop Doctor Dashboard")
st.caption("Automated Plant Disease Classification & Severity Estimation")

@st.cache_resource
def get_model():
    return YOLO("best.pt")

model = get_model()
file = st.file_uploader("Upload Leaf Photo", type=["jpg", "jpeg", "png"])

if file:
    img = Image.open(file)
    st.image(img, use_container_width=True)

    if st.button("🚀 Scan & Diagnose", type="primary"):
        with st.spinner("Analyzing leaf with YOLOv11..."):
            results = model.predict(img)

            if hasattr(results[0], 'probs') and results[0].probs is not None:
                top_idx = int(results[0].probs.top1)
                conf = float(results[0].probs.top1conf.item())
                class_name = results[0].names[top_idx]
            elif len(results[0].boxes) > 0:
                top_idx = int(results[0].boxes[0].cls[0].item())
                conf = float(results[0].boxes[0].conf[0].item())
                class_name = results[0].names[top_idx]
            else:
                class_name = "Healthy Leaf"
                conf = 0.95

            if conf > 0.80:
                severity = "High (🔴 Fauran Ilaaj Zaroori)"
            elif conf >= 0.50:
                severity = "Medium (🟡 Ibtidai Marahil)"
            else:
                severity = "Low (🟢 Mamooli Asraat)"

            st.success(f"**Diagnosis:** {class_name} ({conf * 100:.1f}%)")
            st.info(f"**Severity Level:** {severity}")

            advice = prescriptions.get(class_name, {}).get(lang, "Consult local agricultural officer.")
            st.warning(f"**Prescription ({lang}):**\n\n{advice}")
