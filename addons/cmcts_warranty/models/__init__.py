# -*- coding: utf-8 -*-
"""
File: models/__init__.py
Chức năng: File khởi tạo thư mục models.
Import thứ tự quan trọng: warranty trước (định nghĩa bảng cha),
warranty_claim sau (có quan hệ Many2one tới warranty).
"""
from . import warranty        # Model: cmcts_warranty.warranty (Phiếu Bảo Hành)
from . import warranty_claim  # Model: cmcts_warranty.warranty.claim (Phiếu Yêu cầu BH)
