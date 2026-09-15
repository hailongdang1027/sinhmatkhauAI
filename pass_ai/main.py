#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import re
from datetime import datetime
from collections import Counter

# Chỉ giữ lại Logger và Handle (Lõi cơ học)
from pipeline.logger import PipelineLogger
import handle
handle.read_config("rules.cfg")

DEFAULT_ENTRY_BG = "white"
ERROR_ENTRY_BG = "#ffd6d6"

active_rules = []
learned_masks = set() # Bộ nhớ lưu trữ các Khuôn mẫu AI tự học được

# ==========================================
# CÁC HÀM XỬ LÝ HỌC MÁY (MACHINE LEARNING)
# ==========================================
def get_mask(password):
    """Phân rã mật khẩu thành cấu trúc Mask toán học (VD: ?l?l?d?d?s)"""
    mask = ""
    for char in password:
        if char.islower(): mask += "?l"
        elif char.isupper(): mask += "?u"
        elif char.isdigit(): mask += "?d"
        else: mask += "?s"
    return mask

def load_leak_file():
    """Nạp file rò rỉ, phân tích và lưu lại Top 15 Khuôn mẫu."""
    filepath = filedialog.askopenfilename(title="Chọn file mật khẩu rò rỉ (Leak File)", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if not filepath:
        return
        
    try:
        mask_counter = Counter()
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                pwd = line.strip()
                if pwd:
                    mask_counter[get_mask(pwd)] += 1
                    
        # Lấy Top 15 khuôn mẫu phổ biến nhất
        top_masks = [mask for mask, count in mask_counter.most_common(15)]
        
        learned_masks.clear()
        learned_masks.update(top_masks)
        
        lbl_leak_status.config(text=f"✅ Đã học xong {len(top_masks)} Khuôn mẫu từ file!", fg="green")
        messagebox.showinfo("Hoàn tất", f"Hệ thống đã phân tích và lưu lại {len(top_masks)} cấu trúc phổ biến nhất.\n\nSẵn sàng áp dụng cho Rule [TỰ_HỌC_KHUÔN_MẪU].")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể đọc file: {e}")

# ==========================================
# CÁC HÀM KIỂM TRA ĐẦU VÀO (VALIDATORS)
# ==========================================
def validate_name_field(event):
    widget = event.widget
    val = widget.get().strip()
    if not val:
        widget.config(bg=DEFAULT_ENTRY_BG)
        return
    if re.match(r"^[a-zA-ZÀ-ỹ\s]+$", val):
        widget.config(bg=DEFAULT_ENTRY_BG)
    else:
        widget.config(bg=ERROR_ENTRY_BG)

def is_valid_flexible_date(date_str):
    date_str = date_str.strip()
    if not date_str: return True
    now = datetime.now()
    try:
        if len(date_str) == 10 and date_str.count('/') == 2:
            input_date = datetime.strptime(date_str, "%d/%m/%Y")
            if input_date.date() > now.date(): return False
            return True
        elif len(date_str) == 5 and date_str.count('/') == 1:
            parts = date_str.split('/')
            if len(parts[1]) == 2:
                datetime.strptime(date_str + "/2000", "%d/%m/%Y")
                return True
        elif len(date_str) == 7 and date_str.count('/') == 1:
            parts = date_str.split('/')
            if len(parts[1]) == 4:
                input_date = datetime.strptime("01/" + date_str, "%d/%m/%Y")
                current_month = now.replace(day=1)
                if input_date.date() > current_month.date(): return False
                return True
        return False
    except ValueError:
        return False

def make_date_validator(entry_widget):
    def _on_focus_out(event=None):
        if is_valid_flexible_date(entry_widget.get()):
            entry_widget.config(bg=DEFAULT_ENTRY_BG)
        else:
            entry_widget.config(bg=ERROR_ENTRY_BG)
    return _on_focus_out

def clean_date(date_str):
    return date_str.replace("/", "").replace("-", "").strip()

# ==========================================
# CÁC HÀM XỬ LÝ PIPELINE & RULE
# ==========================================
def parse_params(param_str):
    params = {}
    if not param_str.strip(): return params
    pairs = param_str.split(',')
    for pair in pairs:
        if '=' in pair:
            k, v = pair.split('=', 1)
            k, v = k.strip(), v.strip()
            params[k] = int(v) if v.isdigit() else v
    return params

def add_rule():
    rule_name = combo_rule.get().strip()
    param_str = entry_params.get().strip()
    
    if not rule_name: return
    parsed_params = parse_params(param_str)
    active_rules.append({"rule": rule_name, "params": parsed_params})
    
    display_text = f"[{rule_name}] "
    if parsed_params:
        param_texts = [f"{k}={v}" for k, v in parsed_params.items()]
        display_text += f"({', '.join(param_texts)})"
    
    listbox_rules.insert(tk.END, display_text)
    entry_params.delete(0, tk.END)

def remove_rule():
    selected_indices = listbox_rules.curselection()
    if not selected_indices: return
    for index in reversed(selected_indices):
        listbox_rules.delete(index)
        del active_rules[index]

def generate_wordlist_via_pipeline():
    profile = {
        "fullname": entry_fullname.get().strip().lower(),
        "birthdate": clean_date(entry_birthdate.get()),
        "relative_name": entry_relative_name.get().strip().lower(),
        "relative_birth": clean_date(entry_relative_birth.get()),
        "child_name": entry_child_name.get().strip().lower(),
        "child_birth": clean_date(entry_child_birth.get()),
        "company": entry_company.get().strip().lower(),
        "hometown": entry_hometown.get().strip().lower(),
    }
    
    wcfrom_str = entry_wcfrom.get().strip()
    wcto_str = entry_wcto.get().strip()
    if not wcfrom_str or not wcto_str:
        messagebox.showerror("Lỗi Đầu Vào", "Vui lòng nhập bộ lọc độ dài.")
        return
    try:
        wcfrom_val, wcto_val = int(wcfrom_str), int(wcto_str)
    except ValueError:
        messagebox.showerror("Lỗi", "Bộ lọc độ dài phải là số.")
        return

    try:
        final_passwords = set()
        
        if not active_rules:
            final_passwords.update(handle.generate_basic_wordlist(profile, wcfrom_val, wcto_val))

        for rule_data in active_rules:
            if rule_data["rule"] == "LÕI_CƠ_HỌC":
                final_passwords.update(handle.generate_basic_wordlist(profile, wcfrom_val, wcto_val))

            # ----- RULE 4: TỰ HỌC KHUÔN MẪU (DYNAMIC MASK AI) -----
            elif rule_data["rule"] == "TỰ_HỌC_KHUÔN_MẪU":
                if not learned_masks:
                    messagebox.showwarning("Cảnh báo", "Bạn chưa nạp Tệp rò rỉ! Hãy bấm 'Nạp File Mật Khẩu Lộ' trước khi chạy Rule này.")
                    return
                
                # Bóc tách và tạo biến thể (Phôi)
                words = set()
                for field in ["fullname", "relative_name", "child_name", "company", "hometown"]:
                    val = profile.get(field, "")
                    if val:
                        clean_val = handle.remove_vietnamese_in_dictionary(val)
                        clean_val = re.sub(r"[-_.]+", " ", clean_val).strip()
                        for w in clean_val.split():
                            if len(w) >= 3:
                                words.update([w.lower(), w.capitalize(), w.upper()])
                        if len(clean_val.split()) > 1:
                            full_word = "".join(clean_val.split())
                            words.update([full_word.lower(), full_word.capitalize()])

                dates = set()
                for field in ["birthdate", "relative_birth", "child_birth"]:
                    d_val = profile.get(field, "")
                    if len(d_val) == 8: 
                        dd, mm, yyyy = d_val[0:2], d_val[2:4], d_val[4:8]
                        yy = yyyy[-2:]
                        dates.update([d_val, d_val[::-1], yyyy+mm+dd, dd+mm, mm+dd, yyyy, yy])
                    elif len(d_val) == 4: 
                        dates.update([d_val, d_val[::-1]])
                
                common_nums = ["123", "1234", "12345", "123456", "6868", "8888", "9999"]
                dates.update(common_nums)
                specials = ["", "@", "!", "_", "-", ".", "*", "#", "$"]
                
                # Máy nhào trộn đa chiều tạo ra hàng ngàn biến thể thô
                raw_combinations = set()
                raw_combinations.update(words)
                raw_combinations.update(dates)
                
                for w in words:
                    for d in dates:
                        raw_combinations.update([w+d, d+w])
                        for s in specials:
                            if s:
                                raw_combinations.update([w+s+d, d+s+w, w+d+s, s+w+d])
                
                # LỌC AI: Chỉ giữ lại những tổ hợp khớp 100% với Khuôn Mẫu đã học
                smart_passwords = set()
                for pwd in raw_combinations:
                    if get_mask(pwd) in learned_masks:
                        smart_passwords.add(pwd)
                        
                final_passwords.update(smart_passwords)
                
            # (Các rule khác như LEET, DATE_MIRROR... giữ nguyên logic nếu cần)
            elif rule_data["rule"] == "LEET":
                pass # Thu gọn để tập trung vào Tự Học

        if not final_passwords:
            messagebox.showwarning("Cảnh báo", "Không có mật khẩu nào được sinh ra! Có thể Khuôn mẫu đã học không khớp với độ dài thông tin cá nhân.")
            return

        final_list = sorted([pw for pw in final_passwords if wcfrom_val <= len(pw) <= wcto_val])

        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        fname = profile["fullname"] if profile["fullname"] else "wordlist"
        fname = fname.replace(" ", "_").replace("đ", "d")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = os.path.join(output_dir, f"{fname}_{timestamp}.txt")
        
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("\n".join(final_list) + "\n")
            
        messagebox.showinfo("Thành công", f"AI đã lọc và sinh ra {len(final_list)} mật khẩu chuẩn xác theo thói quen tệp rò rỉ!\n\nFile txt: {os.path.abspath(output_filename)}")
        
    except Exception as e:
        messagebox.showerror("Lỗi hệ thống", f"Lỗi khi chạy bộ sinh: {str(e)}")

# ==========================================
# XÂY DỰNG GIAO DIỆN GUI
# ==========================================
root = tk.Tk()
root.title("Công Cụ Tạo Từ Điển Mật Khẩu (Dynamic AI Learner)")
root.geometry("850x650")

left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# KHỐI HỌC MÁY MỚI TRÊN GUI
frame_ai = tk.LabelFrame(left_frame, text="🧠 Dữ Liệu Học Máy (Data-driven)", padx=10, pady=10, bg="#f0f8ff")
frame_ai.pack(fill=tk.X, pady=5)

btn_load = tk.Button(frame_ai, text="📁 Nạp File Mật Khẩu Lộ (Học Khuôn Mẫu)", bg="#2196F3", fg="white", font=("Arial", 9, "bold"), command=load_leak_file)
btn_load.pack(fill=tk.X, pady=2)
lbl_leak_status = tk.Label(frame_ai, text="Chưa nạp dữ liệu rò rỉ...", fg="#555", bg="#f0f8ff")
lbl_leak_status.pack()

# KHÔI PHỤC ĐẦY ĐỦ THÔNG TIN NGƯỜI DÙNG
frame_profile = tk.LabelFrame(left_frame, text="Thông tin người dùng (Phôi dữ liệu)", padx=10, pady=10)
frame_profile.pack(fill=tk.X, pady=5)

tk.Label(frame_profile, text="Họ và tên:").grid(row=0, column=0, sticky="w")
entry_fullname = tk.Entry(frame_profile, width=30)
entry_fullname.bind("<FocusOut>", validate_name_field)
entry_fullname.grid(row=0, column=1, padx=5, pady=2)

tk.Label(frame_profile, text="Sinh nhật (VD: 06/08/1980):").grid(row=1, column=0, sticky="w")
entry_birthdate = tk.Entry(frame_profile, width=30)
entry_birthdate.bind("<FocusOut>", make_date_validator(entry_birthdate))
entry_birthdate.grid(row=1, column=1, padx=5, pady=2)

tk.Label(frame_profile, text="Người thân:").grid(row=2, column=0, sticky="w")
entry_relative_name = tk.Entry(frame_profile, width=30)
entry_relative_name.bind("<FocusOut>", validate_name_field)
entry_relative_name.grid(row=2, column=1, padx=5, pady=2)

tk.Label(frame_profile, text="Sinh nhật (Nhập khuyết 06/08):").grid(row=3, column=0, sticky="w")
entry_relative_birth = tk.Entry(frame_profile, width=30)
entry_relative_birth.bind("<FocusOut>", make_date_validator(entry_relative_birth))
entry_relative_birth.grid(row=3, column=1, padx=5, pady=2)

tk.Label(frame_profile, text="Con cái:").grid(row=4, column=0, sticky="w")
entry_child_name = tk.Entry(frame_profile, width=30)
entry_child_name.bind("<FocusOut>", validate_name_field)
entry_child_name.grid(row=4, column=1, padx=5, pady=2)

tk.Label(frame_profile, text="Sinh nhật (Nhập khuyết 08/1980):").grid(row=5, column=0, sticky="w")
entry_child_birth = tk.Entry(frame_profile, width=30)
entry_child_birth.bind("<FocusOut>", make_date_validator(entry_child_birth))
entry_child_birth.grid(row=5, column=1, padx=5, pady=2)

tk.Label(frame_profile, text="Nơi làm việc:").grid(row=6, column=0, sticky="w")
entry_company = tk.Entry(frame_profile, width=30)
entry_company.grid(row=6, column=1, padx=5, pady=2)

tk.Label(frame_profile, text="Quê quán:").grid(row=7, column=0, sticky="w")
entry_hometown = tk.Entry(frame_profile, width=30)
entry_hometown.grid(row=7, column=1, padx=5, pady=2)

# KHUNG BỘ LỌC ĐỘ DÀI
frame_config = tk.LabelFrame(left_frame, text="Bộ lọc độ dài", padx=10, pady=10)
frame_config.pack(fill=tk.X, pady=5)
tk.Label(frame_config, text="Từ (wcfrom):").grid(row=0, column=0, sticky="w")
entry_wcfrom = tk.Entry(frame_config, width=10)
entry_wcfrom.grid(row=0, column=1, padx=5, pady=2)

tk.Label(frame_config, text="Đến (wcto):").grid(row=1, column=0, sticky="w")
entry_wcto = tk.Entry(frame_config, width=10)
entry_wcto.grid(row=1, column=1, padx=5, pady=2)

btn_generate = tk.Button(left_frame, text="🔥 SINH TỪ ĐIỂN TỰ ĐỘNG", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=generate_wordlist_via_pipeline)
btn_generate.pack(pady=15, fill=tk.X)

right_frame = tk.Frame(root)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

frame_pipeline = tk.LabelFrame(right_frame, text="Xây dựng Pipeline (Rules)", padx=10, pady=10)
frame_pipeline.pack(fill=tk.BOTH, expand=True)

frame_add_rule = tk.Frame(frame_pipeline)
frame_add_rule.pack(fill=tk.X, pady=5)

tk.Label(frame_add_rule, text="Loại Rule:").grid(row=0, column=0, sticky="w")
combo_rule = ttk.Combobox(frame_add_rule, values=["LÕI_CƠ_HỌC", "CAMEL_CASE", "LEET", "DATE_MIRROR", "COUPLE_DATES", "COMPANY_HOMETOWN", "TỰ_HỌC_KHUÔN_MẪU"], width=20, state="readonly")
combo_rule.current(6)
combo_rule.grid(row=0, column=1, padx=5, pady=2)

tk.Label(frame_add_rule, text="Tham số:").grid(row=1, column=0, sticky="w")
entry_params = tk.Entry(frame_add_rule, width=25)
entry_params.grid(row=1, column=1, padx=5, pady=2)

btn_add_rule = tk.Button(frame_add_rule, text="➕ Thêm Luật", command=add_rule)
btn_add_rule.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")

tk.Label(frame_pipeline, text="Trình tự thực thi:").pack(anchor="w", pady=(10,0))
listbox_rules = tk.Listbox(frame_pipeline, selectmode=tk.EXTENDED, height=15)
listbox_rules.pack(fill=tk.BOTH, expand=True, pady=5)

btn_del_rule = tk.Button(frame_pipeline, text="❌ Xóa Luật đã chọn", command=remove_rule)
btn_del_rule.pack(fill=tk.X)

def init_default_rules():
    combo_rule.set("TỰ_HỌC_KHUÔN_MẪU")
    add_rule()

init_default_rules()
root.mainloop()