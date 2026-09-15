import json
import os
from datetime import datetime

class PipelineLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

    def save(self, profile, pipeline, statistics, output_file):
        """
        Lưu log tiến trình chạy Pipeline.
        Thay vì lưu toàn bộ mật khẩu, hệ thống chỉ lưu tham chiếu (đường dẫn) đến file output.
        """
        filename = datetime.now().strftime("run_%Y%m%d_%H%M%S.json")
        path = os.path.join(self.log_dir, filename)

        data = {
            "created_at": datetime.now().isoformat(),
            "profile": profile,
            "pipeline": pipeline.pipeline,
            "statistics": statistics,
            "output_file": output_file  # <- Trỏ tới file txt
        }

        with open(path, "w", encoding="utf8") as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

        return path