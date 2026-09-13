#!/usr/bin/env python3
"""
BEA AI 图像分析模块
调用多模态大模型识别图像视觉元素，映射为 BEA 极性强度
"""

import base64
import json
import time
import requests
from typing import Dict, Any, Optional
import config
from bea_engine import BEAEngine, generate_mock_result


# ============ BEA 分析 Prompt ============
BEA_ANALYSIS_PROMPT = """你是一位专业的美学分析师，精通「双极情绪美学（BEA）」理论。

BEA 理论核心：
- 亲极 P+（趋近/安全/愉悦）：圆润、柔色、光滑、舒缓、对称、留白、稳定
- 危极 T−（警觉/唤醒/畏惧）：尖锐、强对比、坚硬、突变、失衡、拥挤、冷峻
- 美感 = 可控张力下的情绪奖赏，双极在秩序中组合且危极在安全阈值内

请分析这张图片，从以下6个维度评估每个维度的极性方向和强度（0-10）：

1. shape（形状线条）：曲线/圆角/对称=亲极(P)，锐角/折线/失衡=危极(T)
2. color（色彩色相）：柔暖/低饱和/邻近色=亲极(P)，极端冷/高饱和/撞色=危极(T)
3. brightness（明度对比）：高明度/柔和过渡=亲极(P)，极低明度/硬交界/强反差=危极(T)
4. texture（质感肌理）：光滑/柔软/温润=亲极(P)，粗糙/坚硬/冰冷/毛刺=危极(T)
5. composition（构图空间）：居中/留白/稳定=亲极(P)，偏移/拥挤/失重=危极(T)
6. light（光影）：漫射柔光/均匀受光=亲极(P)，硬光/顶光/长投影=危极(T)

每个维度需要输出：
- direction: "P"（亲极主导）/ "T"（危极主导）/ "mixed"（混合均衡）
- intensity: 0-10 的整数，表示该维度极性的强度
- description: 一句话描述该维度的具体视觉特征（中文，不超过20字）

请严格按照以下 JSON 格式返回，不要返回其他内容：
{
  "shape": {"direction": "P/T/mixed", "intensity": 0-10, "description": "..."},
  "color": {"direction": "P/T/mixed", "intensity": 0-10, "description": "..."},
  "brightness": {"direction": "P/T/mixed", "intensity": 0-10, "description": "..."},
  "texture": {"direction": "P/T/mixed", "intensity": 0-10, "description": "..."},
  "composition": {"direction": "P/T/mixed", "intensity": 0-10, "description": "..."},
  "light": {"direction": "P/T/mixed", "intensity": 0-10, "description": "..."}
}"""


