import os
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from ultralytics import YOLO

# System Settings
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

# Path Setup for YOLOv11
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "best.pt")
model = YOLO(MODEL_PATH)

# Standalone Treatment Database (Added Early Blight!)
TREATMENT_DB = {
    "Tomato___Early_blight": {
        "ur": "علاج: متاثرہ پتوں کو فوراً توڑ کر ضائع کریں۔ پودوں پر کاپر فنگسائڈ (Copper Fungicide) یا مینکوزیب کا اسپرے کریں اور نائٹروجن کا استعمال متوازن رکھیں۔",
        "ps": "درملنه: اغیزمنې پاڼې سمدستي لیرې او تلف کړئ. پر بوټو د مسو فنګس وژونکي (Copper Fungicide) یا مینکوزیب سپری کړئ.",
        "en": "Treatment: Prune lower infected leaves immediately. Apply copper-based fungicides or Mancozeb, and avoid overhead watering."
    },
    "Strawberry___Leaf_scorch": {
        "ur": "علاج: متاثرہ پتوں کو کاٹ کر جلا دیں۔ فنگسائڈ کا اسپرے کریں اور پودوں میں فاصلہ رکھیں۔",
        "ps": "درملنه: اغیزمنې پاڼې پرې کړئ او وسوزوئ. د فنګس وژونکي درمل سپری کړئ او بوټي لیرې وکرئ.",
        "en": "Treatment: Remove infected leaves. Apply fungicide and ensure proper plant spacing."
    },
    "Tomato___Late_blight": {
        "ur": "علاج: پانی کا چھڑکاؤ کم کریں۔ تانبے والی فنگسائڈ کا استعمال کریں اور متاثرہ پودے تلف کریں۔",
        "ps": "درملنه: د اوبو شیندل کم کړئ. د مسو فنګس وژونکي وکاروئ او ناروغه بوټي له منځه یوسئ.",
        "en": "Treatment: Reduce overhead watering. Apply copper-based fungicides and destroy infected plants."
    },
    "Tomato___Bacterial_spot": {
        "ur": "علاج: بیماری سے پاک بیج استعمال کریں۔ تانبے اور مینکوزیب کا مرکب اسپرے کریں۔",
        "ps": "درملنه: له ناروغۍ پاک تخمونه وکاروئ. د مسو او مینکوزیب مخلوط سپری کړئ.",
        "en": "Treatment: Use disease-free seeds. Spray a mixture of copper and mancozeb."
    },
    "Healthy": {
        "ur": "آپ کی فصل بالکل صحت مند ہے! کسی علاج کی ضرورت نہیں، دیکھ بھال جاری رکھیں۔",
        "ps": "ستاسو فصل بالکل روغ دی! هیڅ درملنې ته اړتیا نشته، پاملرنه جاري ساتئ.",
        "en": "Your crop is perfectly healthy! No treatment needed, maintain regular care."
    }
}

UI_LANG = {
    "ur": {"title": "🌱 اے آئی فصل ڈاکٹر", "btn_browse": "تصویر منتخب کریں", "btn_scan": "اسکین کریں", "lbl_res": "تشخیص:", "lbl_sev": "شدت:", "lbl_treat": "تجویز کردہ علاج:", "scanning": "معائنہ جاری ہے..."},
    "ps": {"title": "🌱 د AI فصلونو ډاکټر", "btn_browse": "عکس غوره کړئ", "btn_scan": "سکین کړئ", "lbl_res": "تشخیص:", "lbl_sev": "شدت:", "lbl_treat": "د AI ډاکټر درملنه:", "scanning": "معاینه روانه ده..."},
    "en": {"title": "🌱 AI Crop Doctor", "btn_browse": "Select Image", "btn_scan": "Scan Now", "lbl_res": "Diagnosis:", "lbl_sev": "Severity:", "lbl_treat": "AI Treatment Suggestion:", "scanning": "Scanning..."}
}

class CropDoctorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("AI Crop Doctor Dashboard")
        self.geometry("650x800")
        self.resizable(True, True)
        
        self.current_lang = "ur"
        self.selected_file_path = None
        self.last_results = None

        # --- Top Bar (Language Selector) ---
        self.lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.lang_frame.pack(fill="x", padx=20, pady=10)
        
        self.lang_switch = ctk.CTkOptionMenu(
            self.lang_frame, 
            values=["اردو (Urdu)", "پښتو (Pashto)", "English"],
            command=self.change_language,
            width=120
        )
        self.lang_switch.pack(side="right")
        
        # --- Main Title ---
        self.main_title = ctk.CTkLabel(self, text=UI_LANG["ur"]["title"], font=("Arial", 24, "bold"), text_color="#10b981")
        self.main_title.pack(pady=10)

        # --- Image Upload Preview Box ---
        self.image_label = ctk.CTkLabel(self, text="No Image Selected", width=450, height=220, fg_color=("#e2e8f0", "#1e293b"), corner_radius=12)
        self.image_label.pack(pady=15)

        # --- Control Buttons ---
        self.btn_browse = ctk.CTkButton(self, text=UI_LANG["ur"]["btn_browse"], command=self.browse_image, font=("Arial", 14, "bold"), fg_color="#3b82f6", hover_color="#2563eb", width=250)
        self.btn_browse.pack(pady=5)
        
        self.btn_scan = ctk.CTkButton(self, text=UI_LANG["ur"]["btn_scan"], command=self.scan_image, font=("Arial", 16, "bold"), fg_color="#10b981", hover_color="#059669", width=250)
        self.pack_start = self.btn_scan.pack(pady=10)

        # --- Results Display Panel ---
        self.result_frame = ctk.CTkFrame(self, fg_color=("#f1f5f9", "#0f172a"), corner_radius=12)
        self.result_frame.pack(fill="both", expand=True, padx=20, pady=15)

        self.res_disease_lbl = ctk.CTkLabel(self.result_frame, text=UI_LANG["ur"]["lbl_res"], font=("Arial", 14, "bold"))
        self.res_disease_lbl.pack(anchor="w", padx=15, pady=(10, 2))
        self.res_disease_val = ctk.CTkLabel(self.result_frame, text="", font=("Arial", 14))
        self.res_disease_val.pack(anchor="w", padx=30)

        self.res_severity_lbl = ctk.CTkLabel(self.result_frame, text=UI_LANG["ur"]["lbl_sev"], font=("Arial", 14, "bold"))
        self.res_severity_lbl.pack(anchor="w", padx=15, pady=(10, 2))
        self.res_severity_val = ctk.CTkLabel(self.result_frame, text="", font=("Arial", 14))
        self.res_severity_val.pack(anchor="w", padx=30)

        self.res_treatment_lbl = ctk.CTkLabel(self.result_frame, text=UI_LANG["ur"]["lbl_treat"], font=("Arial", 14, "bold"), text_color="#10b981")
        self.res_treatment_lbl.pack(anchor="w", padx=15, pady=(10, 2))
        
        # Scrollable Box for Treatment with Text Wrapping fixed
        self.res_treatment_val = ctk.CTkTextbox(self.result_frame, font=("Arial", 14), width=580, height=120, fg_color="transparent", activate_scrollbars=True, wrap="word")
        self.res_treatment_val.pack(anchor="w", padx=15, pady=(0, 10))
        
    def change_language(self, choice):
        if "Urdu" in choice: self.current_lang = "ur"
        elif "Pashto" in choice: self.current_lang = "ps"
        else: self.current_lang = "en"
        
        lang = self.current_lang
        self.main_title.configure(text=UI_LANG[lang]["title"])
        self.btn_browse.configure(text=UI_LANG[lang]["btn_browse"])
        
        if self.btn_scan.cget("text") not in ["معائنہ جاری ہے...", "معاینه روانه ده...", "Scanning..."]:
            self.btn_scan.configure(text=UI_LANG[lang]["btn_scan"])
            
        self.res_disease_lbl.configure(text=UI_LANG[lang]["lbl_res"])
        self.res_severity_lbl.configure(text=UI_LANG[lang]["lbl_sev"])
        self.res_treatment_lbl.configure(text=UI_LANG[lang]["lbl_treat"])
        
        if self.last_results:
            self.update_results_ui()

    def browse_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.selected_file_path = file_path
            my_image = ctk.CTkImage(light_image=Image.open(file_path), dark_image=Image.open(file_path), size=(400, 200))
            self.image_label.configure(image=my_image, text="")

    def scan_image(self):
        if not self.selected_file_path:
            return
            
        self.btn_scan.configure(text=UI_LANG[self.current_lang]["scanning"], state="disabled")
        self.update()

        # YOLOv11 Inference Core
        img = Image.open(self.selected_file_path)
        results = model(img)
        
        if len(results[0].boxes) == 0:
            detected_disease = "Healthy"
            confidence_score = 100.0
        else:
            box = results[0].boxes[0]
            class_id = int(box.cls[0])
            confidence_score = float(box.conf[0]) * 100
            detected_disease = model.names[class_id]

        if detected_disease == "Healthy":
            severity = "None"
        elif confidence_score > 80:
            severity = "High (🔴 Fauran Ilaaj Zaroori)"
        elif confidence_score > 50:
            severity = "Medium (🟡 Ibtidai Marahil)"
        else:
            severity = "Low (🟢 Mamooli Asraat)"

        treatment = TREATMENT_DB.get(detected_disease, {
            "ur": "علاج: متاثرہ حصے کو الگ کریں اور ماہرِ زراعت سے مشورہ کریں۔",
            "ps": "درملنه: اغیزمنه برخه جلا کړئ او د کرنې له کارپوه سره مشوره وکړئ.",
            "en": "Treatment: Isolate the infected plant and consult an agricultural expert."
        })

        self.last_results = {
            "disease": f"{detected_disease} ({confidence_score:.1f}%)",
            "severity": severity,
            "treatment_ur": treatment["ur"],
            "treatment_ps": treatment["ps"],
            "treatment_en": treatment["en"]
        }
        
        self.update_results_ui()
        self.btn_scan.configure(text=UI_LANG[self.current_lang]["btn_scan"], state="normal")

    def update_results_ui(self):
        self.res_disease_val.configure(text=self.last_results["disease"])
        self.res_severity_val.configure(text=self.last_results["severity"])
        
        # Safe text update mechanism for CustomTkinter Textbox
        self.res_treatment_val.configure(state="normal")
        self.res_treatment_val.delete("1.0", "end")
        text_key = f"treatment_{self.current_lang}"
        self.res_treatment_val.insert("1.0", self.last_results[text_key])

if __name__ == "__main__":
    app = CropDoctorApp()
    app.mainloop()