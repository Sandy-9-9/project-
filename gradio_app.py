import gradio as gr
import os
import shutil
import subprocess
from PIL import Image

BASE_DIR = os.getcwd()
INPUT_DIR = "inputs/test"
OUTPUT_DIR = "output/output"

def clean_dirs():
    if os.path.exists("inputs"):
        shutil.rmtree("inputs")
    if os.path.exists("output"):
        shutil.rmtree("output")

    os.makedirs(f"{INPUT_DIR}/cloth", exist_ok=True)
    os.makedirs(f"{INPUT_DIR}/image", exist_ok=True)
    os.makedirs(f"{INPUT_DIR}/image-parse", exist_ok=True)
    os.makedirs(f"{INPUT_DIR}/openpose-img", exist_ok=True)
    os.makedirs(f"{INPUT_DIR}/openpose-json", exist_ok=True)
    os.makedirs(f"{INPUT_DIR}/cloth-mask", exist_ok=True)


def run_pipeline(cloth_img, model_img):
    clean_dirs()

    cloth_path = f"{INPUT_DIR}/cloth/cloth.jpg"
    model_path = f"{INPUT_DIR}/image/model.jpg"

    cloth_img.save(cloth_path)
    model_img.save(model_path)

    try:
        # 1️⃣ Resize cloth
        subprocess.run(["python", "run.py"], check=True)

        # 2️⃣ Cloth segmentation
        subprocess.run(["python", "cloth-mask.py"], check=True)

        # 3️⃣ Remove background
        subprocess.run(["python", "remove_bg.py"], check=True)

        # 4️⃣ Human parsing
        subprocess.run([
            "python",
            "Self-Correction-Human-Parsing/simple_extractor.py",
            "--dataset", "lip",
            "--model-restore", "Self-Correction-Human-Parsing/checkpoints/final.pth",
            "--input-dir", f"{INPUT_DIR}/image",
            "--output-dir", f"{INPUT_DIR}/image-parse"
        ], check=True)

        # 5️⃣ OpenPose
        subprocess.run([
            "openpose/build/examples/openpose/openpose.bin",
            "--image_dir", f"{INPUT_DIR}/image",
            "--write_json", f"{INPUT_DIR}/openpose-json",
            "--write_images", f"{INPUT_DIR}/openpose-img",
            "--display", "0",
            "--render_pose", "1",
            "--disable_blending", "true"
        ], check=True)

        # 6️⃣ Generate pairs
        with open(f"{INPUT_DIR}_pairs.txt", "w") as f:
            f.write("model.jpg cloth.jpg")

        # 7️⃣ Final try-on
        subprocess.run([
            "python", "test.py",
            "--name", "output",
            "--dataset_dir", "inputs",
            "--checkpoint_dir", "checkpoints",
            "--save_dir", "output"
        ], check=True)

        result_img = os.listdir(OUTPUT_DIR)[0]
        return Image.open(os.path.join(OUTPUT_DIR, result_img))

    except Exception as e:
        return f"Error: {str(e)}"


# 🟢 GRADIO UI
with gr.Blocks(title="Virtual Cloth Assistant") as demo:
    gr.Markdown("## 👕 AI-Powered Virtual Try-On System")
    gr.Markdown("Upload a cloth image and a person image to see the try-on result.")

    with gr.Row():
        cloth_input = gr.Image(label="Cloth Image", type="pil")
        model_input = gr.Image(label="Model Image", type="pil")

    run_btn = gr.Button("Try It 👗", variant="primary")
    output_img = gr.Image(label="Result")

    run_btn.click(
        fn=run_pipeline,
        inputs=[cloth_input, model_input],
        outputs=output_img
    )

demo.launch(server_name="0.0.0.0", server_port=7860)
