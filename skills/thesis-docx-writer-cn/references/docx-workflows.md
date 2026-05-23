# DOCX 处理工作流

## 工具选择

1. 读取正文：优先 `pandoc --track-changes=all`；没有 pandoc 时用 `python-docx`。
2. 创建新文档：优先 Node `docx`；缺失时用 `python-docx`。
3. 精确编辑：解包 `.docx` 为 OOXML，修改 `word/document.xml`、样式、关系文件后重新打包。
4. 视觉检查：优先 `soffice --headless --convert-to pdf` 转 PDF，再用 `pdftoppm` 转图片。
5. 安全解析：读取 XML 时优先使用 `defusedxml` 或 `lxml` 的安全解析方式。

## 读取和分析

1. 先确认文件路径、是否为副本、是否有修订或批注。
2. 运行依赖检查。
3. 提取文本：
   - 有 pandoc：`pandoc --track-changes=all input.docx -o output.md`
   - 无 pandoc：使用脚本提取段落和表格文本。
4. 检查模板样式：
   - 标题样式。
   - 正文样式。
   - 图表题注样式。
   - 页边距、页眉页脚。
   - 表格数量和图片关系。

## 编辑现有文档

1. 修改前复制备份。
2. 简单正文替换可用 `python-docx`，但要注意它可能改变局部 run 结构。
3. 精确保留格式时，解包 OOXML 后定位文本节点修改。
4. 修改图片、目录、页眉页脚、批注、修订时，优先 OOXML。
5. 修改后重新打包，再提取文本验证。

## 修订与批注

1. 学术、商业、政府、法律或他人文档默认采用备份或修订工作流。
2. 修订标记需要直接操作 WordprocessingML，例如插入、删除和批注节点。
3. 只标记真正变化的文本，不重复标记未修改内容。
4. 批注要写明修改依据，不写空泛意见。

## 转换为 PDF 或图片

1. DOCX 转 PDF：
   - `soffice --headless --convert-to pdf --outdir out input.docx`
2. PDF 转图片：
   - `pdftoppm -jpeg -r 150 input.pdf page`
3. 缺少 `soffice` 或 `pdftoppm` 时，不要声称已完成视觉检查。

## 常见风险

1. `python-docx` 对复杂修订、批注、域代码和目录支持有限。
2. 直接替换 XML 文本可能破坏命名空间或关系文件。
3. 重新打包时不能把外层目录打进 zip 根目录，必须打包目录内部内容。
4. Word 自动目录可能需要用户打开 Word 后更新域。
5. 转换工具不同会导致分页略有差异，应以学校模板和 Word 打开效果为准。
