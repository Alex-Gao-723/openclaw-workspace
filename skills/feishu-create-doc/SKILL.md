# feishu-create-doc

创建飞书云文档。从 Lark-flavored Markdown 内容创建新的飞书云文档，支持指定创建位置（文件夹/知识库/知识空间）。

## 概述

通过 MCP 调用 `create-doc`，从 Lark-flavored Markdown 内容创建一个新的飞书云文档。

## 返回值

工具成功执行后，返回一个 JSON 对象，包含以下字段：
- **`doc_id`**（string）：文档的唯一标识符（token），格式如 `doxcnXXXXXXXXXXXXXXXXXXX`
- **`doc_url`**（string）：文档的访问链接，可直接在浏览器中打开，格式如 `https://www.feishu.cn/docx/doxcnXXXXXXXXXXXXXXXXXXX`
- **`message`**（string）：操作结果消息，如"文档创建成功"

## 参数

### markdown（必填）

文档的 Markdown 内容，使用 **Lark-flavored Markdown** 格式。

调用本工具的 markdown 内容应当尽量结构清晰,样式丰富, 有很高的可读性. 合理的使用 callout 高亮块, 分栏,表格等能力,并合理的运用插入图片与 mermaid 的能力,做到图文并茂..

**编写原则**:
- **结构清晰**：标题层级 ≤ 4 层，用 Callout 突出关键信息
- **视觉节奏**：用分割线、分栏、表格打破大段纯文字
- **图文交融**：流程和架构优先用 Mermaid/PlantUML 可视化
- **克制留白**：Callout 不过度、加粗只强调核心词

**重要提示**：
- **禁止重复标题**：markdown 内容开头不要写与 title 相同的一级标题！title 参数已经是文档标题，markdown 应直接从正文内容开始
- **目录**：飞书自动生成，无需手动添加
- Markdown 语法必须符合 Lark-flavored Markdown 规范

### title（可选）

文档标题。

### folder_token（可选）

父文件夹的 token。如果不提供，文档将创建在用户的个人空间根目录。

folder_token 可以从飞书文件夹 URL 中获取，格式如：`https://xxx.feishu.cn/drive/folder/fldcnXXXX`，其中 `fldcnXXXX` 即为 folder_token。

### wiki_node（可选）

知识库节点 token 或 URL（可选，传入则在该节点下创建文档，与 folder_token 和 wiki_space 互斥）

wiki_node 可以从飞书知识库页面 URL 中获取，格式如：`https://xxx.feishu.cn/wiki/wikcnXXXX`，其中 `wikcnXXXX` 即为 wiki_node token。

### wiki_space（可选）

知识空间 ID（可选，传入则在该空间根目录下创建文档。特殊值 `my_library` 表示用户的个人知识库。与 wiki_node 和 folder_token 互斥）

wiki_space 可以从知识空间设置页面 URL 中获取，格式如：`https://xxx.feishu.cn/wiki/settings/7448000000000009300`，其中 `7448000000000009300` 即为 wiki_space ID。

**参数优先级**：wiki_node > wiki_space > folder_token

---

## Lark-flavored Markdown 完整语法指南

### 基础块类型

#### 文本（段落）
```markdown
普通文本段落
段落中的**粗体文字**
多个段落之间用空行分隔。

居中文本 {align="center"}
右对齐文本 {align="right"}
```

#### 标题
```markdown
# 一级标题
## 二级标题
### 三级标题
#### 四级标题

# 带颜色的标题 {color="blue"}
## 红色标题 {color="red"}
# 居中标题 {align="center"}
```

**颜色值**：red, orange, yellow, green, blue, purple, gray

#### 列表
```markdown
- 无序项1
  - 无序项1.a
  - 无序项1.b
1. 有序项1
2. 有序项2
- [ ] 待办
- [x] 已完成
```

#### 引用块
```markdown
> 这是一段引用
> 可以跨多行
> 引用中支持**加粗**和*斜体*等格式
```

#### 代码块
````markdown
```python
print("Hello")
```
````

支持语言：python, javascript, go, java, sql, json, yaml, shell 等。

#### 分割线
```markdown
---
```

---

### 富文本格式

| 格式 | 语法 |
|------|------|
| 粗体 | `**粗体**` |
| 斜体 | `*斜体*` |
| 删除线 | `~~删除线~~` |
| 行内代码 | `` `代码` `` |
| 下划线 | `<u>下划线</u>` |
| 红色文字 | `<text color="red">红色</text>` |
| 黄色背景 | `<text background-color="yellow">高亮</text>` |
| 链接 | `[链接文字](https://example.com)` |
| 行内公式 | `$E = mc^2$` 或 `<equation>E = mc^2</equation>` |

---

### 高级块类型

#### 高亮块（Callout）
```html
<callout emoji="✅" background-color="light-green" border-color="green">
支持**格式化**的内容
</callout>
```

**背景色选项**：
- light-red / red
- light-blue / blue（提示 💡）
- light-green / green（成功 ✅）
- light-yellow / yellow（警告 ⚠️）
- light-orange / orange
- light-purple / purple
- pale-gray / light-gray / dark-gray

**⚠️ Callout 限制**：内部仅支持文本、标题、列表、待办、引用。不支持表格、代码块、嵌套 Callout、Grid 分栏、图片。

#### 分栏（Grid）
```html
<grid cols="2">
  <column>左栏内容</column>
  <column>右栏内容</column>
</grid>
```

**自定义宽度**：
```html
<grid cols="3">
  <column width="20">左栏(20%)</column>
  <column width="60">中栏(60%)</column>
  <column width="20">右栏(20%)</column>
</grid>
```

#### 表格

**标准 Markdown 表格**：
```markdown
| 列 1 | 列 2 | 列 3 |
|------|------|------|
| A | B | C |
| D | E | F |
```

**飞书增强表格**（支持复杂内容）：
```html
<lark-table column-widths="200,250,280" header-row="true">
  <lark-tr>
    <lark-td>
      **表头1**
    </lark-td>
    <lark-td>
      **表头2**
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      内容1
    </lark-td>
    <lark-td>
      内容2
    </lark-td>
  </lark-tr>
</lark-table>
```

#### 图片
```html
<image url="https://example.com/image.png" width="800" height="600" align="center" caption="图片描述"/>
```

**⚠️ 重要**：只支持 URL 方式，系统会自动下载并上传到飞书。

#### 文件
```html
<file url="https://example.com/document.pdf" name="文档.pdf" view-type="1"/>
```

#### 画板（Mermaid / PlantUML 图表）

**Mermaid 流程图**（推荐）：
````markdown
```mermaid
graph TD
  A[开始] --> B{判断}
  B -->|是| C[处理]
  B -->|否| D[结束]
```
````

**支持图表类型**：flowchart, sequenceDiagram, classDiagram, stateDiagram, gantt, mindmap, erDiagram, pie, timeline

**PlantUML**：
````markdown
```plantuml
@startuml
Alice -> Bob: Hello
Bob --> Alice: Hi!
@enduml
```
````

---

### 181种画板图表库（顶级咨询公司模板）

#### 战略分析类

**波士顿矩阵 (BCG Matrix)**：
````markdown
```mermaid
graph LR
subgraph 高市场增长率
  A[明星业务<br/>高增长-高份额]
  B[问题业务<br/>高增长-低份额]
end
subgraph 低市场增长率
  C[现金牛业务<br/>低增长-高份额]
  D[瘦狗业务<br/>低增长-低份额]
end
```
````

**SWOT分析**：
````markdown
```mermaid
graph TD
subgraph 内部因素
  S[优势 Strengths]
  W[劣势 Weaknesses]
end
subgraph 外部因素
  O[机会 Opportunities]
  T[威胁 Threats]
end
S --> SO[SO战略]
S --> ST[ST战略]
W --> WO[WO战略]
W --> WT[WT战略]
```
````

**安索夫矩阵**：
````markdown
```mermaid
graph LR
subgraph 现有产品
  A[市场渗透]
  B[市场开发]
end
subgraph 新产品
  C[产品开发]
  D[多元化]
end
```
````

#### 流程建模类

**SIPOC模型**：
````markdown
```mermaid
graph LR
S[供应商<br/>Supplier] --> I[输入<br/>Input]
I --> P[流程<br/>Process]
P --> O[输出<br/>Output]
O --> C[客户<br/>Customer]
```
````

**PDCA循环**：
````markdown
```mermaid
graph TD
P[计划 Plan] --> D[执行 Do]
D --> C[检查 Check]
C --> A[行动 Act]
A --> P
```
````

#### 组织管理类

**麦肯锡7S模型**：
````markdown
```mermaid
graph TD
center[共享价值观<br/>Shared Values]
center --> S1[战略 Strategy]
center --> S2[结构 Structure]
center --> S3[系统 Systems]
center --> S4[风格 Style]
center --> S5[员工 Staff]
center --> S6[技能 Skills]
```
````

#### 项目管理类

**WBS工作分解**：
````markdown
```mermaid
graph TD
P[项目目标] --> A[阶段A]
P --> B[阶段B]
A --> A1[任务A1]
A --> A2[任务A2]
```
````

