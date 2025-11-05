from transformers import Qwen3VLForConditionalGeneration, AutoProcessor
from PIL import Image
import torch
import os
import gradio as gr
import io

print("Qwen3-VL-2Bモデルを読み込んでいます...")

# モデルとプロセッサーの読み込み
model_name = "Qwen/Qwen3-VL-2B-Instruct"
processor = AutoProcessor.from_pretrained(model_name)
model = Qwen3VLForConditionalGeneration.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
    device_map="auto"
)

# デバイス確認
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"モデル読み込み完了 (デバイス: {device})")
print(f"モデル: {model_name}")

def process_image_ocr(image):
    """
    Qwen3-VLを使用して画像からテキストを抽出
    """
    if image is None:
        return "エラー: 画像がアップロードされていません"

    try:
        # PIL Imageを一時ファイルとして保存してパスを取得
        # （Qwen3-VLはファイルパスまたはURLを受け取る）
        temp_path = "/tmp/temp_ocr_image.png"
        image.save(temp_path)

        # OCR用のメッセージを構築
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": temp_path,
                    },
                    {
                        "type": "text",
                        "text": "この画像に含まれるすべてのテキストを正確に抽出してください。テキストのみを出力し、説明は不要です。"
                    },
                ],
            }
        ]

        # プロンプトを準備
        text_prompt = processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # 画像とテキストを処理
        inputs = processor(
            text=[text_prompt],
            images=[Image.open(temp_path)],
            padding=True,
            return_tensors="pt"
        )
        inputs = inputs.to(model.device)

        # 推論実行
        with torch.no_grad():
            generated_ids = model.generate(
                **inputs,
                max_new_tokens=512,
                do_sample=False
            )

        # 入力部分を除去してデコード
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]

        output_text = processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0]

        # 一時ファイルを削除
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return output_text.strip()

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
with gr.Blocks(title="Qwen3-VL OCR - Text Recognition Tool", head=get_adsense_script()) as demo:
    # トップバナー広告
    if get_adsense_top():
        gr.HTML(get_adsense_top())

    gr.Markdown(
        """
        # Qwen3-VL OCR - 高精度テキスト認識ツール

        Qwen3-VL-2Bを使用した最新の光学文字認識（OCR）ツールです。
        32言語対応、低照度・傾き・ぼかしにも強い高精度なテキスト抽出が可能です。
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
        - 日本語、英語、中国語など32言語に対応
        - 低照度・ぼかし・傾きがある画像でも高精度

        ### 特徴
        - 稀な文字・専門用語にも対応
        - 長文書の構造解析が可能
        - 印刷文字・手書き文字両方に対応
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
