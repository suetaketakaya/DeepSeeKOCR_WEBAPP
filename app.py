from transformers import AutoModel, AutoTokenizer, LlamaTokenizer
import torch
import os
import gradio as gr
from pathlib import Path

# Fastトークナイザーを無効化（tokenizer.json互換性問題の回避）
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

# ローカルモデル保存先
LOCAL_MODEL_DIR = './models/deepseek-ocr'
model_name = 'deepseek-ai/DeepSeek-OCR'

# CPU環境用のモデル変換関数
def convert_model_to_float32(model):
    """モデル全体をfloat32に変換（全てのサブモジュールを含む、ただし整数型は除く）"""
    bf16_params = []
    # named_parametersを使って全てのパラメータを取得（サブモジュール含む）
    for name, param in model.named_parameters():
        if param.dtype == torch.bfloat16:
            bf16_params.append(name)
            param.data = param.data.to(torch.float32)

    bf16_buffers = []
    int_buffers_protected = []
    # named_buffersを使って全てのバッファを取得（サブモジュール含む）
    for name, buffer in model.named_buffers():
        # 整数型バッファは変換しない
        if buffer.dtype in [torch.int32, torch.int64, torch.long, torch.int, torch.int8, torch.int16, torch.uint8, torch.bool]:
            int_buffers_protected.append(name)
            continue
        if buffer.dtype == torch.bfloat16:
            bf16_buffers.append(name)
            buffer.data = buffer.data.to(torch.float32)

    # すべてのモジュールのパラメータをfloat32に変換（手動で、整数型を保護しながら）
    for module in model.modules():
        for param in module.parameters(recurse=False):
            if param.dtype == torch.bfloat16:
                param.data = param.data.to(torch.float32)

    if bf16_params:
        print(f"bfloat16パラメータを変換しました: {len(bf16_params)}個")
    if bf16_buffers:
        print(f"bfloat16バッファを変換しました: {len(bf16_buffers)}個")
    if int_buffers_protected:
        print(f"整数型バッファを保護しました: {len(int_buffers_protected)}個")

# CUDA設定
# os.environ["CUDA_VISIBLE_DEVICES"] = '0'

print("モデルを読み込んでいます...")

# ローカルモデルの確認
model_exists = os.path.exists(f'{LOCAL_MODEL_DIR}/config.json')

if model_exists:
    print(f"ローカルモデルを読み込んでいます: {LOCAL_MODEL_DIR}")

    # デバッグ: ファイル構造を確認
    import os
    print(f"モデルディレクトリの内容:")
    for file in os.listdir(LOCAL_MODEL_DIR):
        file_path = os.path.join(LOCAL_MODEL_DIR, file)
        print(f"  - {file} ({os.path.getsize(file_path)} bytes)")

    try:
        print("AutoTokenizer.from_pretrained を試行中...")
        tokenizer = AutoTokenizer.from_pretrained(
            LOCAL_MODEL_DIR,
            trust_remote_code=True,
            use_fast=False
        )
        print("AutoTokenizer の読み込みに成功しました")
    except Exception as e:
        print(f"AutoTokenizer でエラー発生: {type(e).__name__}: {e}")
        print(f"LlamaTokenizer を試行中...")

        # vocab_fileを明示的に指定
        import os
        vocab_file = os.path.join(LOCAL_MODEL_DIR, "tokenizer.model")
        print(f"vocab_file パス: {vocab_file}")
        print(f"vocab_file 存在確認: {os.path.exists(vocab_file)}")
        print(f"vocab_file タイプ: {type(vocab_file)}")

        try:
            tokenizer = LlamaTokenizer.from_pretrained(
                LOCAL_MODEL_DIR,
                trust_remote_code=True,
                vocab_file=vocab_file if os.path.exists(vocab_file) else None
            )
            print("LlamaTokenizer の読み込みに成功しました")
        except Exception as e2:
            print(f"LlamaTokenizer でもエラー発生: {type(e2).__name__}: {e2}")
            raise
    model = AutoModel.from_pretrained(
        LOCAL_MODEL_DIR,
        trust_remote_code=True,
        use_safetensors=True,
        torch_dtype=torch.float32 if not torch.cuda.is_available() else torch.bfloat16
    )
