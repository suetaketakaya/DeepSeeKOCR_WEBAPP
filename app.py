from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import torch
import os
import gradio as gr

print("TrOCRモデルを読み込んでいます...")

# モデルとプロセッサーの読み込み
model_name = "microsoft/trocr-large-printed"
processor = TrOCRProcessor.from_pretrained(model_name)
model = VisionEncoderDecoderModel.from_pretrained(model_name)

# デバイス設定
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
model.eval()

print(f"モデル読み込み完了 (デバイス: {device})")
print(f"モデルサイズ: {model_name}")

def process_image_ocr(image):
    """
    TrOCRを使用して画像からテキストを抽出
    """
    if image is None:
        return "エラー: 画像がアップロードされていません"

    try:
        # PIL Imageをそのまま使用（Gradioから受け取る）
        pixel_values = processor(images=image, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(device)

        # 推論実行
        with torch.no_grad():
            generated_ids = model.generate(pixel_values)

        # デコード
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return generated_text

    except Exception as e:
        import traceback
        error_msg = f"エラーが発生しました: {str(e)}\n\n詳細:\n{traceback.format_exc()}"
        print(error_msg)
        return error_msg

# Google AdSense設定（環境変数から取得）
ADSENSE_CLIENT_ID = os.environ.get("ADSENSE_CLIENT_ID", "")
ADSENSE_SLOT_TOP = os.environ.get("ADSENSE_SLOT_TOP", "")
ADSENSE_SLOT_BOTTOM = os.environ.get("ADSENSE_SLOT_BOTTOM", "")

# AdSense広告HTML（設定されている場合のみ表示）
def get_adsense_top():
    if ADSENSE_CLIENT_ID and ADSENSE_SLOT_TOP:
        return f"""
        <div class="adsense-banner-top" style="text-align: center; margin: 20px 0;">
          <ins class="adsbygoogle"
               style="display:block"
               data-ad-client="ca-pub-{ADSENSE_CLIENT_ID}"
               data-ad-slot="{ADSENSE_SLOT_TOP}"
               data-ad-format="auto"
               data-full-width-responsive="true"></ins>
          <script>
               (adsbygoogle = window.adsbygoogle || []).push({{}});
          </script>
        </div>
        """
    return ""

def get_adsense_bottom():
    if ADSENSE_CLIENT_ID and ADSENSE_SLOT_BOTTOM:
        return f"""
        <div class="adsense-banner-bottom" style="text-align: center; margin: 20px 0;">
          <ins class="adsbygoogle"
               style="display:block"
               data-ad-client="ca-pub-{ADSENSE_CLIENT_ID}"
               data-ad-slot="{ADSENSE_SLOT_BOTTOM}"
               data-ad-format="auto"
               data-full-width-responsive="true"></ins>
          <script>
               (adsbygoogle = window.adsbygoogle || []).push({{}});
          </script>
        </div>
        """
    return ""

def get_adsense_script():
    if ADSENSE_CLIENT_ID:
        return f"""
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-{ADSENSE_CLIENT_ID}"
             crossorigin="anonymous"></script>
        """
    return ""

# Gradioインターフェースの作成
with gr.Blocks(title="TrOCR - Text Recognition Tool", head=get_adsense_script()) as demo:
    # トップバナー広告
    if get_adsense_top():
        gr.HTML(get_adsense_top())

    gr.Markdown(
        """
        # TrOCR - テキスト認識ツール

        Microsoft TrOCRを使用した高精度な光学文字認識（OCR）ツールです。
        画像をアップロードして、テキストを抽出できます。
        """
    )

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(
                type="pil",
                label="画像をアップロード"
            )

            submit_btn = gr.Button("テキスト抽出", variant="primary")

        with gr.Column():
            output_text = gr.Textbox(
                label="抽出されたテキスト",
                lines=15,
                max_lines=30,
                placeholder="結果がここに表示されます...",
                show_copy_button=True
            )

    gr.Markdown(
        """
        ### 使い方
        1. 画像をアップロード（PNG, JPG, etc.）
        2. 「テキスト抽出」ボタンをクリック
        3. 抽出されたテキストが表示されます

        ### 対応言語
        - 英語（印刷文字）
        - その他のラテン文字系言語

        ### 注意事項
        - 手書き文字の認識精度は印刷文字より低くなります
        - 画像は明瞭で、テキストが読みやすいものを使用してください
        - 複数行のテキストも認識可能です
        """
    )

    submit_btn.click(
        fn=process_image_ocr,
        inputs=[image_input],
        outputs=[output_text]
    )

    # ボトムバナー広告
    if get_adsense_bottom():
        gr.HTML(get_adsense_bottom())

if __name__ == "__main__":
    # Cloud Run環境ではPORT環境変数を使用
    port = int(os.environ.get("PORT", 7860))
    demo.launch(share=False, server_name="0.0.0.0", server_port=port)
