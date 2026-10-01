# 自备歌曲与歌词

把合法取得的歌曲放到此目录，例如 `song.mp4` 或 `song.m4a`。不要提交音频或完整歌词到仓库。这里的文件默认被 Git 忽略。

歌词时间基于 LRCLIB 条目 36914646；可以自备对应 LRC，或明确运行：

```sh
python tools/reference_lyrics.py fetch
python tools/prepare.py
```

下载到本机的歌词不因下载而变成开源内容。公开仓库只存不含文字的逐词时间和用于核对的哈希。