else:
    print(f"Hugging Faceからモデルをダウンロードしています: {model_name}")
    try:
        print("AutoTokenizer.from_pretrained を試行中...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
            use_fast=False
        )
        print("AutoTokenizer の読み込みに成功しました")
    except Exception as e:
        print(f"AutoTokenizer でエラー発生: {type(e).__name__}: {e}")
        print(f"LlamaTokenizer を試行中...")

        try:
            tokenizer = LlamaTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )
            print("LlamaTokenizer の読み込みに成功しました")
        except Exception as e2:
            print(f"LlamaTokenizer でもエラー発生: {type(e2).__name__}: {e2}")
            raise
    model = AutoModel.from_pretrained(
        model_name,
        trust_remote_code=True,
        use_safetensors=True,
        torch_dtype=torch.float32 if not torch.cuda.is_available() else torch.bfloat16
    )
    
    print("モデルをローカルに保存しています...")
    os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)
    tokenizer.save_pretrained(LOCAL_MODEL_DIR)
    # CPU環境ではfloat32で保存
    if not torch.cuda.is_available():
        model = model.to(torch.float32)
        for param in model.parameters():
            if param.dtype != torch.float32:
                param.data = param.data.to(torch.float32)
    model.save_pretrained(LOCAL_MODEL_DIR, safe_serialization=True)

# モデルを準備
if torch.cuda.is_available():
    try:
        model = model.eval().cuda().to(torch.bfloat16)
        device_info = "GPU"
    except:
        # CPU環境ではすべてfloat32に確実に変換
        model = model.eval()
        convert_model_to_float32(model)
        device_info = "CPU (CUDA利用不可)"
else:
    # CPU環境ではすべてfloat32に確実に変換
    model = model.eval()
    convert_model_to_float32(model)
    device_info = "CPU"

print(f"モデル読み込み完了 (デバイス: {device_info})")

# CPU環境で動作するようにモンキーパッチを適用
if not torch.cuda.is_available():
    print("CPU環境を検出しました。CPU互換モードを有効化します...")

    # .cuda()をパッチ
    original_cuda = torch.Tensor.cuda
    def patched_cuda(self, *args, **kwargs):
        # CPU環境では常にfloat32に変換してから返す
        if self.dtype == torch.bfloat16:
            return self.float()
        return self
    torch.Tensor.cuda = patched_cuda

    # .to()メソッドをパッチしてbfloat16への変換を防ぐ
    original_to = torch.Tensor.to
    def patched_to(self, *args, **kwargs):
        # 引数を解析
        if len(args) > 0:
            # dtype指定がある場合（浮動小数点型のみ変換）
            if isinstance(args[0], torch.dtype) and args[0] == torch.bfloat16:
                # 整数型テンソルはそのまま、浮動小数点型のみfloat32に変換
                if not self.dtype.is_floating_point:
                    return original_to(self, *args, **kwargs)
                args = (torch.float32,) + args[1:]
        if 'dtype' in kwargs and kwargs['dtype'] == torch.bfloat16:
            # 整数型テンソルはそのまま、浮動小数点型のみfloat32に変換
            if not self.dtype.is_floating_point:
                return original_to(self, *args, **kwargs)
            kwargs['dtype'] = torch.float32
        return original_to(self, *args, **kwargs)
    torch.Tensor.to = patched_to

    # torch.autocastをパッチ
    from contextlib import contextmanager
    original_autocast = torch.autocast

    @contextmanager
    def patched_autocast(device_type="cuda", enabled=True, dtype=None, **kwargs):
        # CPU環境ではautocastを完全にスキップ
        if device_type == "cuda" or not enabled:
            # CUDAデバイスまたはenabledがFalseの場合は何もしない
            yield
        else:
            # その他の場合（CPUでenabledがTrue）も何もしない
            yield

    torch.autocast = patched_autocast

    print("CPU互換パッチを適用しました")

