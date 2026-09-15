import re
math = __import__('math')

def calculate_entropy(password):
    """Tính độ hỗn loạn (Entropy) cơ bản của mật khẩu."""
    if not password:
        return 0.0
    freq = {}
    for char in password:
        freq[char] = freq.get(char, 0) + 1
    entropy = 0.0
    length = len(password)
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy

def extract_features(password):
    """
    Chuyển đổi 1 mật khẩu thành một vector đặc trưng số học cho Machine Learning.
    """
    length = len(password)
    
    # 1. Các đặc trưng cơ bản về cấu trúc
    has_upper = 1 if any(c.isupper() for c in password) else 0
    has_lower = 1 if any(c.islower() for c in password) else 0
    has_digit = 1 if any(c.isdigit() for c in password) else 0
    
    # Ký tự đặc biệt ở biên (đầu hoặc cuối)
    boundary_specials = "!@#$%^&*()_+-=[]{}|;':\",./<>?~`"
    has_boundary_special = 1 if (password and password[0] in boundary_specials) or (password and password[-1] in boundary_specials) else 0
    
    # Ký tự đặc biệt ở giữa (Infix)
    middle_chars = password[1:-1] if length > 2 else ""
    has_middle_special = 1 if any(c in boundary_specials for c in middle_chars) else 0

    # 2. Tỷ lệ các thành phần
    digit_count = sum(1 for c in password if c.isdigit())
    digit_ratio = digit_count / length if length > 0 else 0
    
    upper_count = sum(1 for c in password if c.isupper())
    upper_ratio = upper_count / length if length > 0 else 0

    # 3. Kiểm tra các dạng đặc thù (Wi-Fi / Hotline / Sequence)
    # Khớp số điện thoại VN (10 số, bắt đầu bằng 03, 05, 07, 08, 09)
    is_phone_number = 1 if re.match(r"^(03|05|07|08|09)\d{8}$", password) else 0
    
    # Thuần chữ thường không dấu (dạng Wi-Fi quán cafe)
    is_pure_lower_alpha = 1 if password.isalpha() and password.islower() else 0
    
    # Có chứa năm sinh/năm hiện tại ở đuôi (ví dụ: 2025, 2026, 1980...)
    has_year_suffix = 1 if re.search(r"(19\d{2}|20\d{2})$", password) else 0

    # 4. Độ phức tạp toán học
    entropy = calculate_entropy(password)

    # Gom toàn bộ thành một vector đặc trưng trả về
    return [
        length,
        has_upper,
        has_lower,
        has_digit,
        has_boundary_special,
        has_middle_special,
        digit_ratio,
        upper_ratio,
        is_phone_number,
        is_pure_lower_alpha,
        has_year_suffix,
        entropy
    ]