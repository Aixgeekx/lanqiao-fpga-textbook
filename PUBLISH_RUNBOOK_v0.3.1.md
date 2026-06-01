# v0.3.1 发布执行手册

用途：shell 恢复后，按固定顺序生成 PDF、打 ZIP、推送 GitHub 并创建 Release。

## 1. 发布前状态检查

```powershell
git status --short
git log --oneline -5
```

期望结果：

- 工作树干净，或只有本次发布明确需要提交的文件。
- 最新提交包含 `feat: show total pages in textbook footer` 和 `docs: prepare v0.3.1 release notes`。

## 2. 生成教材 PDF

```powershell
python -m py_compile scripts/generate_textbook_v3.py
python scripts/generate_textbook_v3.py
```

期望结果：

- `results/蓝桥杯FPGA开发教程_详细注释版.pdf` 重新生成成功。
- 控制台输出第一遍构建的章节页码和总页数。
- 正式 PDF 页脚显示“当前页 / 总页数”。

## 3. 人工与脚本校验

```powershell
python scripts/validate_release_v0_3_1.py --skip-zip
```

脚本会检查 PDF 页数、可抽取文字长度、核心知识点关键词、页脚“当前页 / 总页数”、Obsidian 教程文件和发布说明文件。

也可以临时执行下面的最小抽查脚本：

```powershell
@'
from pathlib import Path
from pypdf import PdfReader
p = Path('results/蓝桥杯FPGA开发教程_详细注释版.pdf')
r = PdfReader(str(p))
text = '\n'.join(page.extract_text() or '' for page in r.pages)
needles = ['I2C', 'UART', 'SPI', '状态机', '按键消抖', '亚稳态', 'DS1302', 'W25Q128']
print('pages=', len(r.pages))
print('chars=', len(text))
print('missing=', [x for x in needles if x not in text])
'@ | python -
```

人工抽查：

- 封面、目录、前言、每章首页、真题页、附录页。
- 代码块是否溢出，扫描题面是否裁切，表格是否断页严重。
- 目录页码与正文页脚是否一致。

## 4. 生成 ZIP 包

建议使用 ASCII 文件名，避免 GitHub Release 资产名规整中文。

```powershell
$releaseFiles = @(
  'README.md',
  '蓝桥杯FPGA竞赛教程_Obsidian版.md',
  'CHANGELOG.md',
  'RELEASE_NOTES_v0.3.1.md',
  'PRINT_QA_v0.3.1.md',
  'PUBLISH_RUNBOOK_v0.3.1.md',
  'scripts',
  'Aix_tools',
  'results'
)
Compress-Archive -Force -Path $releaseFiles -DestinationPath results/lanqiao-fpga-textbook-v0.3.1.zip
```

打包后执行完整校验：

```powershell
python scripts/validate_release_v0_3_1.py
```

## 5. 推送 GitHub

```powershell
git status --short
git push origin main
```

## 6. 创建 GitHub Release

```powershell
gh release create v0.3.1 `
  results/lanqiao-fpga-textbook-v0.3.1.zip `
  results/蓝桥杯FPGA开发教程_详细注释版.pdf `
  --title "v0.3.1 纸质赛场手册可用性增强版" `
  --notes-file RELEASE_NOTES_v0.3.1.md
```

发布后检查：

- Release 页面存在 v0.3.1。
- ZIP 和 PDF 资产能下载。
- README 中的当前版本、页数、下载链接与实际 Release 一致。
