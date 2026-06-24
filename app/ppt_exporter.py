from __future__ import annotations

from pathlib import Path

from app.models import SlideContent


def _ensure_resolution_setting() -> None:
    """设置 PowerPoint 导出图片分辨率为 1920x1080 (对应 96dpi)."""
    import winreg

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Office\12.0\PowerPoint\Options",
            0,
            winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, "ExportBitmapResolution", 0, winreg.REG_DWORD, 192)
        winreg.CloseKey(key)
    except OSError:
        pass  # 注册表不可写或路径不存在，使用默认分辨率


def export_slides_to_images(
    pptx_path: Path,
    slides: list[SlideContent],
    output_dir: Path,
) -> list[Path]:
    """
    将 PPT 的每一页导出为 PNG 图片。

    Args:
        pptx_path: .pptx 文件路径
        slides: parse_pptx 返回的 SlideContent 列表（用于获取 index）
        output_dir: 输出目录

    Returns:
        按 SlideContent 顺序排列的 PNG 文件路径列表
    """
    if not pptx_path.exists():
        raise FileNotFoundError(f"PPT 文件不存在：{pptx_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    # 尝试注册表设置使导出图片更清晰
    _ensure_resolution_setting()

    import win32com.client
    import pythoncom
    pythoncom.CoInitialize()

    powerpoint = win32com.client.Dispatch("PowerPoint.Application")

    try:
        presentation = powerpoint.Presentations.Open(
            str(pptx_path.resolve()), WithWindow=False
        )

        image_paths: list[Path] = []
        for slide in slides:
            image_path = output_dir / f"slide_{slide.index:03d}.png"
            slide_object = presentation.Slides(slide.index)
            slide_object.Export(str(image_path), "PNG")
            if not image_path.exists():
                raise RuntimeError(
                    f"第 {slide.index} 页导出失败：未生成文件"
                )
            image_paths.append(image_path)

        return image_paths
    finally:
        try:
            presentation.Close()
        except Exception:
            pass
        try:
            powerpoint.Quit()
        except Exception:
            pass
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass
