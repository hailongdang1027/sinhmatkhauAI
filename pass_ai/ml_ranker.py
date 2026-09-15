import re
import math

def calculate_entropy(password):
    """Tính độ hỗn loạn (Entropy) cơ bản của mật khẩu."""
    if not password: return 0.0
    freq = {}
    for char in password:
        freq[char] = freq.get(char, 0) + 1
    entropy = 0.0
    length = len(password)
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy

def heuristic_score(password):
    """
    Chấm điểm mật khẩu dựa trên trọng số hành vi thực tế (0 - 100 điểm).
    Không cần dùng đến thư viện Machine Learning bên ngoài.
    """
    score = 0
    length = len(password)
    
    if length < 6:
        return 0  # Mật khẩu quá ngắn, không khả thi
        
    # 1. Điểm chiều dài (Tối đa 20 điểm)
    # Chiều dài lý tưởng từ 8-12 ký tự sẽ đạt điểm cao
    score += min(length * 2, 20)
    
    # 2. Điểm thành phần chữ/số (Tối đa 30 điểm)
    if any(c.islower() for c in password): score += 10
    if any(c.isupper() for c in password): score += 10
    if any(c.isdigit() for c in password): score += 10
    
    # 3. Ký tự đặc biệt ở biên (Dấu hiệu đặt pass đối phó chính sách - Cộng 15 điểm)
    boundary_specials = "!@#$%^&*()_+-=[]{}|;':\",./<>?~`"
    if (password[0] in boundary_specials) or (password[-1] in boundary_specials):
        score += 15
        
    # 4. Có chứa đuôi năm sinh/năm hiện tại (Dấu hiệu cực kỳ phổ biến - Cộng 20 điểm)
    if re.search(r"(19\d{2}|20\d{2})$", password):
        score += 20
        
    # 5. Các pattern đặc thù (Wi-Fi / SĐT)
    # Nếu là Số điện thoại VN (10 số) -> Đây là mật khẩu Wi-Fi rất phổ biến -> Cho ngay 85 điểm
    if re.match(r"^(03|05|07|08|09)\d{8}$", password):
        return 85
        
    # Thuần chữ thường (Pass Wi-Fi quán cafe) -> Bị trừ điểm thành phần ở trên nhưng vớt lại 10 điểm
    if password.isalpha() and password.islower():
        score += 10
        
    # 6. Thưởng điểm độ hỗn loạn Entropy (Tối đa 15 điểm)
    ent = calculate_entropy(password)
    score += min(ent * 3, 15)

    # Chốt điểm, tối đa là 100
    return min(round(score, 2), 100.0)

if __name__ == "__main__":
    print("[*] Đang chạy bộ chấm điểm Thuần Python (Heuristic Scoring)...\n")
    
    # Danh sách mật khẩu cần kiểm tra thử điểm số
    test_passwords = [
        "DinhTuyen@2026", # Kịch bản: Cá nhân / Doanh nghiệp (Điểm phải rất cao)
        "trasuachau",     # Kịch bản: Wi-Fi / Dễ nhớ
        "123123123",      # Kịch bản: Rác / Quá dễ đoán
        "VanTuyen_1980",  # Kịch bản: Cá nhân chuẩn
        "0987654321"      # Kịch bản: SĐT Hotline Wi-Fi
    ]
    
    print("--- KẾT QUẢ CHẤM ĐIỂM (Thang 100) ---")
    for pwd in test_passwords:
        score = heuristic_score(pwd)
        print(f"Mật khẩu: {pwd:<15} | Điểm đánh giá: {score}/100")