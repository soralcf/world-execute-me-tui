# Copyright / attribution / licensing

这是 Mili《world.execute(me);》的非官方、非商业同人可视化源码项目。与 Mili、DeepSeek 和下列创作者没有从属或合作关系，未经他们认可。**本项目由 AI 辅助编程制作，含 AI 生成的角色美术**；“代码渲染”不表示所有画面均为非 AI 内容。

## 代码与时间数据：MIT

- 本仓库的原创 Python 动画、排版、音频分析和构建代码：Copyright (c) 2026 soralcf，MIT，见 [LICENSE](LICENSE)。
- 视觉构思参考 [MisakaZentai/world-execute-me-dsh-pv](https://github.com/MisakaZentai/world-execute-me-dsh-pv)，取用版本 `cb63fb6ba5832da38d79f95b8469464c1e2ddbf4`。开场连续镜头和完整影片的 TUI 分屏概念均受其启发；后续镜头在本项目重新编写。
- `tools/reference_lyrics.py` 从该项目 `tools/lyrics.py` 原样取用；`data/timing/*_notext.json` 是该项目去除歌词原文后的时间及核对数据。Copyright (c) 2026 MisakaZentai，MIT，见 [LICENSES/reference-MIT.txt](LICENSES/reference-MIT.txt)。不含文本的时间数据许可不覆盖歌词。

## 鲸鱼娘立绘与表情：CC BY-NC-SA 4.0

范围：`assets/whale/whale-*.webp`（八种表情），以及由其生成的角色裁切、像素头像、字符肖像和含相应角色图像的衍生画面。按参考项目及上游保留的声明使用，署名链完整保留如下：

1. **角色原作：溟月 © 上善无形 / Shangshan Wuxing**：[Pixiv](https://www.pixiv.net/users/62155430)、[Bilibili](https://space.bilibili.com/4456176)。
2. **女仆版设计：ZipZipPipe**：[Pixiv](https://www.pixiv.net/users/18604994)、[Bilibili](https://space.bilibili.com/4168597)，[AI 娘化原帖](https://www.pixiv.net/artworks/148186519)。
3. **立绘：Small-tailqwq / dsh-deep-whale**：[上游项目](https://github.com/Small-tailqwq/dsh-deep-whale)。
4. **八种表情：JAdpp / dsh-whale-galgame**：[上游项目](https://github.com/JAdpp/dsh-whale-galgame)、[上游 NOTICE](https://github.com/JAdpp/dsh-whale-galgame/blob/main/NOTICE.md)。
5. **参考仓库中的素材整理：MisakaZentai**：[参考项目](https://github.com/MisakaZentai/world-execute-me-dsh-pv)。

本项目改动：上半身和头部裁切、缩放、像素化、表情切换、镜像、字符点阵采样、终端合成、扫描线与微弱辉光。原始 WebP 素材保留不变。

角色素材及其改编部分按 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 分享：保留署名、许可链接与改动说明，非商业，改编部分相同方式共享。**MIT 不适用于这些美术及其衍生画面**。许可全文见 [LICENSES/CC-BY-NC-SA-4.0.txt](LICENSES/CC-BY-NC-SA-4.0.txt)，上游原文见同目录 `upstream-*`、`galgame-NOTICE.md`。`REFERENCE_UPSTREAM_NOTICE.md` 是完整上游记录，其中提及的 MMD、前端和其他字体并未因此进入本项目。

## 字体：SIL Open Font License 1.1

- `assets/fonts/SpaceMono-Bold.ttf`：Space Mono，Copyright 2016 The Space Mono Project Authors。作为跨平台备用字体，见 [LICENSES/OFL_spacemono.txt](LICENSES/OFL_spacemono.txt)。
- macOS 默认调用本机 Menlo，不分发 Menlo 或其他系统字体。可用 `PV_FONT` 指定自有字体。

## 音乐与歌词：权利归 Mili / 相应权利人

音乐及歌词：**Mili — world.execute(me);**。音频、用户的原始 MP4、下载或自备的完整歌词、含完整歌词的本地时间轴、字幕与带音乐成片均不提交到公开仓库，也不适用 MIT、CC 美术许可或 OFL。这里没有对歌曲或歌词的开源再许可。

[Mili 官方版权指引](https://projectmili.com/copyright-guidelines)（2026-10-01 查看）允许个人非营利、非商业二创；商业或营利用途应按指引另行办理。全部或部分用 AI 创作的同人内容须明确标注 AI 生成；不得暗示官方作品或认可。视频使用持续的 AI 标识、结尾署名和容器元数据，分享时仍应在发布说明中保留本声明与完整素材署名。

歌词可按用户明确运行的命令从 LRCLIB 下载到本机；来源为 [LRCLIB 条目 36914646](https://lrclib.net/api/get/36914646)。API 可访问性不构成对歌词的开源授权。

## 未使用或未分发的内容

未使用参考项目的视频帧、原片 MMD 模型/动作、舞蹈缓存、DeepSeek 前端 bundle、浏览器截图或标识。DeepSeek、Mili 等名称和商标的权利不由本项目许可授予。
