"""Renderer - compiles Manim code to video."""

import subprocess
import os
import glob as glob_mod


def render_scene(
    code: str,
    output_dir: str = "output",
    quality: str = "h",  # l=low, m=medium, h=high, k=4k
    scene_name: str = "GeneratedScene",
    preview: bool = False,
) -> dict:
    """Render Manim code to video."""
    os.makedirs(output_dir, exist_ok=True)

    temp_file = os.path.join(output_dir, "scene.py")
    with open(temp_file, "w") as f:
        f.write(code)

    cmd = [
        "uv", "run", "python", "-m", "manim",
        f"-q{quality}",
        "--media_dir", output_dir,
    ]
    if preview:
        cmd.append("-p")
    cmd.extend([temp_file, scene_name])

    print(f"  Rendering: {' '.join(cmd)}")

    # Fix dvisvgm: set TEXMFDIST so brew's dvisvgm finds texlive resources
    env = os.environ.copy()
    texmf_path = "/opt/homebrew/Cellar/texlive/20260301/share/texmf-dist"
    if os.path.isdir(texmf_path):
        env["TEXMFDIST"] = texmf_path
        env["TEXMFHOME"] = texmf_path

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        env=env,
    )

    if result.returncode != 0:
        error = result.stderr

        # Enhance specific error types
        if "latex error" in error.lower() or "dvi" in error.lower():
            error = _enhance_latex_error(error, output_dir)
        elif "NameError" in error:
            error = _enhance_name_error(error)
        elif "no <bookmark mark=" in error.lower() or "bookmark" in error.lower():
            error += (
                "\n\nBOOKMARK FIX: A wait_until_bookmark() references a bookmark "
                "that doesn't exist in the voiceover text. "
                "Check that every wait_until_bookmark('X') has a matching "
                "<bookmark mark='X'/> in the voiceover text string. "
                "The bookmark names must match EXACTLY (case-sensitive)."
            )

        return {
            "success": False,
            "error": error,
            "stderr": result.stderr,
            "stdout": result.stdout,
        }

    video_path = _find_video(output_dir, quality)

    return {
        "success": True,
        "video_path": video_path,
        "stderr": result.stderr,
        "stdout": result.stdout,
    }


def _enhance_latex_error(error: str, output_dir: str) -> str:
    """Read LaTeX log files to provide better error context."""
    tex_dir = os.path.join(output_dir, "Tex")
    if not os.path.isdir(tex_dir):
        return error + "\n\nLATEX FIX HINT: Do NOT use \\text{} inside MathTex(). Use Text() for words."

    log_files = glob_mod.glob(os.path.join(tex_dir, "*.log"))
    if not log_files:
        return error + "\n\nLATEX FIX HINT: Do NOT use \\text{} inside MathTex(). Use Text() for words."

    # Read the most recent log
    latest_log = max(log_files, key=os.path.getmtime)
    try:
        with open(latest_log) as f:
            log_content = f.read()
    except Exception:
        log_content = ""

    # Also read the .tex source to see what was generated
    tex_files = glob_mod.glob(os.path.join(tex_dir, "*.tex"))
    tex_source = ""
    if tex_files:
        latest_tex = max(tex_files, key=os.path.getmtime)
        try:
            with open(latest_tex) as f:
                tex_source = f.read()
        except Exception:
            pass

    enhanced = error
    enhanced += f"\n\nLATEX LOG ({latest_log}):\n"
    # Show the relevant error lines from log
    for line in log_content.split("\n"):
        if line.startswith("!") or "error" in line.lower() or "not found" in line.lower():
            enhanced += f"  {line}\n"

    if tex_source:
        enhanced += f"\nLATEX SOURCE THAT FAILED:\n{tex_source}\n"

    enhanced += "\nLATEX FIX HINTS:\n"
    enhanced += "- Do NOT use \\text{} inside MathTex() — it requires standalone.cls\n"
    enhanced += "- Use Text('word') for English words, MathTex(r'\\pi r^2') for pure math only\n"
    enhanced += "- For mixed text+math: VGroup(Text('Area = '), MathTex(r'\\pi r^2')).arrange(RIGHT)\n"
    enhanced += "- Or just use Text() for everything if the math is simple\n"

    return enhanced


def _find_video(output_dir: str, quality: str) -> str:
    """Find the rendered video file."""
    for root, dirs, files in os.walk(output_dir):
        for f in sorted(files, reverse=True):  # newest first by name
            if f.endswith(".mp4"):
                return os.path.join(root, f)
    return ""


def _enhance_name_error(error: str) -> str:
    """Add helpful context for NameError."""
    enhanced = error
    if "ease_in" in error or "ease_out" in error or "rate_func" in error.lower():
        enhanced += (
            "\n\nRATE FUNCTION FIX: The rate_func name is wrong. "
            "In Manim, use these exact names:\n"
            "  smooth, linear, rush_into, rush_from, slow_into, there_and_back,\n"
            "  rate_functions.ease_in_sine, rate_functions.ease_out_sine,\n"
            "  rate_functions.ease_in_out_sine\n"
            "OR just use: smooth (default), linear, rush_into, rush_from\n"
            "DO NOT use: ease_in_cubic, ease_out_cubic, ease_in_out_cubic — "
            "these require importing from rate_functions.\n"
            "SIMPLEST FIX: Replace any ease_* with 'smooth'"
        )
    if "CENTER" in error:
        enhanced += "\n\nFIX: 'CENTER' is not defined in Manim. Use ORIGIN instead."
    return enhanced


def validate_code(code: str) -> dict:
    """Quick syntax check without rendering."""
    try:
        compile(code, "<generated>", "exec")
        return {"valid": True, "error": None}
    except SyntaxError as e:
        return {"valid": False, "error": str(e)}
