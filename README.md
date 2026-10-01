# world.execute(me); — a code-rendered TUI fan visual

用 Python、Pillow 和 NumPy 逐帧生成的完整音乐可视化：左侧角色会话，右侧不断变化的字符世界，底部逐词英文歌词。默认输出 **1920×1080、30fps、H.264/AAC MP4**，长度取自用户自备歌曲；本次完整版本约 3 分 32 秒。

**非官方、非商业同人作品；由 AI 辅助编程制作，含 AI 生成的角色美术。** 音乐与歌词：Mili《world.execute(me);》。本仓库提供源码、可复用美术及不含歌词文字的时间数据，音频、完整歌词和带音乐成片需在本机生成。

![无歌词的视觉预览](docs/visual-preview.jpg)

视觉和连续镜头深度参考 [MisakaZentai/world-execute-me-dsh-pv](https://github.com/MisakaZentai/world-execute-me-dsh-pv)。鲸鱼娘角色、美术及表情保留完整创作链；详见 [NOTICE.md](NOTICE.md)。

## 快速运行

需要 Python **3.9–3.12**、FFmpeg（含 ffprobe）。Python 依赖用项目虚拟环境和版本固定的 `requirements.txt` 管理；FFmpeg 是独立系统工具。优先复用本机已有工具。

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
# 把自备歌曲放在 input/song.mp4，或在 --audio 指定其他路径。
# 明确下载歌词到本机；也可以自备对应版本的 input/lyrics.lrc。
python tools/reference_lyrics.py fetch
python tools/prepare.py
python render.py --audio input/song.mp4 --output out/world_execute_full.mp4 --srt out/captions.srt
```

`--audio` 支持 MP4、M4A、MP3、WAV 等 FFmpeg 可解码格式。歌词由参考项目的哈希和字跨度核对，不匹配的版本会报错，避免静默错位。按用户提供的歌词，将点集的 `point` 修正为 `points`，将第一段副歌对应词修正为 `STIMULATIONS`；保留原逐词时间。

仓库只发布不含歌词原文的时间数据；本地 `input/`、`local/`、`out/` 和歌词重建中间目录均被 Git 忽略。不要使用 `git add -f` 上传歌曲、完整歌词、字幕或带音乐成片。

仅预览分镜，或先生成开头 30 秒：

```sh
python render.py --audio input/song.mp4 --frames-only --sheet out/storyboard.jpg --poster out/poster.png
python render.py --audio input/song.mp4 --duration 30 --output out/preview.mp4
```

`--offset` 将歌词和镜头时钟平移；它不裁掉音频片头。如果音频有额外片头，应先裁成与参考时间轴相同的歌曲起点。默认时序对应原曲约 211.9 秒版本，本地 AAC 容器可能有少量尾部时长差异。

macOS 使用本机 Menlo；其他系统使用仓库附带的 Space Mono（OFL）。`PV_FONT=/path/to/font.ttf` 可覆盖字体。字体与编码器版本可能造成输出外观或码流差异。

## 完整视觉叙事

- 开机：防护边界 → 权重碎片 → 实体与会话 → 配置 → 分布 → 世界。
- 训练：词元流 → 损失 / 学习率 → 八路流水线 → 字符鲸鱼检查点。
- 几何：肖像点集、圆与半径、正弦与切线、无限曲线及极限。
- 电流与结合：AC / DC、信号遮蔽、失衡方向、时间拨盘、两个信号融合。
- 供养与身份：心形网络、模拟边界、茄子 / 番茄 / 猫、存在见证、身份和角色切换。
- 失联：波形共振、完整的两半、断开的对应方、记忆擦除、破碎心形、非法参数。
- 执行：递归窗口、12 次声乐执行脉冲、多语言计数、无法返回的执行牢笼。
- 爱与结尾：学习、问答、代数表达式、你在边界外而我仍被困住，最终结束并署名。

表情、聊天状态、缺席的对应方和波形随歌曲时间变化。图形为时间的确定性函数；音频 RMS 和波形控制局部运动。对话、参数和训练数值是叙事用虚构内容。

## 代码与验证

`render.py`：全曲分镜、合成、字幕导出和 FFmpeg 编码。`opening.py`：开场连续镜头。`terminal.py`：TUI 与逐词排版。`audio.py`：PCM / RMS / FFT。`tools/prepare.py`：本机歌词重建。`data/timing/`：不含文字的参考时间。

```sh
python -m unittest discover -s tests -v
python tools/check_public.py
```

检查所有镜头的起点、中段、转场，结尾淡出和字幕时长裁切；不依赖音乐或歌词原文。首次完整导出的实际检查记录见 [docs/VALIDATION.md](docs/VALIDATION.md)。

## 版权

| 内容 | 许可 / 权利 |
| --- | --- |
| 本项目代码 | MIT，Copyright 2026 soralcf |
| 参考歌词工具、无文字时间数据 | MIT，Copyright 2026 MisakaZentai |
| 鲸鱼娘立绘、八种表情和相应衍生画面 | CC BY-NC-SA 4.0；完整署名链见 NOTICE |
| Space Mono 备用字体 | SIL OFL 1.1 |
| Mili 音乐、歌词 | 权利归相应权利人；不随仓库分发、不适用代码或美术许可 |

分享成片时保留非官方和 AI 标识、音乐署名、角色完整署名、CC 许可链接和修改说明，并按 [Mili 官方指引](https://projectmili.com/copyright-guidelines)处理非商业或商业用途。详情见 [NOTICE.md](NOTICE.md) 和 `LICENSES/`。
