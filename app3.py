import streamlit as st
import google.generativeai as genai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas
from streamlit_mic_recorder import mic_recorder
import streamlit.components.v1 as components

# ==========================================
# 1. CẤU HÌNH & KHỞI TẠO BỘ NHỚ TRANG
# ==========================================
st.set_page_config(page_title="Vở Nháp Toán AI", page_icon="📐", layout="wide")

if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "selected_problem" not in st.session_state:
    st.session_state.selected_problem = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# DANH SÁCH 10 BÀI TOÁN 
problems = [
    {"id": 1, "level": "🟢 Nhận diện", "title": "Bài 1", "content": "Cho tam giác DEF. Hãy viết công thức tính cạnh DE bằng định lí côsin."},
    {"id": 2, "level": "🟢 Nhận diện", "title": "Bài 2", "content": "Cho tam giác MNP. Hãy viết công thức định lí sin dựa trên tam giác này."},
    {"id": 3, "level": "🟡 Thể hiện", "title": "Bài 3", "content": "Cho tam giác MNP có góc M = 45°, góc N = 60°, cạnh MP = 10. Tính cạnh NP."},
    {"id": 4, "level": "🟡 Thể hiện", "title": "Bài 4", "content": "Tính bán kính đường tròn ngoại tiếp R của tam giác ABC biết a = 12, góc A = 30°."},
    {"id": 5, "level": "🟠 Củng cố", "title": "Bài 5", "content": "Cho tam giác ABC có a=6, b=8, góc C=30°. Tính diện tích tam giác đó."},
    {"id": 6, "level": "🟠 Củng cố", "title": "Bài 6", "content": "Hai lực F1 = 30N và F2 = 40N tác dụng vào 1 điểm với góc hợp bởi 2 lực là 120°. Tính lực tổng hợp."},
    {"id": 7, "level": "🟠 Củng cố", "title": "Bài 7", "content": "Cho tam giác ABC, biết a=7, b=8, c=5. Tính góc A và diện tích tam giác."},
    {"id": 8, "level": "🟠 Củng cố", "title": "Bài 8", "content": "Hai tàu thủy xuất phát từ cùng một cảng đi theo 2 hướng lệch nhau 60°. Tàu 1 đi với tốc độ 20km/h, tàu 2 là 30km/h. Sau 2 giờ, khoảng cách 2 tàu là bao nhiêu?"},
    {"id": 9, "level": "🔴 Vận dụng", "title": "Bài 9", "content": "Chứng minh rằng trong tam giác ABC: a = b.cosC + c.cosB"},
    {"id": 10, "level": "🔴 Vận dụng", "title": "Bài 10", "content": "Cho tam giác ABC có góc A = 120°, AB = 3, AC = 6. Tính độ dài đường phân giác trong góc A."},
]

