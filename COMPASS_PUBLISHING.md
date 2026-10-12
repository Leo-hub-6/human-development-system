# 罗盘笔记发布约定

当前发布链路：

`Obsidian → git push → GitHub main → GitHub Actions → website-preview/index.html → EdgeOne 自动部署`

## 最小 Frontmatter

```yaml
---
id: C0001
type: compass
role: main
title: "标题"
input_type: 书籍
modules:
  - M02
  - M04
status: published
date: 2026-10-12
summary: "摘要"
---
```

规则：

- `status: draft`：不会进入网站。
- `status: published`：生成网页内容。
- `role: main`：既生成文章，也出现在“罗盘笔记”卡片列表。
- `role: child`：生成文章，但不出现在一级卡片列表；通过父文章中的 Obsidian WikiLink 进入。
- `id` 是稳定身份证，不承担网页排序。
- `order` 控制显示顺序；可以用 100、200、300 预留插入空间。
- `modules` 只写 M01–M10 代码，可多选。
- `input_type` 取值：书籍、课程、文章、论文、讲座、感悟、其他。
- `compass/` 下文件夹名称不参与发布逻辑；脚本递归读取 Markdown，因此以后合并“主内容/辅内容”目录也不影响发布。

## 主内容与子文章链接

Obsidian 中继续使用 WikiLink：

```md
[[C0001-A08-结构之问|结构之问：你的专业在社会这台机器里扮演什么角色？]]
```

只要目标文章也是 `status: published`，网站会自动把它转换成可点击的罗盘文章链接。

## 自动构建

工作流文件：`.github/workflows/build-compass.yml`。

当 `compass/**/*.md`、模板或构建脚本发生变化时，GitHub Actions 自动运行 `scripts/build_compass.py`，生成 `website-preview/index.html` 并提交。
