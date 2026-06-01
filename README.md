# 蓝桥杯 FPGA 竞赛教材

作者：Aix，极道工作室  
定位：零基础教学教程 · 赛场纸质速查手册 · Obsidian 复习资料 · 出版预备稿

## 当前交付物

- `results/蓝桥杯FPGA开发教程_详细注释版.pdf`：完整教材 PDF，适合打印、装订和赛场查阅。
- `蓝桥杯FPGA竞赛教程_Obsidian版.md`：Obsidian 单文件教程，适合搜索、批注和长期复习。
- `蓝桥杯FPGA真题复盘_Obsidian索引.md`：7 份真题/模拟题的复盘入口。
- `PUBLISH_RUNBOOK_v0.3.1.md`：本地生成、验证、打包流程。
- `PRINT_QA_v0.3.1.md`：纸质版和出版前校对清单。
- `scripts/validate_release_v0_3_1.py`：PDF、Markdown、ZIP 的发布验收脚本。

## 教材内容范围

本教材面向零基础读者，覆盖：

- FPGA 基础思维：时钟、复位、寄存器、组合逻辑、模块接口。
- 常用协议：I2C、UART、SPI。
- 工程方法：三段式状态机、Moore/Mealy、按键消抖、亚稳态、跨时钟域。
- 常见外设：数码管动态扫描、SRAM、DS1302 RTC、W25Q128 SPI Flash。
- 竞赛实战：第十六届省赛、三套第十六届模拟题、第十六届国赛、第十七届两套模拟题。

完整扫描题面以 PDF 为准，Obsidian 文件用于检索、复盘和个人知识库维护。

## 本地生成

```powershell
python -m py_compile scripts/generate_textbook_v3.py
python scripts/generate_textbook_v3.py
```

生成后执行：

```powershell
python scripts/validate_release_v0_3_1.py --skip-zip
```

如果需要本地 ZIP 包，按 `PUBLISH_RUNBOOK_v0.3.1.md` 中的打包步骤执行，然后运行：

```powershell
python scripts/validate_release_v0_3_1.py
```

## Obsidian 使用方式

建议把以下文件放入同一个 vault：

- `蓝桥杯FPGA竞赛教程_Obsidian版.md`
- `蓝桥杯FPGA真题复盘_Obsidian索引.md`
- `results/蓝桥杯FPGA开发教程_详细注释版.pdf`

可以在 Obsidian 笔记中嵌入 PDF：

```markdown
![[results/蓝桥杯FPGA开发教程_详细注释版.pdf]]
```

## 纸质使用建议

- 打印前检查 PDF 页脚是否显示“当前页 / 总页数”。
- 装订后用目录页码和页脚总页数检查缺页。
- 做题时先看纸质 PDF 的完整题面，再在 Obsidian 中记录复盘。
- 每次上板失败都记录“现象、原因、解决、下次避免”，不要只写笼统总结。