# ==========================================
# 2. CSS GIAO DIỆN CHUNG
# ==========================================
st.markdown("""
<style>
/* NỀN GIẤY CARO (GRID PAPER) */
[data-testid="stAppViewContainer"] {
    background-color: #f1f5f9 !important;
    background-image: linear-gradient(#e2e8f0 1px, transparent 1px), linear-gradient(90deg, #e2e8f0 1px, transparent 1px) !important;
    background-size: 25px 25px !important;
}
/* XÓA HOÀN TOÀN THANH HEADER TRẮNG CHE ĐỀ BÀI */
[data-testid="stHeader"] {
    display: none !important;
}

/* Ép sát giao diện lên trần nhà */
.block-container {
    padding-top: 0.8rem !important;
    padding-bottom: 1rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

#MainMenu {visibility: hidden;} footer {visibility: hidden;}
::-webkit-scrollbar { width: 35px !important; background-color: #f4f6f8; }
::-webkit-scrollbar-thumb { background-color: #999999; border-radius: 20px; border: 8px solid #f4f6f8; }

.hero-banner { background-color: #2b3a4a; padding: 20px 15px; text-align: center; border-radius: 14px; margin-bottom: 20px; box-shadow: 0 8px 20px rgba(0,0,0,0.08); }
.hero-banner .title-sub { color: #FFD700; font-size: 24px; font-weight: bold; margin: 0; }
.hero-banner h1 { color: #ffffff; font-size: 32px; font-weight: bold; margin: 5px 0 0 0; }

/* === LÀM ĐẸP NÚT BẤM === */
div[data-testid="stButton"] button {
    border-radius: 16px !important;
    border: 1px solid #cbd5e1 !important;
    background-color: #ffffff !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04) !important;
    transition: 0.2s !important;
    min-height: 54px !important;
}
div[data-testid="stButton"] button p {
    font-weight: 800 !important;
    font-size: 15px !important;
}
div[data-testid="stButton"] button:hover {
    border-color: #3b82f6 !important;
    color: #2563eb !important;
    background-color: #eff6ff !important;
}

/* === 1. HÀNG ĐẦU TIÊN: NÚT QUAY LẠI & ĐỀ BÀI XANH PASTEL NẰM CÙNG 1 DÒNG === */
[data-testid="stHorizontalBlock"]:has(.problem-banner-pastel) {
    align-items: center !important;
}
.problem-banner-pastel {
    background: linear-gradient(180deg, #d8ecff 0%, #c7e2fe 100%);
    border: 1px solid #93c5fd;
    padding: 12px 24px;
    border-radius: 16px;
    margin: 0 !important;
    min-height: 54px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0px 4px 12px rgba(59, 130, 246, 0.1);
    text-align: center;
}
.problem-banner-pastel p {
    font-size: 19px;
    margin: 0 !important;
    line-height: 1.4;
    color: #0f172a;
}

/* === LOẠI BỎ KHOẢNG TRẮNG THỪA Ở DƯỚI CỘT TRÁI & CỘT PHẢI === */
[data-testid="stHorizontalBlock"]:has(.left-dock-marker) {
    align-items: flex-start !important;
}
div[data-testid="stColumn"]:has(.left-dock-marker),
div[data-testid="column"]:has(.left-dock-marker),
div[data-testid="stColumn"]:has(.right-palette-marker),
div[data-testid="column"]:has(.right-palette-marker) {
    height: fit-content !important;
    align-self: flex-start !important;
}

/* === 2. THANH DOCK CÔNG CỤ NỔI BÊN TRÁI (ICON SVG CHUẨN NHƯ ẢNH MẪU) === */
div[data-testid="stColumn"]:has(.left-dock-marker),
div[data-testid="column"]:has(.left-dock-marker) {
    background: #ffffff !important;
    border-radius: 18px !important;
    padding: 12px 10px !important;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.07) !important;
    border: 1px solid #e2e8f0 !important;
}
/* Ẩn triệt để chấm tròn radio mặc định trong cột công cụ trái */
div[data-testid="stColumn"]:has(.left-dock-marker) div[role="radiogroup"] label div:not(:has(p)),
div[data-testid="column"]:has(.left-dock-marker) div[role="radiogroup"] label div:not(:has(p)) {
    display: none !important;
}
div[data-testid="stColumn"]:has(.left-dock-marker) div[role="radiogroup"],
div[data-testid="column"]:has(.left-dock-marker) div[role="radiogroup"] {
    gap: 6px !important;
    width: 100% !important;
}
div[data-testid="stColumn"]:has(.left-dock-marker) div[role="radiogroup"] label,
div[data-testid="column"]:has(.left-dock-marker) div[role="radiogroup"] label {
    width: 100% !important;
    margin: 0 !important;
    padding: 10px 14px !important;
    border-radius: 12px !important;
    border: 1.5px solid transparent !important;
    cursor: pointer !important;
    transition: all 0.18s ease !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 12px !important;
}
/* Khung chứa Icon SVG bên trái mỗi công cụ */
div[data-testid="stColumn"]:has(.left-dock-marker) div[role="radiogroup"] label::before,
div[data-testid="column"]:has(.left-dock-marker) div[role="radiogroup"] label::before {
    content: "" !important;
    display: inline-block !important;
    width: 24px !important;
    height: 24px !important;
    flex-shrink: 0 !important;
    background-size: contain !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
}
/* Icon 1: Tự do (Bút chì) */
div[data-testid="stColumn"]:has(.left-dock-marker) div[role="radiogroup"] label:nth-child(1)::before,
div[data-testid="column"]:has(.left-dock-marker) div[role="radiogroup"] label:nth-child(1)::before {
    background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231e293b' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z' fill='%23dbeafe'/%3E%3Cpath d='m15 5 4 4'/%3E%3Cpath d='m3.5 16.5 4 4'/%3E%3C/svg%3E") !important;
}
div[data-testid="stColumn"]:has(.left-dock-marker) div[role="radiogroup"] label:nth-child(1):has(input:checked)::before,
div[data-testid="column"]:has(.left-dock-marker) div[role="radiogroup"] label:nth-child(1):has(input:checked)::before {
    background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%230284c7' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z' fill='%23bae6fd'/%3E%3Cpath d='m15 5 4 4'/%3E%3Cpath d='m3.5 16.5 4 4'/%3E%3C/svg%3E") !important;
}
/* Icon 2: Đường thẳng (Thước kẻ nghiêng) */
div[data-testid="stColumn"]:has(.left-dock-marker) div[role="radiogroup"] label:nth-child(2)::before,
div[data-testid="column"]:has(.left-dock-marker) div[role="radiogroup"] label:nth-child(2)::before {
    background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231e293b' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cg transform='rotate(45 12 12)'%3E%3Crect x='2' y='8' width='20' height='8' rx='1.5' fill='%23dbeafe'/%3E%3Cline x1='6' y1='8' x2='6' y2='11.5'/%3E%3Cline x1='10' y1='8' x2='10' y2='12.5'/%3E%3Cline x1='14' y1='8' x2='14' y2='11.5'/%3E%3Cline x1='18' y1='8' x2='18' y2='12.5'/%3E%3C/g%3E%3C/svg%3E") !important;
}
/* Icon 3: Đa giác (Tam giác) */
div[data-testid="stColumn"]:has(.left-dock-marker) div[role="radiogroup"] label:nth-child(3)::before,
div[data-testid="column"]:has(.left-dock-marker) div[role="radiogroup"] label:nth-child(3)::before {
    background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231e293b' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolygon points='12 3.5 21 19.5 3 19.5' fill='%23dbeafe'/%3E%3C/svg%3E") !important;
}
/* Icon 4: Chữ nhật */
div[data-testid="stColumn"]:has(.left-dock-marker) div[role="radiogroup"] label:nth-child(4)::before,
div[data-testid="column"]:has(.left-dock-marker) div[role="radiogroup"] label:nth-child(4)::before {
    background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231e293b' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3.5' y='3.5' width='17' height='17' rx='2.5' fill='%23dbeafe'/%3E%3C/svg%3E") !important;
}
/* Icon 5: Đường tròn */
div[data-testid="stColumn"]:has(.left-dock-marker) div[role="radiogroup"] label:nth-child(5)::before,
div[data-testid="column"]:has(.left-dock-marker) div[role="radiogroup"] label:nth-child(5)::before {
    background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231e293b' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='8.5' fill='%23dbeafe'/%3E%3C/svg%3E") !important;
}
/* Icon 6: Di chuyển (Bàn tay) */
div[data-testid="stColumn"]:has(.left-dock-marker) div[role="radiogroup"] label:nth-child(6)::before,
div[data-testid="column"]:has(.left-dock-marker) div[role="radiogroup"] label:nth-child(6)::before {
    background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231e293b' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M18 11V6a2 2 0 0 0-4 0v4' fill='%23dbeafe'/%3E%3Cpath d='M14 10V4a2 2 0 0 0-4 0v6' fill='%23dbeafe'/%3E%3Cpath d='M10 10.5V6a2 2 0 0 0-4 0v8' fill='%23dbeafe'/%3E%3Cpath d='M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15' fill='%23dbeafe'/%3E%3C/svg%3E") !important;
}
/* Icon 7: Tẩy */
div[data-testid="stColumn"]:has(.left-dock-marker) div[role="radiogroup"] label:nth-child(7)::before,
div[data-testid="column"]:has(.left-dock-marker) div[role="radiogroup"] label:nth-child(7)::before {
    background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231e293b' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m7 21-4.3-4.3c-1-1-1-2.5 0-3.4l9.6-9.6c1-1 2.5-1 3.4 0l5.6 5.6c1 1 1 2.5 0 3.4L13 21' fill='%23dbeafe'/%3E%3Cpath d='M22 21H7'/%3E%3Cpath d='m5 11 9 9'/%3E%3Ccircle cx='5' cy='5' r='1' fill='%231e293b'/%3E%3Ccircle cx='19' cy='19' r='1' fill='%231e293b'/%3E%3C/svg%3E") !important;
}

div[data-testid="stColumn"]:has(.left-dock-marker) div[role="radiogroup"] label p,
div[data-testid="column"]:has(.left-dock-marker) div[role="radiogroup"] label p {
    white-space: nowrap !important;
    font-size: 15.5px !important;
    font-weight: 500 !important;
    color: #1e293b !important;
    margin: 0 !important;
}
div[data-testid="stColumn"]:has(.left-dock-marker) div[role="radiogroup"] label:hover,
div[data-testid="column"]:has(.left-dock-marker) div[role="radiogroup"] label:hover {
    background: #f8fafc !important;
    border-color: #cbd5e1 !important;
}
div[data-testid="stColumn"]:has(.left-dock-marker) div[role="radiogroup"] label:has(input:checked),
div[data-testid="column"]:has(.left-dock-marker) div[role="radiogroup"] label:has(input:checked) {
    background: #e0f2fe !important;
    border: 1.5px solid #0284c7 !important;
    box-shadow: 0 2px 6px rgba(2, 132, 199, 0.12) !important;
}
div[data-testid="stColumn"]:has(.left-dock-marker) div[role="radiogroup"] label:has(input:checked) p,
div[data-testid="column"]:has(.left-dock-marker) div[role="radiogroup"] label:has(input:checked) p {
    color: #0f172a !important;
    font-weight: 600 !important;
}

/* === 3. THẺ CHỌN MÀU SẮC & NÉT BÚT BÊN PHẢI === */
div[data-testid="stColumn"]:has(.right-palette-marker),
div[data-testid="column"]:has(.right-palette-marker) {
    background: #ffffff !important;
    border-radius: 18px !important;
    padding: 16px 18px !important;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.07) !important;
    border: 1px solid #e2e8f0 !important;
}
/* Ẩn triệt để chấm tròn radio mặc định trong cột phải */
div[data-testid="stColumn"]:has(.right-palette-marker) div[role="radiogroup"] label div:not(:has(p)),
div[data-testid="column"]:has(.right-palette-marker) div[role="radiogroup"] label div:not(:has(p)) {
    display: none !important;
}
.palette-section-title {
    font-size: 14.5px;
    font-weight: 700;
    color: #1e293b;
    margin: 0 0 8px 0;
}

/* --- 3A. BẢNG CHỌN MÀU SẮC (5 HÌNH TRÒN MÀU TRÊN 1 HÀNG) --- */
div[data-testid="stElementContainer"]:has(.color-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"],
div.element-container:has(.color-title-marker) + div.element-container div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    justify-content: flex-start !important;
    gap: 14px !important;
    padding: 2px 2px 10px 2px !important;
}
div[data-testid="stElementContainer"]:has(.color-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"] label,
div.element-container:has(.color-title-marker) + div.element-container div[role="radiogroup"] label {
    width: 28px !important;
    height: 28px !important;
    min-width: 28px !important;
    max-width: 28px !important;
    min-height: 28px !important;
    max-height: 28px !important;
    border-radius: 50% !important;
    padding: 0 !important;
    margin: 0 !important;
    cursor: pointer !important;
    border: 2px solid transparent !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}
div[data-testid="stElementContainer"]:has(.color-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"] label > div,
div.element-container:has(.color-title-marker) + div.element-container div[role="radiogroup"] label > div {
    display: none !important;
}
div[data-testid="stElementContainer"]:has(.color-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"] label:nth-child(1),
div.element-container:has(.color-title-marker) + div.element-container div[role="radiogroup"] label:nth-child(1) {
    background-color: #0f172a !important;
}
div[data-testid="stElementContainer"]:has(.color-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"] label:nth-child(2),
div.element-container:has(.color-title-marker) + div.element-container div[role="radiogroup"] label:nth-child(2) {
    background-color: #ea1e24 !important;
}
div[data-testid="stElementContainer"]:has(.color-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"] label:nth-child(3),
div.element-container:has(.color-title-marker) + div.element-container div[role="radiogroup"] label:nth-child(3) {
    background-color: #2563eb !important;
}
div[data-testid="stElementContainer"]:has(.color-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"] label:nth-child(4),
div.element-container:has(.color-title-marker) + div.element-container div[role="radiogroup"] label:nth-child(4) {
    background-color: #16a34a !important;
}
div[data-testid="stElementContainer"]:has(.color-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"] label:nth-child(5),
div.element-container:has(.color-title-marker) + div.element-container div[role="radiogroup"] label:nth-child(5) {
    background-color: #f97316 !important;
}
div[data-testid="stElementContainer"]:has(.color-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"] label:has(input:checked),
div.element-container:has(.color-title-marker) + div.element-container div[role="radiogroup"] label:has(input:checked) {
    border: 2px solid #ffffff !important;
    box-shadow: 0 0 0 2.5px #3b82f6, 0 4px 10px rgba(59, 130, 246, 0.25) !important;
    transform: scale(1.12) !important;
}

/* --- 3B. BẢNG CHỌN NÉT BÚT (CHẤM TRÒN Ở TRÊN, CHỮ Ở DƯỚI, KHÔNG CÓ NÚT TRÒN ĐỎ) --- */
div[data-testid="stElementContainer"]:has(.thickness-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"] label div:not(:has(p)),
div.element-container:has(.thickness-title-marker) + div.element-container div[role="radiogroup"] label div:not(:has(p)) {
    display: none !important;
}
div[data-testid="stElementContainer"]:has(.thickness-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"],
div.element-container:has(.thickness-title-marker) + div.element-container div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: stretch !important;
    justify-content: space-between !important;
    gap: 8px !important;
    width: 100% !important;
}
div[data-testid="stElementContainer"]:has(.thickness-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"] label,
div.element-container:has(.thickness-title-marker) + div.element-container div[role="radiogroup"] label {
    flex: 1 1 0% !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: flex-end !important;
    height: 58px !important;
    padding: 6px 4px !important;
    margin: 0 !important;
    border-radius: 12px !important;
    border: 1.5px solid transparent !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
}
div[data-testid="stElementContainer"]:has(.thickness-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"] label:hover,
div.element-container:has(.thickness-title-marker) + div.element-container div[role="radiogroup"] label:hover {
    background-color: #f8fafc !important;
    border-color: #e2e8f0 !important;
}
div[data-testid="stElementContainer"]:has(.thickness-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"] label::before,
div.element-container:has(.thickness-title-marker) + div.element-container div[role="radiogroup"] label::before {
    content: "" !important;
    display: block !important;
    background-color: #334155 !important;
    border-radius: 50% !important;
    margin: auto 0 !important;
    transition: background-color 0.15s ease !important;
}
div[data-testid="stElementContainer"]:has(.thickness-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"] label:nth-child(1)::before,
div.element-container:has(.thickness-title-marker) + div.element-container div[role="radiogroup"] label:nth-child(1)::before {
    width: 6px !important;
    height: 6px !important;
}
div[data-testid="stElementContainer"]:has(.thickness-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"] label:nth-child(2)::before,
div.element-container:has(.thickness-title-marker) + div.element-container div[role="radiogroup"] label:nth-child(2)::before {
    width: 10px !important;
    height: 10px !important;
}
div[data-testid="stElementContainer"]:has(.thickness-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"] label:nth-child(3)::before,
div.element-container:has(.thickness-title-marker) + div.element-container div[role="radiogroup"] label:nth-child(3)::before {
    width: 15px !important;
    height: 15px !important;
}
div[data-testid="stElementContainer"]:has(.thickness-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"] label:nth-child(4)::before,
div.element-container:has(.thickness-title-marker) + div.element-container div[role="radiogroup"] label:nth-child(4)::before {
    width: 20px !important;
    height: 20px !important;
}
div[data-testid="stElementContainer"]:has(.thickness-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"] label p,
div.element-container:has(.thickness-title-marker) + div.element-container div[role="radiogroup"] label p {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #475569 !important;
    margin: 0 !important;
    line-height: 1.2 !important;
    white-space: nowrap !important;
    text-align: center !important;
}
div[data-testid="stElementContainer"]:has(.thickness-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"] label:has(input:checked),
div.element-container:has(.thickness-title-marker) + div.element-container div[role="radiogroup"] label:has(input:checked) {
    background-color: #eff6ff !important;
    border-color: #3b82f6 !important;
}
div[data-testid="stElementContainer"]:has(.thickness-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"] label:has(input:checked)::before,
div.element-container:has(.thickness-title-marker) + div.element-container div[role="radiogroup"] label:has(input:checked)::before {
    background-color: #2563eb !important;
}
div[data-testid="stElementContainer"]:has(.thickness-title-marker) + div[data-testid="stElementContainer"] div[role="radiogroup"] label:has(input:checked) p,
div.element-container:has(.thickness-title-marker) + div.element-container div[role="radiogroup"] label:has(input:checked) p {
    color: #1d4ed8 !important;
    font-weight: 700 !important;
}

/* === 4. BO TRÒN & ĐỔ BÓNG KHUNG BẢNG VẼ === */
div[data-testid="stColumn"]:has(.center-canvas-marker) iframe,
div[data-testid="column"]:has(.center-canvas-marker) iframe {
    border-radius: 16px !important;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08) !important;
    border: 1.5px solid #cbd5e1 !important;
}

/* KHUNG CHAT NỔI (ROBOT) - ĐÓNG/MỞ MƯỢT, KHÔNG BỊ BIẾN THÀNH THANH NGANG KHI HẠ XUỐNG */
@keyframes chatPopOpen {
    from { opacity: 0; transform: scale(0.85); }
    to { opacity: 1; transform: scale(1); }
}
[data-testid="stExpander"] { position: fixed !important; bottom: 40px !important; right: 15px !important; width: auto !important; z-index: 99999; }
[data-testid="stExpander"] details { box-shadow: 0px 8px 24px rgba(0,0,0,0.15); transition: none !important; transform-origin: bottom right; }

/* Trạng thái thu gọn thành hình tròn (bao gồm cả khoảnh khắc vừa bấm hạ xuống) */
div[data-testid="stExpander"] details:not([open]),
div[data-testid="stExpander"] details.chatbot-closing {
    width: 65px !important;
    height: 65px !important;
    border-radius: 50% !important;
    background-color: transparent !important;
    border: none !important;
    overflow: hidden !important;
}
div[data-testid="stExpander"] details:not([open]) summary,
div[data-testid="stExpander"] details.chatbot-closing summary {
    background: #ffffff !important;
    border: 2px solid #ea1e24 !important;
    border-radius: 50% !important;
    width: 65px !important;
    height: 65px !important;
    padding: 0 !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    list-style: none !important;
}
div[data-testid="stExpander"] details:not([open]) summary::-webkit-details-marker,
div[data-testid="stExpander"] details.chatbot-closing summary::-webkit-details-marker { display: none !important; }
div[data-testid="stExpander"] details:not([open]) summary *,
div[data-testid="stExpander"] details.chatbot-closing summary *,
div[data-testid="stExpander"] details:not([open]) summary p::before,
div[data-testid="stExpander"] details.chatbot-closing summary p::before,
div[data-testid="stExpander"] details.chatbot-closing [data-testid="stExpanderDetails"] {
    display: none !important;
}
div[data-testid="stExpander"] details:not([open]) summary::after,
div[data-testid="stExpander"] details.chatbot-closing summary::after {
    content: "🤖" !important;
    font-size: 32px !important;
    display: block !important;
}

/* Trạng thái khi mở khung chat */
div[data-testid="stExpander"] details[open]:not(.chatbot-closing) {
    width: 380px !important;
    max-width: 90vw;
    background-color: #ffffff;
    border-radius: 16px !important;
    border: 1px solid #ddd;
    overflow: hidden;
    animation: chatPopOpen 0.18s ease-out forwards;
}
div[data-testid="stExpander"] details[open]:not(.chatbot-closing) summary {
    background: linear-gradient(90deg, #ea1e24 0%, #f97316 100%) !important;
    color: white !important;
    padding: 12px 15px !important;
    border-radius: 16px 16px 0 0 !important;
}
[data-testid="stExpanderDetails"] { max-height: 60vh; overflow-y: auto; padding: 15px; }

/* ẨN NÚT GỬI & DỌN DẸP Ô UPLOAD */
[data-testid="stFileUploadDropzone"] small, [data-testid="stFileUploadDropzone"] span, [data-testid="stFileUploadDropzone"] svg { display: none !important; }
[data-testid="stFileUploadDropzone"] { min-height: 35px !important; padding: 8px !important; background-color: #f8f9fa; border: 1px dashed #bbb !important; border-radius: 8px !important; display: flex; justify-content: center; align-items: center; margin-bottom: -15px; }
[data-testid="stFileUploadDropzone"]::after { content: "📸 Click vào đây để Upload ảnh"; font-size: 13px; font-weight: 500; color: #666; }
[data-testid="stFormSubmitButton"] { display: none !important; }
/* === GIAO DIỆN TRANG CHỦ MỚI THEO ẢNH THIẾT KẾ === */
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@800;900&display=swap');

.home-header-wrap {
    text-align: center;
    margin-top: 4px;
    margin-bottom: 26px;
    position: relative;
    z-index: 2;
}
.home-badge-pill {
    display: inline-block;
    background: #dbe4ef;
    color: #1e293b;
    font-size: 14px;
    font-weight: 600;
    padding: 6px 20px;
    border-radius: 999px;
    border: 1px solid #cbd5e1;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
    margin-bottom: 14px;
}
.home-main-title {
    font-family: 'Merriweather', 'Times New Roman', serif !important;
    font-size: 38px !important;
    font-weight: 900 !important;
    color: #0f172a !important;
    letter-spacing: 0.5px;
    margin: 0 0 10px 0 !important;
    text-transform: uppercase;
}
.home-sub-title {
    font-size: 17px;
    color: #1e293b;
    font-weight: 500;
    margin: 0;
}

/* Căn giữa 4 thẻ hoạt động */
[data-testid="stHorizontalBlock"]:has(.home-activity-marker) {
    max-width: 1180px !important;
    margin: 0 auto !important;
    gap: 22px !important;
    align-items: stretch !important;
    position: relative;
    z-index: 2;
}

/* Biến từng cột thành Thẻ trắng bo tròn chứa cả nội dung và nút bấm */
div[data-testid="stColumn"]:has(.home-activity-marker),
div[data-testid="column"]:has(.home-activity-marker) {
    border-radius: 22px !important;
    padding: 22px 20px 22px 20px !important;
    box-shadow: 0 14px 32px rgba(15, 23, 42, 0.07) !important;
    border: 1.5px solid #ffffff !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    transition: transform 0.22s ease, box-shadow 0.22s ease !important;
}
div[data-testid="stColumn"]:has(.home-activity-marker):hover,
div[data-testid="column"]:has(.home-activity-marker):hover {
    transform: translateY(-5px) !important;
    box-shadow: 0 20px 38px rgba(15, 23, 42, 0.12) !important;
}

/* Màu nền tỏa sáng Pastel nhẹ cho từng thẻ */
div[data-testid="stColumn"]:has(.home-card-1),
div[data-testid="column"]:has(.home-card-1) {
    background: radial-gradient(circle at 50% 35%, #e0f2fe 0%, #ffffff 70%) !important;
}
div[data-testid="stColumn"]:has(.home-card-2),
div[data-testid="column"]:has(.home-card-2) {
    background: radial-gradient(circle at 50% 35%, #ede9fe 0%, #ffffff 70%) !important;
}
div[data-testid="stColumn"]:has(.home-card-3),
div[data-testid="column"]:has(.home-card-3) {
    background: radial-gradient(circle at 50% 35%, #ffedd5 0%, #ffffff 70%) !important;
}
div[data-testid="stColumn"]:has(.home-card-4),
div[data-testid="column"]:has(.home-card-4) {
    background: radial-gradient(circle at 50% 35%, #ffe4e6 0%, #ffffff 70%) !important;
}

/* Nội dung bên trong thẻ */
.card-step-label {
    font-size: 13px;
    font-weight: 800;
    color: #0f172a;
    text-transform: uppercase;
    text-align: left;
    margin-bottom: 8px;
    letter-spacing: 0.3px;
}
.card-svg-box {
    height: 145px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 4px 0 12px 0;
}
.card-main-heading {
    font-size: 20.5px;
    font-weight: 800;
    color: #0f172a;
    text-align: center;
    margin-bottom: 10px;
}
.card-desc-text {
    font-size: 14px;
    color: #334155;
    text-align: center;
    line-height: 1.5;
    min-height: 64px;
    margin-bottom: 8px;
}

/* Đổi màu 4 nút bấm dạng viên thuốc (Pill Button) nằm trong thẻ */
div[data-testid="stColumn"]:has(.home-activity-marker) div[data-testid="stButton"] button,
div[data-testid="column"]:has(.home-activity-marker) div[data-testid="stButton"] button {
    border-radius: 999px !important;
    min-height: 44px !important;
    height: 44px !important;
    border: none !important;
    box-shadow: 0 4px 10px rgba(15, 23, 42, 0.08) !important;
}
div[data-testid="stColumn"]:has(.home-activity-marker) div[data-testid="stButton"] button p,
div[data-testid="column"]:has(.home-activity-marker) div[data-testid="stButton"] button p {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #0f172a !important;
}

div[data-testid="stColumn"]:has(.home-card-1) div[data-testid="stButton"] button,
div[data-testid="column"]:has(.home-card-1) div[data-testid="stButton"] button {
    background: linear-gradient(180deg, #bae6fd 0%, #93c5fd 100%) !important;
}
div[data-testid="stColumn"]:has(.home-card-2) div[data-testid="stButton"] button,
div[data-testid="column"]:has(.home-card-2) div[data-testid="stButton"] button {
    background: linear-gradient(180deg, #ddd6fe 0%, #c4b5fd 100%) !important;
}
div[data-testid="stColumn"]:has(.home-card-3) div[data-testid="stButton"] button,
div[data-testid="column"]:has(.home-card-3) div[data-testid="stButton"] button {
    background: linear-gradient(180deg, #fed7aa 0%, #fdba74 100%) !important;
}
div[data-testid="stColumn"]:has(.home-card-4) div[data-testid="stButton"] button,
div[data-testid="column"]:has(.home-card-4) div[data-testid="stButton"] button {
    background: linear-gradient(180deg, #fecdd3 0%, #fda4af 100%) !important;
}

/* Hình vẽ Toán học phác thảo ở 4 góc nền trang chủ */
.math-doodle-bg {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    opacity: 0.38;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. TRANG CHỦ: 4 HOẠT ĐỘNG HỌC TẬP CHÍNH
# ==========================================
if st.session_state.current_page == "home":
    st.markdown("""
    <div class="math-doodle-bg">
        <svg width="180" height="180" viewBox="0 0 180 180" style="position:absolute; top:110px; left:10px;">
            <polygon points="20,150 110,25 145,150" fill="none" stroke="#64748b" stroke-width="2"/>
            <polygon points="48,132 98,62 118,132" fill="none" stroke="#64748b" stroke-width="1.5"/>
        </svg>
        <svg width="240" height="170" viewBox="0 0 240 170" style="position:absolute; top:15px; right:15px;">
            <path d="M 10 80 Q 45 10, 80 80 T 150 80" fill="none" stroke="#64748b" stroke-width="2"/>
            <polygon points="120,95 190,25 225,115" fill="none" stroke="#64748b" stroke-width="2"/>
            <text x="135" y="145" fill="#64748b" font-family="serif" font-style="italic" font-size="18">A² = a(m+b)/2</text>
        </svg>
        <svg width="260" height="180" viewBox="0 0 260 180" style="position:absolute; bottom:10px; left:15px;">
            <line x1="30" y1="150" x2="30" y2="20" stroke="#64748b" stroke-width="2"/>
            <line x1="10" y1="125" x2="210" y2="125" stroke="#64748b" stroke-width="2"/>
            <path d="M 30 125 Q 75 20, 120 125 T 200 95" fill="none" stroke="#64748b" stroke-width="2"/>
            <text x="15" y="25" fill="#64748b" font-family="serif" font-style="italic" font-size="16">y</text>
            <text x="215" y="130" fill="#64748b" font-family="serif" font-style="italic" font-size="16">x</text>
            <text x="145" y="165" fill="#64748b" font-family="serif" font-style="italic" font-size="18">ln - x = sin α</text>
        </svg>
        <svg width="240" height="140" viewBox="0 0 240 140" style="position:absolute; bottom:10px; right:15px;">
            <text x="20" y="55" fill="#64748b" font-family="serif" font-style="italic" font-size="18">h = r = 16 / h</text>
            <text x="10" y="110" fill="#64748b" font-family="serif" font-style="italic" font-size="19">(1 = ac²)² · (ln - a²)/2</text>
        </svg>
    </div>

    <div class="home-header-wrap">
        <div class="home-badge-pill">Toán Hình Học 10</div>
        <h1 class="home-main-title">BÀI: ĐỊNH LÍ CÔSIN VÀ ĐỊNH LÍ SIN</h1>
        <p class="home-sub-title">Hãy chọn một hoạt động học tập để bắt đầu: 🧭</p>
    </div>
    """, unsafe_allow_html=True)

    col_act1, col_act2, col_act3, col_act4 = st.columns(4, gap="medium")

    with col_act1:
        st.markdown("""
        <div class="home-activity-marker home-card-1">
            <div class="card-step-label">HOẠT ĐỘNG 1</div>
            <div class="card-svg-box">
                <svg width="135" height="125" viewBox="0 0 140 130">
                    <polygon points="55,30 85,20 115,32 115,98 85,86 55,98" fill="#bae6fd" stroke="#475569" stroke-width="2" stroke-linejoin="round"/>
                    <line x1="85" y1="20" x2="85" y2="86" stroke="#475569" stroke-width="1.5" stroke-dasharray="3,3"/>
                    <path d="M 65 45 Q 75 40 78 52 T 70 75 Z" fill="#86efac" stroke="#15803d" stroke-width="1.2"/>
                    <path d="M 92 38 Q 105 42 103 58 T 94 72 Z" fill="#86efac" stroke="#15803d" stroke-width="1.2"/>
                    <circle cx="48" cy="68" r="32" fill="#93c5fd" stroke="#334155" stroke-width="2.2"/>
                    <circle cx="48" cy="68" r="25" fill="#f8fafc" stroke="#475569" stroke-width="1.5"/>
                    <polygon points="48,47 54,68 48,63 42,68" fill="#ef4444"/>
                    <polygon points="48,89 54,68 48,73 42,68" fill="#64748b"/>
                    <circle cx="48" cy="68" r="3.5" fill="#1e293b"/>
                </svg>
            </div>
            <div class="card-main-heading">Hoạt động trải nghiệm</div>
            <div class="card-desc-text">Tình huống thực tế mở đầu và khám phá bài toán đo khoảng cách.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Vào Hoạt động 1", key="btn_act1", use_container_width=True):
            st.session_state.current_page = "trai_nghiem"
            st.rerun()

    with col_act2:
        st.markdown("""
        <div class="home-activity-marker home-card-2">
            <div class="card-step-label">HOẠT ĐỘNG 2</div>
            <div class="card-svg-box">
                <svg width="140" height="125" viewBox="0 0 145 130">
                    <circle cx="42" cy="42" r="16" fill="#fef08a" stroke="#ca8a04" stroke-width="2"/>
                    <rect x="36" y="56" width="12" height="7" rx="2" fill="#cbd5e1" stroke="#475569" stroke-width="1.5"/>
                    <line x1="42" y1="16" x2="42" y2="21" stroke="#eab308" stroke-width="2.5" stroke-linecap="round"/>
                    <line x1="20" y1="28" x2="25" y2="31" stroke="#eab308" stroke-width="2.5" stroke-linecap="round"/>
                    <line x1="64" y1="28" x2="59" y2="31" stroke="#eab308" stroke-width="2.5" stroke-linecap="round"/>
                    <polygon points="88,22 88,78 58,78" fill="#f1f5f9" stroke="#475569" stroke-width="2" stroke-linejoin="round"/>
                    <polygon points="92,28 92,78 122,78" fill="#e2e8f0" stroke="#475569" stroke-width="2" stroke-linejoin="round"/>
                    <polygon points="52,80 128,80 116,96 64,96" fill="#a5b4fc" stroke="#475569" stroke-width="2" stroke-linejoin="round"/>
                    <rect x="24" y="92" width="98" height="18" rx="3" transform="rotate(4 73 101)" fill="#f0abfc" stroke="#6b21a8" stroke-width="1.8"/>
                    <line x1="35" y1="92" x2="35" y2="99" stroke="#6b21a8" stroke-width="1.5"/>
                    <line x1="50" y1="93" x2="50" y2="100" stroke="#6b21a8" stroke-width="1.5"/>
                    <line x1="65" y1="94" x2="65" y2="101" stroke="#6b21a8" stroke-width="1.5"/>
                    <line x1="80" y1="95" x2="80" y2="102" stroke="#6b21a8" stroke-width="1.5"/>
                    <line x1="95" y1="96" x2="95" y2="103" stroke="#6b21a8" stroke-width="1.5"/>
                </svg>
            </div>
            <div class="card-main-heading">Hình thành kiến thức</div>
            <div class="card-desc-text">Mô phỏng tàu thuyền, đo đạc thực nghiệm và chứng minh Định lí Côsin.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📐 Mở Hình thành kiến thức", key="btn_act2", use_container_width=True):
            st.session_state.current_page = "hinh_thanh_kien_thuc"
            st.rerun()

    with col_act3:
        st.markdown("""
        <div class="home-activity-marker home-card-3">
            <div class="card-step-label">HOẠT ĐỘNG 3</div>
            <div class="card-svg-box">
                <svg width="135" height="125" viewBox="0 0 140 130">
                    <rect x="30" y="22" width="58" height="76" rx="6" transform="rotate(-8 59 60)" fill="#fdba74" stroke="#475569" stroke-width="2"/>
                    <rect x="42" y="34" width="34" height="22" rx="3" transform="rotate(-8 59 45)" fill="#fff7ed" stroke="#9a3412" stroke-width="1.5"/>
                    <rect x="82" y="24" width="12" height="62" rx="2" transform="rotate(28 88 55)" fill="#fbbf24" stroke="#475569" stroke-width="2"/>
                    <polygon points="68,80 78,86 68,94" fill="#fde68a" stroke="#475569" stroke-width="1.8"/>
                    <line x1="98" y1="45" x2="84" y2="105" stroke="#64748b" stroke-width="3.5" stroke-linecap="round"/>
                    <line x1="98" y1="45" x2="112" y2="105" stroke="#64748b" stroke-width="3.5" stroke-linecap="round"/>
                    <circle cx="98" cy="42" r="5" fill="#94a3b8" stroke="#334155" stroke-width="2"/>
                </svg>
            </div>
            <div class="card-main-heading">Củng cố</div>
            <div class="card-desc-text">Luyện tập các bài toán Nhận diện, Thể hiện và Củng cố (Bài 1 - Bài 8).</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("✏️ Luyện tập Củng cố", key="btn_act3", use_container_width=True):
            st.session_state.current_page = "danh_sach_cung_co"
            st.rerun()

    with col_act4:
        st.markdown("""
        <div class="home-activity-marker home-card-4">
            <div class="card-step-label">HOẠT ĐỘNG 4</div>
            <div class="card-svg-box">
                <svg width="135" height="125" viewBox="0 0 140 130">
                    <path d="M 48 30 L 92 30 L 86 66 C 84 80, 56 80, 54 66 Z" fill="#fde047" stroke="#854d0e" stroke-width="2.2"/>
                    <path d="M 48 36 C 32 36, 32 58, 51 60" fill="none" stroke="#eab308" stroke-width="4" stroke-linecap="round"/>
                    <path d="M 92 36 C 108 36, 108 58, 89 60" fill="none" stroke="#eab308" stroke-width="4" stroke-linecap="round"/>
                    <rect x="65" y="76" width="10" height="16" fill="#facc15" stroke="#854d0e" stroke-width="2"/>
                    <rect x="48" y="92" width="44" height="14" rx="3" fill="#fda4af" stroke="#881337" stroke-width="2"/>
                    <polygon points="70,42 73,48 80,49 75,54 76,60 70,57 64,60 65,54 60,49 67,48" fill="#f59e0b"/>
                    <circle cx="34" cy="78" r="5" fill="#fb7185"/>
                    <circle cx="105" cy="26" r="4" fill="#facc15"/>
                    <circle cx="106" cy="75" r="5" fill="#facc15"/>
                </svg>
            </div>
            <div class="card-main-heading">Vận dụng</div>
            <div class="card-desc-text">Giải quyết bài toán thực tiễn và chứng minh hệ thức (Bài 9 - Bài 10).</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔥 Thử thách Vận dụng", key="btn_act4", use_container_width=True):
            st.session_state.current_page = "danh_sach_van_dung"
            st.rerun()

# ==========================================
# 3A. MÀN HÌNH HOẠT ĐỘNG 1: HOẠT ĐỘNG TRẢI NGHIỆM (TẠM ĐỂ KHUNG CHỜ)
# ==========================================
elif st.session_state.current_page == "trai_nghiem":
    col_back, col_title = st.columns([1.5, 10.5], gap="medium")
    with col_back:
        if st.button("⬅️ Quay lại", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
    with col_title:
        st.markdown("""
        <div class="problem-banner-pastel">
            <p><strong style="color: #0369a1;">HOẠT ĐỘNG 1: HOẠT ĐỘNG TRẢI NGHIỆM</strong></p>
        </div>
        """, unsafe_allow_html=True)
    st.info("📌 Nội dung Hoạt động trải nghiệm sẽ được cập nhật tại đây.")


# ==========================================
# 3B. MÀN HÌNH HOẠT ĐỘNG 2: HÌNH THÀNH KIẾN THỨC (NHÚNG FILE HTML)
# ==========================================
elif st.session_state.current_page == "hinh_thanh_kien_thuc":
    col_back, col_title = st.columns([1.5, 10.5], gap="medium")
    with col_back:
        if st.button("⬅️ Quay lại", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
    with col_title:
        st.markdown("""
        <div class="problem-banner-pastel">
            <p><strong style="color: #3730a3; text-transform: uppercase;">HOẠT ĐỘNG 2 - HÌNH THÀNH KIẾN THỨC:</strong> Khám phá và chứng minh công thức Định lí Côsin</p>
        </div>
        """, unsafe_allow_html=True)

    try:
        with open("gemini-code-DaiHaiTrinh ver5.html", "r", encoding="utf-8") as f:
            html_code = f.read()
        components.html(html_code, height=800, scrolling=True)
    except FileNotFoundError:
        st.error("⚠️ Không tìm thấy file 'gemini-code-DaiHaiTrinh ver5.html'. Hãy kiểm tra lại tên file trong thư mục!")


# ==========================================
# 3C. MÀN HÌNH HOẠT ĐỘNG 3 (CỦNG CỐ) & HOẠT ĐỘNG 4 (VẬN DỤNG)
# ==========================================
elif st.session_state.current_page in ["danh_sach_cung_co", "danh_sach_van_dung"]:
    is_cung_co = (st.session_state.current_page == "danh_sach_cung_co")
    filtered_problems = [p for p in problems if (p["id"] <= 8 if is_cung_co else p["id"] >= 9)]
    
    col_back, col_title = st.columns([1.5, 10.5], gap="medium")
    with col_back:
        if st.button("⬅️ Quay lại", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
    with col_title:
        header_text = "HOẠT ĐỘNG 3: LUYỆN TẬP CỦNG CỐ (BÀI 1 - BÀI 8)" if is_cung_co else "HOẠT ĐỘNG 4: THỬ THÁCH VẬN DỤNG (BÀI 9 - BÀI 10)"
        st.markdown(f"""
        <div class="problem-banner-pastel">
            <p><strong style="color: #0369a1;">{header_text}</strong> — Chọn một bài toán để bắt đầu</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    cols = st.columns(4 if is_cung_co else 2)
    for i, prob in enumerate(filtered_problems):
        with cols[i % len(cols)]:
            st.markdown(f"<div style='text-align:center; margin-bottom: 6px; font-weight:bold;'>{prob['level']}</div>", unsafe_allow_html=True)
            if st.button(prob['title'], key=f"btn_{prob['id']}", use_container_width=True):
                st.session_state.selected_problem = prob
                st.session_state.current_page = "workspace"
                st.session_state.messages = []
                st.rerun()

# ==========================================
# 4. MÀN HÌNH LÀM BÀI CHÍNH THỨC
# ==========================================
elif st.session_state.current_page == "workspace":
    
    prob = st.session_state.selected_problem
    
    # HÀNG TRÊN CÙNG: NÚT QUAY LẠI (TRÁI) + KHUNG ĐỀ BÀI (GIỮA) + NÚT BÀI TIẾP THEO (PHẢI)
    col_back, col_prob, col_next = st.columns([1.5, 8.8, 1.7], gap="medium")
    
    with col_back:
        # Bấm Quay lại sẽ trở về danh sách chọn bài (Củng cố hoặc Vận dụng) chứ không về thẳng Trang chủ
        if st.button("⬅️ Quay lại", use_container_width=True):
            st.session_state.current_page = "danh_sach_cung_co" if prob["id"] <= 8 else "danh_sach_van_dung"
            st.rerun()
            
    with col_prob:
        st.markdown(f"""
        <div class="problem-banner-pastel">
            <p><strong style="color: #0369a1; text-transform: uppercase;">{prob['title']}:</strong> {prob['content']}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_next:
        if st.button("Bài tiếp theo ➡️", use_container_width=True):
            next_id = (prob["id"] % len(problems)) + 1
            st.session_state.selected_problem = next(p for p in problems if p["id"] == next_id)
            st.session_state.messages = []
            st.rerun()
    
    # === CẤU HÌNH AI & PROMPT (GIỮ NGUYÊN 100%) ===
    api_key = "AQ.Ab8RN6JUI1s_qHLxVMy5I3tn_XWrXrqBwSZCgWxG2OEHJzhnhg"
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.5-flash-lite')
    
    system_prompt = f"""
BẠN LÀ TRỢ LÍ AI TOÁN HỌC - CHUYÊN VIÊN CHẤM BÀI TOÁN HÌNH HỌC (ĐỊNH LÍ SIN, CÔSIN).
Học sinh đang giải bài toán này: "{prob['content']}"

Nhiệm vụ chính của bạn khi nhận được HÌNH ẢNH hoặc TIN NHẮN:
1. **Phân tích hình ảnh:** Tìm các phác thảo, hình vẽ và đặc biệt là các bài giải, công thức được gõ/viết.
2. **Xác định bài toán:** Hiểu rõ học sinh đang muốn giải bài nào.
3. **Chấm bài (Nếu học sinh đã làm bài):**
   - Kiểm tra xem học sinh có sử dụng đúng Định lí Côsin hoặc Định lí Sin không.
   - Kiểm tra các bước biến đổi công thức và tính toán.
   - Đánh giá mức độ chính xác của kết quả cuối cùng.
   - Đưa ra lời nhận xét chi tiết, khen ngợi nếu đúng, chỉ rõ lỗi sai nếu có và hướng dẫn cách sửa.
4. **Hướng dẫn giải (NẾU HỌC SINH HỎI CÁCH LÀM HOẶC BÍ):**
   - QUY TẮC TỐI THƯỢNG 1: TUYỆT ĐỐI KHÔNG ĐƯỢC GIẢI SẴN. KHÔNG ĐƯỢC VIẾT SẴN CÔNG THỨC (ví dụ: không được viết a^2 = b^2 + c^2...).
   - QUY TẮC TỐI THƯỢNG 2: Bạn phải đóng vai trò người dẫn dắt. Hãy đặt ra CHỈ MỘT (01) câu hỏi gợi mở duy nhất ở mỗi lần chat để ép học sinh tự nhớ lại kiến thức.
   - BẮT BUỘC phải DỪNG LẠI và ĐỢI học sinh gõ câu trả lời, sau đó mới được hướng dẫn bước tiếp theo.
   - Mẫu phản hồi chuẩn: "Khi biết độ dài 3 cạnh và muốn tìm 1 góc, em nhớ đến định lí nào?" (Dừng lại, không giải thích thêm).

**Quan trọng nhất về giao diện:**
- Bạn CHỈ được trả lời bằng mã Markdown chuẩn.
- Bạn CHỈ được trình bày công thức Toán trong cặp dấu `$$ ... $$` hoặc `$ ... $` để đảm bảo công thức hiển thị mượt mà trên giao diện thầy Trung.
- KHÔNG hiển thị bất kỳ văn bản thô nào dạng Casio hay mã LaTeX thô.
- Hãy nói chuyện bằng giọng văn của một người thầy giáo tận tâm, khích lệ.
"""

    # --- LAYOUT: DOCK CÔNG CỤ TRÁI - CANVAS GIỮA - HỘP MÀU SẮC PHẢI ---
    st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True) 
    
    col_tools, col_canvas, col_colors = st.columns([1.8, 7.4, 2.8], gap="medium")
    
    with col_tools:
        st.markdown('<div class="left-dock-marker"></div>', unsafe_allow_html=True)
        tool_choice = st.radio(
            "🛠️ Công cụ:",
            ("Tự do", "Đường thẳng", "Đa giác", "Chữ nhật", "Đường tròn", "Di chuyển", "Tẩy"),
            horizontal=False,
            label_visibility="collapsed"
        )
        
    with col_colors:
        st.markdown('<div class="right-palette-marker"></div>', unsafe_allow_html=True)
        st.markdown('<div class="palette-section-title color-title-marker">Màu sắc</div>', unsafe_allow_html=True)
        color_choice = st.radio(
            "🎨 Màu sắc:",
            ("Đen", "Đỏ", "Xanh dương", "Xanh lá", "Cam"),
            horizontal=True,
            label_visibility="collapsed"
        )
        st.markdown('<div class="palette-section-title thickness-title-marker" style="margin-top: 8px;">Nét bút</div>', unsafe_allow_html=True)
        thickness_choice = st.radio(
            "📏 Nét bút:",
            ("Nhỏ", "Vừa", "Lớn", "Rất lớn"),
            horizontal=True,
            label_visibility="collapsed"
        )

    thickness_map = {
        "Nhỏ": 2, "Vừa": 3, "Lớn": 4.5,
        "Rất lớn": 5.5
    }
    stroke_width = thickness_map.get(thickness_choice, 4)

    color_map = {
        "Đen": "#0f172a",
        "Đỏ": "#ea1e24",
        "Xanh dương": "#2563eb",
        "Xanh lá": "#16a34a",
        "Cam": "#f97316"
    }
    active_color = color_map.get(color_choice, "#0f172a")
    
    drawing_mode = "freedraw"
    if "Tự do" in tool_choice: drawing_mode = "freedraw"
    elif "Đường thẳng" in tool_choice: drawing_mode = "line"
    elif "Đa giác" in tool_choice: drawing_mode = "polygon"
    elif "Chữ nhật" in tool_choice: drawing_mode = "rect"
    elif "Đường tròn" in tool_choice: drawing_mode = "circle"
    elif "Di chuyển" in tool_choice: drawing_mode = "transform"
    elif "Tẩy" in tool_choice:
        drawing_mode = "freedraw"
        active_color = "#f9f9f9"
        stroke_width += 15 

    with col_canvas:
        st.markdown('<div class="center-canvas-marker"></div>', unsafe_allow_html=True)
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.2)", 
            stroke_width=stroke_width,
            stroke_color=active_color, 
            background_color="#f9f9f9",
            update_streamlit=True,
            width=850,
            height=500,
            drawing_mode=drawing_mode,
            key="canvas",
        )

    # =========================================================
    # === KHUNG CHAT (GIỮ NGUYÊN 100% TỪ FILE APP2.PY CỦA BẠN) ===
    # =========================================================
    with st.expander("Trợ lí AI ✨", expanded=False):
        # 1. CSS GIAO DIỆN MESSENGER, ICON ẢNH & MỞ KHÓA VÙNG BẤM MICRO
        st.markdown("""
            <style>
            /* Hiệu ứng 3 chấm */
            .typing-indicator { display: flex; align-items: center; margin-bottom: 10px; }
            .typing-indicator span { height: 8px; width: 8px; margin: 0 2px; background-color: #999; border-radius: 50%; animation: typing 1.4s infinite ease-in-out both; }
            .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
            .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
            @keyframes typing { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }

            /* Ẩn mũi tên gập/mở trên thanh tiêu đề đỏ */
            [data-testid="stExpander"] summary svg,
            [data-testid="stExpander"] summary [data-testid="stIcon"],
            [data-testid="stExpanderToggleIcon"] { 
                display: none !important; 
            }

            [data-testid="stExpander"] summary {
                display: flex !important;
                align-items: center !important;
                flex-direction: row !important;
                padding-left: 12px !important;
            }

            [data-testid="stExpander"] summary p {
                display: inline-flex !important;
                align-items: center !important;
                flex-direction: row !important;
                gap: 12px !important;
                margin: 0 !important;
                font-weight: bold;
                font-size: 18px !important;
            }

            /* Icon Robot trên thanh tiêu đề đỏ */
            [data-testid="stExpander"] summary p::before {
                content: "" !important;
                display: inline-block !important;
                width: 38px !important;
                height: 38px !important;
                flex-shrink: 0 !important;
                background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cdefs%3E%3ClinearGradient id='bg' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' stop-color='%23ffffff'/%3E%3Cstop offset='100%25' stop-color='%23e0e5ec'/%3E%3C/linearGradient%3E%3ClinearGradient id='face' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' stop-color='%231a202c'/%3E%3Cstop offset='100%25' stop-color='%232d3748'/%3E%3C/linearGradient%3E%3C/defs%3E%3Ccircle cx='50' cy='50' r='48' fill='url(%23bg)' stroke='%23e0e5ec' stroke-width='2'/%3E%3Crect x='10' y='40' width='10' height='20' rx='4' fill='%23a0aec0'/%3E%3Crect x='80' y='40' width='10' height='20' rx='4' fill='%23a0aec0'/%3E%3Crect x='18' y='30' width='64' height='40' rx='16' fill='url(%23face)'/%3E%3Ccircle cx='35' cy='45' r='5' fill='%2300e6ff'/%3E%3Ccircle cx='65' cy='45' r='5' fill='%2300e6ff'/%3E%3Cpath d='M 40 60 Q 50 68 60 60' fill='none' stroke='%2300e6ff' stroke-width='3' stroke-linecap='round'/%3E%3Crect x='48' y='15' width='4' height='15' fill='%23a0aec0'/%3E%3Ccircle cx='50' cy='12' r='6' fill='%23ff3366'/%3E%3C/svg%3E") !important;
                background-size: contain !important;
                background-position: center !important;
                background-repeat: no-repeat !important;
                border: 2px solid white !important;
                border-radius: 50% !important;
            }

            /* ===== XÓA CỘT AVATAR BÊN TRÁI & CĂN ĐỀU 2 LỀ (JUSTIFY) ===== */
            [data-testid="stChatMessage"] > div:not([data-testid="stChatMessageContent"]),
            [data-testid="stChatMessageAvatarUser"],
            [data-testid="stChatMessageAvatarAssistant"] {
                display: none !important;
                width: 0 !important;
            }

            [data-testid="stChatMessage"] {
                padding: 8px 10px !important;
                margin-bottom: 6px !important;
                border-radius: 12px !important;
            }

            [data-testid="stChatMessageContent"] {
                width: 100% !important;
                max-width: 100% !important;
                padding: 0 !important;
            }

            .ai-msg, 
            [data-testid="stChatMessageContent"] p,
            [data-testid="stChatMessageContent"] li {
                text-align: justify !important;
                text-justify: inter-word !important;
                line-height: 1.6 !important;
                font-size: 16px !important;
                color: #111 !important;
                margin-bottom: 6px !important;
            }

            /* CHỈ ẨN THẺ ĐÁNH DẤU & KHUNG SCRIPT (Dùng srcdoc để KHÔNG ẩn nhầm Micro) */
            div[data-testid="stElementContainer"]:has(.messenger-mic),
            div[data-testid="stElementContainer"]:has(.messenger-img),
            div[data-testid="stElementContainer"]:has(.messenger-input),
            div[data-testid="stElementContainer"]:has(.left-dock-marker),
            div[data-testid="stElementContainer"]:has(.center-canvas-marker),
            div[data-testid="stElementContainer"]:has(.right-palette-marker),
            div.element-container:has(.messenger-mic),
            div.element-container:has(.messenger-img),
            div.element-container:has(.messenger-input),
            div.element-container:has(.left-dock-marker),
            div.element-container:has(.center-canvas-marker),
            div.element-container:has(.right-palette-marker),
            div[data-testid="stElementContainer"]:has(iframe[srcdoc]),
            div.element-container:has(iframe[srcdoc]) {
                display: none !important;
            }

            /* ===== ÉP 3 CỘT (MIC - ẢNH - Ô NHẬP) NẰM TRÊN CÙNG 1 HÀNG NGANG ===== */
            [data-testid="stHorizontalBlock"]:has(.messenger-input) {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                align-items: center !important;
                gap: 6px !important;
                width: 100% !important;
                position: relative !important;
                padding-top: 4px !important;
            }

            /* 1. CỘT MICRO (Mở khóa hoàn toàn vùng click chuột) */
            div[data-testid="column"]:has(.messenger-mic),
            div[data-testid="stColumn"]:has(.messenger-mic) {
                position: relative !important;
                flex: 0 0 36px !important;
                width: 36px !important;
                min-width: 36px !important;
                max-width: 36px !important;
                height: 40px !important;
                padding: 0 !important;
                background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzAwNzhGRiI+PHBhdGggZD0iTTEyIDE0YzEuNjYgMCAzLTEuMzQgMy0zVjVjMC0xLjY2LTEuMzQtMy0zLTNTOSAzLjM0IDkgNXY2YzAgMS42NiAxLjM0IDMgMyAzem01LjkxLTNjLS40OSAwLS45LjM2LS45OC44NUMxNi41MiAxNC4yIDE0LjQ3IDE2IDEyIDE2cy00LjUyLTEuOC00LjkzLTQuMTVjLS4wOC0uNDktLjQ5LS44NS0uOTgtLjg1LS42MSAwLTEuMDkuNTQtMSAxLjE0LjQ5IDMgMi44OSA1LjM1IDUuOTEgNS43OFYyMGMwIC41NS40NSAxIDEgMXMxLS40NSAxLTF2LTIuMDhjMy4wMi0uNDMgNS40Mi0yLjc4IDUuOTEtNS43OC4xLS42LS4zOS0xLjE0LTEtMS4xNHoiLz48L3N2Zz4=") !important;
                background-repeat: no-repeat !important;
                background-position: center !important;
                background-size: 28px !important;
            }
            div[data-testid="column"]:has(.messenger-mic) [data-testid="stElementContainer"],
            div[data-testid="stColumn"]:has(.messenger-mic) [data-testid="stElementContainer"] {
                width: 36px !important;
                height: 40px !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            div[data-testid="column"]:has(.messenger-mic) iframe,
            div[data-testid="stColumn"]:has(.messenger-mic) iframe {
                position: absolute !important;
                top: 0 !important;
                left: 0 !important;
                width: 36px !important;
                height: 40px !important;
                min-height: 40px !important;
                z-index: 30 !important;
                opacity: 0.001 !important;
                cursor: pointer !important;
                border: none !important;
                pointer-events: auto !important;
            }

            /* 2. CỘT TẢI ẢNH */
            div[data-testid="column"]:has(.messenger-img),
            div[data-testid="stColumn"]:has(.messenger-img) {
                flex: 0 0 36px !important;
                width: 36px !important;
                min-width: 36px !important;
                max-width: 36px !important;
                height: 40px !important;
                padding: 0 !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            div[data-testid="column"]:has(.messenger-img) button,
            div[data-testid="stColumn"]:has(.messenger-img) button {
                background-color: transparent !important;
                border: none !important;
                box-shadow: none !important;
                color: transparent !important;
                background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Crect x='3' y='2.5' width='18' height='19' rx='3.5' fill='%23ffffff' stroke='%230078ff' stroke-width='2.2'/%3E%3Ccircle cx='8.5' cy='8.5' r='2.2' fill='%230078ff'/%3E%3Cpath d='M3 16.5 L7.5 13 C8.2 12.4 9.1 12.5 9.8 13.2 L11.2 14.6 L14.8 10.5 C15.6 9.6 16.9 9.6 17.7 10.5 L21 14.5 L21 18.5 C21 20.2 19.7 21.5 18 21.5 L6 21.5 C4.3 21.5 3 20.2 3 18.5 Z' fill='%230078ff'/%3E%3C/svg%3E") !important;
                background-repeat: no-repeat !important;
                background-position: center !important;
                background-size: 27px !important;
                width: 36px !important;
                height: 40px !important;
                min-height: 40px !important;
                cursor: pointer !important;
                padding: 0 !important;
                margin: 0 !important;
            }
            div[data-testid="column"]:has(.messenger-img) button svg,
            div[data-testid="stColumn"]:has(.messenger-img) button svg,
            div[data-testid="column"]:has(.messenger-img) button span,
            div[data-testid="stColumn"]:has(.messenger-img) button span { 
                display: none !important; 
            }

            /* 3. CỘT Ô NHẬP CHỮ */
            div[data-testid="column"]:has(.messenger-input),
            div[data-testid="stColumn"]:has(.messenger-input) {
                flex: 1 1 0% !important;
                width: auto !important;
                min-width: 0 !important;
                max-width: 100% !important;
                padding: 0 !important;
            }
            div[data-testid="column"]:has(.messenger-input) [data-testid="stForm"],
            div[data-testid="stColumn"]:has(.messenger-input) [data-testid="stForm"] {
                border: none !important;
                padding: 0 !important;
                margin: 0 !important;
            }
            div[data-testid="column"]:has(.messenger-input) div[data-baseweb="input"],
            div[data-testid="stColumn"]:has(.messenger-input) div[data-baseweb="input"],
            div[data-testid="column"]:has(.messenger-input) div[data-baseweb="base-input"],
            div[data-testid="stColumn"]:has(.messenger-input) div[data-baseweb="base-input"] {
                border-radius: 22px !important;
                background-color: #f0f2f5 !important;
                border: none !important;
                box-shadow: none !important;
                height: 40px !important;
                position: relative !important;
            }
            /* Thêm icon máy bay giấy nhỏ gọn bên phải ô nhập như ảnh mẫu */
            div[data-testid="column"]:has(.messenger-input) div[data-baseweb="input"]::after,
            div[data-testid="stColumn"]:has(.messenger-input) div[data-baseweb="input"]::after {
                content: "" !important;
                position: absolute !important;
                right: 12px !important;
                top: 50% !important;
                transform: translateY(-50%) !important;
                width: 18px !important;
                height: 18px !important;
                background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2394a3b8'%3E%3Cpath d='M2.01 21L23 12 2.01 3 2 10l15 2-15 2z'/%3E%3C/svg%3E") !important;
                background-repeat: no-repeat !important;
                background-size: contain !important;
                pointer-events: none !important;
            }
            div[data-testid="column"]:has(.messenger-input) input,
            div[data-testid="stColumn"]:has(.messenger-input) input {
                background-color: #f0f2f5 !important;
                padding-left: 14px !important;
                padding-right: 32px !important;
                font-size: 15px !important;
            }
            div[data-testid="InputInstructions"],
            div[data-testid="column"]:has(.messenger-input) button[kind="primaryFormSubmit"],
            div[data-testid="stColumn"]:has(.messenger-input) button[kind="primaryFormSubmit"] {
                display: none !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # 2. VÙNG HIỂN THỊ TIN NHẮN (Hiển thị chuẩn LaTeX)
        chat_container = st.container(height=280, border=False)
        with chat_container:
            if not st.session_state.messages:
                st.markdown('<div class="ai-msg">Tôi là trợ lí AI! Nếu bạn có thắc mắc gì về bài toán trên, hãy hỏi tôi nhé!</div>', unsafe_allow_html=True)

            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    if isinstance(msg["content"], list):
                        for item in msg["content"]:
                            if "text" in item:
                                st.markdown(item["text"])
                            elif "image" in item:
                                st.image(item["image"], width=200)
                    else:
                        st.markdown(msg["content"])

        st.markdown("<hr style='margin: 6px 0 8px 0; border: none; border-top: 1px solid #e0e0e0;'>", unsafe_allow_html=True)

        # 3. THANH NHẬP LIỆU (MIC - ẢNH - TEXT)
        col_voice, col_upload, col_input = st.columns([1, 1, 8], gap="small")

        with col_voice:
            st.markdown('<div class="messenger-mic"></div>', unsafe_allow_html=True)
            audio_bytes = mic_recorder(start_prompt="START_MIC", stop_prompt="STOP_MIC", key="recorder")

        with col_upload:
            st.markdown('<div class="messenger-img"></div>', unsafe_allow_html=True)
            with st.popover(" "):
                uploaded_image = st.file_uploader("Upload", type=['jpg','png','jpeg'], label_visibility="collapsed")

        with col_input:
            st.markdown('<div class="messenger-input"></div>', unsafe_allow_html=True)
            with st.form(key="chat_form_teacher", clear_on_submit=True, border=False):
                user_input = st.text_input("Hỏi trợ lí AI...", placeholder="Nhập câu hỏi và ấn Enter...", key="text_chat", label_visibility="collapsed")
                submit_button = st.form_submit_button("Nút Tàng Hình")

        # 4. KỊCH BẢN MỞ RỘNG NÚT BẤM MICRO & THANH THU ÂM MÀU HỒNG
        components.html("""
        <script>
        (function() {
            const parentDoc = window.parent.document;
            let timerInterval = null;
            let seconds = 0;

            function formatTime(sec) {
                const m = Math.floor(sec / 60);
                const s = sec % 60;
                return m + ":" + (s < 10 ? "0" + s : s);
            }

            setInterval(() => {
                // Thu gọn khung chat về hình tròn ngay lập tức khi bấm vào thanh tiêu đề
                const expDetails = parentDoc.querySelector('[data-testid="stExpander"] details');
                const expSummary = parentDoc.querySelector('[data-testid="stExpander"] summary');
                if (expDetails && expSummary && !expSummary.dataset.boundInstantClose) {
                    expSummary.dataset.boundInstantClose = "true";
                    expSummary.addEventListener('click', () => {
                        if (expDetails.hasAttribute('open')) {
                            expDetails.classList.add('chatbot-closing');
                        } else {
                            expDetails.classList.remove('chatbot-closing');
                        }
                    }, true);
                }
                if (expDetails && !expDetails.hasAttribute('open')) {
                    expDetails.classList.remove('chatbot-closing');
                }
                const row = parentDoc.querySelector('[data-testid="stHorizontalBlock"]:has(.messenger-input)');
                const micCol = parentDoc.querySelector('[data-testid="stColumn"]:has(.messenger-mic), [data-testid="column"]:has(.messenger-mic)');
                if (!row || !micCol) return;

                let recBar = parentDoc.getElementById('custom-rec-bar');
                if (!recBar) {
                    recBar = parentDoc.createElement('div');
                    recBar.id = 'custom-rec-bar';
                    recBar.style.cssText = 'display:none; position:absolute; inset:0; background:#ffdde8; border-radius:24px; padding:4px; z-index:9990; align-items:center; pointer-events:none;';
                    recBar.innerHTML = `
                        <div style="width:100%; height:36px; background:#ff0055; border-radius:20px; display:flex; align-items:center; justify-content:space-between; padding:0 6px; box-sizing:border-box;">
                            <div style="width:26px; height:26px; background:#ffffff; border-radius:50%; display:flex; align-items:center; justify-content:center;">
                                <div style="width:10px; height:10px; background:#ff0055; border-radius:2px;"></div>
                            </div>
                            <span style="color:#ffffff; font-size:13.5px; font-weight:600; font-family:sans-serif;">Đang thu âm... (bấm để dừng)</span>
                            <div id="custom-rec-timer" style="background:#ffffff; color:#ff0055; font-weight:700; font-size:13px; padding:2px 10px; border-radius:12px; font-family:sans-serif;">0:00</div>
                        </div>
                    `;
                    row.appendChild(recBar);
                }

                const micIframe = micCol.querySelector('iframe');
                if (!micIframe || !micIframe.contentDocument) return;

                // Ép nút bấm bên trong iframe luôn phủ kín 100% khung để bấm vào đâu cũng nhận
                const innerBtn = micIframe.contentDocument.querySelector('button');
                if (innerBtn) {
                    innerBtn.style.cssText = 'position:fixed !important; inset:0 !important; width:100vw !important; height:100vh !important; margin:0 !important; padding:0 !important; cursor:pointer !important;';
                }

                const btnText = micIframe.contentDocument.body ? micIframe.contentDocument.body.innerText : "";
                const isRecording = btnText.includes("STOP_MIC");

                if (isRecording) {
                    if (recBar.style.display === 'none') {
                        recBar.style.display = 'flex';
                        seconds = 0;
                        const timerEl = parentDoc.getElementById('custom-rec-timer');
                        if (timerEl) timerEl.innerText = "0:00";
                        if (timerInterval) clearInterval(timerInterval);
                        timerInterval = setInterval(() => {
                            seconds++;
                            const tEl = parentDoc.getElementById('custom-rec-timer');
                            if (tEl) tEl.innerText = formatTime(seconds);
                        }, 1000);
                    }
                    // Khi đang thu âm, phủ vùng bấm dừng lên toàn bộ thanh hồng
                    micIframe.style.cssText = 'position:absolute !important; top:0 !important; left:0 !important; width:340px !important; height:44px !important; z-index:9999 !important; opacity:0.001 !important; cursor:pointer !important;';
                } else {
                    if (recBar.style.display !== 'none') {
                        recBar.style.display = 'none';
                        if (timerInterval) {
                            clearInterval(timerInterval);
                            timerInterval = null;
                        }
                    }
                    // Khi chờ thu âm, giữ vùng bấm chuẩn xác ngay trên icon Micro
                    micIframe.style.cssText = 'position:absolute !important; top:0 !important; left:0 !important; width:36px !important; height:40px !important; z-index:30 !important; opacity:0.001 !important; cursor:pointer !important;';
                }
            }, 150);
        })();
        </script>
        """, height=0)

        # =========================================================
        # 5. XỬ LÝ GỬI TEXT HOẶC ẢNH UPLOAD
        # =========================================================
        if submit_button and (user_input or uploaded_image):
            if uploaded_image is not None and uploaded_image.size > (5 * 1024 * 1024):
                st.session_state.messages.append({"role": "assistant", "content": "⚠️ Dung lượng file quá mức cho phép (Tối đa 5MB)."})
                st.rerun()

            user_display = []
            if user_input: user_display.append({"text": user_input})
            if uploaded_image:
                img_uploaded = Image.open(uploaded_image)
                user_display.append({"image": img_uploaded})
            st.session_state.messages.append({"role": "user", "content": user_display})

            content_to_send = [system_prompt]
            if user_input: content_to_send.append(user_input)
            if uploaded_image: content_to_send.append(img_uploaded)

            if canvas_result.image_data is not None:
                img_array = canvas_result.image_data.astype(np.uint8)
                if np.any(img_array[:, :, :3] != 249):
                    rgba_image = Image.fromarray(img_array)
                    new_size = (int(rgba_image.width / 2), int(rgba_image.height / 2))
                    rgba_image = rgba_image.resize(new_size)
                    canvas_image = Image.new("RGB", rgba_image.size, (255, 255, 255))
                    canvas_image.paste(rgba_image, mask=rgba_image)
                    content_to_send.append(canvas_image)

            try:
                with chat_container:
                    with st.chat_message("assistant"):
                        temp_box = st.empty()
                        temp_box.markdown('<div class="typing-indicator"><span></span><span></span><span></span></div>', unsafe_allow_html=True)
                        response = model.generate_content(content_to_send, stream=True)
                        full_response = ""
                        for chunk in response:
                            full_response += chunk.text
                            temp_box.markdown(f"{full_response} ▌")
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"Lỗi: {e}"})
            st.rerun()

        # =========================================================
        # 6. XỬ LÝ KHI CÓ GIỌNG NÓI (ĐẦY ĐỦ 4 MỤC & VÍ DỤ CỦA BẠN)
        # =========================================================
        if audio_bytes and audio_bytes['bytes'] != st.session_state.get('last_audio'):
            st.session_state['last_audio'] = audio_bytes['bytes']

            audio_part = {
                "mime_type": "audio/wav",
                "data": audio_bytes['bytes']
            }

            audio_prompt = r"""
            Bạn là một chuyên gia nhận diện giọng nói và biên dịch Toán học, đặc biệt chuyên sâu về Hình học lớp 10 (Định lí Côsin, Định lí Sin, Giải tam giác).
            Nhiệm vụ của bạn là chuyển đổi đoạn âm thanh tiếng Việt thành văn bản Toán học chuẩn xác.

            TUYỆT ĐỐI TUÂN THỦ CÁC QUY TẮC SAU:

            1. ĐỊNH DẠNG LATEX (BẮT BUỘC):
            - Mọi biến số, công thức, con số, biểu thức toán học phải được bọc trong cặp dấu $...$ (Inline LaTeX) hoặc $$...$$ (Display LaTeX nếu là phương trình dài).
            - Văn bản tiếng Việt thông thường phải nằm ngoài dấu $.
            - Ví dụ SAI: "$Cho tam giác ABC có a = 5$"
            - Ví dụ ĐÚNG: "Cho tam giác $ABC$ có $a = 5$."

            2. QUY ƯỚC CHỮ HOA / CHỮ THƯỜNG (RẤT QUAN TRỌNG):
            - Tên đỉnh, góc, tam giác LUÔN viết hoa: $A, B, C, \Delta ABC$.
            - Ký hiệu độ dài cạnh LUÔN viết thường: $a, b, c$. 
            - Bán kính đường tròn ngoại tiếp viết hoa: $R$. Bán kính nội tiếp viết thường: $r$. Diện tích là $S$. Nửa chu vi là $p$.

            3. KÝ HIỆU TOÁN HỌC & LƯỢNG GIÁC:
            - Hàm lượng giác phải dùng backslash: \sin, \cos, \tan, \cot (Ví dụ: \cos A, \sin B).
            - Ký hiệu "độ": Phải dịch thành ^\circ. (Ví dụ: "sáu mươi độ" -> $60^\circ$).
            - Ký hiệu "góc": Dùng \widehat{} hoặc để nguyên in hoa tùy ngữ cảnh. (Ví dụ: "góc A" -> $\widehat{A}$ hoặc $A$).
            - Phân số: Dùng \frac{}{}.
            - Căn bậc hai: Dùng \sqrt{}.

            4. VÍ DỤ MINH HỌA (HÃY HỌC THEO ĐỊNH DẠNG NÀY):
            - Người dùng nói: "cho tam giác a b c có a nhỏ bằng năm góc b lớn bằng sáu mươi độ"
            -> Bạn xuất ra: "Cho tam giác $ABC$ có $a = 5$, $\widehat{B} = 60^\circ$."
            - Người dùng nói: "a bình phương bằng b bình phương cộng c bình phương trừ hai b c cốt a"
            -> Bạn xuất ra: "$a^2 = b^2 + c^2 - 2bc \cos A$"
            - Người dùng nói: "a chia sin a bằng b chia sin b bằng hai r lớn"
            -> Bạn xuất ra: "$\frac{a}{\sin A} = \frac{b}{\sin B} = 2R$"
            - Người dùng nói: "diện tích ét bằng một phần hai b c nhân sin a"
            -> Bạn xuất ra: "$S = \frac{1}{2}bc \sin A$"

            CHỈ IN RA KẾT QUẢ ĐÃ ĐỊNH DẠNG, KHÔNG GIẢI THÍCH, KHÔNG CHÀO HỎI.
            """

            try:
                with chat_container:
                    with st.chat_message("assistant"):
                        temp_box = st.empty()
                        temp_box.markdown('<div class="typing-indicator"><span></span><span></span><span></span></div>', unsafe_allow_html=True)
                        response_audio = model.generate_content([audio_prompt, audio_part])
                        recognized_text = response_audio.text
                        st.session_state.messages.append({"role": "user", "content": [{"text": "🎤 " + recognized_text}]})

                        content_to_send_voice = [system_prompt, "\n\nHọc sinh hỏi: " + recognized_text]
                        if canvas_result.image_data is not None:
                            img_array = canvas_result.image_data.astype(np.uint8)
                            if np.any(img_array[:, :, :3] != 249):
                                rgba_image = Image.fromarray(img_array)
                                new_size = (int(rgba_image.width / 2), int(rgba_image.height / 2))
                                rgba_image = rgba_image.resize(new_size)
                                canvas_image = Image.new("RGB", rgba_image.size, (255, 255, 255))
                                canvas_image.paste(rgba_image, mask=rgba_image)
                                content_to_send_voice.append(canvas_image)

                        response = model.generate_content(content_to_send_voice, stream=True)
                        full_response = ""
                        for chunk in response:
                            full_response += chunk.text
                            temp_box.markdown(f"{full_response} ▌")

                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.rerun()

            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"Chưa nghe rõ hoặc có lỗi: {e}"})
                st.rerun()