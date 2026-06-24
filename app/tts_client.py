from __future__ import annotations

import asyncio
import os
import subprocess
from pathlib import Path
from typing import Protocol, Sequence

from dotenv import load_dotenv

from app.models import SlideScript


VOICE_OPTIONS: dict[str, str] = {
    "zh-CN-XiaoxiaoNeural": "晓晓 - 女声",
    "zh-CN-YunxiNeural": "云希 - 男声",
}

WINDOWS_VOICE_OPTIONS: dict[str, str] = {
    "Microsoft Huihui Desktop": "慧慧 - 女声（Windows 本机）",
}


class TTSClientProtocol(Protocol):
    file_extension: str

    async def synthesize_to_file(self, text: str, voice: str, output_path: Path) -> None:
        ...


class EdgeTTSClient:
    file_extension = "mp3"

    async def synthesize_to_file(self, text: str, voice: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.unlink(missing_ok=True)

        last_error = ""
        for _ in range(3):
            output_path.unlink(missing_ok=True)
            result = await asyncio.to_thread(
                subprocess.run,
                [
                    "edge-tts",
                    "--voice",
                    voice,
                    "--text",
                    " ".join(text.split()),
                    "--write-media",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
            )
            last_error = result.stderr.strip()
            if output_path.exists() and output_path.stat().st_size > 0:
                return

        raise RuntimeError(last_error or "edge-tts 未生成有效音频文件。")


class WindowsSapiTTSClient:
    file_extension = "wav"

    async def synthesize_to_file(self, text: str, voice: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.unlink(missing_ok=True)
        command = _build_windows_sapi_command(text, voice, output_path.resolve())
        result = await asyncio.to_thread(
            subprocess.run,
            ["powershell.exe", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Windows 系统语音生成失败。")
        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError("Windows 系统语音未生成有效音频文件。")


async def generate_audio_files(
    scripts: Sequence[SlideScript],
    voice: str,
    output_dir: Path,
    tts_client: TTSClientProtocol,
) -> list[Path]:
    if not scripts:
        raise ValueError("没有可生成语音的讲稿。")
    if voice not in VOICE_OPTIONS and voice not in WINDOWS_VOICE_OPTIONS and voice not in AZURE_VOICE_OPTIONS and voice not in MINIMAX_VOICE_OPTIONS and voice not in VOLC_ENGINE_VOICE_OPTIONS:
        raise ValueError(f"未知语音：{voice}")

    output_dir.mkdir(parents=True, exist_ok=True)
    audio_paths: list[Path] = []

    for script in scripts:
        output_path = output_dir / f"slide_{script.slide_index:03d}.{tts_client.file_extension}"
        await tts_client.synthesize_to_file(script.script, voice, output_path)
        audio_paths.append(output_path)

    return audio_paths


def _ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _build_windows_sapi_command(text: str, voice: str, output_path: Path) -> str:
    normalized_text = " ".join(text.split())
    return "\n".join(
        [
            "Add-Type -AssemblyName System.Speech",
            "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer",
            f"$synth.SelectVoice({_ps_quote(voice)})",
            f"$synth.SetOutputToWaveFile({_ps_quote(str(output_path))})",
            f"$synth.Speak({_ps_quote(normalized_text)}) | Out-Null",
            "$synth.Dispose()",
        ]
    )


AZURE_VOICE_OPTIONS: dict[str, str] = {
    "zh-CN-XiaoxiaoNeural": "晓晓 - 女声",
    "zh-CN-YunxiNeural": "云希 - 男声",
    "zh-CN-YunjianNeural": "云健 - 男声",
    "zh-CN-XiaoyiNeural": "晓伊 - 女声",
    "zh-CN-YunyangNeural": "云扬 - 男声",
    "zh-CN-XiaochenNeural": "晓辰 - 女声",
    "zh-CN-XiaohanNeural": "晓涵 - 女声",
    "zh-CN-XiaomengNeural": "晓梦 - 女声",
    "zh-CN-XiaomoNeural": "晓墨 - 女声",
    "zh-CN-XiaoqiuNeural": "晓秋 - 女声",
    "zh-CN-XiaoruiNeural": "晓瑞 - 女声",
    "zh-CN-XiaoshuangNeural": "晓双 - 女声",
    "zh-CN-XiaoyanNeural": "晓颜 - 女声",
    "zh-CN-XiaoyouNeural": "晓悠 - 女声",
    "zh-CN-YunxiNeural": "云希 - 男声",
    "zh-CN-YunyangNeural": "云扬 - 男声",
    "zh-CN-YunyeNeural": "云野 - 男声",
    "zh-CN-YunzeNeural": "云泽 - 男声",
}


class AzureTTSClient:
    """Azure Cognitive Services 语音合成客户端。

    环境变量：
        AZURE_SPEECH_KEY: Azure Speech 资源的 Key
        AZURE_SPEECH_REGION: 区域，例如 eastasia、chinaeast2
    """
    file_extension = "wav"

    async def synthesize_to_file(self, text: str, voice: str, output_path: Path) -> None:
        import azure.cognitiveservices.speech as speechsdk

        speech_key = os.getenv("AZURE_SPEECH_KEY", "").strip()
        service_region = os.getenv("AZURE_SPEECH_REGION", "").strip()
        if not speech_key or not service_region:
            raise ValueError(
                "请配置 AZURE_SPEECH_KEY 和 AZURE_SPEECH_REGION 环境变量。"
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.unlink(missing_ok=True)

        config = speechsdk.SpeechConfig(
            subscription=speech_key,
            region=service_region,
        )
        config.speech_synthesis_voice_name = voice

        audio_config = speechsdk.audio.AudioOutputConfig(
            filename=str(output_path)
        )
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=config,
            audio_config=audio_config,
        )

        result = synthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return

        cancellation = result.cancellation_details
        if cancellation:
            raise RuntimeError(
                f"Azure TTS 失败：{cancellation.reason}"
                + (f"：{cancellation.error_details}" if cancellation.error_details else "")
            )
        raise RuntimeError("Azure TTS 失败，原因未知。")


MINIMAX_VOICE_OPTIONS: dict[str, str] = {
    "male-qn-jingying": "精英青年 - 男声（沉稳汇报）",
    "Chinese (Mandarin)_Humorous_Elder": "幽默大叔 - 男声（年长、有辨识度）",
    "Chinese (Mandarin)_Radio_Host": "电台男主播 - 男声（成熟稳重）",
    "Chinese (Mandarin)_Gentleman": "温润绅士 - 男声（成熟温和）",
    "presenter_male": "男性主持人 - 男声（正式清晰）",
    "audiobook_male_1": "男性有声书 1 - 男声（稳重叙述）",
    "audiobook_male_2": "男性有声书 2 - 男声（成熟叙述）",
    "male-qn-qingse": "青瑟 - 男声（自然青年）",
    "male-qn-badao": "霸道青年 - 男声（有力量）",
    "female-chengshu": "成熟女性 - 女声（稳重）",
    "presenter_female": "女性主持人 - 女声（正式清晰）",
    "audiobook_female_1": "女性有声书 1 - 女声（稳重叙述）",
    "female-yujie": "御姐 - 女声（成熟）",
    "female-tianmei": "甜美 - 女声",
    "female-shaonv": "少女 - 女声",
}



VOLC_ENGINE_VOICE_OPTIONS: dict[str, str] = {
    # 以下音色来自火山引擎方舟音色库（seed-tts-2.0 模型）
    # 实际可用音色以控制台 > 音色库 为准，可在 .env 中通过 VOLC_SPEAKER 覆盖
    "zh_female_zhijia": "知家 - 亲切女声",
    "zh_female_mengmeng": "萌萌 - 可爱女声",
    "zh_female_xiaowan": "晓婉 - 温柔女声",
    "zh_female_xiaomei": "晓梅 - 知性女声",
    "zh_male_zhiming": "志明 - 稳重男声",
    "zh_male_xiaoyong": "晓勇 - 阳光男声",
    "zh_male_xiaogang": "晓刚 - 成熟男声",
}

class MiniMaxTTSClient:
    """MiniMax TTS 语音合成客户端（T2A V2 API）。

    环境变量：
        MINIMAX_API_KEY: MiniMax API Key
        MINIMAX_GROUP_ID: MiniMax Group ID
    """
    file_extension = "wav"

    async def synthesize_to_file(self, text: str, voice: str, output_path: Path) -> None:
        load_dotenv(override=True)
        api_key = os.getenv("MINIMAX_API_KEY", "").strip()
        group_id = os.getenv("MINIMAX_GROUP_ID", "").strip()
        if not api_key:
            raise ValueError("请配置 MINIMAX_API_KEY 环境变量。")
        if not group_id:
            raise ValueError("请配置 MINIMAX_GROUP_ID 环境变量。")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.unlink(missing_ok=True)

        import httpx

        base_url = os.getenv("MINIMAX_API_BASE_URL", "https://api.minimax.chat").rstrip("/")
        url = f"{base_url}/v1/t2a_v2"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept-Encoding": "identity",
        }

        payload = {
            "model": "speech-2.8-hd",
            "text": " ".join(text.split()),
            "voice_setting": {
                "voice_id": voice,
                "speed": 1.0,
                "pitch": 0,
                "vol": 1.0,
                "latex_read": False,
            },
            "audio_setting": {
                "format": "wav",
                "sample_rate": 32000,
                "bitrate": 128000,
                "channel": 1,
            },
            "language_boost": "auto",
            "stream": False,
            "output_format": "hex",
        }

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url, headers=headers, json=payload)
            data = resp.json()

        base_resp = data.get("base_resp", {})
        if base_resp.get("status_code", 0) != 0:
            raise RuntimeError(
                f"MiniMax TTS 失败（code {base_resp.get('status_code')}）："
                f"{base_resp.get('status_msg', '未知错误')}"
            )

        audio_hex = data.get("data", {}).get("audio")
        if not audio_hex:
            raise RuntimeError("MiniMax TTS did not return audio data.")

        try:
            audio_bytes = bytes.fromhex(audio_hex)
        except ValueError as exc:
            raise RuntimeError("MiniMax TTS returned audio is not valid hex.") from exc

        output_path.write_bytes(audio_bytes)

        if output_path.stat().st_size == 0:
            raise RuntimeError("MiniMax TTS 未生成有效音频文件。")



class VolcengineTTSClient:
    """火山引擎方舟平台 TTS 语音合成客户端。

    使用 X-Api-App-Key + X-Api-Access-Key + X-Api-Resource-Id 鉴权。
    音色 ID 需从 火山引擎控制台 > 方舟 > 音色库 获取。

    环境变量：
        VOLC_ENGINE_API_KEY: 语音技术 Access Token
        VOLC_ENGINE_APP_ID: 语音技术 App ID
        VOLC_ENGINE_RESOURCE_ID: 方舟推理接入点 endpoint ID（默认 seed-tts-2.0）
        VOLC_ENGINE_BASE_URL: API 基础地址（默认 https://openspeech.bytedance.com）
    """
    file_extension = "wav"

    async def synthesize_to_file(self, text: str, voice: str, output_path: Path) -> None:
        load_dotenv(override=True)
        access_token = os.getenv("VOLC_ENGINE_API_KEY", "").strip()
        app_id = os.getenv("VOLC_ENGINE_APP_ID", "").strip()
        resource_id = os.getenv("VOLC_ENGINE_RESOURCE_ID", "seed-tts-2.0").strip()
        base_url = os.getenv("VOLC_ENGINE_BASE_URL", "https://openspeech.bytedance.com").rstrip("/")

        if not access_token:
            raise ValueError("请配置 VOLC_ENGINE_API_KEY（Access Token）环境变量。")
        if not app_id:
            raise ValueError("请配置 VOLC_ENGINE_APP_ID（App ID）环境变量。")

        import httpx
        import uuid

        uid = str(uuid.uuid4())[:12]
        url = f"{base_url}/api/v3/tts/unidirectional"
        headers = {
            "X-Api-App-Key": app_id,
            "X-Api-Access-Key": access_token,
            "X-Api-Resource-Id": resource_id,
            "Content-Type": "application/json",
        }
        payload = {
            "app": {"appid": app_id, "token": access_token, "cluster": "volcano_tts"},
            "user": {"uid": uid},
            "audio": {
                "voice_type": voice,
                "encoding": "wav",
                "speed_ratio": 1.0,
                "volume_ratio": 1.0,
                "pitch_ratio": 1.0,
            },
            "request": {
                "reqid": uid,
                "text": " ".join(text.split()),
                "text_type": "plain",
                "operation": "query",
            },
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.unlink(missing_ok=True)

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url, headers=headers, json=payload)
            content_type = resp.headers.get("content-type", "")

            if resp.status_code != 200:
                raise RuntimeError(
                    f"火山引擎 TTS 请求失败（HTTP {resp.status_code}）：{resp.text[:200]}"
                )

            if "audio" in content_type.lower():
                output_path.write_bytes(resp.content)
            else:
                error_body = resp.text[:300]
                raise RuntimeError(
                    f"火山引擎 TTS 返回非音频响应（{content_type}）：{error_body}"
                )

        if output_path.stat().st_size == 0:
            raise RuntimeError("火山引擎 TTS 未生成有效音频文件。")
