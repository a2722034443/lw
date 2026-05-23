# 图件标准检索与绘制参考

## 检索来源优先级

1. 标准组织或官方规范：
   - 国际标准化组织流程图相关标准页面。
   - 对象管理组织 UML 规范页面。
   - diagrams.net 或 draw.io 官方文档。
2. 高校课程资料或教材式说明：
   - 软件工程课程中的用例图、活动图、时序图说明。
   - 数据库课程中的实体-联系图说明。
3. 学校论文格式文件：
   - 图名位置。
   - 图号编号方式。
   - 字体、字号、居中要求。
4. 工具文档：
   - diagrams.net 导入、导出、编辑 XML 的说明。

## 推荐检索词

### 实体-联系图

- “实体 联系 图 矩形 椭圆 菱形 基数”
- “数据库 ER 图 实体 属性 关系 画法”
- “Chen ER diagram entity attribute relationship cardinality”

### 用例图

- “UML 用例图 参与者 系统边界 包含 扩展”
- “OMG UML use case diagram actor include extend”
- “UML use case diagram standard notation”

### 流程图

- “流程图 标准符号 开始 结束 判断 处理 输入输出”
- “ISO 5807 flowchart symbols”
- “flowchart symbols process decision terminator input output”

### 活动图

- “UML 活动图 初始节点 结束节点 判断 泳道”
- “UML activity diagram initial final decision fork join”

### 时序图

- “UML 时序图 生命线 激活条 同步消息 返回消息”
- “UML sequence diagram lifeline activation message”

### 功能模块图

- “系统功能模块划分图 画法”
- “软件工程 功能模块图 层次结构”

### 系统架构图

- “系统架构图 分层架构 表现层 业务层 数据层”
- “software architecture diagram layered architecture”

### 数据流图

- “数据流图 外部实体 处理 数据存储 数据流”
- “DFD external entity process data store data flow”

## 常见错误

1. 把实体-联系图画成数据库表格。
2. 把用例图画成流程图。
3. 把功能模块图画成系统架构图。
4. 把数据流图画成业务流程图。
5. 所有节点都用同一种矩形，无法体现图类规范。
6. 使用英文表名和字段名，违反中文论文图件要求。
7. 节点文字过长，导入后挤出图形。
8. 线条大量交叉，关系看不清。
9. 没有图号和图名。
10. 图中使用彩色装饰，论文打印后辨识度下降。

## 实体-联系图中文转写建议

将数据库字段转换为中文属性，而不是原样写字段名：

| 字段或概念 | 图中写法 |
| --- | --- |
| id | 编号、主键编号 |
| username | 用户名 |
| role | 用户角色 |
| is_active | 账户状态 |
| user_id | 关联用户、上传患者、发起患者 |
| image_path | 图像路径 |
| description | 症状描述 |
| status | 状态、诊断状态、库存状态 |
| risk_level | 风险等级 |
| medical_advice | 医疗建议 |
| patient_id | 就诊患者 |
| diagnosis_id | 关联诊断 |
| present_illness | 现病史总结 |
| batch_number | 生产批次号 |
| quantity | 库存余量 |
| expiry_date | 有效期阈值 |

## 实体-联系图关系表达

如果用户没有给出额外关系，按表结构外键和业务语义推导：

- 拥有外键的一方通常是“多”。
- 被引用主键的一方通常是“一”。
- 一条病历只关联一条诊断记录时，诊断记录到病历档案可画“一对一”。
- 没有外键但存在后台管理语义时，用虚线表示业务维护关系。

## draw.io 样式片段

实体：

```text
rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;fontFamily=Microsoft YaHei,SimSun;fontSize=16;fontStyle=1;
```

属性：

```text
ellipse;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;fontFamily=Microsoft YaHei,SimSun;fontSize=13;
```

主键或外键属性：

```text
ellipse;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;fontFamily=Microsoft YaHei,SimSun;fontSize=13;fontStyle=4;
```

关系：

```text
rhombus;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;fontFamily=Microsoft YaHei,SimSun;fontSize=15;
```

普通连接：

```text
endArrow=none;html=1;strokeColor=#000000;fontFamily=Microsoft YaHei,SimSun;fontSize=14;
```

业务维护或可扩展关系：

```text
endArrow=none;html=1;strokeColor=#000000;dashed=1;fontFamily=Microsoft YaHei,SimSun;fontSize=14;
```