def process_image_gradio(image, task, crop_mode):
    """
    Gradio用の画像処理関数
    """
    if image is None:
        return "エラー: 画像がアップロードされていません", None

    # 一時ファイルとして画像を保存
    temp_image = "./temp_input_image.png"

    try:
        # PIL Imageをファイルとして保存
        if image.mode == 'RGBA':
            # RGBA画像はRGBに変換してから保存
            rgb_image = image.convert('RGB')
            rgb_image.save(temp_image, 'PNG')
        else:
            image.save(temp_image, 'PNG')

        print(f"画像を保存しました: {temp_image}")

        # タスクに応じたプロンプトを設定
        if task == "Markdown":
            prompt = "<image>\n<|grounding|>Convert the document to markdown. "
        else:
            prompt = "<image>\nFree OCR. "

        # 出力ディレクトリ
        output_path = './output'
        os.makedirs(output_path, exist_ok=True)

        print(f"画像処理を開始します... タスク: {task}, クロップ: {crop_mode}")

        # モデルを再度float32に変換（infer内部で動的に作成される可能性があるため）
        if not torch.cuda.is_available():
            convert_model_to_float32(model)
            # sam_modelや他のサブモジュールも明示的に変換
            for name, module in model.named_modules():
                if hasattr(module, 'sam_model') and module.sam_model is not None:
                    convert_model_to_float32(module.sam_model)
                if hasattr(module, 'clip_model') and module.clip_model is not None:
                    convert_model_to_float32(module.clip_model)

        # 処理の実行（CPUモード対応）
        res = model.infer(
            tokenizer,
            prompt=prompt,
            image_file=temp_image,
            output_path=output_path,
            base_size=1024,
            image_size=640,
            crop_mode=(crop_mode == "有効"),
            save_results=True,
            test_compress=True
        )

        # 保存されたファイルから結果を読み込む
        result_file = os.path.join(output_path, 'result.mmd')
        result_image = os.path.join(output_path, 'result_with_boxes.jpg')

        result_text = ""
        result_img = None

        # テキスト結果を読み込み
        if os.path.exists(result_file):
            with open(result_file, 'r', encoding='utf-8') as f:
                result_text = f.read()
            print(f"結果を読み込みました: {result_file}")
        else:
            result_text = "結果ファイルが見つかりませんでした。"

        # バウンディングボックス付き画像を読み込み
        if os.path.exists(result_image):
            result_img = result_image
            print(f"結果画像を読み込みました: {result_image}")

        print("処理が完了しました")
        return result_text, result_img

    except Exception as e:
        import traceback
        error_msg = f"エラーが発生しました: {str(e)}\n\n詳細:\n{traceback.format_exc()}"
        print(error_msg)
        return error_msg, None
    finally:
        # 一時ファイルのクリーンアップ
        if os.path.exists(temp_image):
            try:
                os.remove(temp_image)
            except:
                pass

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
with gr.Blocks(title="DeepSeek-OCR Chat Tool", head=get_adsense_script()) as demo:
    # トップバナー広告
    if get_adsense_top():
        gr.HTML(get_adsense_top())

    gr.Markdown(
        """
        # DeepSeek-OCR チャットツール

        画像をアップロードして、OCR処理またはMarkdown変換を行います。
        """
    )

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(
                type="pil",
                label="画像をアップロード"
            )

            task_radio = gr.Radio(
                choices=["OCR", "Markdown"],
                value="OCR",
                label="処理タイプ"
            )

            crop_mode_radio = gr.Radio(
                choices=["有効", "無効"],
                value="有効",
                label="クロップモード"
            )

            submit_btn = gr.Button("処理実行", variant="primary")

        with gr.Column():
            output_text = gr.Textbox(
                label="OCR結果テキスト",
                lines=15,
                max_lines=30,
                placeholder="結果がここに表示されます...",
                show_copy_button=True
            )

            output_image = gr.Image(
                label="検出結果（バウンディングボックス付き）",
                type="filepath"
            )

    gr.Markdown(
        """
        ### 使い方
        1. 画像をアップロード
        2. 処理タイプを選択（OCRまたはMarkdown）
        3. クロップモードを設定
        4. 「処理実行」ボタンをクリック
        5. 結果がWeb上に表示され、`./output` ディレクトリにも保存されます

        ### 出力ファイル
        - `output/result.mmd`: OCR結果のテキスト
        - `output/result_with_boxes.jpg`: バウンディングボックス付き画像
        - `output/images/`: 抽出された画像（ある場合）
        """
    )

    submit_btn.click(
        fn=process_image_gradio,
        inputs=[image_input, task_radio, crop_mode_radio],
        outputs=[output_text, output_image]
    )

    # ボトムバナー広告
    if get_adsense_bottom():
        gr.HTML(get_adsense_bottom())

if __name__ == "__main__":
    # Cloud Run環境ではPORT環境変数を使用
    port = int(os.environ.get("PORT", 7860))
    demo.launch(share=False, server_name="0.0.0.0", server_port=port)

