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

# Google Analytics設定（環境変数から取得）
GA_MEASUREMENT_ID = os.environ.get("GA_MEASUREMENT_ID", "G-01HQFFXE17")

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

def get_favicon():
    """ファビコン設定"""
    # SVGをdata URIとして埋め込み
    favicon_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64"><rect width="64" height="64" fill="%232563eb" rx="8"/><rect x="14" y="12" width="36" height="40" fill="white" rx="2"/><rect x="18" y="18" width="20" height="3" fill="%232563eb" rx="1"/><rect x="18" y="24" width="28" height="3" fill="%232563eb" rx="1"/><rect x="18" y="30" width="24" height="3" fill="%232563eb" rx="1"/><rect x="18" y="36" width="26" height="3" fill="%232563eb" rx="1"/><line x1="12" y1="28" x2="52" y2="28" stroke="%2360a5fa" stroke-width="2" opacity="0.7"/><circle cx="48" cy="44" r="6" fill="none" stroke="%2310b981" stroke-width="2.5"/><line x1="52" y1="48" x2="56" y2="52" stroke="%2310b981" stroke-width="2.5" stroke-linecap="round"/></svg>'''

    return f'''
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,{favicon_svg}">
    <link rel="apple-touch-icon" href="data:image/svg+xml,{favicon_svg}">
    '''

def get_seo_meta_tags():
    """SEO最適化用メタタグ"""
    site_url = "https://deepseekocr-9a570.web.app"
    return f"""
    <!-- SEO Meta Tags -->
    <meta name="description" content="無料のAI OCRツール。Qwen3-VL技術で画像から高精度にテキストを抽出。32言語対応、日本語・英語・中国語など多言語の文字認識が可能。オンラインで簡単にテキスト変換。">
    <meta name="keywords" content="OCR,画像からテキスト抽出,文字認識,無料OCRツール,AI文字認識,オンラインOCR,日本語OCR,画像テキスト化,Qwen3-VL,テキスト抽出ツール">
    <meta name="author" content="Qwen3-VL OCR">
    <meta name="robots" content="index, follow">
    <meta name="language" content="Japanese">

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{site_url}">
    <meta property="og:title" content="無料OCRツール - 画像からテキスト抽出 | AI文字認識">
    <meta property="og:description" content="Qwen3-VL技術で画像から高精度にテキストを抽出。32言語対応の無料オンラインOCRツール。">
    <meta property="og:image" content="{site_url}/favicon.svg">

    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="{site_url}">
    <meta property="twitter:title" content="無料OCRツール - 画像からテキスト抽出 | AI文字認識">
    <meta property="twitter:description" content="Qwen3-VL技術で画像から高精度にテキストを抽出。32言語対応の無料オンラインOCRツール。">
    <meta property="twitter:image" content="{site_url}/favicon.svg">

    <!-- JSON-LD 構造化データ -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "WebApplication",
      "name": "Qwen3-VL OCR - 画像からテキスト抽出",
      "description": "無料のAI OCRツール。画像から高精度にテキストを抽出。32言語対応。",
      "url": "{site_url}",
      "applicationCategory": "UtilityApplication",
      "operatingSystem": "Any",
      "offers": {{
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "JPY"
      }},
      "featureList": "OCR, 画像文字認識, 多言語対応, AI技術, 無料"
    }}
    </script>
    """

def get_analytics_script():
    """Google Analyticsトラッキングコード"""
    if GA_MEASUREMENT_ID:
        return f"""
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());
          gtag('config', '{GA_MEASUREMENT_ID}');
        </script>
        """
    return ""

def get_adsense_script():
    if ADSENSE_CLIENT_ID:
        return f"""
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-{ADSENSE_CLIENT_ID}"
             crossorigin="anonymous"></script>
        """
    return ""

def get_head_scripts():
    """すべてのヘッダースクリプトとメタタグを結合"""
    return get_favicon() + get_seo_meta_tags() + get_analytics_script() + get_adsense_script()

# Gradioインターフェースの作成
with gr.Blocks(
    title="無料OCRツール - 画像からテキスト抽出 | AI文字認識 Qwen3-VL",
    head=get_head_scripts()
) as demo:
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
