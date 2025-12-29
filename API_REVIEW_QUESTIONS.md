# ❓ Câu Hỏi Làm Rõ Requirement

Trước khi review chi tiết, tôi cần làm rõ một số điểm:

## 1. API `/process_document_submission`

**Câu hỏi:**
- "So sánh các trường" nghĩa là gì?
  - A. Parse Excel/PDF thành structured data (JSON/dict) rồi so sánh từng field? đúng rồi
  - B. Chỉ dùng OCR để extract text rồi so sánh text? đúng nhưng mà nó ko phải so sánh giống y hệt vì các files khác nhau template
  - C. So sánh visual (image comparison)? và chỉ ra trường sai khác
  
- Input là 2 files (Excel hoặc PDF) - có phải:
  - 2 files cùng loại (Excel vs Excel, PDF vs PDF)? ko. lộn xộn. nhiều files khác nhau về định dạng + template nhưng biểu diễn 1 trường 
  - Hay 2 files khác loại (Excel vs PDF)?
  - Hay nhiều files trong 1 task_id? nhiều

## 2. API `/compare_document_contents`

**Câu hỏi:**
- Bạn có **bắt buộc** dùng LLM để compare không?
  - Hiện tại code chỉ dùng OCR text comparison (difflib)
  - LLM sẽ dùng để làm gì? (semantic comparison, field extraction, etc.) bắt buộc dùng llm để ocr
  
- Output mong muốn:
  - Chỉ similarity score?
  - Hay chi tiết từng field khác nhau? đúng
  - Hay structured diff (field-by-field comparison)?

## 3. Storage & Processing Flow

**Câu hỏi:**
- Có cần download files về local filesystem (`/tmp/documents`) không? tùy. nếu có giải pháp tốt hơn thì mời bạn 
  - Hay process trực tiếp từ MinIO (streaming)? dùng minio nếu streaming tốt hơn thì hãy code giúp tôi
  - Hay có thể dùng temporary storage khác? tùy vào giải pháp của bạn

- Files sau khi process có cần lưu lại không?có
  - Converted PDFs? ko cần convert
  - Images? ko
  - OCR results? có 

---

**Vui lòng trả lời để tôi có thể đưa ra review và solutions chính xác!**