class AIAnalyzer:
    """AI 图像分析器"""

    def __init__(self):
        self.engine = BEAEngine()
        self.mock_mode = config.MOCK_MODE

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        分析图片，返回完整 BEA 分析结果

        Args:
            image_path: 图片文件路径

        Returns:
            完整 BEA 分析结果
        """
        start_time = time.time()

        if self.mock_mode:
            # 模拟模式：返回模拟数据
            time.sleep(1.5)  # 模拟分析延迟
            result = generate_mock_result()
            result["analysis_time"] = round(time.time() - start_time, 2)
            result["mock"] = True
            return result

        # 1. 图片转 base64
        image_base64 = self._image_to_base64(image_path)

        # 2. 调用 AI 模型识别极性
        polarities = self._call_ai_model(image_base64)

        # 3. BEA 计算引擎分析
        result = self.engine.analyze(polarities)

        # 4. 添加元信息
        result["analysis_time"] = round(time.time() - start_time, 2)
        result["mock"] = False
        result["ai_provider"] = config.AI_PROVIDER

        return result

    def _image_to_base64(self, image_path: str) -> str:
        """图片转 base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _call_ai_model(self, image_base64: str) -> Dict[str, Any]:
        """调用多模态大模型"""
        if config.AI_PROVIDER == "doubao":
            return self._call_doubao(image_base64)
        elif config.AI_PROVIDER == "openai":
            return self._call_openai(image_base64)
        else:
            raise ValueError(f"不支持的 AI 提供商: {config.AI_PROVIDER}")

    def _call_doubao(self, image_base64: str) -> Dict[str, Any]:
        """调用豆包视觉模型"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.DOUBAO_API_KEY}",
        }

        payload = {
            "model": config.DOUBAO_MODEL_ID,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": BEA_ANALYSIS_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                        },
                    ],
                }
            ],
            "temperature": 0.3,
            "max_tokens": 2000,
        }

        try:
            response = requests.post(
                config.DOUBAO_API_URL,
                headers=headers,
                json=payload,
                timeout=config.ANALYSIS_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()

            # 解析返回内容
            content = data["choices"][0]["message"]["content"]
            return self._parse_ai_response(content)

        except Exception as e:
            print(f"豆包 API 调用失败: {e}")
            # 失败时返回模拟数据
            return self._get_fallback_polarities()

    def _call_openai(self, image_base64: str) -> Dict[str, Any]:
        """调用 OpenAI GPT-4V"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.OPENAI_API_KEY}",
        }

        payload = {
            "model": config.OPENAI_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": BEA_ANALYSIS_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                        },
                    ],
                }
            ],
            "temperature": 0.3,
            "max_tokens": 2000,
        }

        try:
            response = requests.post(
                config.OPENAI_API_URL,
                headers=headers,
                json=payload,
                timeout=config.ANALYSIS_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()

            content = data["choices"][0]["message"]["content"]
            return self._parse_ai_response(content)

        except Exception as e:
            print(f"OpenAI API 调用失败: {e}")
            return self._get_fallback_polarities()

    def _parse_ai_response(self, content: str) -> Dict[str, Any]:
        """解析 AI 返回的 JSON"""
        try:
            # 尝试直接解析 JSON
            # 去除可能的 markdown 代码块标记
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            data = json.loads(content)

            # 验证并规范化数据
            required_dims = ["shape", "color", "brightness", "texture", "composition", "light"]
            result = {}

            for dim in required_dims:
                if dim in data:
                    d = data[dim]
                    direction = d.get("direction", "mixed")
                    if direction not in ["P", "T", "mixed"]:
                        direction = "mixed"
                    intensity = max(0, min(10, int(d.get("intensity", 5))))
                    description = d.get("description", "")[:50]
                    result[dim] = {
                        "direction": direction,
                        "intensity": intensity,
                        "description": description,
                    }
                else:
                    result[dim] = {"direction": "mixed", "intensity": 5, "description": ""}

            return result

        except json.JSONDecodeError as e:
            print(f"AI 返回 JSON 解析失败: {e}")
            print(f"原始内容: {content[:200]}")
            return self._get_fallback_polarities()

    def _get_fallback_polarities(self) -> Dict[str, Any]:
        """获取备用极性数据（AI 调用失败时使用）"""
        return {
            "shape": {"direction": "mixed", "intensity": 5, "description": "曲直结合，比例均衡"},
            "color": {"direction": "P", "intensity": 4, "description": "柔和暖调，低饱和"},
            "brightness": {"direction": "mixed", "intensity": 5, "description": "明暗适中，过渡自然"},
            "texture": {"direction": "P", "intensity": 4, "description": "光滑细腻，质感温润"},
            "composition": {"direction": "P", "intensity": 4, "description": "居中稳定，留白合理"},
            "light": {"direction": "mixed", "intensity": 5, "description": "柔光为主，局部提神"},
        }


if __name__ == "__main__":
    # 测试
    import sys
    if len(sys.argv) > 1:
        analyzer = AIAnalyzer()
        result = analyzer.analyze_image(sys.argv[1])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("用法: python ai_analyzer.py <image_path>")
