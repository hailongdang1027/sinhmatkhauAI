# rules/executor.py
from .registry import RULES

class RuleExecutor:
    def __init__(self):
        # Nạp danh sách các luật mặc định từ registry
        self.rule_map = dict(RULES)

    def register(self, rule_name, rule_class):
        """
        Đăng ký một Rule mới vào hệ thống tại thời điểm chạy (runtime).
        """
        self.rule_map[rule_name] = rule_class

    def execute_pipeline(self, pipeline, profile):
        """
        Duyệt qua danh sách các bước trong Pipeline và thực thi tuần tự.
        """
        passwords = set()
        statistics = {
            "steps_executed": 0,
            "generated_passwords": 0
        }

        # Lấy danh sách các bước (steps) từ đối tượng RulePipeline
        steps = pipeline.get_steps()
        
        for step in steps:
            rule_name = step.get("rule")
            params = step.get("params", {})
            
            # Nếu luật đã được đăng ký, tiến hành khởi tạo và chạy
            if rule_name in self.rule_map:
                rule_class = self.rule_map[rule_name]
                
                # Khởi tạo instance của Rule kèm theo tham số (ví dụ: max_change=2)
                rule_instance = rule_class(**params)
                
                # Chạy hàm execute và cập nhật lại tập passwords
                passwords = rule_instance.execute(passwords, profile)
                statistics["steps_executed"] += 1
            else:
                raise KeyError(f"Rule '{rule_name}' chưa được đăng ký trong hệ thống!")

        statistics["generated_passwords"] = len(passwords)
        return passwords, statistics