**甘特图**：
````markdown
```mermaid
gantt
title 项目进度计划
dateFormat YYYY-MM-DD
section 阶段1
  任务A :a1, 2026-01-01, 7d
  任务B :a2, after a1, 5d
section 阶段2
  任务C :b1, after a2, 10d
```
````

#### 营销销售类

**AARRR漏斗**：
````markdown
```mermaid
graph TD
A[获取 Acquisition] --> R1[激活 Activation]
R1 --> R2[留存 Retention]
R2 --> R3[收益 Revenue]
R3 --> R4[推荐 Referral]
```
````

#### 其他

**思维导图**：
````markdown
```mermaid
mindmap
root((核心主题))
  分支1
    子分支1.1
    子分支1.2
  分支2
    子分支2.1
```
````

**时序图**：
````markdown
```mermaid
sequenceDiagram
  participant A as 用户
  participant B as 系统
  participant C as 数据库
  A->>B: 请求数据
  B->>C: 查询数据
  C-->>B: 返回结果
  B-->>A: 响应数据
```
````

---

### 颜色编码系统（架构图规范）

| 组件类型 | 颜色 | 用途 |
|---------|------|------|
| 输入/输出 | `#3498db` 🟦 | 数据入口和出口 |
| 处理节点 | `#f39c12` 🟨 | 转换和处理逻辑 |
| 决策点 | `#e74c3c` 🟥 | 条件判断、分支 |
| 存储 | `#27ae60` 🟩 | 数据库、文件、缓存 |
| 融合/排序 | `#9b59b6` 🟪 | 多路合并、精排 |
| 外部服务 | `#2c3e50` ⬛ | 第三方依赖 |

**使用示例**：
````markdown
```mermaid
graph TB
A[用户输入] -->|文本| B[LLM处理]
B --> C{条件判断}
C -->|是| D[数据库存储]
C -->|否| E[缓存返回]
style A fill:#3498db,color:#fff
style B fill:#f39c12
style C fill:#e74c3c,color:#fff
style D fill:#27ae60
style E fill:#9b59b6,color:#fff
```
````

---

## 使用示例

### 示例 1：创建简单文档
```json
{
  "title": "项目计划",
  "markdown": "# 项目概述\n\n这是一个新项目。\n\n## 目标\n\n- 目标 1\n- 目标 2"
}
```

### 示例 2：创建到指定文件夹
```json
{
  "title": "会议纪要",
  "folder_token": "fldcnXXXXXXXXXXXXXXXXXXXXXX",
  "markdown": "# 周会 2025-01-15\n\n## 讨论议题\n\n1. 项目进度\n2. 下周计划"
}
```

### 示例 3：使用飞书扩展语法
```json
{
  "title": "产品需求",
  "markdown": "<callout emoji=\"💡\" background-color=\"light-blue\">\n重要需求说明\n</callout>\n\n## 功能列表\n\n| 功能 | 优先级 |\n|------|--------|\n| 登录 | P0 |\n| 导出 | P1 |"
}
```

### 示例 4：创建到知识库
```json
{
  "title": "技术文档",
  "wiki_node": "wikcnXXXXXXXXXXXXXXXXXXXXXX",
  "markdown": "# API 接口说明\n\n这是一个知识库文档。"
}
```

---

## 最佳实践

- **空行分隔**：不同块类型之间用空行分隔
- **转义字符**：特殊字符用 `\` 转义：`\*` `\~` `` \` ``
- **图片**：使用公开可访问的 URL，系统自动下载上传
- **分栏**：列宽总和必须为 100
- **表格选择**：简单数据用 Markdown，复杂嵌套用 `<lark-table>`
- **提及用户**：@用户用 `<mention-user id="ou_xxx"/>`，需先 search-user 获取 ID
- **目录**：飞书自动生成，无需手动添加
- **长文档**：分段创建，先用 create-doc 创建框架，再用 update-doc append 模式追加

---

## ⚠️ 重要注意事项

### Callout 高亮块限制
Callout 内部**不支持**：表格、代码块、嵌套 Callout、Grid 分栏、图片。

### 画板创建与读取
- **创建时**：使用 Mermaid/PlantUML 代码块
- **读取时**：返回 `<whiteboard token="xxx"/>`，无法获取原始源码
- **更新时**：无法直接修改，需替换为新代码块

### 图片/文件
- 创建时使用 URL，读取时返回 token
- 读取返回的 token 无法原样用于创建

### 多维表格/电子表格
只能创建空表，创建后使用对应 API 写入数据。
